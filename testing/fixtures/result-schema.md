# Interoperability result fixture format

A compatibility claim is only as good as the record behind it. This page defines the machine-readable record that every interoperability result should be stored as, so that sender, receiver, exact build, feature, emitted and accepted representations, final state and uncertainty are never lost between a test run and a compatibility table. No fixtures exist yet; this is the format they will use.

## Before you start

The format follows the recommendations in [test oracles](../interoperability/test-oracles.md) and the [test matrix](../interoperability/test-matrix.md). It is a design (`[hypothesis]` as a method) and has not been used for a real run.

## One record per directed pair per feature

A record describes one sender, one receiver and one feature, in one direction. The reverse direction is a separate record.

| Field | Type | Meaning |
| ----- | ---- | ------- |
| `id` | string | Stable id: `feature/sender/receiver/runid` |
| `feature` | string | Wiki feature key, for example `poll-vote` |
| `sender` | object | `software`, `version`, `build` (image digest or commit), `config` (flags that matter, search backend on or off) |
| `receiver` | object | Same shape as `sender` |
| `emitted` | object | `representation` (a short name such as `Create(Answer)`), `payload` (path to the captured or constructed JSON), `provenance` (`captured` or `constructed`) |
| `accepted` | object | What the receiver did with it: one of `native`, `translated`, `ignored`, `rejected`, `lossy`, `untested`, plus `detail` |
| `http` | object | Delivery response: `status`, `headers` path, `elapsed_ms` |
| `final_state` | object | `checks`: a list of `{where, query, expected, observed}`, where `where` is `sender`, `receiver` or `client`, and `deadline_s` |
| `classification` | enum | `verified-compatible`, `verified-incompatible`, `eventually-convergent`, `harness-invalid`, `unresolved` |
| `evidence` | enum | How it was established: `running-instance`, `captured-payload`, `source-reading`, `inferred` |
| `uncertainty` | string | What would change the conclusion |
| `observed_at` | string | UTC timestamp of the run |
| `sanitized` | boolean | True only if tokens, keys and non-public content were removed |

Rules: `classification` may only be `verified-compatible` if a `final_state` check at the receiver passed after the stated deadline; an HTTP 2xx alone never qualifies. `inferred` evidence cannot yield a `verified-*` class.

## Example

Constructed to show the shape. It is not a real result.

```json
{
  "id": "poll-vote/akkoma/catodon/example-run",
  "feature": "poll-vote",
  "sender":   { "software": "Akkoma",  "version": "unknown", "build": "sha256:<digest>", "config": { "search": false } },
  "receiver": { "software": "Catodon", "version": "unknown", "build": "sha256:<digest>", "config": {} },
  "emitted":  { "representation": "Create(Answer)", "payload": "payloads/vote-1.json", "provenance": "constructed" },
  "accepted": { "value": "untested", "detail": "" },
  "http":     { "status": 202, "headers": "headers/vote-1.txt", "elapsed_ms": 41 },
  "final_state": {
    "deadline_s": 60,
    "checks": [{ "where": "receiver", "query": "poll option tally", "expected": 1, "observed": null }]
  },
  "classification": "unresolved",
  "evidence": "inferred",
  "uncertainty": "No receiver-side trace; tally read only through the client API.",
  "observed_at": "2026-11-11T00:00:00Z",
  "sanitized": true
}
```

## Technical details

- Store fixtures under `testing/fixtures/<run-id>/` as one JSON file per record plus a `payloads/` and `headers/` directory. Compatibility pages may be generated from them; a generated page names the run id and date.
- A page that cites a fixture links the record, not a screenshot.
- Never commit real credentials, real keys or non-public content. Use fixture accounts; set `sanitized` only after checking.

## Open questions

Whether to adopt FediTest's result format instead of this one is undecided; compare them before the first run.

## Sources

- [FediTest](https://feditest.org/) — an existing federation test framework whose format should be compared
- [Test oracles that give false federation failures](../interoperability/test-oracles.md) — the five-way outcome model this format reuses
