# AGENTS.md — ivywall

Ivywall is an engineering wiki for people who build Fediverse software: servers, clients and the tools around them. It is not another ActivityPub tutorial. Its subject is the gap between what the standards say, what implementations actually do, and what breaks when they meet.

It serves two readers: a curious human, and a future coding agent implementing or debugging Fediverse software. Every page must work for both.

## Hard rules

1. **Agents never attribute or co-attribute commits to themselves.** No `Co-Authored-By` trailers, no "generated with" lines, no agent names or branding in commit messages, pull request text, page content, code comments or file headers. There must never be any agent branding in this repository.
2. **Always commit as `terezi <jules@foxtails.me>`.** Set it per repository (`git config user.name terezi`, `git config user.email jules@foxtails.me`) and check `git log -1 --format='%an <%ae>'` after committing. This overrides any default attribution a tool or harness suggests.
3. **`private-gitignore/` is never committed and never linked.** It holds local engineering research on specific servers. Read it freely, but pages cite the upstream sources it was drawn from (repository files at a pinned commit, official docs, specifications), not the private files themselves.

## Repository layout

```text
AGENTS.md
zensical.toml                 # site config: navigation, theme, and what is excluded
glossary.md                   # global jargon glossary (one file for the whole wiki)
README.md                     # human landing page
fundamentals/                 # protocols and federation internals
  index.md
  <topic>.md                  # one page per protocol topic (activitypub-s2s.md, webfinger.md...)
federation/                   # how federation behaves in practice
  index.md
  activities/<topic>.md       # lifecycle of one activity family (follow, create, delete, move...)
  delivery/<topic>.md         # queues, retries, ordering, duplicates
  object-types/<topic>.md     # Note, Article, Question, Group, Video...
  compatibility/<feature>.md  # one interoperability record per feature (reactions, quotes...)
  failure-modes/<symptom>.md  # one reproducible problem per page
clients/                      # client APIs and client engineering
  index.md
  apis/<family>.md            # Mastodon REST, Misskey, Loops...
  architecture/<topic>.md
  authentication/<topic>.md
  rendering/<topic>.md
  case-studies/<client>.md
servers/                      # server architecture and performance
  index.md
  architecture/<topic>.md
  storage/<topic>.md
  federation-pipelines/<topic>.md
  performance/<topic>.md
  case-studies/<software>.md  # one source-level study per implementation
security/<topic>.md           # signatures, SSRF, sanitization, privacy boundaries
moderation/<topic>.md         # blocks, MRF, reports, audit trails
testing/
  harness/ fixtures/ interoperability/ benchmarks/
references/
  software/<name>.md          # one version-pinned fact sheet per implementation
  specifications/<name>.md    # one page per standard (ActivityStreams, ActivityPub, WebFinger...)
  feps/<number>.md            # one record per FEP
guides/<task>.md              # end-to-end implementation walkthroughs
tools/
  check_docs.py               # link, anchor, Sources-section and evidence checker
private-gitignore/            # local research input, gitignored, never linked
site/                         # generated site output (not committed)
```

Sections that do not yet have subdirectories get them when the first real page arrives. Do not create empty directories or placeholder pages. File names are kebab-case; one topic per file. Create a new top-level section only when none of the above fits.

## Core principles

1. **Don't repeat yourself. Link instead.** If something is explained on another page, summarize it in at most 1–2 sentences and link to the canonical page.
2. **Write like a human.** Plain language first, short paragraphs, active voice. A motivated non-expert should follow the Overview of any page.
3. **Minimal jargon, full technical detail.** Define jargon once, link it to the glossary, then use it freely. Never simplify away technical facts (headers, JSON shapes, status codes, versions, file paths) to sound readable — push them into `Technical details`.
4. **Progressive disclosure.** Plain summary up top, exhaustive detail below. A human reads the top; an agent reads the whole page.
5. **Standard, practice, and one server are three different things.** Always separate what a specification requires, what implementations commonly do, and what only a particular server does. Never write "ActivityPub does X" when you mean "Mastodon does X".
6. **No global verdicts.** Do not label software best or worst. A poor choice for a large public instance can be an excellent reference for a single-user server. State tradeoffs and the context they apply in.
7. **Everything is versioned.** Protocol support changes between releases. A statement about an implementation names the version (and, when behaviour depends on code, the commit).

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

## Page types

Pick exactly one type per page. If a topic spans types, split into linked pages.

| Type | Where | What it is |
| ---- | ----- | ---------- |
| Hub | every section `index.md` | What the section covers, curated links to every page in it |
| Protocol | `fundamentals/`, `references/specifications/` | One protocol or mechanism: what the spec requires, with real requests and JSON |
| Lifecycle | `federation/activities/`, `federation/delivery/` | A traced sequence: each HTTP request, database mutation, queued job and notification |
| Compatibility record | `federation/compatibility/` | One feature across implementations, per version and direction |
| Failure mode | `federation/failure-modes/` | One reproducible problem, searchable by symptom |
| Case study | `servers/case-studies/`, `clients/case-studies/` | One implementation studied at source level |
| Software fact sheet | `references/software/` | Version-pinned reference facts for one implementation |
| FEP record | `references/feps/` | One proposal and who emits, accepts or rejects it |
| Engineering | `servers/…`, `clients/…`, `security/`, `moderation/`, `testing/` | A practical problem and how to solve and verify it |
| Guide | `guides/` | A start-to-finish implementation walkthrough linking to case studies |

## Templates

Copy the matching template. Delete sections that genuinely don't apply, but never delete `Technical details` or `Sources`. If detail is unknown, say what is unknown.

### Hub

```markdown
# <Section name>

Plain-language overview: what this section answers and who needs it. 3–5 sentences.

## Pages

- [Page](page.md) — what it covers, in one sentence.

## Notes and open questions

What is not covered yet, what is uncertain.

## Sources

- [Title](URL) — what this source covers
```

### Protocol page

```markdown
# <Mechanism name>

Plain-language overview. What problem this solves and where it sits in a federated exchange. 3–6 sentences.

## What the specification requires

Normative behaviour, quoting section numbers. Mark MUST/SHOULD/MAY as the spec does.

## What implementations do

Common practice, and where it departs from the spec. Link to compatibility records and case studies.

## Technical details

Real HTTP requests and responses, JSON examples, headers, state transitions, error codes.

## Pitfalls

Mistakes that cost people time, each with symptom and fix.

## Sources

- [Title](URL) — what this source covers
```

### Lifecycle page

```markdown
# <Lifecycle title, e.g. "Life of a federated post">

Plain-language summary of the whole journey. 3–5 sentences.

## Actors and starting state

Which servers and accounts take part, and what each already knows.

## Step by step

One numbered step per event. Each gives: the HTTP request (method, path, key headers), the database change, the queued job, the notification, and what can fail. Where implementations differ, say so and link to the case study.

## Technical details

Full payloads and header sets.

## Pitfalls

## Sources
```

### Compatibility record

```markdown
# <Feature, e.g. "Emoji reactions">

Plain-language overview: what users expect from this feature and why implementations disagree. 3–5 sentences.

## Summary

| Software | Version | Emits | Accepts | Notes |
| -------- | ------- | ----- | ------- | ----- |

Values for Emits and Accepts: `native`, `translated`, `ignored`, `rejected`, `lossy`, `untested`. Define each in the Technical details section on first use in the record.

## Information lost in translation

What a remote feature becomes, or whether it disappears, when another implementation receives it.

## Technical details

Wire format per implementation (JSON excerpt), the code path that produces or consumes it (file at a pinned commit), and the evidence label for every row.

## Test procedure

How to reproduce each row, or why it cannot yet be tested.

## Sources
```

### Failure-mode page

```markdown
# <Symptom, e.g. "Replies missing on remote threads">

Plain-language description of what the user sees. 2–4 sentences.

## Expected and observed behaviour

## Root cause

The protocol operation that fails and why.

## Affected versions

| Software | Versions | Status |
| -------- | -------- | ------ |

## Code path

Files and functions, at a pinned commit.

## Reproduction

Exact steps, or what is missing to make it reproducible.

## Technical details

## Sources
```

### Case study

```markdown
# <Software name and version range>

Plain-language overview: what it is, who it is for, what is distinctive about its engineering. 3–6 sentences.

## Architecture

Language, framework, process model, queues, storage. Link the architecture and storage pages instead of restating general designs.

## Key code paths

Inbox receipt, object resolution, delivery, timeline fan-out, media. Each names files and functions at a pinned commit.

## API coverage

## Federation behaviour

What it emits and accepts, linked to compatibility records.

## Resource usage

Measured memory, CPU, database size, with conditions. Unmeasured is stated as unmeasured.

## Strengths, known bugs and tradeoffs

## Technical details

## Sources
```

### Engineering page and guide

```markdown
# <Problem-oriented title>

Plain-language overview: which problem this solves, who hits it, the short answer. 2–4 sentences.

## Before you start

Versions the page was checked against, prerequisites.

## <Task sections>

One section per task or decision, in the order a developer meets them. Each gives: what to do, a minimal code, SQL or HTTP example, what to expect, and how it fails. Recommendations say whether they are a measured finding or a design opinion.

## Technical details

## Pitfalls

## Open questions

What has not been measured or verified, and what experiment would settle it.

## Sources
```

### Software fact sheet and FEP record

A software fact sheet starts with the exact version, release date and commit, then a table of facts, each with its evidence label and source file. A FEP record starts with the FEP number, title, status (`proposed`, `draft`, `final`, `withdrawn`, `experimental`) and date checked, then a table of which software emits, accepts, partially implements or rejects it, per version.

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
2. Pick the one correct page type, copy its template, use the right directory and a kebab-case name.
3. Read the relevant `private-gitignore/` research and the upstream source. Verify claims against the pinned version; move anything unverified to open questions with a `[hypothesis]` label.
4. Draft the Overview in plain language, then complete Technical details.
5. Add glossary entries for new jargon. Add the page to `nav` and to its section hub, and update neighbouring pages to link back.
6. Run `python3 tools/check_docs.py` and `zensical build --strict` before committing.
7. Commit as `terezi <jules@foxtails.me>` with a plain message and no attribution trailer of any kind.
