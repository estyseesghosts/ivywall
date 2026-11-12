# Compatibility: poll options and votes

Federated polls can fail at several stages: a server may reject an option, a voter may be unable to find the poll, or the origin may not record a vote. A successful request to a local client API does not by itself prove that the remote poll tally changed. These findings combine a historical test-laboratory report with separately inspected source; they do not establish universal compatibility between server families.

## Summary

| Software and version | Emits | Accepts | Notes |
| --- | --- | --- | --- |
| [Akkoma v3.20.0](../../references/software/akkoma.md) | untested here | partial source evidence | The option validator requires `name` and `type`, with `type` equal to `Note`. This does not establish the whole poll or voting contract. `[source]` [option validator](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/object_validators/question_options_validator.ex#L12-L28). |
| Other implementations | version not established for this experiment | untested here | The historical report names Catodon, Misskey and Mastodon in a six-server lab, but the poll summary does not identify their exact deployed revisions. Do not transfer its results to a particular release. `[reported]` [run 5](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L7-L16). |

Here **untested** means that the cited evidence does not establish this direction; **partial source evidence** means one relevant validation path has been inspected, not that complete end-to-end support has been proven.

## Information lost in translation

An unrecognized option or a missing vote can make a poll appear with incomplete results even when other kinds of posts federate. The published run report does not contain enough peer-version and captured-traffic evidence to determine which missing votes reflect an implementation bug, search behavior, timing, or test-harness error. Reported counts should not be read as per-version support ratings.

## Technical details

Akkoma v3.20.0's `QuestionOptionsValidator` requires each validated option's `type` to be `Note` and its `name` to be present. The report of the 19 October 2026 lab run describes earlier Pinetree-generated options without that type, and attributes rejection to this validation rule. The lab's exact Akkoma build is not identified in that report, and the historical Pinetree binary ID is not a source commit. We can verify the v3.20.0 rule separately; we cannot establish from that alone that it was the precise code running in the lab. `[source]` [Akkoma validator](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/object_validators/question_options_validator.ex#L20-L28); `[reported]` [run report](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L134-L145).

The same report records a poll-storm check of 50 polls and 442 successful vote calls out of 455, with five missing tally results on Catodon-origin polls and 13 failed calls. These are different measurements, not a common numerator and denominator. The report attributes some failures to vote resolution, but the supplied summary does not independently establish the exact receiver cause or peer versions. The test used Pinetree executable identifier `f58be005c558f650` and Birchtree `e24d75aea1085a06`; these identify test binaries, not necessarily Git commits. Both were purpose-built test implementations, not normative references. `[reported]` [run setup](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L7-L16), [poll-storm results](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md#L75-L78).

The same lab's problem log describes a Birchtree test implementation that initially interpreted a future `closed` timestamp as already closed; it reports a fix and a successful later vote. This is a historical harness-subject result, not evidence that Akkoma or Catodon has the same defect. `[reported]` [problem log](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L155-L162).

## Test procedure

On isolated servers with recorded images and commits, create a single-choice poll with a `Question`, an `endTime` in the future and options represented as `Note` objects. Deliver variants with and without each option's `type`, and compare the receiver's activity log and persisted poll, not just the HTTP acknowledgment. Resolve the poll from the voter, vote, capture the outgoing activity and inspect the origin's final count after a stated deadline. Repeat with future `closed` timestamps, delayed delivery, duplicate votes and a disabled search service. Record all versions, configuration, traffic and failure stage before assigning a cause.

## Sources

- [Akkoma v3.20.0 option validator](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/object_validators/question_options_validator.ex#L12-L28) — source-level option requirements.
- [19 October 2026 run 5 report](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-19-phase7-run5.md) — historical setup, counts and interpretations, not independently reproduced here.
- [Lab problem log](https://github.com/estyseesghosts/pinetree/blob/1c1d00cc955e2ef602d1640d8f7f7d84d985de2a/docs/federation-bench-2026-10-18-session2-problems.md#L155-L162) — reported future-`closed` handling and follow-up.
