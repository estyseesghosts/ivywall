#!/usr/bin/env python3
"""A minimal single-user ActivityPub server for the Ivywall "Hello, Federation" guide.

Standard library plus the `openssl` command. It publishes one actor, verifies signed inbox
deliveries, answers Follow with Accept, delivers notes to followers, and keeps its state correct
under duplicates, reordering and Undo. A teaching example: no timelines, edits, media or queue.

  python3 server.py --user alice --host example.org --port 8080 --data ./data --token SECRET
Run it behind a TLS proxy (--scheme https, the default); --scheme http --allow-private is for tests.
"""
import argparse, base64, hashlib, ipaddress, json, os, re, socket, subprocess, tempfile, threading, time
from functools import partialmethod
import urllib.error, urllib.parse, urllib.request
from email.utils import formatdate, parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AS = "https://www.w3.org/ns/activitystreams"
SIGNED_HEADERS = ["(request-target)", "host", "date", "digest"]
MAX_BODY_BYTES, MAX_CLOCK_SKEW_SECONDS = 64 * 1024, 300
NO_REDIRECTS = urllib.request.build_opener(  # a redirect could lead a fetch to an address we never checked
    type("NoRedirects", (urllib.request.HTTPRedirectHandler,), {"redirect_request": lambda *args, **kwargs: None}))


# ---- RSA-SHA256 through the openssl command line, and legacy (draft-cavage) HTTP signatures

def openssl(*arguments, data=b""):
    done = subprocess.run(["openssl", *arguments], input=data, capture_output=True)
    return done.returncode == 0, done.stdout

def rsa_verify(public_key_pem, data, signature):
    with tempfile.TemporaryDirectory() as folder:
        open(folder + "/key.pem", "w").write(public_key_pem)
        open(folder + "/signature", "wb").write(signature)
        return openssl("dgst", "-sha256", "-verify", folder + "/key.pem", "-signature", folder + "/signature", data=data)[0]

def digest_header(body):
    return "SHA-256=" + base64.b64encode(hashlib.sha256(body).digest()).decode()

def signing_string(signed_names, method, path, headers):
    return "\n".join(f"(request-target): {method.lower()} {path}" if name == "(request-target)"
                     else f"{name}: {headers[name]}" for name in signed_names).encode()

def sign_headers(key_path, key_id, method, url, body):
    parts = urllib.parse.urlparse(url)
    headers = {"host": parts.netloc, "date": formatdate(usegmt=True), "digest": digest_header(body)}
    signature = openssl("dgst", "-sha256", "-sign", key_path, data=signing_string(SIGNED_HEADERS, method, parts.path, headers))[1]
    headers["signature"] = (f'keyId="{key_id}",algorithm="rsa-sha256",headers="{" ".join(SIGNED_HEADERS)}",'
                            f'signature="{base64.b64encode(signature).decode()}"')
    return headers


# ---- the actor: identity, state, outbound requests, inbound verification and handlers

class Actor:
    def __init__(self, user, host, scheme, data_folder, allow_private=False, token=""):
        self.user, self.host, self.scheme, self.allow_private, self.token = user, host, scheme, allow_private, token
        self.id = f"{scheme}://{host}/users/{user}"
        os.makedirs(data_folder, exist_ok=True)
        self.key_path, self.state_path = data_folder + "/key.pem", data_folder + "/state.json"
        if not os.path.exists(self.key_path):
            openssl("genrsa", "-out", self.key_path, "2048")
        self.public_key_pem = openssl("rsa", "-in", self.key_path, "-pubout")[1].decode()
        self.lock, self.cached_actors, self.log = threading.RLock(), {}, []    # log: one entry per delivery attempt
        self.state = {"followers": {}, "following": {}, "notes": {}, "remote": {}, "likes": {}, "boosts": {},
                      "applied": {}, "tombstones": [], "counter": 0}
        if os.path.exists(self.state_path):
            self.state = json.load(open(self.state_path))

    def save(self):
        json.dump(self.state, open(self.state_path + ".tmp", "w"))
        os.replace(self.state_path + ".tmp", self.state_path)        # atomic: state is never half-written

    def new_id(self, kind):
        self.state["counter"] += 1
        return f"{self.id}/{kind}/{self.state['counter']}"

    def actor_document(self):
        return {"@context": [AS, "https://w3id.org/security/v1"], "id": self.id, "type": "Person",
                "preferredUsername": self.user, "inbox": self.id + "/inbox", "outbox": self.id + "/outbox",
                "publicKey": {"id": self.id + "#main-key", "owner": self.id, "publicKeyPem": self.public_key_pem}}

    # -- outbound requests: same scheme only, no private addresses unless allowed, no redirects

    def check_url(self, url):
        parts = urllib.parse.urlparse(url)
        if parts.scheme != self.scheme:
            raise ValueError("scheme not allowed")
        for *_, address in socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == "https" else 80)):
            ip = ipaddress.ip_address(address[0])
            if not self.allow_private and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved):
                raise ValueError("destination address not allowed")

    def request(self, method, url, body=None, signed=False, accept="application/activity+json"):
        self.check_url(url)
        headers = {"Accept": accept, "Content-Type": "application/activity+json"}
        if signed:
            headers.update(sign_headers(self.key_path, self.id + "#main-key", method, url, body or b""))
        with NO_REDIRECTS.open(urllib.request.Request(url, body, headers, method=method), timeout=5) as response:
            return response.status, response.read(1024 * 1024)

    def fetch_actor(self, actor_id, force=False):
        cached = self.cached_actors.get(actor_id)
        if cached and (not force or time.time() - cached[1] < 60):    # a forced refresh happens at most once a minute
            return cached[0]
        document = json.loads(self.request("GET", actor_id)[1])
        if document.get("id") != actor_id:
            raise ValueError("actor id does not match the URL it was fetched from")
        self.cached_actors[actor_id] = (document, time.time())
        return document

    def resolve(self, handle):
        """acct:user@host -> actor document, through WebFinger."""
        user, host = handle.removeprefix("acct:").split("@", 1)
        url = f"{self.scheme}://{host}/.well-known/webfinger?resource=acct:{user}@{host}"
        links = json.loads(self.request("GET", url, accept="application/jrd+json")[1])["links"]
        return self.fetch_actor(next(link["href"] for link in links if link["rel"] == "self"))

    def deliver(self, inbox, activity, attempts=3):
        """POST a signed activity from a background thread. Retry network errors and 5xx, never other 4xx."""
        def post_with_retries():
            for attempt in range(attempts):
                try:
                    outcome = self.request("POST", inbox, json.dumps(activity).encode(), signed=True)[0]
                except urllib.error.HTTPError as error:
                    outcome = error.code
                except OSError as error:
                    outcome = str(error)[:40]
                self.log.append((inbox, activity["type"], outcome))
                if isinstance(outcome, int) and outcome < 500:
                    return                                            # delivered, or permanently refused
                time.sleep(0.2 * 2 ** attempt)
        thread = threading.Thread(target=post_with_retries, daemon=True)
        thread.start()
        return thread

    # -- inbound: verify who signed, check they may do what they claim, then apply

    def verify(self, path, headers, body):
        """Return the id of the actor whose key signed this POST, or raise PermissionError."""
        headers = {name.lower(): value for name, value in headers.items()}
        signature = dict(re.findall(r'(\w+)="([^"]*)"', headers.get("signature", "")))
        names = signature.get("headers", "").split()
        if not set(SIGNED_HEADERS) <= set(names):
            raise PermissionError("signature is missing or does not cover the required headers")
        if headers.get("digest") != digest_header(body):
            raise PermissionError("digest does not match body")
        if abs(time.time() - parsedate_to_datetime(headers["date"]).timestamp()) > MAX_CLOCK_SKEW_SECONDS:
            raise PermissionError("date outside allowed skew")
        owner = signature["keyId"].split("#")[0]
        for refetch_key in (False, True):                  # second pass: the owner may have rotated its key
            key = self.fetch_actor(owner, force=refetch_key).get("publicKey", {})
            if key.get("id") == signature["keyId"] and key.get("owner") == owner and rsa_verify(
                    key["publicKeyPem"], signing_string(names, "POST", path, headers), base64.b64decode(signature["signature"])):
                return owner
        raise PermissionError("signature does not verify")

    def handle(self, activity, signer):
        """Apply one verified activity. Returns "applied" or "ignored"; raises PermissionError if forged."""
        if activity.get("actor") != signer:
            raise PermissionError("activity actor is not the signing actor")
        if urllib.parse.urlparse(activity["id"]).netloc != urllib.parse.urlparse(signer).netloc:
            raise PermissionError("activity id is not on the actor's host (policy)")
        with self.lock:
            handler = getattr(self, "on_" + str(activity.get("type")).lower(), None)
            if activity["id"] in self.state["applied"] or not handler:
                return "ignored"                           # a replay of something already applied, or unsupported
            outcome = handler(activity, signer)
            if outcome == "applied":                       # remember only what actually changed state
                self.state["applied"][activity["id"]] = {k: activity.get(k) for k in ("type", "actor", "object")}
            self.save()                                    # commit before the caller sends 202
            return outcome

    @staticmethod
    def id_of(thing):
        return thing.get("id") if isinstance(thing, dict) else thing

    def on_follow(self, activity, signer):
        if self.id_of(activity["object"]) != self.id:
            return "ignored"
        inbox = self.fetch_actor(signer)["inbox"]
        self.state["followers"][signer] = {"inbox": inbox}
        self.save()                                        # persist the follower first, then answer
        self.deliver(inbox, {"@context": AS, "id": self.new_id("activities"), "type": "Accept",
                             "actor": self.id, "object": activity})
        return "applied"

    def on_accept(self, activity, signer):
        follow = self.state["following"].get(signer)
        if follow and follow["follow"] == self.id_of(activity.get("object")):
            follow["state"] = "accepted"
            return "applied"
        return "ignored"

    def on_create(self, activity, signer):
        note = activity.get("object")
        if not isinstance(note, dict) or note.get("type") != "Note" or note.get("attributedTo") != signer:
            return "ignored"
        if note["id"] in self.state["tombstones"] or note["id"] in self.state["remote"]:
            return "ignored"                               # deleted earlier, or already stored
        self.state["remote"][note["id"]] = note
        return "applied"

    def on_delete(self, activity, signer):
        object_id = self.id_of(activity.get("object"))
        stored = self.state["remote"].get(object_id)
        # Only the owner may delete. An object we never saw is presumed owned by whoever shares its host.
        shares_host = urllib.parse.urlparse(str(object_id)).netloc == urllib.parse.urlparse(signer).netloc
        if not (stored["attributedTo"] == signer if stored else shares_host):
            return "ignored"
        self.state["remote"].pop(object_id, None)
        if object_id not in self.state["tombstones"]:
            self.state["tombstones"].append(object_id)     # remembered even if the object was never seen
        return "applied"

    def record_reaction(self, bucket, activity, signer):
        note_id = self.id_of(activity.get("object"))
        if note_id not in self.state["notes"]:
            return "ignored"
        self.state[bucket].setdefault(note_id, {})[activity["id"]] = signer
        return "applied"

    on_like = partialmethod(record_reaction, "likes")
    on_announce = partialmethod(record_reaction, "boosts")

    def on_undo(self, activity, signer):
        undone = activity.get("object")
        if isinstance(undone, str):                        # an id only: recover what we applied under it
            undone = {"id": undone, **self.state["applied"].get(undone, {"actor": None})}
        if undone.get("actor") != signer:
            return "ignored"                               # unknown activity, or nobody may undo another's
        if undone["type"] == "Follow":
            return "applied" if self.state["followers"].pop(signer, None) else "ignored"
        bucket = {"Like": "likes", "Announce": "boosts"}.get(undone["type"], "likes")
        for reactions_to_one_note in self.state[bucket].values():    # {activity id: actor} per note
            if reactions_to_one_note.pop(undone["id"], None):
                return "applied"
        return "ignored"

    # -- local actions

    def publish(self, content):
        with self.lock:
            note = {"id": self.new_id("notes"), "type": "Note", "attributedTo": self.id, "content": content,
                    "to": [AS + "#Public"], "cc": [self.id + "/followers"]}
            self.state["notes"][note["id"]] = note
            self.save()
            inboxes = {follower["inbox"] for follower in self.state["followers"].values()}   # one POST per inbox
        create = {"@context": AS, "id": self.new_id("activities"), "type": "Create", "actor": self.id,
                  "to": note["to"], "cc": note["cc"], "object": note}
        return note["id"], [self.deliver(inbox, create) for inbox in inboxes]

    def follow(self, handle):
        target = self.resolve(handle)
        with self.lock:
            follow = {"@context": AS, "id": self.new_id("activities"), "type": "Follow", "actor": self.id, "object": target["id"]}
            self.state["following"][target["id"]] = {"follow": follow["id"], "state": "pending"}
            self.save()
        return self.deliver(target["inbox"], follow)


# ---- HTTP: discovery, the actor, the inbox, and token-protected admin calls

def serve(actor, port):
    inbox_path = urllib.parse.urlparse(actor.id).path + "/inbox"

    class Handler(BaseHTTPRequestHandler):
        log_message = lambda *_: None

        def reply(self, status, document, content_type="application/activity+json"):
            body = json.dumps(document).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urllib.parse.urlparse(self.path)
            handle = f"acct:{actor.user}@{actor.host}"
            if url.path == "/.well-known/webfinger" and urllib.parse.parse_qs(url.query).get("resource") == [handle]:
                return self.reply(200, {"subject": handle, "links": [{"rel": "self", "href": actor.id,
                                  "type": "application/activity+json"}]}, "application/jrd+json")
            if url.path == urllib.parse.urlparse(actor.id).path:
                return self.reply(200, actor.actor_document())
            self.reply(404, {"error": "not found"})

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length <= MAX_BODY_BYTES else None
            if body is None:
                return self.reply(413, {"error": "too large"})
            if self.path == inbox_path:
                try:
                    signer = actor.verify(self.path, dict(self.headers), body)
                    return self.reply(202, {"result": actor.handle(json.loads(body), signer)})  # 202 means received
                except PermissionError as error:
                    return self.reply(401, {"error": str(error)})
                except (ValueError, KeyError, TypeError, urllib.error.URLError) as error:
                    return self.reply(400, {"error": str(error)[:80]})
            if actor.token and self.headers.get("X-Admin-Token") == actor.token:
                arguments = json.loads(body or b"{}")
                if self.path == "/admin/publish":
                    return self.reply(200, {"id": actor.publish(arguments["content"])[0]})
                if self.path == "/admin/follow":
                    return self.reply(200, {"queued": bool(actor.follow(arguments["handle"]))})
            self.reply(404, {"error": "not found"})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--host", required=True, help="public host name, with :port if not 443")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--data", default="./data")
    parser.add_argument("--scheme", default="https", choices=["https", "http"])
    parser.add_argument("--allow-private", action="store_true", help="tests only: allow loopback and private targets")
    parser.add_argument("--token", default=os.environ.get("ADMIN_TOKEN", ""), help="enables the admin calls")
    options = parser.parse_args()
    local_actor = Actor(options.user, options.host, options.scheme, options.data, options.allow_private, options.token)
    serve(local_actor, options.port)
    print(f"serving {local_actor.id} on 127.0.0.1:{options.port}")
    threading.Event().wait()
