#!/usr/bin/env python3
"""A minimal single-user ActivityPub server for the Ivywall "Hello, Federation" guide.

Standard library plus the `openssl` command line only. It publishes one actor,
verifies signed inbox deliveries, answers Follow with Accept, delivers notes to
followers, and handles Undo, Delete and duplicate delivery without corrupting
its state. It is a teaching example: no timelines, OAuth, media or moderation.

Run:  python3 server.py --user alice --host example.org --port 8080 --data ./data
Behind a TLS proxy use --scheme https (the default). For local tests use
--scheme http --allow-private.
"""
import argparse
import base64
import hashlib
import ipaddress
import json
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from email.utils import formatdate, parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AS = "https://www.w3.org/ns/activitystreams"
PUBLIC = AS + "#Public"
MAX_BODY = 64 * 1024
MAX_FETCH = 1024 * 1024
DATE_SKEW = 300


# ---- crypto: RSA-SHA256 through the openssl command line -------------------

def openssl(args, data=b""):
    p = subprocess.run(["openssl"] + args, input=data, capture_output=True)
    return p.returncode, p.stdout


def make_key(path):
    if not os.path.exists(path):
        openssl(["genrsa", "-out", path, "2048"])
    return open(path).read(), openssl(["rsa", "-in", path, "-pubout"])[1].decode()


def rsa_sign(key_path, data):
    code, sig = openssl(["dgst", "-sha256", "-sign", key_path], data)
    if code:
        raise RuntimeError("openssl sign failed")
    return sig


def rsa_verify(pub_pem, data, sig):
    with tempfile.TemporaryDirectory() as d:
        pub, sf = os.path.join(d, "pub.pem"), os.path.join(d, "sig.bin")
        open(pub, "w").write(pub_pem)
        open(sf, "wb").write(sig)
        return openssl(["dgst", "-sha256", "-verify", pub, "-signature", sf], data)[0] == 0


# ---- legacy HTTP signatures (draft-cavage) ---------------------------------

def digest_of(body):
    return "SHA-256=" + base64.b64encode(hashlib.sha256(body).digest()).decode()


def signing_string(names, method, path, headers):
    lines = []
    for n in names:
        lines.append(f"(request-target): {method.lower()} {path}" if n == "(request-target)"
                     else f"{n}: {headers[n]}")
    return "\n".join(lines).encode()


def sign_headers(key_path, key_id, method, url, body):
    u = urllib.parse.urlparse(url)
    path = u.path + ("?" + u.query if u.query else "")
    h = {"host": u.netloc, "date": formatdate(usegmt=True), "digest": digest_of(body)}
    names = ["(request-target)", "host", "date", "digest"]
    sig = base64.b64encode(rsa_sign(key_path, signing_string(names, method, path, h))).decode()
    h["signature"] = (f'keyId="{key_id}",algorithm="rsa-sha256",'
                      f'headers="{" ".join(names)}",signature="{sig}"')
    return h


def parse_signature(value):
    return dict(re.findall(r'(\w+)="([^"]*)"', value))


# ---- the server ------------------------------------------------------------

class Actor:
    def __init__(self, user, host, scheme, data, allow_private=False, token="admin"):
        self.user, self.host, self.scheme = user, host, scheme
        self.base = f"{scheme}://{host}"
        self.id = f"{self.base}/users/{user}"
        self.allow_private = allow_private
        self.token = token
        os.makedirs(data, exist_ok=True)
        self.key_path = os.path.join(data, "key.pem")
        _, self.pub_pem = make_key(self.key_path)
        self.state_path = os.path.join(data, "state.json")
        self.lock = threading.RLock()
        self.cache = {}          # actor id -> (document, fetched_at)
        self.log = []            # delivery results, for tests
        self.state = {"followers": {}, "following": {}, "notes": {}, "remote": {}, "likes": {},
                      "boosts": {}, "applied": {}, "tombstones": [], "counter": 0}
        if os.path.exists(self.state_path):
            self.state = json.load(open(self.state_path))

    def save(self):
        tmp = self.state_path + ".tmp"
        json.dump(self.state, open(tmp, "w"), indent=1)
        os.replace(tmp, self.state_path)          # commit state before anything is acknowledged

    # -- documents
    def actor_doc(self):
        return {"@context": [AS, "https://w3id.org/security/v1"], "id": self.id, "type": "Person",
                "preferredUsername": self.user, "inbox": self.id + "/inbox",
                "outbox": self.id + "/outbox", "followers": self.id + "/followers",
                "publicKey": {"id": self.id + "#main-key", "owner": self.id,
                              "publicKeyPem": self.pub_pem}}

    def webfinger(self):
        return {"subject": f"acct:{self.user}@{self.host}",
                "links": [{"rel": "self", "type": "application/activity+json", "href": self.id}]}

    # -- outbound fetch with SSRF limits, no redirects, size and time limits
    def check_url(self, url):
        u = urllib.parse.urlparse(url)
        if u.scheme not in ("https", "http") or (u.scheme == "http" and self.scheme == "https"):
            raise ValueError("scheme not allowed")
        for fam, _, _, _, sa in socket.getaddrinfo(u.hostname, u.port or (443 if u.scheme == "https" else 80)):
            ip = ipaddress.ip_address(sa[0])
            if not self.allow_private and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved):
                raise ValueError("destination address not allowed")

    def request(self, method, url, body=None, signed=False, accept="application/activity+json"):
        self.check_url(url)
        headers = {"Accept": accept, "User-Agent": "ivywall-minimal-actor"}
        if body is not None:
            headers["Content-Type"] = "application/activity+json"
        if signed:
            headers.update(sign_headers(self.key_path, self.id + "#main-key", method, url, body or b""))
        req = urllib.request.Request(url, data=body, method=method, headers=headers)

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        opener = urllib.request.build_opener(NoRedirect)
        with opener.open(req, timeout=5) as r:
            return r.status, r.read(MAX_FETCH)

    def fetch_actor(self, url, force=False):
        with self.lock:
            hit = self.cache.get(url)
            if hit and not force:
                return hit[0]
            if hit and time.time() - hit[1] < 60:      # bounded refresh: one forced refetch a minute
                return hit[0]
        _, raw = self.request("GET", url)
        doc = json.loads(raw)
        if doc.get("id") != url:
            raise ValueError("actor id does not match the URL it was fetched from")
        with self.lock:
            self.cache[url] = (doc, time.time())
        return doc

    def resolve(self, acct):
        user, host = acct.removeprefix("acct:").split("@", 1)
        url = f"{self.scheme}://{host}/.well-known/webfinger?resource=acct:{urllib.parse.quote(user + '@' + host)}"
        _, raw = self.request("GET", url, accept="application/jrd+json")
        for link in json.loads(raw).get("links", []):
            if link.get("rel") == "self" and "activity+json" in link.get("type", ""):
                return self.fetch_actor(link["href"])
        raise ValueError("no ActivityPub self link")

    # -- delivery: signed POST with bounded retries; result recorded
    def deliver(self, inbox, activity, retries=3):
        body = json.dumps(activity).encode()

        def run():
            for attempt in range(retries):
                try:
                    status, _ = self.request("POST", inbox, body, signed=True)
                    self.log.append((inbox, activity["type"], status))
                    return
                except urllib.error.HTTPError as e:
                    self.log.append((inbox, activity["type"], e.code))
                    if 400 <= e.code < 500 and e.code != 429:
                        return                                  # permanent
                except Exception as e:                           # network error: retry
                    self.log.append((inbox, activity["type"], str(e)[:40]))
                time.sleep(2 ** attempt * 0.2)
        t = threading.Thread(target=run, daemon=True)
        t.start()
        return t

    def new_id(self, kind):
        with self.lock:
            self.state["counter"] += 1
            return f"{self.id}/{kind}/{self.state['counter']}"

    # -- inbound verification
    def verify(self, method, path, headers, body):
        """Return the actor id that signed the request, or raise PermissionError."""
        h = {k.lower(): v for k, v in headers.items()}
        if "signature" not in h:
            raise PermissionError("no signature")
        sig = parse_signature(h["signature"])
        names = sig.get("headers", "").split()
        for need in ("(request-target)", "host", "date", "digest"):
            if need not in names:
                raise PermissionError(f"{need} is not signed")
        if h.get("digest") != digest_of(body):
            raise PermissionError("digest does not match body")
        if abs(time.time() - parsedate_to_datetime(h["date"]).timestamp()) > DATE_SKEW:
            raise PermissionError("date outside allowed skew")
        key_id = sig["keyId"]
        owner = key_id.split("#")[0]
        data = signing_string(names, method, path, h)
        raw = base64.b64decode(sig["signature"])
        for force in (False, True):                       # second pass: bounded key refresh
            doc = self.fetch_actor(owner, force=force)
            pk = doc.get("publicKey", {})
            if pk.get("id") == key_id and pk.get("owner") == owner and rsa_verify(pk["publicKeyPem"], data, raw):
                return owner
        raise PermissionError("signature does not verify")

    # -- inbound processing: returns "applied" or "ignored"
    def handle(self, a, signer):
        if a.get("actor") != signer:
            raise PermissionError("activity actor is not the signing actor")
        aid, kind = a.get("id", ""), a.get("type")
        if urllib.parse.urlparse(aid).netloc != urllib.parse.urlparse(signer).netloc:
            raise PermissionError("activity id is not on the actor's host (policy)")
        with self.lock:
            if aid in self.state["applied"]:
                return "ignored"                          # replay of something already applied
            out = getattr(self, "on_" + str(kind).lower(), lambda *_: "ignored")(a, signer)
            if out == "applied":                          # remember only what changed state
                self.state["applied"][aid] = {"type": kind, "actor": signer, "object": a.get("object")}
            self.save()
            return out

    def obj_id(self, o):
        return o.get("id") if isinstance(o, dict) else o

    def on_follow(self, a, signer):
        if self.obj_id(a["object"]) != self.id:
            return "ignored"
        doc = self.fetch_actor(signer)
        self.state["followers"][signer] = {"inbox": doc["inbox"], "follow": a["id"]}
        self.save()                                       # persist first, then answer
        self.deliver(doc["inbox"], {"@context": AS, "id": self.new_id("activities"), "type": "Accept",
                                    "actor": self.id, "object": a})
        return "applied"

    def on_accept(self, a, signer):
        mine = self.obj_id(a.get("object"))
        f = self.state["following"].get(signer)
        if f and f["follow"] == mine:
            f["state"] = "accepted"
            return "applied"
        return "ignored"

    def on_reject(self, a, signer):
        mine = self.obj_id(a.get("object"))
        f = self.state["following"].get(signer)
        if f and f["follow"] == mine:
            f["state"] = "rejected"
            return "applied"
        return "ignored"

    def on_create(self, a, signer):
        n = a.get("object")
        if not isinstance(n, dict) or n.get("type") != "Note" or n.get("attributedTo") != signer:
            return "ignored"
        if n["id"] in self.state["tombstones"] or n["id"] in self.state["remote"]:
            return "ignored"                              # deleted earlier, or a duplicate object
        self.state["remote"][n["id"]] = n
        return "applied"

    def on_update(self, a, signer):
        n = a.get("object")
        old = self.state["remote"].get(n.get("id")) if isinstance(n, dict) else None
        if old and old.get("attributedTo") == signer:
            self.state["remote"][n["id"]] = n
            return "applied"
        return "ignored"

    def on_delete(self, a, signer):
        oid = self.obj_id(a.get("object"))
        old = self.state["remote"].get(oid)
        owned = (old and old.get("attributedTo") == signer) or (
            old is None and urllib.parse.urlparse(oid or "").netloc == urllib.parse.urlparse(signer).netloc)
        if not owned:
            return "ignored"
        self.state["remote"].pop(oid, None)
        if oid not in self.state["tombstones"]:
            self.state["tombstones"].append(oid)          # also when the object was never seen
        return "applied"

    def _local_note(self, a):
        return self.obj_id(a.get("object")) in self.state["notes"]

    def on_like(self, a, signer):
        if not self._local_note(a):
            return "ignored"
        self.state["likes"].setdefault(self.obj_id(a["object"]), {})[a["id"]] = signer
        return "applied"

    def on_announce(self, a, signer):
        if not self._local_note(a):
            return "ignored"
        self.state["boosts"].setdefault(self.obj_id(a["object"]), {})[a["id"]] = signer
        return "applied"

    def on_undo(self, a, signer):
        inner = a.get("object")
        if isinstance(inner, str):                        # id only: resolve from what we applied
            rec = self.state["applied"].get(inner)
            if not rec:
                return "ignored"                          # unknown: do NOT mark this Undo as applied
            inner = {"id": inner, "type": rec["type"], "actor": rec["actor"], "object": rec["object"]}
        if inner.get("actor") != signer:
            return "ignored"                              # may only undo your own activity
        iid, kind = inner["id"], inner.get("type")
        if kind == "Follow":
            return "applied" if self.state["followers"].pop(signer, None) else "ignored"
        bucket = {"Like": "likes", "Announce": "boosts"}.get(kind)
        for per_note in self.state.get(bucket, {}).values() if bucket else []:
            if per_note.pop(iid, None):
                return "applied"
        return "ignored"

    # -- local actions (admin API)
    def publish(self, content):
        with self.lock:
            nid = self.new_id("notes")
            note = {"id": nid, "type": "Note", "attributedTo": self.id, "content": content,
                    "published": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "to": [PUBLIC], "cc": [self.id + "/followers"]}
            self.state["notes"][nid] = note
            self.save()
            targets = {f["inbox"] for f in self.state["followers"].values()}   # one POST per inbox
        act = {"@context": AS, "id": self.new_id("activities"), "type": "Create", "actor": self.id,
               "to": note["to"], "cc": note["cc"], "object": note}
        return nid, [self.deliver(i, act) for i in targets]

    def follow(self, acct):
        doc = self.resolve(acct)
        with self.lock:
            fid = self.new_id("activities")
            self.state["following"][doc["id"]] = {"follow": fid, "state": "pending"}
            self.save()
        return self.deliver(doc["inbox"], {"@context": AS, "id": fid, "type": "Follow",
                                           "actor": self.id, "object": doc["id"]})


def make_handler(actor):
    class H(BaseHTTPRequestHandler):
        def send(self, status, doc, ctype="application/activity+json"):
            body = json.dumps(doc).encode() if not isinstance(doc, bytes) else doc
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            if u.path == "/.well-known/webfinger":
                want = urllib.parse.parse_qs(u.query).get("resource", [""])[0]
                if want.lower() == f"acct:{actor.user}@{actor.host}".lower():
                    return self.send(200, actor.webfinger(), "application/jrd+json")
                return self.send(404, {"error": "not found"})
            if u.path == "/users/" + actor.user:
                return self.send(200, actor.actor_doc())
            if u.path == actor.id.removeprefix(actor.base) + "/outbox":
                items = list(actor.state["notes"].values())
                return self.send(200, {"@context": AS, "id": actor.id + "/outbox", "type": "OrderedCollection",
                                       "totalItems": len(items), "orderedItems": items})
            note = actor.base + u.path
            if note in actor.state["notes"]:
                return self.send(200, actor.state["notes"][note])
            if u.path == "/admin/state" and self.headers.get("X-Admin-Token") == actor.token:
                return self.send(200, {k: v for k, v in actor.state.items() if k != "counter"})
            self.send(404, {"error": "not found"})

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                return self.send(413, {"error": "too large"})
            body = self.rfile.read(length)
            if self.path == f"/users/{actor.user}/inbox":
                try:
                    signer = actor.verify("POST", self.path, dict(self.headers), body)
                    out = actor.handle(json.loads(body), signer)
                except PermissionError as e:
                    return self.send(401, {"error": str(e)})
                except (ValueError, KeyError, TypeError, urllib.error.URLError) as e:
                    return self.send(400, {"error": str(e)[:80]})
                return self.send(202, {"result": out})      # 202 = received; "result" is for the tests
            if self.path.startswith("/admin/") and self.headers.get("X-Admin-Token") == actor.token:
                args = json.loads(body or b"{}")
                if self.path == "/admin/publish":
                    return self.send(200, {"id": actor.publish(args["content"])[0]})
                if self.path == "/admin/follow":
                    actor.follow(args["acct"])
                    return self.send(200, {"ok": True})
            self.send(404, {"error": "not found"})
    return H


def serve(actor, port):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(actor))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--host", required=True, help="public host name, with :port if not 443")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--data", default="./data")
    ap.add_argument("--scheme", default="https", choices=["https", "http"])
    ap.add_argument("--allow-private", action="store_true", help="tests only: allow loopback and private targets")
    ap.add_argument("--token", default=os.environ.get("ADMIN_TOKEN", ""))
    args = ap.parse_args()
    if not args.token:
        raise SystemExit("set --token or ADMIN_TOKEN for the admin endpoints")
    a = Actor(args.user, args.host, args.scheme, args.data, args.allow_private, args.token)
    serve(a, args.port)
    print(f"serving {a.id} on 127.0.0.1:{args.port}")
    threading.Event().wait()
