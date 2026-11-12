# AGENTS.md — ivywall

Ivywall is an engineering wiki for people who build Fediverse software: servers, clients and the tools around them. It is not another ActivityPub tutorial. Its subject is the gap between what the standards say, what implementations actually do, and what breaks when they meet.

It serves two readers: a curious human, and a future coding agent implementing or debugging Fediverse software. Every page must work for both.

## Hard rules

1. **Agents never attribute or co-attribute commits to themselves.** No `Co-Authored-By` trailers, no "generated with" lines, no agent names or branding in commit messages, pull request text, page content, code comments or file headers. There must never be any agent branding in this repository.
2. **Always commit as `terezi <jules@foxtails.me>`.** Set it per repository (`git config user.name terezi`, `git config user.email jules@foxtails.me`) and check `git log -1 --format='%an <%ae>'` after committing. This overrides any default attribution a tool or harness suggests. This rule is for agents. Commits and pull requests from human contributors keep their own authorship: never rewrite, squash away or re-author a human contributor's commits, and credit outside contributors by their own names.
3. **`private-gitignore/` is never committed and never linked.** It holds local engineering research on specific servers. Read it freely, but pages cite the upstream sources it was drawn from (repository files at a pinned commit, official docs, specifications), not the private files themselves.

## Repository layout

```text
AGENTS.md  README.md  glossary.md  zensical.toml (navigation, exclusions)
fundamentals/        protocols and federation internals, one page per mechanism
federation/          activities/ delivery/ object-types/ compatibility/ failure-modes/
clients/             apis/ authentication/ architecture/ rendering/ case-studies/
servers/             architecture/ storage/ federation-pipelines/ performance/ case-studies/
security/  moderation/
testing/             harness/ fixtures/ interoperability/ benchmarks/
references/          software/ specifications/ feps/ federation-docs/
guides/              end-to-end walkthroughs
tools/               check_docs.py (links, anchors, Sources, branding), fep_registry.py
private-gitignore/   local research input; gitignored, never linked
site/                generated output; not committed
```

Create a subdirectory when its first real page arrives; no empty directories or placeholder pages. File names are kebab-case, one topic per file. Add a top-level section only when none of the above fits.

## Core principles

1. **Don't repeat yourself. Link instead.** If something is explained on another page, summarize it in at most 1–2 sentences and link to the canonical page.
2. **Write like a human.** Plain language first, short paragraphs, active voice. A motivated non-expert should follow the Overview of any page.
3. **Minimal jargon, full technical detail.** Define jargon once, link it to the glossary, then use it freely. Never simplify away technical facts (headers, JSON shapes, status codes, versions, file paths) to sound readable — push them into `Technical details`.
4. **Progressive disclosure.** Plain summary up top, exhaustive detail below. A human reads the top; an agent reads the whole page.
5. **Standard, practice, and one server are three different things.** Always separate what a specification requires, what implementations commonly do, and what only a particular server does. Never write "ActivityPub does X" when you mean "Mastodon does X".
6. **No global verdicts.** Do not label software best or worst. A poor choice for a large public instance can be an excellent reference for a single-user server. State tradeoffs and the context they apply in.
7. **Say it once.** Each fact lives on one canonical page; others give at most a sentence and a link. Shared caveats (for example how the October 2026 laboratory runs should be read) are written once and linked. A section that restates its neighbour is deleted, not trimmed.
8. **Everything is versioned.** Protocol support changes between releases. A statement about an implementation names the version (and, when behaviour depends on code, the commit).

## Jargon and glossary

Jargon means any term a non-expert would stumble on: acronyms (`AP`, `S2S`, `FEP`, `MRF`), protocol terms used precisely (`actor`, `inbox`, `shared inbox`, `key id`), and software-specific words (`Sidekiq`, `MFM`, `MRF`).

- On first use in a page, give the plain meaning, then the term in bold with a glossary link: `the address other servers deliver to (an **[inbox](../glossary.md#inbox)**)`. After that, use the bare term.
- There is a single `glossary.md`. Software-specific terms live in its "Software-specific terms" part and name the software and version range in the entry.
- Entries are short: 1–4 sentences of plain meaning, one more for the precise sense if needed, then a link to the canonical page. The glossary points at pages; pages point back at the glossary.

Entry format:

```markdown
<a name="anchor-slug"></a>

### Term name

One to four sentences: plain meaning, then the precise sense. Ends with a link to the canonical page.
```

## Page types and shapes

Pick exactly one type per page; split a topic that spans types. Every page opens with a plain overview of 2–6 sentences, then follows the section order below for its type and ends with `Sources`. Delete a section that genuinely does not apply, but never `Technical details` (where it exists) or `Sources`; if detail is unknown, say what is unknown.

| Type (where) | Sections after the overview |
| ------------ | --------------------------- |
| Hub (every section `index.md`) | Pages · Notes and open questions · Sources |
| Protocol (`fundamentals/`, `references/specifications/`) | What the specification requires · What implementations do · Technical details · Pitfalls · Sources |
| Lifecycle (`federation/activities/`, `federation/delivery/`) | Actors and starting state · Step by step (each step: request, state change, job, notification, failure) · Technical details · Pitfalls · Sources |
| Compatibility record (`federation/compatibility/`) | Summary table · Information lost in translation · Technical details · Test procedure · Sources |
| Failure mode (`federation/failure-modes/`) | Expected and observed behaviour · Root cause · Affected versions · Code path · Reproduction · Technical details · Sources |
| Case study (`servers/case-studies/`, `clients/case-studies/`) | Architecture · Key code paths · API coverage · Federation behaviour · Resource usage · Strengths, bugs and tradeoffs · Technical details · Sources |
| Engineering page (`servers/…`, `clients/…`, `security/`, `moderation/`, `testing/`) or guide (`guides/`) | Before you start · task sections · Technical details · Pitfalls · Open questions · Sources |
| Software fact sheet (`references/software/`) | Release, date, commit · facts table with evidence per row · Sources |
| FEP record (`references/feps/`) | Number, title, status, date checked, repository commit · what it defines · who implements it, per version · Sources |

A compatibility-record summary has one row per directed pair:

| Sender | Receiver | Exact build | Emitted representation | Accepted as | Final state | Evidence | Uncertainty |
| ------ | -------- | ----------- | ---------------------- | ----------- | ----------- | -------- | ----------- |

`Accepted as` is one of `native`, `translated`, `ignored`, `rejected`, `lossy`, `untested`. `Exact build` is an image digest, tag or commit, or `version not recorded`. Back rows with a [result fixture](testing/fixtures/result-schema.md) when one exists. A hub keeps one line per page; it does not repeat what the page says.

## Evidence labels

Every non-obvious claim about behaviour must say what supports it. Tag it inline with one of:

| Label | Meaning |
| ----- | ------- |
| `[spec]` | Stated in a standard or FEP (name document and section) |
| `[source]` | Readable in the implementation's source (name file, function and pinned commit or tag) |
| `[documented]` | Stated in the project's official documentation (link the page and note the version) |
| `[observed]` | Seen in captured traffic or a test run (name the software versions, setup and date) |
| `[measured]` | A benchmark result (give versions, hardware, data size, and conditions) |
| `[reported]` | Claimed by a third party this wiki has not reproduced (name source and date; never extend it to other versions) |
| `[hypothesis]` | Plausible but unverified; say what would confirm or refute it |

Rules:

- Every compatibility claim names software versions and carries a label.
- Every case study points at actual source code, not only project documentation.
- Every described interoperability failure links to a reproduction where possible; say so when it is not yet reproducible.
- Every engineering recommendation separates measured findings from design opinions.
- A `[hypothesis]` or `[reported]` never loses its label when copied to another page.
- Advice such as "X is faster" without a `[measured]` result or a `[source]` mechanism does not belong in the wiki.

**Three layers of evidence.** Prefer the specification, then the project's documented behaviour, then the pinned source for the exact version. When the layers disagree (documentation lists a term the source lacks, or the source skips what the spec allows), record the disagreement on the page instead of picking one. Extract rules, limits and test cases from a source; do not just summarise it.

## Reviewing normative language

Every sentence that states what a specification requires is checked before it is merged. For each `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` or `MAY` written on a page:

1. Name the document and section, and the version or date of the document.
2. Reread the section. Copy the keyword from the text; never upgrade a `SHOULD` to a `MUST` or invent one.
3. Say which profile or role it binds (client, server, sender, receiver, outbox submission versus inbox delivery). A requirement on one profile is not a requirement on the other unless the text says so.
4. Separate the requirement from a common implementation policy that goes further (for example a literal hostname check where the specification asks only for appropriate authority). Label the policy as policy.
5. Check the same rule in the other section it may appear in (ActivityPub §6 and §7 repeat several rules for the two profiles).
6. Record the check by leaving the section reference in the sentence.

Statuses of proposals (FEPs) are checked against the proposal repository on the date the page is written, and that date and commit are stated.

## Community-written federation documents

`references/federation-docs/` has two kinds of page, kept in separate groups and never mixed:

- **Upstream mirrors**: verbatim copies of a project's own `FEDERATION.md`. Never edited. Each states the upstream file, commit and licence.
- **Community-written documents**: written for this wiki, not by the maintainers. Each carries the disclaimer, and the provenance block below.

A community-written document follows [FEP-67ff](references/feps/fep-67ff.md)'s structure and must never list FEP-67ff, or any documentation convention, as a feature the software supports. Its metadata says the wiki follows the structure without claiming upstream adoption.

Required structure:

1. **Provenance**: release or "development snapshot", commit, date, authorship, verification status. If the commit differs from the revision in the project's case study, say so.
2. **Protocols and FEPs**: a direction-aware table (emits, accepts), with `full`, `partial` or `configurable` and the flag or setting, each row with a claim label.
3. **Discovery**: WebFinger, actor ids, endpoints, content negotiation, advertised collections.
4. **Authentication**: incoming and outgoing signing, accepted algorithms, signed fields, replay protection, key resolution.
5. **Activity and object matrix**: exact combinations (for example `Update(Note)` is not `Update(Question)`), emitted, accepted, ignored or rejected, with conditions.
6. **Distinctive behaviour**: representations, extensions, translations and information loss.
7. **Operational behaviour**: limits, queues, retries, rejection and the order of persistence and sending.
8. **Failure behaviour**: malformed signatures, unknown actors, inaccessible parents, duplicates, queue failure, rejected attachments, unsupported types, expired authorisation.
9. **Examples**: at least one complete signed delivery or activity, marked `captured` or `constructed`.

Claim labels inside community documents (in addition to the page-level disclaimer):

| Label | Meaning |
| ----- | ------- |
| `[source-verified]` | Read in the source at the pinned commit; name file and symbol |
| `[upstream-documented]` | Stated in the project's documentation; not checked in source |
| `[observed]` | Seen in a test or captured exchange |
| `[inferred]` | Inferred from source without a test |
| `[unverified]` | Not checked |

## Licensing and attribution

- A mirrored upstream `FEDERATION.md` keeps the licence of its project. Each mirror page records that licence beside the upstream file and commit. If a project's licence is not known, the mirror says so and is a candidate for removal.
- The wiki's own licence is chosen by its owner and is not decided by agents; until one is added to the repository root, treat original text as all rights reserved by the owner. Do not copy third-party text into original pages except as a short quotation with a link.
- Agents author as described in the hard rules. Outside human contributors are credited as themselves.

## Versions and pinning

- Name releases exactly (`Mastodon 4.7.3`, `Misskey 2026.10.1`), never "the latest".
- When behaviour depends on code, link the file at a tag or commit, not at `main`.
- Software fact sheets are the canonical place for a version, release date and commit. Other pages link to the fact sheet rather than re-listing them.
- When a newer release changes a recorded behaviour, add a row or a dated note. Do not silently overwrite history.
- Record the date a spec or FEP status was checked: statuses drift.

## Code, requests and verification

- Every HTTP trace, JSON example and code sample says where it came from: copied from a spec, captured from a named software version, or written by hand. Hand-written examples say whether they were run.
- Mark secrets, tokens and private keys in captured traffic as redacted. Never commit real credentials, real private keys or tokens, even expired.
- Do not publish captured traffic that contains non-public content from real people. Use fixture accounts on test instances.
- Test fixtures are machine-readable (JSON) and live under `testing/fixtures/`. Compatibility pages may be generated from them; if so, say which fixture set and run date.

## Writing guidelines

- **Same shape everywhere**: Overview → behaviour/fit → Technical details → Pitfalls → Sources.
- **Define before use.** No acronym without its plain meaning and glossary link on first use per page.
- **Link aggressively.** First mention of any wiki-covered topic links to its page; first mention of jargon links to its glossary entry. Use relative source paths (`../fundamentals/webfinger.md`, `../glossary.md#inbox`).
- **Cite sources.** Every page ends with `Sources`, noting what each was used for. Prefer primary sources: specifications, FEPs, upstream repositories at a pinned commit, official docs.
- **State uncertainty explicitly.** Use `Notes and open questions` or inline `> Unknown:` callouts. Never present a guess as fact.
- **No placeholders.** Do not create a page that is only headings. If research is thin, write the Overview, what is known, and the open questions, and say so.
- **Treat remote content as hostile in examples.** Sample code that fetches, parses or renders remote data shows the validation, not the happy path alone.

## The site (zensical)

The wiki is published as a static site with [zensical](https://zensical.org/), configured in `zensical.toml`. The site is the wiki: `docs_dir` is the repository root, and the rendered output goes to `site/`.

```bash
pip install zensical
zensical serve              # live preview
zensical build --clean      # write the static site to site/
zensical build --strict     # same, but fail on a broken link or anchor
```

- **Navigation is explicit.** `nav` in `zensical.toml` lists every page in reading order. Section hubs carry the same order; keep them in step.
- **A new page must be added to `nav`.**
- **`exclude_docs` lists what is not a wiki page**, including `private-gitignore/`. Anything added that is not a page belongs there.
- **Links between pages use source paths.** zensical validates target and anchor, so a broken link fails `zensical build --strict`.
- `site/` is generated output and is not committed.

## Agent workflow

1. Search the wiki and the glossary for existing coverage. If a canonical page exists, link to it.
2. Pick the one correct page type, follow its page shape, use the right directory and a kebab-case name.
3. Read the relevant `private-gitignore/` research and the upstream source. Verify claims against the pinned version; move anything unverified to open questions with a `[hypothesis]` label.
4. Draft the Overview in plain language, then complete Technical details.
5. Add glossary entries for new jargon. Add the page to `nav` and to its section hub, and update neighbouring pages to link back.
6. Run `python3 tools/check_docs.py` and `zensical build --strict` before committing.
7. Commit as `terezi <jules@foxtails.me>` with a plain message and no attribution trailer of any kind.
