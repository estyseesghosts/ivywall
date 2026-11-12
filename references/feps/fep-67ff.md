# FEP-67ff: FEDERATION.md

FEP-67ff is a documentation convention, not a protocol feature. It asks a project to keep a `FEDERATION.md` file in the root of its own code repository that says what the software supports, so other developers can achieve interoperability without reading the code. The wiki's [project federation documents](../federation-docs/index.md) follow its structure.

## Record

| Field | Value |
| ----- | ----- |
| Number | FEP-67ff |
| Title | FEDERATION.md |
| Status | **FINAL**, finalized 2024-09-22 `[spec]` |
| Received | 2023-09-05 |
| Author | silverpill |
| Status checked | 2026-11-11, at FEP repository commit `bae8b04520` |

## What it requires

- The file MUST be valid Markdown and MUST be at the root of the project's code repository (it MAY link to documentation kept elsewhere).
- It SHOULD list the implemented federation protocols and the supported FEPs. Beyond that its structure is free. `[spec]`

## Why it is not a supported feature

Because the requirement is about where the file lives, only the project itself can conform. A document written by someone else and kept in a different repository, such as the community-written pages in this wiki, can follow the suggested outline but does not make the software conform to FEP-67ff, and must not list it under supported FEPs. Projects that publish their own file (for example Mastodon, Akkoma, Iceshrimp.NET, Loops and snac) do list it, and that is accurate for them.

## Technical details

The FEP's non-normative template lists protocols, supported FEPs, an ActivityPub section for activities and extensions, and additional documentation. The wiki's required structure for community-written documents extends it; see AGENTS.md.

## Sources

- [FEP-67ff proposal](https://codeberg.org/fediverse/fep/src/commit/bae8b04520f72ceba74b4cdae043693f98bfad3f/fep/67ff/fep-67ff.md) — text, template and status, at the checked commit
