# FEP-044f: consent-respecting quote posts

FEP-044f describes a way to quote a post that lets the quoted author consent to, and later revoke, the quote. It also lets an author publish a policy saying who may quote their posts. Quote support is otherwise implemented ad hoc and differently by each server, so this FEP is the main attempt at a shared, verifiable model.

## Record

| Field | Value |
| ----- | ----- |
| Number | FEP-044f |
| Title | Consent-respecting quote posts |
| Status | **DRAFT** (not final) `[spec]` |
| Received | 2025-04-03 |
| Author | Claire |
| Status checked | 2026-11-11, at FEP repository commit `bae8b04520` |

A draft can still change. Do not describe software as conforming to a final standard.

## What it defines

| Concept | Term | Purpose |
| ------- | ---- | ------- |
| Quote reference | `quote` (`https://w3id.org/fep/044f#quote`) | Points from the quoting post to the quoted object |
| Quote policy | `interactionPolicy.canQuote` with `automaticApproval` and `manualApproval` | Advertises who may quote and who needs manual review |
| Request | `QuoteRequest` activity (`object` = quoted post, `instrument` = quote post) | Asks the quoted author for approval |
| Answer | `Accept` (with a `QuoteAuthorization` as `result`) or `Reject` | Grants or refuses |
| Stamp | `QuoteAuthorization` object, referenced by `quoteAuthorization` on the quote | Proof of approval; verified by checking its `interactingObject`, `interactionTarget` and `attributedTo` and that it can be authenticated |
| Revocation | A `Delete` of the stamp | Withdraws approval; recipients are told to re-verify opportunistically |

Compatibility section: the FEP names the legacy carriers `_misskey_quote`, `quoteUrl`, `quoteUri` and FEP-e232 object links as things a receiver may recognise, which is not the same as approval. `[spec]` FEP-044f.

## Who emits and accepts it

The FEP lists implementations in its own text. These are the proposal authors' statements as of the checked commit, `[documented]` upstream and not verified against each project's source by this wiki.

| Software | Stated support in the FEP text |
| -------- | ------------------------------ |
| Mastodon | 4.4 verifies and displays remote quotes; 4.5 adds authoring and quote policies, limited to automatic approval for public, followers or nobody |
| Iceshrimp.NET | quotes and is quoted, with a fixed automatic public permission |
| Loops | can always be quoted, fixed automatic public permission |
| Pixelfed | can be quoted by default, with followers-only or none options; can revoke quotes; cannot create or view quotes directly |
| Friendica, PieFed | quote and are quoted (PieFed: can always be quoted), fixed automatic public permission |
| Bonfire, ktistec, WordPress ActivityPub | quote, are quoted, customise policies (Bonfire and ktistec also revoke) |
| Smithereen | authoring and issuing `QuoteAuthorization`; does not verify quotes or request stamps |

Not listed there: Misskey-family servers, Akkoma, NodeBB, Lemmy, Wafrn and others. For those, and for the contradictions between this table and other pages, see the [quote compatibility record](../../federation/compatibility/quotes.md) and the community-written federation documents for [Pixelfed](../federation-docs/pixelfed.md) and [Wafrn](../federation-docs/wafrn.md).

> Unknown: per-version behaviour of the studied servers against this draft.

## Technical details

The policy vocabulary reuses GoToSocial's interaction-policy namespace. Receivers should treat the two separate questions apart: recognising that post A quotes post B (any carrier), and whether the quoted author approved it (a valid stamp, or one of the FEP's explicit exceptions, such as a self-quote). The FEP's non-normative guidance says software should refuse to display unapproved quotes; whether a client chooses to is a product decision.

## Sources

- [FEP-044f proposal](https://codeberg.org/fediverse/fep/src/commit/bae8b04520f72ceba74b4cdae043693f98bfad3f/fep/044f/fep-044f.md) — text and status, at the checked commit
