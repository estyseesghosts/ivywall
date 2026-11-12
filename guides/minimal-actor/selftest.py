#!/usr/bin/env python3
"""Self-test for server.py: two instances on loopback exchange real signed HTTP.

It checks the milestones in the guide: discovery, signed inbox, Follow/Accept,
publishing, Like and Undo, duplicate delivery, Delete before Create, and a set
of deliberately invalid requests. Exit status is non-zero if any check fails.
This tests the example against itself; it is not an interoperability test.
"""
import json
import sys
import tempfile
import time
import urllib.error
import urllib.request

import server as S

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  ({detail})" if detail and not ok else ""))


def wait(cond, secs=10):
    end = time.time() + secs
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.1)
    return False


def post(url, body, headers):
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def signed_post(sender, target_actor, activity, mutate=None):
    """POST `activity` to target_actor's inbox, signed as `sender`."""
    url = target_actor.id + "/inbox"
    body = json.dumps(activity).encode()
    h = S.sign_headers(sender.key_path, sender.id + "#main-key", "POST", url, body)
    h["Content-Type"] = "application/activity+json"
    if mutate:
        body, h = mutate(body, h)
    return post(url, body, h)


def main():
    tmp = tempfile.mkdtemp()
    A = S.Actor("alice", "127.0.0.1:18081", "http", tmp + "/a", allow_private=True, token="t")
    B = S.Actor("bob", "127.0.0.1:18082", "http", tmp + "/b", allow_private=True, token="t")
    sa, sb = S.serve(A, 18081), S.serve(B, 18082)

    # 1. discovery
    doc = A.resolve("acct:alice@127.0.0.1:18081")
    check("webfinger resolves to the actor document", doc["id"] == A.id and doc["publicKey"]["owner"] == A.id)

    # 2. follow, accept
    B.follow("acct:alice@127.0.0.1:18081")
    check("Follow arrives, is persisted, and is answered with Accept",
          wait(lambda: B.id in A.state["followers"] and B.state["following"].get(A.id, {}).get("state") == "accepted"))

    # 3. publish and deliver
    nid, threads = A.publish("Hello, federation")
    for t in threads:
        t.join(10)
    check("a published note is delivered to the follower's inbox once", nid in B.state["remote"]
          and sum(1 for x in A.log if x[1] == "Create") == 1)

    # 4. like and undo
    like = {"@context": S.AS, "id": B.id + "/activities/like1", "type": "Like", "actor": B.id, "object": nid}
    check("a signed Like is applied", signed_post(B, A, like)[1].get("result") == "applied" and nid in A.state["likes"])
    check("the same Like delivered again has no second effect", signed_post(B, A, like)[1].get("result") == "ignored")
    undo = {"@context": S.AS, "id": B.id + "/activities/undo1", "type": "Undo", "actor": B.id, "object": like["id"]}
    signed_post(B, A, undo)
    check("Undo naming the Like id removes it", not A.state["likes"].get(nid))
    undo_unknown = {"@context": S.AS, "id": B.id + "/activities/undo2", "type": "Undo", "actor": B.id,
                    "object": B.id + "/activities/never-seen"}
    r = signed_post(B, A, undo_unknown)[1].get("result")
    check("Undo of an unknown activity is ignored and not recorded as applied",
          r == "ignored" and undo_unknown["id"] not in A.state["applied"])

    # 5. delete before create must not resurrect
    note_id = B.id + "/notes/ghost"
    delete = {"@context": S.AS, "id": B.id + "/activities/del1", "type": "Delete", "actor": B.id, "object": note_id}
    signed_post(B, A, delete)
    create = {"@context": S.AS, "id": B.id + "/activities/cr1", "type": "Create", "actor": B.id,
              "object": {"id": note_id, "type": "Note", "attributedTo": B.id, "content": "late"}}
    r = signed_post(B, A, create)[1].get("result")
    check("a Create arriving after its Delete is refused", r == "ignored" and note_id not in A.state["remote"])

    # 5b. duplicate Create has no second effect
    dup = {"@context": S.AS, "id": B.id + "/activities/cr2", "type": "Create", "actor": B.id,
           "object": {"id": B.id + "/notes/dup", "type": "Note", "attributedTo": B.id, "content": "once"}}
    first = signed_post(B, A, dup)[1].get("result")
    again = signed_post(B, A, dup)[1].get("result")
    check("a Create delivered twice is stored once", first == "applied" and again == "ignored"
          and sum(1 for k in A.state["remote"] if k.endswith("/notes/dup")) == 1)

    # 6. deleting someone else's object is refused
    other = {"@context": S.AS, "id": B.id + "/activities/del2", "type": "Delete", "actor": B.id,
             "object": A.id + "/notes/1"}
    check("Delete of an object on another host is ignored",
          signed_post(B, A, other)[1].get("result") == "ignored" and (A.id + "/notes/1") not in A.state["tombstones"])

    # 7. invalid requests
    ok_activity = {"@context": S.AS, "id": B.id + "/activities/like2", "type": "Like", "actor": B.id, "object": nid}

    def tamper(body, h):
        return body.replace(b"like2", b"like3"), h
    check("modified body is rejected (401)", signed_post(B, A, ok_activity, tamper)[0] == 401)

    def drop_sig(body, h):
        h.pop("signature")
        return body, h
    check("missing signature is rejected (401)", signed_post(B, A, ok_activity, drop_sig)[0] == 401)

    def old_date(body, h):
        h["date"] = "Mon, 01 Jan 2024 00:00:00 GMT"
        return body, h
    check("stale Date is rejected (401)", signed_post(B, A, ok_activity, old_date)[0] == 401)

    spoof = {"@context": S.AS, "id": B.id + "/activities/like4", "type": "Like", "actor": A.id, "object": nid}
    check("valid signature but a different claimed actor is rejected (401)", signed_post(B, A, spoof)[0] == 401)

    wrong_host = {"@context": S.AS, "id": "http://127.0.0.1:18081/activities/x", "type": "Like", "actor": B.id,
                  "object": nid}
    check("activity id on another host is rejected (401)", signed_post(B, A, wrong_host)[0] == 401)

    try:
        A.allow_private = False
        A.check_url("http://127.0.0.1:9/x")
        blocked = False
    except ValueError:
        blocked = True
    A.allow_private = True
    check("remote fetch of a loopback address is refused when private targets are not allowed", blocked)

    sa.shutdown()
    sb.shutdown()
    print(f"{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
