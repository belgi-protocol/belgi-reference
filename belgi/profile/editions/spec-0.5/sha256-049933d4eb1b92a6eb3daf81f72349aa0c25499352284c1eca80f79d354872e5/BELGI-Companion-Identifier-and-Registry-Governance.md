# BELGI - Companion specification: Identifier and registry governance

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is a BELGI companion specification. It defines the allocation, lifecycle, snapshot, and change-control rules for stable BELGI identifiers without making a registry the source of identifier meaning or replay authority.

## Introduction

BELGI specifications use stable identifiers for specification families, profiles, companions, terms, procedures, algorithms, verification methods, media types, problem types, and other controlled protocol surfaces.

An identifier registry can coordinate those allocations and record their lifecycle. It cannot replace the exact defining artifact that owns meaning, and a mutable registry view cannot replace the exact-edition material preserved for replay.

This companion specification defines publisher-controlled identifier rules, one closed allocation lifecycle, immutable registry snapshots, fail-closed handling, and a publicly reviewable BELGI allocation process. It also separates identifier lifecycle from signer-key authorization and revocation.

## 1 Scope

This document defines:

- controlled HTTPS identifiers for BELGI-owned URI identifier families;
- minimum registry-entry and definition-linkage requirements;
- collision, reservation, allocation, and non-reassignment rules;
- the closed identifier lifecycle;
- immutable registry snapshots and a non-authoritative mutable latest view;
- registration, modification, review, and appeal procedures; and
- producer and consumer obligations for identifier handling.

This document is applicable to BELGI specifications, profiles, companions, conformance artifacts, registries, producers, and consumers that allocate or process globally reusable BELGI identifiers or BELGI-controlled media-type values.

This document does not define:

- the semantic meaning of a registered identifier;
- the replay procedure, replay outcome classes, or replay problem types owned by BELGI - Part 2;
- the algorithms, representations, media formats, profiles, or companion vocabularies referenced by registry entries;
- signer authorization, trusted-signer policy, signer-key compromise handling, or signer-key revocation;
- a mandatory online lookup or publication service; or
- an IANA, IETF, ISO, or other external registration process or status.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in BELGI - Parts 1 to 3 and the following apply.

### 3.1 allocation

recorded assignment of one identifier string or other registered value to one registry entry under one change controller

### 3.2 defining artifact

exact source artifact that normatively defines the meaning or format associated with an allocated identifier

### 3.3 definition locator

stable Clause number within a defining artifact that identifies the location of the registered definition

### 3.4 registry entry

record of an allocation, its lifecycle status, its exact defining artifact and definition locator where semantics are assigned, its change controller, and its lifecycle history

### 3.5 registry event

append-only record of one authorized reservation, activation, deprecation, retirement, prohibition, or revocation decision that establishes or changes allocation status

### 3.6 registry snapshot

immutable versioned document containing one closed set of registry entries and registry events

### 3.7 latest view

mutable discovery view identifying a currently designated registry snapshot or current policy information

### 3.8 reserved identifier

allocated identifier string to which no semantics are assigned and which is unavailable for normative use

### 3.9 active identifier

identifier assigned to one defining artifact and permitted for new normative use under that artifact

### 3.10 deprecated identifier

identifier whose assigned meaning is retained while new normative use is discouraged or disallowed as recorded by its deprecation event

### 3.11 retired identifier

identifier whose assigned historical meaning is retained and whose new normative use is forbidden

### 3.12 prohibited identifier

identifier whose record is retained while use is forbidden for the reason fixed by its prohibition event

### 3.13 signer-key revocation

trust-policy decision that a verification key is no longer authorized for a stated signer, scope, or time

## 4 Symbols and abbreviated terms

### 4.1 Symbols

No symbols are listed in this document.

### 4.2 Abbreviated terms

No abbreviated terms are listed in this document.

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 13 are normative unless stated otherwise.

Stable local requirement identifiers beginning with `IR-` label requirements for traceability into machine-readable registry and conformance material. The `IR-` prefix is reserved to this companion specification. A retired `IR-` requirement identifier shall not be reused. A requirement identifier is not a substitute for the requirement text.

Requirement identifier: `IR-TRACE-001`.

This document owns identifier allocation, registry lifecycle, registry snapshots, and registry change control. The exact defining artifact owns the meaning or format associated with an identifier. BELGI - Part 2 owns replay procedure and replay failure classification.

## 6 Companion identity and authority boundary

### 6.1 Companion identifier and version designator

The companion identifier of this companion specification is:

`https://belgi.dev/ids/companion/identifier-and-registry-governance`

The current draft version designator is:

`0.5`

The owning publisher and change controller is:

`belgi`

### 6.2 BELGI dependency declaration

This companion specification and the BELGI documents named in Clause 2 are
members of the coherent `spec-0.5` Working Draft family.

The materialized immutable designator for each exact `spec-0.5` source is
established from the closed coherent source set. This document therefore does
not embed a digest of a same-family registry snapshot or semantic document
that would depend back on this document. Replay-relevant use shall preserve
the materialized immutable designators in accordance with BELGI - Parts 1 to
3.

### 6.3 Part 3 boundary served

This companion specification serves the identifier and registry-governance boundary defined by BELGI - Part 3, Clause 11.5. It serves no semantic extension point in Part 3, Clause 8, and it does not define profile, companion, term, algorithm, procedure, representation, or replay meaning.

### 6.4 Machine-readable material

The registry schema, registry snapshot, registry inventory, and identifier-registry conformance corpus associated with this companion are subordinate machine-readable artifacts. Their exact source-byte bindings are established outside the semantic documents so that no same-family digest cycle is created.

No registry artifact or conformance case may introduce an allocation rule, lifecycle rule, identifier meaning, or failure behavior absent from this document or the exact defining artifact.

Operation names, candidate fields, expected-result labels, and reason codes in
the identifier-registry conformance corpus are corpus-local controls. They are
not registered identifiers, required implementation diagnostics, replay
problems, replay outcomes, or a second failure taxonomy. The applicable
requirement text and exact defining artifact remain authoritative.

Those corpus-local controls, JSON Schema keywords, schema structural metadata,
JSON Pointers, and inventory bookkeeping values are not meaning-bearing compact
identifier vocabularies under 7.5 unless an owning normative clause explicitly
declares a value to be part of an implementation-facing vocabulary.

### 6.5 Compatibility statement

This `0.5` Working Draft succeeds exact `0.4`. This companion specification
declares no backward compatibility, forward compatibility, or replay
substitution with its predecessor.

## 7 Controlled identifier rules

### 7.1 Publisher-controlled HTTPS identifiers

A BELGI-owned URI identifier allocated for a specification family, profile family, companion family, term, procedure, algorithm, verification method, representation, problem type, adapter protocol, or other normative BELGI surface shall be an absolute HTTPS URI under the publisher-controlled prefix:

`https://belgi.dev/ids/`

For an allocation under that prefix, the exact lexical grammar is:

```regex
^https://belgi\.dev/ids/[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?(?:/[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?)*$
```

This expression is applied as a whole-string match. Its terminal `$` denotes
the absolute end of the string, not a position before a final line terminator.

The grammar admits one or more non-empty slash-separated path segments. Each
segment uses only lowercase ASCII letters, ASCII digits, full stops, and
hyphens, and begins and ends with a lowercase ASCII letter or ASCII digit. It
admits no port, user information, query, fragment, empty segment, trailing
slash, percent-encoded octet, uppercase letter, or underscore.

This is an allocation grammar, not a generic URI-validity test. A received
candidate that is a syntactically valid absolute HTTPS URI but differs from an
allocated identifier by case, percent encoding, delimiter, path spelling, or
another URI variation is an unknown identifier, not a malformed URI solely
because it is outside this allocation grammar. It shall not compare equal to
the allocated identifier.

A non-BELGI publisher allocating an identifier for use at a BELGI extension point shall use an absolute HTTPS URI under that publisher's documented change control unless the governing BELGI specification explicitly requires another registered identifier scheme.

Media types and other registry values whose defining syntax is not a URI are governed by their defining syntax and are not converted into HTTPS identifiers by this clause.

Requirement identifier: `IR-ID-HTTPS-001`.

### 7.2 Opaque exact comparison

A controlled HTTPS identifier shall be processed as one opaque exact string. A consumer shall not dereference it, follow a redirect, infer meaning from path segments, case-fold it, percent-normalize it, remove or add delimiters, or accept a URI variant as equal.

The identifier string is not an immutable designator and does not by itself identify one exact source edition.

Requirement identifier: `IR-ID-OPAQUE-001`.

### 7.3 Stability, no aliases, and no reassignment

An allocated identifier shall identify at most one assigned meaning for its entire lifetime. It shall not be reassigned, reused, or made an alias for another identifier.

A label, abbreviation, predecessor reference, successor reference, redirect, normalized URI form, or registry relationship shall not create identifier equivalence or replay substitution.

A meaning-bearing change shall receive a new identifier. An editorial clarification that does not change meaning may retain the identifier only through the modification procedure of Clause 11.2.

Requirement identifier: `IR-ID-STABILITY-001`.

### 7.4 Predecessor URNs

The `urn:belgi:*` identifiers used by predecessor draft editions remain identifiers only within the exact predecessor material that defined them. In the `spec-0.3` registry they shall be retained as retired historical allocations and shall not be emitted for new `spec-0.3` normative use.

A predecessor or successor relationship between an old URN and a controlled HTTPS identifier is discovery metadata only. It shall not authorize aliasing, redirect following, fallback, equivalence, normalization, or replay substitution.

Requirement identifier: `IR-ID-LEGACY-001`.

The `spec-0.2` Package integrity anchor verification companion also used these
two HTTPS strings as values in a defective URI-text designator construction:

```text
https://belgi.dev/definitions/package-integrity-anchor/ed25519-detached-manifest-signature
https://belgi.dev/definitions/substrate/crypto/ed25519
```

Those values remain part of the exact preserved `spec-0.2` source bytes. They
are not registry schema v1 allocations, globally reusable identifiers, aliases,
substitutes, predecessor mappings, successor mappings, or migration targets.
The BELGI publisher permanently reserves both strings from reuse and shall not
allocate either string a meaning under this or a later BELGI identifier
namespace. Their preservation shall not authorize URI-text hashing or
substitution for the method and algorithm identifiers defined by a later exact
edition.

Requirement identifier: `IR-ID-LEGACY-DESIGNATOR-001`.

### 7.5 Registry schema v1 scope and exact-edition-local compact identifier vocabularies

The BELGI identifier registry schema version 1 governs:

- controlled HTTPS identifiers allocated under `https://belgi.dev/ids/`; and
- BELGI-owned media-type values allocated by exact BELGI representation specifications.

Every snapshot using registry schema version 1 shall also carry the predecessor
`urn:belgi:*` family identifiers as first-class retired historical entries.
Those records exist to make retirement, non-reassignment, and discovery-only
predecessor or successor relationships machine-checkable; they are not active
allocations in the controlled HTTPS namespace.

An exact-edition-local compact identifier vocabulary is a named set of
non-URI tokens that carry meaning in a normative carrier, profile, companion,
representation, or replay interface. Its namespace identity is the ordered pair
of the defining family identifier and the vocabulary name declared by the exact
defining artifact. The exact defining edition owns each token's meaning; the
family line owns non-reassignment of that token within the named namespace.

The defining artifact shall require exact string comparison without case
folding, Unicode normalization, whitespace trimming, prefix expansion, URI
resolution, or other normalization. It shall prohibit two different meanings
from receiving the same token within the same named namespace. Once a token is
assigned within that namespace, no later edition of the defining family shall
assign it a different meaning, and retirement or removal shall not make it
available for reassignment.

Such a compact identifier token is not required to appear in the schema v1
global registry. It remains subordinate to its exact defining edition and is
not globally reusable without that family, vocabulary, and exact-edition
context.

Corpus case identifiers, corpus operation names, validation-stage labels,
corpus-only expected-result labels, diagnostic reason labels, JSON Schema
keywords, schema structural metadata, JSON Pointers, and inventory bookkeeping
values are outside this clause when they serve only conformance-fixture or
schema-description mechanics and are not exposed as normative implementation
vocabulary. A normative schema `enum` or `const` string that carries
implementation-facing meaning is within this clause and shall receive an
owner-declared namespace.

A local token shall not be treated as globally reusable outside its exact declared scope. If a later specification externalizes it as a globally reusable identifier, that specification shall allocate a new controlled HTTPS identifier under Clause 7.1; it shall not silently promote, prefix, or alias the local token.

Requirement identifier: `IR-REGISTRY-SCOPE-001`.

## 8 Registry entry and allocation integrity

### 8.1 Minimum entry shape

Each registry entry shall contain, at minimum:

- `identifier`;
- `kind`;
- `allocationStatus`;
- `changeController`; and
- `introducedIn`.

In a registry schema v1 entry, `kind` shall be exactly one of:

```text
specification | profile | companion | term | procedure |
digest-algorithm | signature-algorithm | verification-method |
representation | problem-type | result-code | field-name |
adapter-protocol | media-type
```

These values form the exact-edition-local `registry-entry-kind` vocabulary
owned by this companion specification.

An entry that assigns semantics shall also contain one `definingDesignator` and one `definitionLocator`. A reserved entry shall contain neither field.

An entry may contain predecessor or successor references only as explicitly non-authoritative discovery metadata. It shall not contain an alias field or another field that authorizes substitution.

When a registry schema v1 entry contains a `predecessorIdentifier` or
`successorIdentifier`, its corresponding `predecessorRelationship` or
`successorRelationship` value shall be exactly
`non-authoritative-discovery-only`. That token means the relationship supports
discovery only and grants no aliasing, equivalence, normalization, fallback,
or replay substitution.

A registry schema v1 `media-type` entry shall carry `registrationAuthority` with the
exact value `belgi` and `externalRegistrationStatus` with the exact value
`not-iana-registered`. The first token identifies the BELGI publisher as the
owner of this registry allocation. The second records that the entry makes no
IANA-registration claim; it shall not be interpreted as an IANA decision or as
authority to replace the applicable external registry.

Requirement identifier: `IR-ENTRY-001`.

### 8.2 Exact defining artifact and Clause locator

The `definingDesignator` shall identify the exact defining artifact in accordance with BELGI - Parts 1 and 2. The `definitionLocator` shall be a stable Clause locator in the form `Clause N` or `Clause N.N`, continued to the required decimal depth, and shall identify the Clause within that exact artifact at which the registered meaning or format is normatively defined.

The defining artifact and identified clause own meaning. The registry may summarize a registration for discovery but shall not restate, widen, narrow, or override the definition.

If registry or discovery material conflicts with the exact defining artifact, the exact defining artifact prevails and the conflict shall fail closed at the governing procedure stage.

Requirement identifier: `IR-DEFINITION-001`.

### 8.3 Collision prevention

Before reservation or activation, the registry authority shall compare the proposed identifier as an exact string against every existing and reserved identifier in every registry kind governed by the same registry.

An exact-string collision shall reject. A visually similar string, confusable Unicode string, normalized URI variant, case variant, or misleading hierarchy shall be reviewed for confusion risk and shall reject when it could create ambiguous or unsafe processing.

Requirement identifier: `IR-COLLISION-001`.

### 8.4 Reservation

Reservation allocates one identifier string without assigning semantics. A reserved identifier shall not have a defining designator or definition locator and shall not be emitted, interpreted, or advertised as a defined normative value.

Reservation does not authorize later assignment without the activation review required by Clause 11.1.

Requirement identifier: `IR-RESERVATION-001`.

## 9 Lifecycle and revocation boundary

### 9.1 Closed lifecycle

The `allocationStatus` value shall be exactly one of:

`reserved | active | deprecated | retired | prohibited`

The lifecycle meanings are:

- `reserved`: the string is allocated but has no assigned semantics and no normative use is permitted;
- `active`: the assigned meaning is fixed by the defining artifact and new normative use is permitted by that artifact;
- `deprecated`: the assigned meaning is retained, while the deprecation event records a `newUseDisposition` of either `discouraged` or `disallowed`;
- `retired`: the assigned historical meaning is retained and new normative use is forbidden; and
- `prohibited`: the entry is retained and use is forbidden for the reason fixed by the prohibition event.

Lifecycle status does not create a new meaning, make a successor equivalent, or change the exact defining artifact.

Requirement identifier: `IR-LIFECYCLE-001`.

### 9.2 Transition events

Every reservation, activation, or lifecycle change shall append one event containing the identifier, resulting status, rationale, effective edition, and decision-source designator where one exists. An initial reservation or activation event has no prior status; every later lifecycle event shall record the prior status. Existing events shall not be changed or removed.

The `eventType` value shall be exactly one of:

`reservation | activation | deprecation | retirement | prohibition | revocation`

The event-to-resulting-status mapping is:

- `reservation` to `reserved`;
- `activation` to `active`;
- `deprecation` to `deprecated`;
- `retirement` to `retired`; and
- `prohibition` to `prohibited`.

A `revocation` event shall result in `retired` or `prohibited` in accordance
with 9.3; it does not create a `revoked` allocation status.

The permitted transitions are:

- `reserved` to `active` or `prohibited`;
- `active` to `deprecated`, `retired`, or `prohibited`;
- `deprecated` to `active`, `retired`, or `prohibited`; and
- `retired` to `prohibited`.

`prohibited` is terminal. `retired` shall not return to active or deprecated. A lifecycle event shall not change the identifier string, defining meaning, or change controller. A metadata modification or change-controller transfer is governed separately by 11.2 and shall not be encoded as a lifecycle event.

Requirement identifier: `IR-TRANSITION-001`.

### 9.3 Identifier revocation and signer-key revocation

There is no generic `revoked` allocation status. A decision described as revocation shall be recorded as an event that results in `retired` or `prohibited`, preserves the entry and its history, and does not make the string available for reassignment.

Signer-key compromise or signer-key revocation is a separate trust-profile and operator-policy concern. It shall not alter an identifier allocation, algorithm definition, verification-method definition, or cryptographic verification result. A specification that evaluates signer authorization shall separately identify the exact authorization policy, scope, effective-time rule, and replay-relevant revocation evidence on which that evaluation depends.

Requirement identifier: `IR-REVOCATION-001`.

### 9.4 Local registry vocabulary governance

The implementation-facing registry tokens defined by 8.1, 9.1, and 9.2 form
the following named compact identifier vocabularies:

| Vocabulary | Tokens | Namespace identity |
| --- | --- | --- |
| `registry-entry-kind` | the fourteen values listed in 8.1 | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-entry-kind`) |
| `registry-discovery-relationship` | `non-authoritative-discovery-only` | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-discovery-relationship`) |
| `registry-registration-authority` | `belgi` | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-registration-authority`) |
| `registry-external-registration-status` | `not-iana-registered` | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-external-registration-status`) |
| `registry-allocation-status` | `reserved`, `active`, `deprecated`, `retired`, `prohibited` | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-allocation-status`) |
| `registry-event-type` | `reservation`, `activation`, `deprecation`, `retirement`, `prohibition`, `revocation` | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-event-type`) |
| `registry-new-use-disposition` | `discouraged`, `disallowed` | (`https://belgi.dev/ids/companion/identifier-and-registry-governance`, `registry-new-use-disposition`) |

Within each namespace, tokens shall be compared as exact strings without
case folding, Unicode normalization, whitespace trimming, prefix expansion, or
other normalization. No two meanings may share one token in the same namespace.
Once assigned, a token shall not be reassigned a different meaning by a later
edition of this companion family, and retirement or removal shall not make it
available for reassignment.

Requirement identifier: `IR-LOCAL-VOCABULARY-001`.

## 10 Snapshot and replay-authority rules

### 10.1 Immutable snapshots

A registry snapshot shall be an immutable, versioned document with closed `entries` and `events` collections. The snapshot shall have an immutable designator over its exact source bytes. An entry or event in a released snapshot shall not be changed, removed, reordered where order is significant, or silently replaced.

A new registry state shall be issued as a new snapshot. Existing snapshot bytes and immutable designators shall remain available for their required historical lifetime.

Requirement identifier: `IR-SNAPSHOT-001`.

### 10.2 Mutable latest view

A mutable latest route or view may identify a current snapshot, current production guidance, or current security notice for discovery and authoring.

The latest view, a redirect, DNS resolution, network response, local cache, package-provided registry material, or implementation default shall not determine replay meaning, replace a preserved exact defining artifact, authorize successor substitution, or change a historical semantic tuple or verdict.

Requirement identifier: `IR-LATEST-001`.

### 10.3 Exact registry edition authority

A registry snapshot is replay-relevant authority only when an owning exact BELGI specification explicitly declares that exact snapshot to be replay-relevant and the replay package preserves its immutable designator and required bytes in accordance with BELGI - Parts 1 and 2.

By default, a replay-relevant use shall bind the exact defining artifact directly rather than the complete registry snapshot. A registry snapshot used only for discovery, collision review, or current production policy shall not enter replay closure.

Requirement identifier: `IR-AUTHORITY-001`.

### 10.4 Acyclic binding

A semantic document shall not embed the content digest of a same-family registry snapshot that points back to that semantic document. Registry artifacts shall point to exact semantic-document designators and clause locators, while an external inventory binds the registry schema, snapshot, and conformance artifacts after their bytes are closed.

Requirement identifier: `IR-ACYCLIC-001`.

## 11 Registration and change control

### 11.1 BELGI Specification-Required-style allocation

Activation of an identifier shall require publicly reviewable defining text that is sufficiently stable and precise for independent implementation, one named change controller, an exact-string collision check, security and compatibility considerations, and one recorded allocation decision.

The reviewer shall confirm that the defining artifact, rather than the registry entry or a machine-readable corpus, is the first owner of meaning.

Requirement identifier: `IR-REGISTRATION-001`.

### 11.2 Modification

An authorized modification may correct contact data, locators, non-normative summaries, or other registry metadata without changing the identifier's assigned meaning.

A meaning-bearing change shall allocate a new identifier and shall not be described as a clarification, compatible registry update, alias, or correction.

Every metadata modification shall have a public decision record identifying the
entry, changed fields, prior and replacement values, authority, rationale, and
effective registry edition. A change-controller transfer shall require an
authenticated public decision from the current controller or the appeal
authority and shall record the prior controller, replacement controller,
authority, rationale, and effective registry edition. Either change shall
appear only in a new immutable registry snapshot and shall not mutate an
existing snapshot.

A metadata modification or change-controller transfer is not a registry
lifecycle event unless it also changes allocation status. When status changes,
the new snapshot shall contain the separate lifecycle event required by Clause
9; that event shall not carry or imply the metadata or controller change.

Requirement identifier: `IR-MODIFICATION-001`.

### 11.3 Review and conflict handling

Every allocation and lifecycle request shall receive a recorded review against the criteria of this document. A reviewer with an authorship, financial, organizational, or other material conflict shall disclose that conflict and recuse. A replacement reviewer shall be named in the decision record.

The review record shall identify the request, reviewer, considered defining artifact, collision result, security and compatibility considerations, decision, rationale, and effective registry edition.

Requirement identifier: `IR-REVIEW-001`.

### 11.4 Appeal

An allocation, modification, lifecycle, or reviewer-recusal decision may be appealed through a publicly documented BELGI appeal route. The appeal shall identify the challenged decision and grounds. A reviewer who did not make the challenged decision shall issue a reasoned, recorded disposition or refer the matter to the named BELGI change controller.

An appeal shall not mutate an existing registry snapshot. A successful appeal shall produce a public appeal-disposition decision record and, where registry state changes, a new registry snapshot. If the disposition changes allocation status, the new snapshot shall also contain the separate lifecycle event required by Clause 9; a metadata or controller disposition shall not be encoded as a lifecycle event.

Requirement identifier: `IR-APPEAL-001`.

### 11.5 External-process non-claim

The process in Clauses 11.1 to 11.4 is the BELGI Specification-Required-style process. It incorporates the public-specification, expert-review, change-control, conflict, and appeal pressure described by RFC 8126 without claiming that BELGI, its registry, or its reviewers are IANA, IETF, ISO, or another external registration authority or process.

Use of RFC 6838 vendor-tree syntax or an RFC 6839 structured syntax suffix likewise does not by itself establish IANA media-type registration. External registration status shall be stated only from the applicable external registry.

Requirement identifier: `IR-EXTERNAL-001`.

## 12 Producer and consumer behavior

### 12.1 New normative use

A producer shall emit an identifier in new normative material only when the governing exact BELGI edition permits that identifier and the applicable allocation status permits new use.

An active identifier permits new use. A deprecated identifier permits new use only when its deprecation event records `discouraged` and the governing exact edition still permits it; a `disallowed` deprecated identifier shall not be emitted. Reserved, retired, and prohibited identifiers shall not be emitted for new normative use.

Requirement identifier: `IR-PRODUCER-001`.

### 12.2 Historical interpretation

Lifecycle change shall not alter the historical meaning fixed by an exact defining artifact. A consumer processing preserved material shall use only the exact defining artifact selected under BELGI - Parts 1 and 2 and shall not substitute a successor, predecessor, alias, registry summary, or current web response.

A consumer may interpret a deprecated or retired historical identifier only when the governing exact edition permits that historical use and all required exact defining material is available. Prohibited use is governed by the independently selected verifier security policy under 12.5.

Requirement identifier: `IR-CONSUMER-001`.

### 12.3 Malformed, unknown, unsupported, and conflicting identifiers

A syntactically malformed identifier, unknown identifier, reserved identifier, known but unsupported identifier, identifier prohibited by the governing exact edition or the selected verifier security policy, or identifier whose registry or discovery material conflicts with the exact defining artifact shall fail closed at the procedure stage that owns the identifier's use.

The owning specification shall assign the applicable deterministic representation result, replay problem, or other failure class. This companion shall not create a generic central identifier-error facade or replace the failure taxonomy of BELGI - Part 2.

Requirement identifier: `IR-FAILURE-001`.

### 12.4 No downgrade or fallback

Failure to recognize, support, resolve, or admit an identifier shall not authorize algorithm negotiation, weaker-algorithm selection, procedure fallback, successor substitution, predecessor substitution, alias lookup, prefix matching, registry-latest replacement, or another attempt to reinterpret the candidate under a different identifier.

Requirement identifier: `IR-DOWNGRADE-001`.

### 12.5 Current security policy

A verifier may independently select a current security or support policy at the external bootstrap boundary defined by BELGI - Part 2. That policy may refuse execution of a historically defined algorithm, verification method, procedure, or other operation.

The verifier shall not treat the mutable latest view itself as executable policy. A refusal shall be attributed to the selected policy, shall not rewrite the claim's exact defining material or historical meaning, and shall not produce a substituted semantic tuple or verdict. A replay report that records such a refusal should identify the selected policy or immutable registry snapshot that informed it.

Requirement identifier: `IR-SECURITY-POLICY-001`.

## 13 Conformance

### 13.1 Conformance classes

The following conformance classes are defined:

- BELGI Identifier Registry Publisher;
- BELGI Identifier-allocating Specification; and
- BELGI Identifier-aware Consumer.

### 13.2 BELGI Identifier Registry Publisher

An implementation conforms as a BELGI Identifier Registry Publisher if it publishes registry entries, events, snapshots, reviews, and appeals in accordance with Clauses 7 to 11 and does not make a mutable latest view replay authority.

### 13.3 BELGI Identifier-allocating Specification

A specification conforms as a BELGI Identifier-allocating Specification if every identifier it allocates satisfies Clauses 7 to 9, the exact defining artifact owns its meaning, and its registration follows Clause 11.

### 13.4 BELGI Identifier-aware Consumer

An implementation conforms as a BELGI Identifier-aware Consumer if it applies the exact-comparison, authority, historical-use, fail-closed, and no-downgrade rules of Clauses 7, 10, and 12.

### 13.5 Conformance statement

A conformance statement shall identify the implementation or specification, this document and its exact edition, the conformance class claimed, each applicable exact registry snapshot, each independently selected security or support policy where one is used, and the date of the statement.

Requirement identifier: `IR-CONFORMANCE-001`.

## 14 Security considerations

Identifier collision, confusable strings, alias substitution, registry poisoning, mutable latest views, downgrade, lifecycle erasure, and change-controller impersonation can cause independent implementations to select different meaning or different procedures for the same preserved material.

Clauses 7 to 12 require exact comparison, one assignment for the lifetime of an identifier, collision review, append-only lifecycle events, immutable snapshots, exact defining artifacts, authenticated change control, fail-closed processing, and no downgrade or fallback.

Registry status is not a substitute for signer authorization. A cryptographically valid signature and an authorized signer are separate determinations. A profile that makes signer authorization replay-relevant must preserve the exact policy, scope, effective-time rule, and evidence required for that determination.

## 15 Privacy considerations

Registry entries and decision records expose change-controller, reviewer, publication, and lifecycle metadata. A registry shall publish only the information required to establish allocation authority, review accountability, interoperability, and security rationale.

Replay packages need not preserve mutable registry views, reviewer identities, or appeal records unless an owning exact specification makes that material replay-relevant. Applicable privacy and retention obligations apply independently to personal data in governance records.

## Annex A (informative) External policy relationship

RFC 8126, _Guidelines for Writing an IANA Considerations Section in RFCs_, is the policy-pattern reference for the BELGI process in Clause 11. It is available at `https://www.rfc-editor.org/rfc/rfc8126.html`.

The BELGI process is independently defined and operated. This companion specification makes no external registration, recognition, certification, or standards-body claim.
