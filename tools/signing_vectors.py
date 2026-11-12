#!/usr/bin/env python3
"""Generate and verify the HTTP signature test vectors in testing/fixtures/signing/.

  python3 tools/signing_vectors.py verify     # check every vector (used by CI)
  python3 tools/signing_vectors.py generate   # rebuild vectors.json with a fresh throw-away key

Standard library plus the `openssl` command line. The private key exists only
during `generate` and is deleted; only the public key and the signatures are kept.
Each vector records the exact request and the expected verification result, so
an implementation can be tested without this script.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "testing", "fixtures", "signing", "vectors.json")
HOST_A, HOST_B = "a.example", "b.example"
BODY = '{"@context":"https://www.w3.org/ns/activitystreams","id":"https://a.example/activities/1","type":"Like","actor":"https://a.example/actor","object":"https://b.example/notes/1"}'
DATE = "Wed, 11 Nov 2026 12:00:00 GMT"
CREATED = 1794398400


def sh(args, data=b""):
    p = subprocess.run(["openssl"] + args, input=data, capture_output=True)
    return p.returncode, p.stdout


def verify_rsa(pub_pem, data, sig):
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "p"), "w").write(pub_pem)
        open(os.path.join(d, "s"), "wb").write(sig)
        return sh(["dgst", "-sha256", "-verify", os.path.join(d, "p"), "-signature", os.path.join(d, "s")], data)[0] == 0


def legacy_digest(body):
    return "SHA-256=" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()


def content_digest(body):
    return "sha-256=:" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode() + ":"


def legacy_base(names, method, path, headers):
    return "\n".join(f"(request-target): {method.lower()} {path}" if n == "(request-target)" else f"{n}: {headers[n]}"
                     for n in names)


def rfc9421_base(comps, method, target, headers, params):
    lines = []
    for c in comps:
        lines.append(f'"{c}": ' + (method if c == "@method" else target if c == "@target-uri" else headers[c]))
    lines.append(f'"@signature-params": {params}')
    return "\n".join(lines)


def check(v, pub):
    """Return (verifies, reason) for one vector, recomputing everything from the request."""
    h = {k.lower(): x for k, x in v["headers"].items()}
    body = v["body"]
    if v["scheme"] == "legacy":
        sig = dict(re.findall(r'(\w+)="([^"]*)"', h["signature"]))
        names = sig["headers"].split()
        if "digest" not in names:
            return False, "digest not signed"
        if h["digest"] != legacy_digest(body):
            return False, "digest does not match body"
        path = urlparse(v["target"]).path
        base = legacy_base(names, v["method"], path, h)
        ok = verify_rsa(pub, base.encode(), base64.b64decode(sig["signature"]))
        return ok, "" if ok else "signature does not verify"
    inp = h["signature-input"]
    label, params = inp.split("=", 1)
    comps = re.findall(r'"([^"]+)"', params.split(")")[0])
    if "content-digest" not in comps:
        return False, "content-digest not signed"
    if h["content-digest"] != content_digest(body):
        return False, "content-digest does not match body"
    base = rfc9421_base(comps, v["method"], v["target"], h, params)
    sigb = re.search(r":([^:]+):", h["signature"]).group(1)
    ok = verify_rsa(pub, base.encode(), base64.b64decode(sigb))
    return ok, "" if ok else "signature does not verify"


def build(key_path):
    def sign(base):
        return base64.b64encode(sh(["dgst", "-sha256", "-sign", key_path], base.encode())[1]).decode()

    target = f"https://{HOST_B}/users/bob/inbox"
    path = "/users/bob/inbox"
    vectors = []

    def legacy(vid, desc, body=BODY, names=("(request-target)", "host", "date", "digest"), sign_path=path,
               header_digest=None, expected=(True, "")):
        h = {"host": HOST_B, "date": DATE, "digest": header_digest or legacy_digest(BODY)}
        sig = sign(legacy_base(list(names), "POST", sign_path, h))
        h["signature"] = (f'keyId="https://{HOST_A}/actor#main-key",algorithm="rsa-sha256",'
                          f'headers="{" ".join(names)}",signature="{sig}"')
        vectors.append({"id": vid, "scheme": "legacy", "description": desc, "method": "POST", "target": target,
                        "body": body, "headers": h, "expected": {"verifies": expected[0], "reason": expected[1]}})

    legacy("legacy-valid", "Valid draft-cavage signature over request-target, host, date and digest.")
    legacy("legacy-body-modified", "Body changed after signing: the Digest no longer matches.",
           body=BODY.replace("Like", "Lake"), expected=(False, "digest does not match body"))
    legacy("legacy-digest-not-signed", "The signature does not cover the Digest header, so the body is unprotected.",
           names=("(request-target)", "host", "date"), expected=(False, "digest not signed"))
    legacy("legacy-wrong-path", "Signed for a different request-target than the one delivered.",
           sign_path="/users/carol/inbox", expected=(False, "signature does not verify"))

    def rfc(vid, desc, body=BODY, comps=("@method", "@target-uri", "content-digest"), sign_target=target,
            expected=(True, "")):
        h = {"content-digest": content_digest(BODY)}
        params = "(" + " ".join(f'"{c}"' for c in comps) + f');created={CREATED};keyid="https://{HOST_A}/actor#main-key";alg="rsa-v1_5-sha256"'
        sig = sign(rfc9421_base(list(comps), "POST", sign_target, h, params))
        h["signature-input"] = "sig1=" + params
        h["signature"] = f"sig1=:{sig}:"
        vectors.append({"id": vid, "scheme": "rfc9421", "description": desc, "method": "POST", "target": target,
                        "body": body, "headers": h, "expected": {"verifies": expected[0], "reason": expected[1]}})

    rfc("rfc9421-valid", "Valid RFC 9421 signature with rsa-v1_5-sha256 over @method, @target-uri and content-digest.")
    rfc("rfc9421-body-modified", "Body changed after signing: Content-Digest no longer matches.",
        body=BODY.replace("Like", "Lake"), expected=(False, "content-digest does not match body"))
    rfc("rfc9421-digest-not-signed", "content-digest is not a covered component.",
        comps=("@method", "@target-uri"), expected=(False, "content-digest not signed"))
    rfc("rfc9421-wrong-target", "Signed for a different target URI.",
        sign_target=f"https://{HOST_B}/users/carol/inbox", expected=(False, "signature does not verify"))
    return vectors


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if mode == "generate":
        with tempfile.TemporaryDirectory() as d:
            key = os.path.join(d, "k.pem")
            sh(["genrsa", "-out", key, "2048"])
            pub = sh(["rsa", "-in", key, "-pubout"])[1].decode()
            doc = {"note": "Test vectors. The key is a throw-away generated for these vectors; its private half was deleted. "
                           "Hosts use .example names. Every request is constructed, none captured.",
                   "public_key": pub, "date_used": DATE, "vectors": build(key)}
        json.dump(doc, open(OUT, "w"), indent=1)
        print(f"wrote {len(doc['vectors'])} vectors")
        return 0
    doc = json.load(open(OUT))
    bad = 0
    for v in doc["vectors"]:
        ok, why = check(v, doc["public_key"])
        want = v["expected"]
        good = ok == want["verifies"] and (ok or why == want["reason"])
        bad += not good
        print(("PASS " if good else "FAIL ") + v["id"] + ("" if good else f"  got ({ok}, {why!r}) want {want}"))
    print(f"{len(doc['vectors']) - bad}/{len(doc['vectors'])} vectors behave as expected")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
