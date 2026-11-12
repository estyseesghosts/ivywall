# Loops Video 1.0.0-beta.15

Loops is a federated short-video server, with asynchronous video processing and a specialized social model. A client upload, video conversion, ActivityPub delivery and remote playback are separate stages. This case study covers [the pinned beta.15 release](../../references/software/loops-server.md), not later development. It is a source review: interoperability, exploitability and production capacity have not been tested here.

## Architecture

The backend uses PHP and Laravel, with a Vue web application, MySQL-oriented relational storage, Redis queues and Horizon workers. FFmpeg-based processing generates playable media, and deployment supports object storage; the release also contains optional real-time/live-stream components. The provided configuration separates web handling, queue workers and scheduled work. `[source]` [PHP dependencies](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/composer.json), [web dependencies](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/package.json), [deployment](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/docker-compose.yml), [Horizon](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/config/horizon.php).

Profiles, videos, comments, relationships and received activities have relational records. The media bytes and derivatives are outside those records, and Redis backs queue and cache operations. A database backup alone is therefore insufficient for restoring the complete service. `[source]` [profile migration](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/database/migrations/2024_03_22_062441_create_profiles_table.php), [video migration](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/database/migrations/2024_03_23_232030_create_videos_table.php), [activity migration](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/database/migrations/2025_09_14_054926_create_activities_table.php).

## Key code paths

### Upload and media

An uploaded video is validated and processed separately from the initial request. Video optimization invokes FFmpeg, and remote videos have their own fetch and processing job. Queue success, storage availability and derivative readiness affect whether a video can be played even if its social record exists. Validate codecs, maximum sizes, timeouts and actual storage settings for the deployment; source inspection alone does not measure transcoding throughput. `[source]` [local optimizer](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Video/VideoOptimizeJob.php), [remote video job](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessRemoteVideoJob.php#L74).

### Federation receipt

Inbox verification is a queued job. The verification code parses signature metadata, requires `(request-target)`, `host` and `date` to be signed, checks date validity, validates the actor URL and verifies a digest when it appears among signed headers. Later processing dispatches to user or shared inbox jobs. These checks and resulting domain operations are distinct steps; an HTTP acknowledgment is not evidence that media or a post was persisted. `[source]` [verification job](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessInboxActivityWithVerification.php#L63), [shared inbox processor](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessSharedInboxActivity.php).

### Outgoing delivery

The ActivityPub builder constructs video or comment activities, while a dispatcher and inbox resolver select recipients and queue deliveries. The resolver groups by shared inbox where available, reducing duplicate network requests; the collection of destinations still consumes memory and database work as reach grows. This is a source observation, not a measured scaling limit. `[source]` [Create builder](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Federation/ActivityBuilders/CreateActivityBuilder.php), [dispatcher](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Services/FederationDispatcher.php), [inbox resolver](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Services/InboxResolverService.php).

## API coverage

The release exposes a Loops-specific client API, OAuth and federation routes. It should not be assumed to implement the complete Mastodon status/timeline interface merely because it supports ActivityPub. Check actual routes, permissions and media readiness in the pinned release when writing a client adapter. `[source]` [API routes](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/routes/api.php), [dependencies](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/composer.json).

## Federation behaviour

The activity service maps recognized activities to handlers and validators. `Create` validation is specialized to video-bearing notes or replies to an existing conversation, rather than accepting all generic text posts as equivalent videos. The activity map should be inspected for exact supported operations; no general `Move` or `Reject` handler is established by that map. A serializer or parser accepting a field is not proof that another server will render or preserve it. `[source]` [activity service](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Services/ActivityService.php), [Create validator](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Federation/Validators/CreateValidator.php).

## Security and trust boundaries

In beta.15, the verification job has a special `Delete` branch when remote actor data or public-key material cannot be obtained: it returns a valid result with an existing or constructed actor without successfully verifying a signature with that missing key. Subsequent origin and handler checks still apply. The delete handler accepts a nullable actor and has ownership checks conditional on its presence. This is a **source-level security concern**, not a demonstrated exploit; a controlled test must establish reachability, affected objects and end-to-end impact. A domain match is not cryptographic proof of authority. `[source]` [verification branch](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessInboxActivityWithVerification.php#L63), [delete validator](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Federation/Validators/DeleteValidator.php), [delete handler](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Federation/Handlers/DeleteHandler.php).

Remote-video fetching can contact attacker-controlled hosts and consume significant bandwidth, CPU and disk. Test private-address and DNS-rebinding defenses, redirects, response limits, temporary-file cleanup and storage access at the actual downloader; the existence of URL checks is not proof that every fetch or redirect is safe. `[source]` [remote video job](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessRemoteVideoJob.php#L74).

## Resource usage and tradeoffs

CPU, memory, bandwidth, queue latency and storage growth are **unmeasured**. Video transforms can be isolated in workers and scaled independently, but this adds operational components and leaves results dependent on storage, codecs and queue capacity. Benchmark local and remote video ingestion, fan-out over differing inbox counts, retries, and restore on representative media before making sizing claims.

## Technical details and open questions

Record release commit, queue settings, actor and destination IDs, response codes and final records in isolated federation tests. Exercise unsupported `Create` objects, duplicate IDs, reordered delete and create, unavailable keys, direct/shared inboxes, and failure during transcoding. Treat the source-level Delete concern above as a hypothesis about real-world impact until a controlled reproduction settles the path.

## Sources

- [Loops v1.0.0-beta.15 source](https://github.com/joinloops/loops-server/tree/0d2a881e459327ff5d551850ec55664e29717982) and [release notes](https://github.com/joinloops/loops-server/releases/tag/v1.0.0-beta.15) — studied version and release context.
- [Inbox verification](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessInboxActivityWithVerification.php#L63), [Delete handler](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Federation/Handlers/DeleteHandler.php) — inbound trust boundary.
- [Federation dispatcher](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Services/FederationDispatcher.php), [remote-video job](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessRemoteVideoJob.php#L74) — delivery and media pipeline.
