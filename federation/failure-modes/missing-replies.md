# Failure mode: replies missing on remote threads

A user can open a post and see fewer replies on their server than on another server. A reply is delivered to its addressed recipients, not automatically to every server that has cached the parent. The local conversation view also depends on which replies the server has fetched and which the current viewer may see. The conditions below explain a possible failure path; no cross-server reproduction is claimed here. `[spec]` [ActivityPub §7.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery).

## Expected and observed behaviour

A user may expect a public thread to look identical everywhere. ActivityPub does not require every server caching a parent to receive every reply: delivery uses the activity's addresses. A missing reply can therefore reflect recipient selection, delivery failure, policy, access control, incomplete fetching, or a presentation limit. Which cause applies to a particular report needs a trace, not an assumption that the reply was never delivered. `[spec]` [ActivityPub §7.1](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery); `[source]` Mastodon 4.7.3 [context controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses/contexts_controller.rb#L14).

## Root cause and affected versions

A reply author addresses an activity to actors and collections. The public audience marker indicates public access but is not itself a delivery endpoint. The Recommendation requires inbox forwarding when its specified conditions all hold, while allowing recipients to filter forwarding under local policy; it does **not** require all replies to be forwarded to every server that knows the parent. See [server-to-server delivery](../../fundamentals/activitypub-s2s.md). `[spec]` [ActivityPub §§5.6, 7.1.1–7.1.2](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery).

In Mastodon 4.7.3, an authenticated request for the context of a status can schedule an asynchronous reply refresh when `should_fetch_replies?` is true. Its reply-fetching service limits each call to five replies and rejects reply URIs whose host differs from the reference URI as an amplification defense. The context endpoint also imposes response limits; an anonymous request has lower limits than an authenticated one. These facts are about this release, not evidence that it caused a specific missing reply. `[source]` [context controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses/contexts_controller.rb#L14), [reply fetch service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_replies_service.rb#L7).

## Reproduction and investigation

No reproduction of a missing federated reply is included here. On isolated, version-pinned instances, publish a public parent on server A and a reply from server B, with a user viewing the parent on server C. Record each activity's `to` and `cc`, actor and object IDs, HTTP delivery to C, queue outcome, the resulting stored object and the context API response before and after refresh. Repeat while changing follow relationships and authentication. Check C's domain and account policy and the viewer's visibility before attributing the difference to backfill. Use test accounts and redact tokens.

## Technical details

For Mastodon 4.7.3 the context endpoint limits anonymous responses to 40 ancestors, 60 descendants and a descendant depth of 20; the authenticated context uses a 4,096 limit for each direction. A limit can produce a short response even when more objects are stored. A refresh is asynchronous, so a first response and a later response can differ. `[source]` [context controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses/contexts_controller.rb#L14).

## A benchmark false positive

The Pinetree/Birchtree laboratory's October 2026 problems record reports that an earlier reply check only read Misskey-shaped `replyId`; it therefore recorded failures when the API response used Mastodon-shaped `in_reply_to_id`. The same record says the cross-family check repeated the mistake and that copied-note linkage was checked afterward. This is a report about a test oracle, not proof that a real reply-delivery bug cannot occur. The run 5 summary later records 60 successful samples out of 503 replies in its reply storm; a sample is not an exhaustive end-to-end verification of all replies. `[reported]` [field mismatch](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L101-L104), [cross-family recheck](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L163-L167), [run 5 reply sample](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L79-L83).

The run report identifies Pinetree build `f58be005c558f650` and Birchtree build `e24d75aea1085a06`; exact versions of every peer involved in each reply sample are not identified in that summary. Pinetree and Birchtree were minimal test servers, so neither is a reference implementation. `[reported]` [run setup](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L8-L13).

## Sources

- [ActivityPub Recommendation §§5.6, 7.1–7.1.2](https://www.w3.org/TR/2018/REC-activitypub-20180123/#delivery) — public addressing, delivery and forwarding.
- [Mastodon 4.7.3 context controller](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/controllers/api/v1/statuses/contexts_controller.rb#L14) — visibility, limits and refresh scheduling.
- [Mastodon 4.7.3 reply fetch service](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/app/services/activitypub/fetch_replies_service.rb#L7) — host restriction and per-call limit.
- [Pinetree/Birchtree laboratory problems](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L101-L106) and [run 5 summary](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L79-L83) — historical test-oracle and sampling reports.
