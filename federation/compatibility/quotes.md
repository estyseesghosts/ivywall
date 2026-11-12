# Compatibility: quote posts

A quote post refers to another post while adding its author's own content. Servers disagree on how to express that relationship and whether they negotiate the quoted author's permission. A visible link to a post, a structured quote relationship, and an authorization to quote are three separate things. The entries below describe source code in [Mastodon 4.7.3](../../references/software/mastodon.md) and [Misskey 2026.10.1](../../references/software/misskey.md); they do not establish a live end-to-end result.

## Summary

| Software | Version | Emits | Accepts | Notes |
| -------- | ------- | ----- | ------- | ----- |
| Mastodon | 4.7.3 | native | native / translated | Emits structured `quote`, legacy aliases when serializable, and an authorization URI when present; the parser recognizes multiple quote fields. Processing and approval depend on policy and state. `[source]` [serializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/note_serializer.rb), [parser](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/parser/status_parser.rb), [request handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/quote_request.rb). |
| Misskey | 2026.10.1 | native | native / translated | Emits `_misskey_quote`, `quoteUrl` and an HTML link fallback; resolves the two legacy fields on import. The cited paths alone do not establish a FEP-044f authorization exchange. `[source]` [renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [importer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts). |

Values are defined in the [glossary](../../glossary.md#compatibility-values). Quote recognition is separate from authorization; see below.

## Information lost in translation

Misskey's legacy quote identifiers establish a reference, not proof of consent under [FEP-044f](../../references/feps/fep-044f.md). Mastodon 4.7.3 distinguishes a `quoteAuthorization` URI from the target and can process a `QuoteRequest` and return an `Accept` or `Reject` according to its policy. A receiver that keeps only an HTML link loses the machine-readable relationship; one that stores only the target URI cannot infer an authorization decision from it. `[source]` [Mastodon parser](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/parser/status_parser.rb), [quote request handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/quote_request.rb), [Misskey renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts).

Misskey 2026.10.1 attempts to resolve `_misskey_quote` and `quoteUrl`; if neither resolves and any failure is transient it raises an error, while permanent failure can leave the quote relationship unresolved. It does not follow that every quoted target will be fetched, rendered, or permitted. `[source]` [ApNoteService](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts).

## Technical details

These are hand-written, unexecuted excerpts based on the linked serializers. They omit the surrounding `Create`, audience, signatures and mandatory context; the fictional IDs are examples only.

Misskey 2026.10.1's note renderer includes the same target in two legacy properties and can append an HTML fallback link. `[source]` [ApRendererService](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts):

```json
{"type":"Note","content":"Comment <span class=\"quote-inline\">RE: <a href=\"https://b.example/notes/1\">https://b.example/notes/1</a></span>","_misskey_quote":"https://b.example/notes/1","quoteUrl":"https://b.example/notes/1"}
```

Mastodon 4.7.3's serializer emits `quote` for a quote and, if the quoted status is present, `_misskey_quote` and `quoteUri`; `quoteAuthorization` is included only when an approval URI exists. The representation of a deleted or unavailable quoted status can differ. `[source]` [NoteSerializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/note_serializer.rb):

```json
{"type":"Note","quote":"https://b.example/notes/1","_misskey_quote":"https://b.example/notes/1","quoteUri":"https://b.example/notes/1","quoteAuthorization":"https://b.example/authorizations/2"}
```

Mastodon's parser checks `quote`, `_misskey_quote`, `quoteUrl`, and `quoteUri` in that order, selecting the first available URI and marking the absence of the `quote` property as legacy. Its `QuoteRequest` handler validates the requesting actor's host and the local target, checks the quote policy, and either schedules an acceptance or a rejection. Successful acceptance also checks that the quoted status and quoting actor match the request before storing approval and notifying. `[source]` [status parser](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/parser/status_parser.rb), [request handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/quote_request.rb).

## Test procedure

No cross-server test has been run for these versions. With isolated pinned instances and fixture accounts, create public posts on each server and quote in each direction. Capture the complete serialized object and delivery result, then inspect the remote API's relationship and displayed fallback separately. For Mastodon's authorization path, exercise permitted and denied quote policies and record the request, response, stored approval and eventual visibility. Also test an inaccessible or deleted target, a temporary fetch failure, a legacy-only object, and a revoked authorization. Use controlled actors and redacted credentials; never infer authorization success merely from a visible link.

## Quote representations seen in the laboratory

A quote can be carried several ways, and recognising a quote is not the same as having its author's consent. `[reported]` from a test server's design notes, which summarise parser and serializer behaviour in Mastodon, Glitch-Soc, Misskey, Sharkey and Akkoma/Pleroma and which this wiki has not read in source.

| Convention | Carrier | Families |
| ---------- | ------- | -------- |
| FEP-044f | `quote`, `QuoteRequest`, authorization stamp | Mastodon, Glitch-Soc parse it |
| Misskey legacy | `_misskey_quote` (with and without a slash in the IRI) | Misskey, Sharkey, Catodon |
| Other legacy | `quoteUrl`, `quoteUri` (Fedibird) | various |
| Link fallback | `RE: <url>` text or a link tag | Akkoma/Pleroma and older paths |

Key points: a legacy quote is not an authorized FEP-044f quote; a receiver that ignores every quote without a stamp loses Misskey-family quotes, and one that treats legacy quotes as approved bypasses consent. In the lab a Birchtree node returned HTTP 422 on Pinetree `QuoteRequest` activities (untagged enum parse failures), while ordinary quote checks still passed via fallback links, so a passing quote-display test says nothing about structured authorization. `[reported]` [Pinetree quote-posts design](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/quote-posts.md), [problem log items 32 and 33](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/federation-bench-2026-10-18-session2-problems.md).

## Sources

- [Mastodon 4.7.3 NoteSerializer](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/serializers/activitypub/note_serializer.rb), [StatusParser](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/parser/status_parser.rb), [QuoteRequest handler](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/lib/activitypub/activity/quote_request.rb) — quote serialization, parsing and approval.
- [Misskey 2026.10.1 renderer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/ApRendererService.ts), [note importer](https://github.com/misskey-dev/misskey/blob/4840fa6d576128ba916ba69169258ca177d40faf/packages/backend/src/core/activitypub/models/ApNoteService.ts) — legacy fields, fallback and target resolution.
- [FEP-044f](https://codeberg.org/fediverse/fep/src/branch/main/fep/044f/fep-044f.md) — consent-respecting quote vocabulary and protocol.
- [Pinetree quote-posts design note](https://github.com/estyseesghosts/pinetree/blob/f1665e6dd2f2ea8c115ce7c5ead98b5791a32fc6/docs/quote-posts.md) — the five quote carriers and the authorization states, at Pinetree f1665e6
