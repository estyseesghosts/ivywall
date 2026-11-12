# Client authentication with OAuth

A Fediverse client logs in through the server's OAuth authorization endpoint, not by collecting the user's password. The security rules come from three general OAuth documents and apply regardless of server software; this page extracts them into one login flow for native and browser clients. Which of these rules each server enforces is mostly unknown, and is recorded as such.

## The rules, by source

| Rule | Source |
| ---- | ------ |
| Use the authorization code grant. Public clients MUST use PKCE; confidential clients SHOULD. Use `S256`, not `plain`, so the verifier is never sent in the request | RFC 9700 §2.1.1 |
| Do not use the implicit grant (SHOULD NOT) or the resource owner password grant (MUST NOT) | RFC 9700 §2.1.2, §2.4 |
| The server compares redirect URIs by exact string match, except the port in a native app's loopback URI | RFC 9700 §2.1 |
| Refresh tokens for public clients MUST be sender-constrained or rotated on every use | RFC 9700 §2.2.2 |
| A native app sends the user to the system browser, not an embedded web view | RFC 8252 §1, §8.12 |
| Native redirect options: a private-use URI scheme (§7.1), an HTTPS URL the app has claimed with the OS (§7.2), or a loopback address with a variable port for desktop apps (§7.3) | RFC 8252 §7 |
| A browser app chooses one of three architectures, listed from most to least secure: backend-for-frontend (§6.1), token-mediating backend (§6.2), browser-only OAuth client (§6.3). The older single-domain pattern is discouraged | RFC 10017 §6, §7 |

`[spec]` RFC 9700 (January 2025), RFC 8252 (October 2017), RFC 10017 (August 2026). Section numbers are from each document's table of contents.

## Login flow

1. **Register** the client with the server (Mastodon-style servers have an app-registration endpoint; Misskey offers MiAuth or OAuth with client metadata).
2. **Create a verifier and its S256 challenge**, and a random `state`.
3. **Open the authorization URL** in the system browser (native) or by redirect (browser app) with `response_type=code`, the challenge, `state`, scopes and the exact registered redirect URI.
4. **Receive the redirect**, check `state`, take the `code`.
5. **Exchange the code** at the token endpoint with the verifier.
6. **Store the token** in the platform's secure store (native) or keep it out of JavaScript-readable storage (browser; the backend holds it in the first two architectures).
7. **Renew** with the refresh token if the server issues one, replacing it each time if it rotates. **Log out** by revoking the token and deleting local state.
8. **On failure**: an invalid or expired code restarts at step 2; a revoked token returns the user to step 3; never fall back to asking for a password.

## What servers support

| Server | Documented or read | Evidence |
| ------ | ------------------ | -------- |
| Mastodon | OAuth with scopes and app registration | `[documented]` [OAuth scopes](https://docs.joinmastodon.org/api/oauth-scopes/) |
| Misskey 2026.10.1 | OAuth authorization code; requires S256 proof-key challenge; validates the redirect URI against client metadata; MiAuth as an alternative | `[source]` see the [Misskey API page](../apis/misskey.md) |
| Catodon | OAuth for the optional ActivityPub client API; URL-identified clients | `[upstream-documented]` [Catodon document](../../references/federation-docs/catodon.md) |
| Others | whether PKCE is required, whether refresh tokens rotate, how redirect URIs are matched | > Unknown: read each server's authorization endpoint |

[FEP-d8c2](../../references/feps/registry.md) (draft) proposes an OAuth profile for the ActivityPub client API so servers vary less; the registry lists no implementer.

## Pitfalls

- Embedding a web view for login, which exposes credentials to the app.
- A redirect URI registered as a prefix or pattern; exact match is the rule.
- Keeping long-lived tokens in browser storage that scripts can read.
- Assuming a server offers refresh tokens or revocation; test both.

## Sources

- [RFC 9700: Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700) — PKCE, redirect matching, grants to avoid, refresh tokens
- [RFC 8252: OAuth 2.0 for Native Apps](https://www.rfc-editor.org/rfc/rfc8252) — external user agent and redirect options
- [RFC 10017: OAuth 2.0 for Browser-Based Applications](https://www.rfc-editor.org/rfc/rfc10017) — architecture patterns for web clients
