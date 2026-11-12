# Glossary

Plain-language definitions for jargon used across the wiki. Entries are short and point to the page that tells the full story. Software-specific terms are at the end and name the software they apply to.

## General and protocol terms

<a name="activitypub"></a>

### ActivityPub (AP)

The W3C standard that lets social servers send each other posts, follows and likes, and (in theory) lets clients talk to servers. Precisely: a protocol built on [ActivityStreams](#activitystreams) with a server-to-server part and a client-to-server part. See [Fundamentals](fundamentals/index.md).

<a name="activitystreams"></a>

### ActivityStreams 2.0

The JSON vocabulary that describes actors, objects and activities ("Alice created a Note"). It is the data model ActivityPub carries. See [Fundamentals](fundamentals/index.md).

<a name="actor"></a>

### Actor

An account-like entity that can send and receive activities: a person, a group, a service. Each actor has an id (a URL), an inbox and usually an outbox. See [Fundamentals](fundamentals/index.md).

<a name="inbox"></a>

### Inbox

The URL where other servers deliver activities addressed to an actor. A **shared inbox** is one server-wide URL that receives an activity once for many local recipients, saving requests. See [Federation](federation/index.md).

<a name="fep"></a>

### FEP (Fediverse Enhancement Proposal)

A numbered community document that proposes or records an extension to the Fediverse protocols, such as quotes or follower synchronization. Statuses range from proposed to final or withdrawn. See [References](references/index.md).

<a name="nodeinfo"></a>

### NodeInfo

A small JSON document a server publishes about itself: software name, version, enabled protocols, usage counts. Clients and other servers use it to guess what a server supports. See [Fundamentals](fundamentals/index.md).

<a name="webfinger"></a>

### WebFinger

A lookup that turns an address like `user@example.com` into the URL of that account's actor. See [Fundamentals](fundamentals/index.md).

<a name="http-signature"></a>

### HTTP signature

A signature over selected HTTP headers that proves a request came from the server holding a given key. Federation uses it so a server can check who sent an activity. See [Security and privacy](security/index.md).

<a name="ssrf"></a>

### SSRF (server-side request forgery)

An attack where someone gets your server to fetch a URL of their choosing, for example one pointing at an internal network address. Federating servers fetch remote URLs constantly, so they are exposed to it. See [Security and privacy](security/index.md).

<a name="json-ld"></a>

### JSON-LD

A way of writing linked data as JSON, using a `@context` to give keys precise meaning. ActivityStreams documents are JSON-LD, but many implementations treat them as plain JSON. See [Fundamentals](fundamentals/index.md).

<a name="compatibility-values"></a>

### Compatibility values

The six values used in compatibility records for what a server does with a feature: **native** (handled as its own concept), **translated** (mapped to something similar), **ignored** (silently dropped), **rejected** (refused with an error), **lossy** (kept but with information lost), **untested** (nobody has checked). See [Federation](federation/index.md).

## Software-specific terms

<a name="mfm"></a>

### MFM (Misskey Flavored Markdown)

Misskey's markup for text effects and rich formatting in posts. Other software shows it as plain text or rewritten HTML. Applies to Misskey and its forks. See [References](references/index.md).

<a name="mrf"></a>

### MRF (Message Rewrite Facility)

A pluggable pipeline in Pleroma and Akkoma that inspects and can change or reject each incoming activity, used for moderation policy. See [Moderation](moderation/index.md).

<a name="sidekiq"></a>

### Sidekiq

The background job processor used by Mastodon (and other Ruby software) to run delivery and processing work off the web request. See [Servers](servers/index.md).
