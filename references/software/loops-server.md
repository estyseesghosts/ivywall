# Loops Video fact sheet

**Studied release:** v1.0.0-beta.15, released 23 October 2026, commit [`0d2a881e459327ff5d551850ec55664e29717982`](https://github.com/joinloops/loops-server/tree/0d2a881e459327ff5d551850ec55664e29717982). This is a static review, not a live security or interoperability test.

## Facts

| Fact | Value and evidence |
| --- | --- |
| Runtime | PHP/Laravel backend and Vue web application. `[source]` [PHP dependencies](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/composer.json), [web dependencies](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/package.json). |
| Persistence | MySQL-oriented relational database, Redis queues and separately stored video media. `[source]` [deployment](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/docker-compose.yml), [remote video job](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessRemoteVideoJob.php). |
| Client API | Loops-specific API and OAuth-related dependencies; Mastodon API parity is not established. `[source]` [routes](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/routes/api.php). |
| Federation | Specialized ActivityPub handlers and signed request verification with a special `Delete` fallback needing further security testing. `[source]` [activity service](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Services/ActivityService.php), [verification job](https://github.com/joinloops/loops-server/blob/0d2a881e459327ff5d551850ec55664e29717982/app/Jobs/Federation/ProcessInboxActivityWithVerification.php). |

## Technical details

See the [Loops case study](../../servers/case-studies/loops-server.md) for federation and media stages, trust boundaries and unresolved test questions.

## Sources

- [Beta.15 release notes](https://github.com/joinloops/loops-server/releases/tag/v1.0.0-beta.15) — release information.
- [Pinned source tree](https://github.com/joinloops/loops-server/tree/0d2a881e459327ff5d551850ec55664e29717982) — code review baseline.
