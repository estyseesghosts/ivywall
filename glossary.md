# Glossary

Plain-language definitions for jargon used across the wiki. Entries are short and point to the page that tells the full story. Software-specific terms are at the end and name the software they apply to.

## General and protocol terms

<a name="activitypub"></a>

### ActivityPub (AP)

The W3C standard that defines both a client-to-server protocol and a way for social servers to exchange posts, follows and likes. Precisely: a protocol built on [ActivityStreams](#activitystreams) with a server-to-server part and a client-to-server part. See [Fundamentals](fundamentals/index.md).

<a name="activitystreams"></a>

### ActivityStreams 2.0

The JSON vocabulary that describes actors, objects and activities ("Alice created a Note"). It is the data model ActivityPub carries. See [Fundamentals](fundamentals/index.md).

<a name="actor"></a>

### Actor

An account-like entity that can send and receive activities: a person, a group, a service. ActivityPub actors have an identifier and advertise inbox and outbox URLs. [ActivityPub §4](https://www.w3.org/TR/2018/REC-activitypub-20180123/#actors) specifies these properties. See [Fundamentals](fundamentals/index.md).

<a name="inbox"></a>

### Inbox

The URL where other servers deliver activities addressed to an actor. A **shared inbox** is an optional endpoint advertised by actors that can receive a delivery for multiple local recipients. See [ActivityPub §7.1.3](https://www.w3.org/TR/2018/REC-activitypub-20180123/#shared-inbox-delivery). See [Federation](federation/index.md).

<a name="fep"></a>

### FEP (Fediverse Enhancement Proposal)

A numbered community document that proposes or records an extension to the Fediverse protocols, such as quotes or follower synchronization. Statuses range from proposed to final or withdrawn. See [References](references/index.md).

<a name="nodeinfo"></a>

### NodeInfo

A small JSON document a server publishes about itself: software name, version, enabled protocols, usage counts. Clients and other servers use it to guess what a server supports. See [Fundamentals](fundamentals/index.md).

<a name="webfinger"></a>

### WebFinger

A resource-discovery protocol that can turn an account address such as `user@example.com` into links including an ActivityPub actor URL; results and checks depend on the service. See [RFC 7033](https://www.rfc-editor.org/rfc/rfc7033). See [Fundamentals](fundamentals/index.md).

<a name="http-signature"></a>

### HTTP signature

A cryptographic signature over selected HTTP request components. A verified signature demonstrates possession of a signing key; the receiver must separately decide whom that key represents and whether the action is authorized. See [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421). See [Security and privacy](security/index.md).

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

Misskey's markup for text effects and rich formatting in posts. Other software may retain only the rendered representation. See the [Misskey 2026.10.1 case study](servers/case-studies/misskey.md). See [References](references/index.md).

<a name="mrf"></a>

### MRF (Message Rewrite Facility)

A pluggable Pleroma-family pipeline that can inspect, modify or reject federated messages for moderation policy. See the [Akkoma v3.20.0 implementation](https://akkoma.dev/AkkomaGang/akkoma/src/commit/98fcccccb1534280960d7123620c03a54b4b2442/lib/pleroma/web/activity_pub/mrf.ex#L66). See [Moderation](moderation/index.md).

<a name="sidekiq"></a>

### Sidekiq

A background job processor used by Mastodon 4.7.3 to run delivery and processing work off the web request. See its [queue configuration](https://github.com/mastodon/mastodon/blob/8ff11c2bb7b9f0714e947b10fa3629c6542c7121/config/sidekiq.yml). See [Servers](servers/index.md).
