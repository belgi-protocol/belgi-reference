# BELGI - Companion specification: JSON representation

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications; BELGI - Part 4: Software change admission profile; BELGI - Companion specification: Package integrity anchor verification; BELGI - Companion specification: Identifier and registry governance
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is the implementation-neutral JSON representation binding for
structures defined by Parts 1 to 4 in the coherent `spec-0.5` Working Draft
family. It also identifies one experimental Part 5 structure without promoting
Part 5 into `spec-0.5`.

This document is a member of the coherent `spec-0.5` Working Draft family.
The exact `spec-0.4` source edition remains immutable and is not replaced by
this source.

Its machine-readable material and requirement statements do not by themselves establish that the Python reference implementation or another implementation has adopted this draft.

## Introduction

BELGI Parts 1 to 4 and the Package integrity anchor verification companion define the semantic, replay, profile, and verification material represented by this draft. Part 3 governs the representation-specific extension point without making one JSON library or one implementation's parser behavior normative.

This companion fixes a bounded JSON text domain, one identified canonical JSON byte procedure, one exact Draft 2020-12 schema set, trusted schema-role selection, the relationship between representation prose and schemas, identified bounded directory and ZIP projections for replay packages, and BELGI-owned media-type allocations. It retains the existing eleven schema identities while keeping their source authority in the specification repository.

Identifier allocation and lifecycle governance are defined by the Identifier and registry governance companion. Implementation adoption remains outside this document.

## 1 Scope

This document defines:

- the accepted UTF-8 JSON text, Unicode, and number domains for BELGI JSON material;
- RFC 8785 JSON canonicalization for values admitted by that stricter domain;
- an exact JSON Schema Draft 2020-12 dialect and schema inventory;
- caller-trusted selection of an instance schema by role;
- conjunctive prose-and-schema validity;
- a bounded validation order;
- portable replay-package member paths and their physical projection;
- bounded directory and ZIP container projections;
- representation resource limits, recovery order, and rejection priority;
- relocation equivalence; and
- clause-linked machine-readable corpora.

This document does not define:

- general identifier allocation, lifecycle, downgrade, or retirement rules outside the identifiers allocated by this document;
- semantic domains for implementation-specific evaluator parameters;
- a general JSON transport for every BELGI extension;
- implementation adoption by Python, Go, or another runtime; or
- promotion of Part 5 into `spec-0.5`.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.5, 2026-07-21
- BELGI - Part 4: Software change admission profile, Version 0.5, 2026-07-21
- BELGI - Companion specification: Package integrity anchor verification, Version 0.5, 2026-07-21
- BELGI - Companion specification: Identifier and registry governance, Version 0.5, 2026-07-21
- RFC 8259, The JavaScript Object Notation Data Interchange Format
- RFC 7493, The I-JSON Message Format
- RFC 8785, JSON Canonicalization Scheme, including verified Errata IDs 6292 and 7920 as of 2026-07-19
- RFC 6838, Media Type Specifications and Registration Procedures
- RFC 6839, Additional Media Type Structured Syntax Suffixes
- RFC 1951, DEFLATE Compressed Data Format Specification version 1.3
- PKWARE, .ZIP File Format Specification, APPNOTE 6.3.10
- JSON Schema: A Media Type for Describing JSON Documents, Draft 2020-12
- JSON Schema Validation: A Vocabulary for Structural Validation of JSON, Draft 2020-12

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in the normative BELGI dependencies identified in Clause 6.2 and the following apply.

### 3.1 BELGI JSON text

exactly one completely consumed RFC 8259 JSON text admitted by Clause 7 and encoded as UTF-8

### 3.2 canonical JSON bytes

UTF-8 bytes produced from an admitted BELGI JSON value by the procedure in Clause 9

### 3.3 schema role

caller-trusted name selecting one root schema from the exact schema inventory

### 3.4 dependency role

inventory role for a dialect or schema resource that supports root-schema evaluation but is not selected as an instance root

### 3.5 representation prose

the JSON text, Unicode, number, canonicalization, role-selection, validation, portable-path, container, resource, and package-recovery requirements in this document

### 3.6 portable logical member path

ASCII name in the domain defined by 14.1 that identifies one member of a logical replay package

### 3.7 physical member path

container entry name that projects to one portable logical member path according to 14.2

### 3.8 logical member map

complete mapping from portable logical member paths to their exact preserved octet sequences

### 3.9 representation rejection

failure produced before a candidate physical container is admitted as one logical replay package

## 4 Symbols and abbreviated terms

### 4.1 Symbols

`Valid(r, b)` denotes representation validity for trusted role `r` and candidate byte sequence `b`.

### 4.2 Abbreviated terms

- I-JSON: Internet JSON
- JCS: JSON Canonicalization Scheme
- CRC-32: 32-bit cyclic redundancy check used by the ZIP projection
- UTF-8: Unicode Transformation Format, 8-bit form

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 23 are normative unless stated otherwise.

Stable local requirement identifiers beginning with `JR-` label requirements for traceability into machine-readable material. The `JR-` prefix is reserved to this companion, and a retired `JR-*` requirement identifier shall never be reused. An identifier is not a substitute for the requirement text.

This document does not alter the semantic authority of Part 1, the replay authority of Part 2, the extension-governance authority of Part 3, the profile authority of Part 4, or the verification-method authority of the Package integrity anchor verification companion. Schema acceptance creates no semantic object, replayability result, integrity result, verdict, profile conformance, or organizational authorization.

## 6 Companion identity and exact material

### 6.1 Companion identity

The companion identifier is:

`https://belgi.dev/ids/companion/json-representation`

The current draft version designator is:

`0.5`

This source is a normative member of the coherent `spec-0.5` Working Draft
family.

This `0.5` Working Draft succeeds exact `0.4`. This companion specification
declares no backward compatibility, forward compatibility, or replay
substitution with its predecessor.

The owning publisher and change controller is:

`belgi`

This companion serves the reserved extension point in BELGI - Part 3, Clause 8.11, for representation-specific schemas and serialization bindings. It serves no other Part 3 extension point in this draft.

### 6.2 Exact-edition dependency and applicability declaration

The following exact editions are normative BELGI dependencies of this companion:

| Dependency | Family identifier | Required draft version |
|---|---|---|
| BELGI - Part 1: Core semantic model | `https://belgi.dev/ids/specification/part-1` | `0.5` |
| BELGI - Part 2: Claim carriers and replay package | `https://belgi.dev/ids/specification/part-2` | `0.5` |
| BELGI - Part 3: Profiles and companion specifications | `https://belgi.dev/ids/specification/part-3` | `0.5` |
| BELGI - Part 4: Software change admission profile | `https://belgi.dev/ids/profile/software-change-admission` | `0.5` |
| BELGI - Companion specification: Package integrity anchor verification | `https://belgi.dev/ids/companion/package-integrity-anchor-verification` | `0.5` |
| BELGI - Companion specification: Identifier and registry governance | `https://belgi.dev/ids/companion/identifier-and-registry-governance` | `0.5` |

Each dependency shall be bound to its exact defining source bytes by immutable designator. The family identifier and version label in this table aid closed-family identification but shall not substitute for that exact source-byte binding.

BELGI - Part 5: Operational-action admission profile, Version 0.3, is referenced only as excluded experimental context under family identifier `https://belgi.dev/ids/profile/operational-action-admission`. It is not a normative dependency of this companion. Its contextual identification neither activates nor promotes Part 5, does not incorporate Part 5 into `spec-0.5`, and authorizes no Part 5 conformance claim.

### 6.3 Canonical schema inventory

This companion edition's schema inventory is the exact UTF-8 byte sequence of
`schema-inventory.json` designated for this companion edition. Its immutable
designator shall use SHA-256 over those exact bytes; a filename, mutable route,
family identifier, version label, or registry entry shall not substitute for
that source-byte binding.

The inventory binds each normative schema source path, schema URI, source-byte
digest, role, local dependency set, semantic-applicability track, and
requirement identifier. It also binds every exact conformance corpus selected
for that inventory. Clauses 12 and 22 define corpus roles and operation
semantics; a corpus is selected for an exact edition only through inclusion in
that edition's inventory.

Every entry in this companion edition's schema inventory shall have semantic
applicability `shared` or `parts-1-to-4`. Every corpus bound by its
`conformanceCorpora` member shall exercise only material with one of those
semantic applicability values. The `entries` and `conformanceCorpora` members
are closed: a schema or corpus omitted from them shall not become selected
through dependency discovery, a matching filename or URI, registry state, or
colocation with the inventory.

A file with the same name or URI but different bytes is not the inventory designated by this draft.

### 6.4 Schema identity and source authority

The schema inventory and the schema bytes it binds are normative material of this draft. Generated implementation copies, digest constants, package data, mutable URL responses, and validator caches shall not override those bytes.

For this companion edition, `schemaIdBase` shall be exactly
`https://belgi.dev/schemas/carrier/rc.v2`, and `dialectUri` shall be exactly
`https://belgi.dev/schemas/carrier/rc.v2/BELGI-JSON-Schema-Dialect.schema.json`.
Every schema selected by the base inventory shall have a source path and `$id`
under that `rc.v2` identity. Every selected non-dialect schema shall name the
exact `rc.v2` dialect through `$schema`, and every relative `$ref` shall resolve
within the exact graph selected by the inventory.

The complete `rc.v1` schema graph is an immutable predecessor. Its source
bytes, `$id` values, dialect identity, and published URIs shall not be changed,
rebound, redirected as substitutes, or treated as aliases for `rc.v2`. Reuse of
a filename or unchanged validation semantics does not preserve schema-resource
identity across those bases. This edition changes the validation semantics of
`ReplayReport.schema.json`; the other `rc.v2` resources are identity successors
with unchanged validation semantics relative to their exact `rc.v1`
counterparts.

The named BELGI Draft 2020-12 dialect is normative material. A validator shall support every vocabulary that the dialect marks as required or reject the dialect. Interpreting it through a partial keyword subset is not validation under this draft.

The Operational-Action overlay inventory is the exact UTF-8 byte sequence of `operational-action/schema-inventory.json` designated for the Part 5 working-draft context. It shall bind all of the following by immutable designator:

- the exact schema inventory selected by this companion edition through `baseSchemaInventory`;
- the exact current Part 5 working-draft source through `profileSource`;
- exactly one overlay schema entry, named `OperationalActionJudgedObjectCarrier.schema.json` and assigned role `operational-action-judged-object`; and
- the exact Operational-Action corpus described by Clause 12.

The overlay shall contain no other schema entry. It shall neither redefine nor
override a schema name, role, schema URI, or source path bound by this companion
edition's schema inventory. An overlay containing such a collision is not the
overlay designated by this draft. An overlay dependency on a base schema shall
resolve only against the exact schema inventory bound by `baseSchemaInventory`.
The overlay schema's source path, `$id`, and `$schema` shall use the same
`rc.v2` schema identity and dialect selected by that base inventory.

### 6.5 Applicability separation

This companion edition's schema inventory and selected corpora contain only
material marked `parts-1-to-4` or `shared` and serve the bounded representation
of the `spec-0.5` Working Draft family. Their selection by this source edition
does not establish adoption by Python, Go, or another implementation.

The Operational-Action overlay and the corpus it binds shall each declare
semantic applicability `part-5-working-draft`. They are experimental Part 5
material outside this companion edition's schema graph, selected corpora, and
`spec-0.5` conformance set. Their presence or successful evaluation shall not
promote or adopt Part 5, alter the dependency declaration in 6.2, establish
implementation adoption, or authorize a Part 5 conformance claim.

Requirement identifier: `JR-PART5-001`.

## 7 JSON text domain

### 7.1 Encoding and complete consumption

Input shall be exactly one RFC 8259 JSON text encoded as UTF-8. The entire byte sequence shall be consumed. A leading byte-order mark, malformed UTF-8, incomplete JSON text, or trailing non-whitespace content shall reject.

Whitespace admitted by RFC 8259 may surround the single JSON text. Comments, trailing commas, single-quoted strings, leading plus signs, leading zeroes, `NaN`, and infinities shall reject.

Requirement identifiers: `JR-UTF8-001` and `JR-SYNTAX-001`.

### 7.2 Object member names

Object member names shall be compared after JSON escape decoding as sequences of Unicode scalar values. Two names that decode to the same sequence are duplicates. A duplicate at any nesting depth shall reject.

Requirement identifier: `JR-NAME-001`.

### 7.3 Unicode domain

A string value or decoded object member name containing a surrogate code point from U+D800 through U+DFFF shall reject unless the JSON escape sequence is one valid high-surrogate/low-surrogate pair denoting its corresponding supplementary scalar value. A string value or decoded object member name containing a Unicode noncharacter shall reject. The noncharacters are U+FDD0 through U+FDEF and U+nFFFE and U+nFFFF in every plane from 0 through 16, inclusive.

For noncharacters, this rule deliberately strengthens and adapts the guidance in RFC 7493, Section 2.1, into a requirement over every decoded string, including a top-level string. This clarification does not change the accepted domain fixed by this draft.

Requirement identifier: `JR-UNICODE-001`.

### 7.4 Normalization

No Unicode normalization shall be performed. Canonically equivalent but scalar-sequence-distinct strings remain distinct values. Canonically equivalent but scalar-sequence-distinct object member names remain distinct names.

Requirement identifier: `JR-NORMALIZATION-001`.

### 7.5 JSON data model

Array order is significant. Object member order has no JSON-data-model meaning. Exact preserved input octets remain distinguishable from the parsed value and from canonical JSON bytes.

## 8 Number domain

An input number token shall satisfy all of the following rules:

1. It satisfies the RFC 8259 number grammar.
2. It decodes to a finite IEEE 754 binary64 value using round-to-nearest, ties-to-even.
3. Every lexical spelling of negative zero rejects.
4. Overflow and mathematically nonzero underflow to zero reject.
5. Every mathematically integral value lies in the inclusive interval `[-9007199254740991, 9007199254740991]`.
6. The exact rational value denoted by the input token equals the exact rational value denoted by RFC 8785 serialization of the decoded value.

The final rule admits alternate value-preserving spellings, including `1.2300`, while rejecting silent precision collapse, including `1.0000000000000000000000000001`. A value requiring greater range or precision shall be represented by a string under a separately defined semantic vocabulary.

JSON booleans are not numbers or integers. JSON Schema integer matching is based on mathematical value only after successful admission by this clause; lexical spelling does not create a distinct integer value.

Requirement identifier: `JR-NUMBER-001`.

## 9 Canonical JSON bytes

The stable identifier of the canonicalization procedure defined by this clause is:

`https://belgi.dev/ids/procedure/canonicalization/rfc-8785-jcs`

The identifier is opaque and shall be compared as an exact string. Its immutable designator shall bind the exact defining source bytes of this companion edition; hashing the identifier text or dereferencing the identifier is not a source-byte binding.

Canonical JSON bytes shall be produced only from a value admitted by Clauses 7 and 8 and valid under Clause 11.

The canonicalization procedure is RFC 8785 JCS with the stricter input domain of this document and the following fixed consequences:

- output is UTF-8 without a byte-order mark;
- output contains no insignificant whitespace and no trailing line feed;
- strings and numbers use RFC 8785 and referenced ECMAScript serialization;
- object members are ordered recursively by unsigned UTF-16 code units of their decoded names;
- array order is unchanged; and
- Unicode normalization is not performed.

An implementation-specific key-sorting or phrase-hash procedure shall not be relabeled as this procedure merely because it accepts the same data. A media type, schema role, filename, registry result, or package field shall not select this procedure.

Requirement identifier: `JR-CANONICAL-001`.

## 10 Trusted role and media-type bindings

### 10.1 Trusted role selection

One caller-supplied and independently trusted role binding shall select one root schema from the exact inventory before instance validation.

An instance `$schema` member, filename, package-member name, media type, mutable URL response, or implementation default shall not select or replace the trusted role.

The selectable root roles are:

- `claim-record`;
- `judged-object`;
- `evidence-state`;
- `evaluator`;
- `package-integrity-manifest`;
- `package-integrity-anchor`;
- `replay-report`; and
- `operational-action-judged-object`, subject to Clause 6.5.

The roles `dialect`, `common-definitions`, and `failure-taxonomy` are dependency roles and shall not be selected as instance roots.

Requirement identifier: `JR-ROLE-001`.

### 10.2 BELGI media-type allocations

This companion allocates the following BELGI vendor-tree media types:

| Representation | Media type |
|---|---|
| claim record JSON | `application/vnd.belgi.claim-record+json` |
| judged-object carrier JSON | `application/vnd.belgi.judged-object-carrier+json` |
| evidence-state carrier JSON | `application/vnd.belgi.evidence-state-carrier+json` |
| evaluator carrier JSON | `application/vnd.belgi.evaluator-carrier+json` |
| package-integrity manifest JSON | `application/vnd.belgi.package-integrity-manifest+json` |
| package-integrity anchor JSON | `application/vnd.belgi.package-integrity-anchor+json` |
| operational-action judged-object carrier JSON | `application/vnd.belgi.operational-action-judged-object-carrier+json` |
| replay-package ZIP projection | `application/vnd.belgi.replay-package+zip` |

These are BELGI allocations using RFC 6838 vendor-tree syntax and applicable structured-suffix syntax. This document does not claim that they are registered by IANA. No media type is allocated for the directory projection.

Requirement identifier: `JR-MEDIA-001`.

### 10.3 No semantic selection by media type

A media type identifies representation format only. It shall not select or authorize a trusted schema role, package-member role, profile, companion, replay procedure, package-representation procedure, canonicalization procedure, digest algorithm, signature algorithm, or package-integrity verification method. Such selection shall remain independently trusted and shall use the applicable exact stable identifier and defining-source-byte binding.

Requirement identifier: `JR-MEDIA-002`.

## 11 Structural validity and authority

### 11.1 Exact schema graph

Every selected root schema shall use the exact named dialect bound by the inventory. Every non-meta-schema reference shall resolve inside the exact inventory. A missing, extra, renamed, digest-drifted, identifier-drifted, dependency-drifted, or unresolved required schema resource shall reject.

Requirement identifier: `JR-SCHEMA-001`.

### 11.2 Validation behavior

Exact JSON types apply. A validator shall not coerce strings, numbers, booleans, or null values. Missing, unknown, wrong-type, and null values shall obey the selected exact schema.

BELGI-owned envelope objects are closed where the selected schema uses `additionalProperties: false`. Profile-owned JSON value maps remain structurally opaque where governing semantic text does not define their value domain.

A string value constrained by a normative schema `enum` or `const` and exposed
as implementation-facing vocabulary is an exact-edition-local compact
identifier token. Its namespace identity is the ordered pair of the companion
identifier in 6.1 and the exact schema resource identity plus JSON Pointer that
locates the governing `enum` or `const`. Tokens in one such namespace shall be
compared after JSON string decoding as exact sequences of Unicode scalar values,
without case folding, Unicode normalization, whitespace trimming, prefix
expansion, or other normalization. No two meanings may share one token in the
same namespace. Once assigned, a token shall not be reassigned a different
meaning at that schema identity and pointer by a later edition of this companion
family, and retirement or removal shall not make it available for reassignment.

JSON object member names, JSON Schema keywords, schema identifiers, references,
JSON Pointers, inventory role labels, requirement identifiers, and corpus-local
controls are structural metadata rather than implementation-facing vocabulary
unless an owning normative clause explicitly declares otherwise.

When an `enum` or `const` constrains a globally registered identifier or a
compact token whose meaning is already owned by another exact BELGI dependency,
that defining artifact and its namespace remain authoritative. The schema
identity and JSON Pointer bind only the representation constraint and do not
allocate, alias, or reassign the imported value. The schema-local namespace rule
above applies only where this companion and exact schema first define the
implementation-facing representation vocabulary.

The exact dialect requires the Draft 2020-12 format-assertion vocabulary. A format used by the bound schema graph is therefore an assertion rather than an annotation.

Requirement identifier: `JR-SCOPE-001`.

### 11.3 Package-integrity anchor field binding

For trusted role `package-integrity-anchor`, the JSON object fields `verificationMethodIdentifier` and `verificationMethodDesignator` carry respectively the stable verification-method identifier and the immutable designator of its exact defining source. The fields `signatureAlgorithmIdentifier` and `signatureAlgorithmDesignator` carry respectively the stable signature-algorithm identifier and the immutable designator of its exact defining source. The fields `verificationKeyText`, `verificationKeyDesignator`, and `signatureBase64` carry the exact key text, its exact binding, and the canonical signature text governed by the Package integrity anchor verification companion.

The stable identifier and exact-source designator in each pair shall be validated independently. A stable-identifier URI paired with a digest of different source bytes shall reject. The schema shall enforce the fixed stable identifiers and lexical grammars; the decoded-length, exact re-encoding, cryptographic, and no-fallback requirements remain conjunctive prose requirements.

Requirement identifier: `JR-PIA-001`. The mapped method requirements remain `PIA-METHOD-001`, `PIA-SOURCE-001`, `PIA-KEY-001`, `PIA-BASE64-001`, `PIA-ED25519-001`, and `PIA-FAIL-001` in the Package integrity anchor verification companion.

For trusted role `package-integrity-manifest`, each binding object carries
`algorithmIdentifier` and `algorithmDesignator` as the stable digest-algorithm
identifier and the immutable designator of its exact defining source. A
canonical-projection binding additionally carries
`canonicalizationRuleIdentifier` and `canonicalizationRuleDesignator`. An
exact-preserved-octets binding carries neither canonicalization field.

For trusted role `claim-record`, a replay-relevant member-inventory entry that
designates a narrower projection carries `projectionRuleIdentifier` and
`projectionRuleDesignator`. The two projection fields are either both present
or both absent. Claim-record-integrity-recovery entries, auxiliary entries, and
required carrier-root entries carry neither projection field.

Each `*Identifier` field governed by this paragraph is a non-empty absolute-URI
string and is compared exactly after JSON decoding. Each identifier and its
paired designator shall be validated independently under Part 2, 10.4. The
schema enforces pair presence and structural type; it cannot establish that
the exact designated source assigns the selected identifier the selected
meaning. No field, schema default, or designator digest-algorithm token supplies
a missing half of a pair.

Requirement identifier: `JR-RULE-BINDING-001`. The mapped replay requirement
is `P2-RULE-BINDING-001` in Part 2.

For trusted roles `claim-record` and `package-integrity-anchor`, the fields
`packageIdentifier` and `packageIntegrityManifestMember` carry the two
consistency bindings governed by Part 2, 10.2. The fixed representation member
consumed as the manifest has logical member name `package-integrity-manifest`.
The schema requires and validates each field within one document but does not
perform cross-document equality. Equality is applied only after claim-record
integrity recovery, and neither field selects a trusted role or physical
member.

Requirement identifier: `JR-PIA-TARGET-001`. The mapped requirements are
`P2-ANCHOR-TARGET-001` in Part 2 and `PIA-TARGET-001` in the Package Integrity
Anchor Verification companion.

For trusted role `replay-report`, `packageIdentifier` is a required property
whose JSON value represents the language-neutral report value governed by Part
2, 13.1. It shall be the exact non-empty JSON string yielded by the complete
atomic Step 1 bounded bootstrap view, or JSON `null` when Step 1 failed before
that view and value both existed. Partial parsing, a physical-container value,
an adapter or source hint, an implementation sentinel, an anchor value, or a
caller default shall not supply the property.

A `replayable` report shall contain a string `packageIdentifier`. A null
`packageIdentifier` shall occur only in a `non-replayable` report. A
non-replayable report can still contain the exact string when Step 1 succeeded
and a later replay step failed. The schema shall enforce the required property,
the string-or-null representation domain, and the status implications. Part 2
remains authoritative for whether Step 1 completed and which exact string it
yielded. The shared `packageIdentifier` definition in `Common.schema.json`
remains a non-empty string and shall not be widened; only the replay-report
property admits null. JSON string length, not a trimmed or normalized view,
determines whether the candidate satisfies that non-empty constraint.

Requirement identifier: `JR-REPORT-IDENTITY-001`. The mapped replay
requirement is `P2-REPORT-IDENTITY-001` in Part 2.

### 11.4 Conjunctive authority

For trusted role `r` and candidate bytes `b`:

```text
Valid(r, b) = RepresentationProse(b) AND Schema(r, Parse(b))
```

Neither representation prose nor schema silently overrides the other. If either rejects, the representation is invalid. If the two sources contradict, this exact draft is internally inconsistent for that input and an implementation shall fail closed rather than select a preferred authority.

### 11.5 Bounded validation order

For one already selected and digest-verified schema plus candidate bytes, validation shall proceed in this order:

1. UTF-8 and byte-order-mark validation;
2. complete JSON syntax validation;
3. duplicate-name, Unicode-domain, and number-domain validation;
4. exact schema validation; and
5. optional canonical-byte production only after Steps 1 to 4 succeed.

This clause fixes required rejection and stage ordering. It does not define one primary diagnostic among simultaneous defects or package-wide recovery behavior.

Requirement identifier: `JR-PRECEDENCE-001`.

## 12 JSON value conformance corpus

The JSON value conformance corpus selected by this companion edition is the
exact UTF-8 byte sequence of `conformance/JSONRepresentation.v2.json`, with
corpus role `json-representation`, bound by this companion edition's schema
inventory. It binds the exact `spec-0.4` `JSONRepresentation.v1.json`
predecessor and preserves every predecessor case. It shall contain only cases whose
trusted roles and schema dependencies are bound by that inventory, and shall
contain no Operational-Action or other Part 5 case.

The successor corpus adds replay-report schema vectors for a non-replayable
report with unavailable JSON null, rejection of null in a replayable report,
acceptance of the exact string in a replayable report, and acceptance of the
exact string in a non-replayable report whose Step 1 succeeded before a later
failure. These cases exercise `JR-REPORT-IDENTITY-001`; they do not relabel or
modify the predecessor replay-report case.

The experimental Operational-Action corpus is the exact UTF-8 byte sequence of
`operational-action/JSONRepresentation.v1.json` bound by the Operational-Action
overlay inventory. It shall declare semantic applicability
`part-5-working-draft` and shall contain exactly one case:
`schema.valid.operational-action`, using operation `schema-validate` and
trusted role `operational-action-judged-object`. It shall not add a case or
trusted role to this companion edition's selected corpus. The case-shape,
operation, stage, and result requirements in the remainder of this clause apply
to both corpora; an unqualified reference to the conformance corpus means the
corpus selected by this companion edition.

Each exact corpus contains candidate input bytes as lowercase hexadecimal text, expected acceptance or rejection, the applicable validation stage, and stable local requirement identifiers.

Every case contains:

- `caseId`, a unique stable case identifier;
- `operation`, selecting one of the operations defined below;
- `inputHex`, the complete candidate input bytes encoded as an even-length sequence of lowercase hexadecimal octets;
- `expected`, containing the Boolean `accepted` result, the validation `stage`, and a corpus-local `resultCode`; and
- `requirementIds`, a non-empty set of requirement identifiers from this document.

The three operations have the following exact meanings:

- `representation-validate` evaluates only the representation-domain requirements in Clauses 7 and 8. It has no `trustedRole`, performs no schema validation, and produces no canonical bytes.
- `schema-validate` requires `trustedRole` and evaluates full representation validity through Clause 11, including the selected exact schema graph. It does not produce canonical bytes.
- `canonicalize` requires `trustedRole`, first establishes full representation validity through Clause 11, and then applies Clause 9. An accepted case contains `canonicalHex`, the complete canonical output bytes encoded as lowercase hexadecimal octets. A rejected case contains no `canonicalHex` because no canonical output is produced before full validity is established.

`unavailableDependencies`, when present on a `schema-validate` case, names exact inventory dependencies intentionally unavailable to that case's schema-resolution environment. It does not remove those dependencies from the normative inventory.

The exact `stage` values are `utf8`, `json-syntax`, `json-domain`, `schema`, and `complete`. They correspond respectively to Steps 1, 2, 3, 4, and successful completion of all applicable steps in 11.5. A `representation-validate` case may use only `utf8`, `json-syntax`, `json-domain`, or `complete`; it shall not use `schema`. A `schema-validate` or `canonicalize` case may use any of the five stage values. A case has stage `complete` if and only if it is accepted. Every accepted `canonicalize` case contains `expected.canonicalHex`; no other case contains that member. `resultCode` is a stable corpus-local reason label for relating a case to its expected outcome. It is not a required implementation diagnostic, error type, output vocabulary, or rule for choosing one primary diagnostic when multiple defects are present.

The corpus `caseId`, `operation`, `stage`, and `resultCode` values are
conformance-fixture controls rather than normative implementation-facing
compact identifier vocabularies. Their use does not create a second result,
problem, or diagnostic namespace.

The corpus is example material linked to the requirements in this document. A consumer shall not infer a new requirement from a vector when the normative text is silent. A vector shall not override this document or the exact schemas.

The existence of either corpus is not evidence that an implementation executes it, agrees with it, or conforms to this draft. Execution of the experimental Operational-Action corpus does not establish adoption of this companion or Part 5.

## 13 Replay-package representation boundary

### 13.1 Relationship to Parts 2 and 3

BELGI - Part 2 remains authoritative for logical replay-package membership, inventory, closure, integrity, replay steps, replay outcomes, and replay problem types. This companion serves the representation-specific extension point in BELGI - Part 3, 8.11, by defining a portable physical representation and its decoding into one logical member map.

The package-representation procedure yields either one logical member map or one representation rejection. A representation rejection is not a replay report, replay problem, replay outcome, semantic tuple, verdict, or organizational authorization. This companion does not add a more-specific replay problem type under BELGI - Part 3, 8.10.

### 13.2 Implementation-owner separation

A producer projects logical members into one selected physical representation. A verifier validates and decodes that representation before integrating the resulting logical member map with the replay procedure in BELGI - Part 2, Clause 12. This document defines neither producer orchestration nor a runtime extraction interface.

### 13.3 Trusted projection selection

The caller shall select exactly one of the following package-representation procedures independently before interpreting candidate bytes or entries:

```text
https://belgi.dev/ids/procedure/replay-package/directory-v1
https://belgi.dev/ids/procedure/replay-package/zip-v1
```

The procedure identifiers are opaque and shall be compared as exact strings. Their immutable designators shall bind the exact defining source bytes of this companion edition. The corpus labels `directory` and `zip` are operation-local labels, not substitutes for those identifiers.

A filename, suffix, magic value, embedded media type, mutable response header, package field, registry result, or fallback shall not select or change the procedure. In particular, `application/vnd.belgi.replay-package+zip` describes an already selected ZIP representation and does not authorize the ZIP procedure.

Requirement identifier: `JR-PROCEDURE-001`.

## 14 Portable logical member paths and physical mapping

### 14.1 Portable logical member path domain

A portable logical member path shall be ASCII text containing from one to 32 `/`-separated segments, with no leading or trailing `/`. Each segment shall contain from one to 255 octets, shall begin and end with an ASCII lowercase letter or decimal digit, and shall contain internally only ASCII lowercase letters, decimal digits, `.`, `_`, and `-`.

A segment shall not be `.` or `..`. A path shall not contain an empty segment. A segment basename, taken before its first `.`, shall not equal `con`, `prn`, `aux`, `nul`, `com1` through `com9`, or `lpt1` through `lpt9`.

NOTE The basename rule reserves names that operating systems may interpret as device names even when a suffix is present. Taking the basename before the first `.` makes the rule independent of a particular host and prevents values such as `con.txt` from entering the portable domain.

The complete path shall contain no more than 1024 octets. Uppercase, non-ASCII, backslash, colon, control characters, NUL, a leading or trailing dot, and a leading or trailing space therefore reject. Validation shall not perform Unicode normalization, case folding, locale-sensitive comparison, or host-path interpretation.

Requirement identifier: `JR-PATH-001`.

### 14.2 Fixed member identities and physical projection

The following bindings are fixed:

| Logical member | Required role | Required classification | Trusted JSON role | Physical member path |
|---|---|---|---|---|
| `claim-record` | `claim-record` | `replay-relevant` | `claim-record` | `claim-record.json` |
| `package-integrity-manifest` | `package-integrity-manifest` | `claim-record-integrity-recovery` | `package-integrity-manifest` | `package-integrity-manifest` |
| `package-integrity-anchor` | `package-integrity-anchor` | `claim-record-integrity-recovery` | `package-integrity-anchor` | `package-integrity-anchor` |
| `judged-object-carrier-root` | `judged-object-carrier-root` | `replay-relevant` | `judged-object` | `judged-object-carrier-root` |
| `evidence-state-carrier-root` | `evidence-state-carrier-root` | `replay-relevant` | `evidence-state` | `evidence-state-carrier-root` |
| `evaluator-carrier-root` | `evaluator-carrier-root` | `replay-relevant` | `evaluator` | `evaluator-carrier-root` |

The physical member path for logical member `claim-record` shall be exactly `claim-record.json`. Every other physical member path shall equal its logical member path. The logical path `claim-record.json` is reserved and shall reject. This mapping is injective. It shall not be inferred from filename extensions, media types, archive metadata, package-provided schema declarations, or any other candidate-controlled field.

Requirement identifiers: `JR-PROJECTION-001` and `JR-ROLE-002`.

## 15 Directory projection

The stable identifier of the directory projection procedure is `https://belgi.dev/ids/procedure/replay-package/directory-v1`.

A directory projection shall be read without following aliases and shall satisfy all of the following requirements:

- the root and every necessary ancestor are real directories;
- every member leaf is a regular file with link count one;
- symbolic links, reparse points, hardlinks, FIFOs, sockets, devices, and every other special node reject;
- no empty or unneeded directory, unlisted file, or other entry is admitted;
- the complete entry set is enumerated under the resource envelope before semantic interpretation;
- each leaf is opened relative to an already verified root without following links; and
- object identity, type, size, and relevant ancestry remain stable across enumeration and bounded reading.

A platform that cannot establish these invariants shall fail closed. Resolving a final string path or checking only that it appears to remain under a root is insufficient.

The selected root and its external ancestors are not directory entries for this
procedure. Every child entry observed directly below the selected root or
below a traversed real directory shall increment `directoryEntryCount` exactly
once, before any later name, type, collision, emptiness, or necessity decision.
This includes real directories, regular files, and entries that a later stage
rejects as aliases, links, special nodes, or unsupported types. Every observed
non-directory entry shall also increment `memberCount`, whether or not a later
stage admits it as a logical member.

After counting an observed real directory, the verifier shall not traverse its
descendants when that directory's relative path cannot be a proper prefix of
any physical member path admitted by Clause 14. Such pruning does not erase the
directory observation or its later Stage 4 defect. Every other traversable real
directory discovered before a Stage 3 terminal shall be enumerated completely
within the baseline resource envelope, even when another observed entry already
establishes a later-stage defect. Host enumeration order shall not change the
selected representation result.

Requirement identifiers: `JR-DIRECTORY-001` and
`JR-DIRECTORY-BOUND-001`.

The operation-local corpus success code `snapshot-established` is governed for directory cases by this clause together with Clause 17. It does not denote complete package or replay success.

## 16 ZIP projection

The stable identifier of the ZIP projection procedure is `https://belgi.dev/ids/procedure/replay-package/zip-v1`.

The ZIP projection is the following bounded subset of PKWARE APPNOTE 6.3.10:

- one single-disk archive with no prefix or trailing bytes;
- no records other than one local file header plus its file data per logical member, one matching central-directory file header per logical member, and one final end-of-central-directory record;
- zero in every disk-number and central-directory-entry disk-start field, equal on-disk and total entry counts, and relative local-header offsets, central-directory offset, central-directory size, and entry counts that describe the exact contiguous record layout;
- `version needed to extract` equal to `20` (`0x0014`, APPNOTE version 2.0) in both the local and matching central header, and a central `version made by` whose low byte is `20` (`0x14`) and whose creator-system high byte is `0` or `3`;
- compression method `0` (STORE) or `8` (DEFLATE);
- no encryption, data descriptor, ZIP64 record or sentinel, archive comment, entry comment, extra field, central-directory encryption or signature, or split disk;
- for STORE, a general-purpose bit-flag value of `0x0000` or `0x0800`; for DEFLATE, a general-purpose bit-flag value whose only possible set bits are bits 1, 2, and 11, so its mask is `0x0806`; bits 1 and 2 carry the APPNOTE DEFLATE compression-option indication and bit 11 is the UTF-8-name flag; every other bit shall be zero;
- a raw file-name field consisting only of ASCII octets, interpreted one-to-one as the physical member-path text in Clause 14; bit 11 does not widen this ASCII domain and no legacy code-page, Unicode normalization, or replacement decoding is performed;
- byte-identical local and central names and equal method, flags, CRC-32, compressed size, and uncompressed size fields;
- bounded streaming output according to Clause 18 that equals the declared uncompressed size and CRC-32 and ends exactly at the compressed-data boundary, or Stage 5 rejects with `member-stream-mismatch`; for DEFLATE, the declared compressed-data interval shall contain exactly one raw RFC 1951 compressed data set, so a concatenated second data set or any unused trailing compressed octet rejects;
- central-directory external attributes that establish a regular file under this BELGI subset: for creator system `3`, this companion defines the upper-16-bit file-type mask `0xF000` to be regular only when it equals `0x8000`; for creator system `0`, both volume-label bit `0x08` and directory bit `0x10` shall be clear; creator system `3` shall also have those two low DOS attribute bits clear; an explicit directory entry, symbolic-link, directory attribute, device, unknown creator system, or other special or unestablished type rejects at Stage 4, subject to Clause 20 priority; an explicit directory name ending in `/` therefore selects `invalid-entry-name`, while an otherwise valid path carrying a directory or unestablished type selects `unsupported-entry-type`; and
- direct projection of member bytes into the logical member map without extraction into a host path.

Archive entry order and timestamp fields do not affect the logical projection.

Requirement identifier: `JR-ZIP-001`.

The operation-local corpus success code `snapshot-established` is governed for ZIP cases by this clause together with Clause 17. It does not denote complete package or replay success.

## 17 Complete-entry-set rules

The complete enumerated entry set shall contain neither exact duplicate physical paths nor a file/directory prefix pair such as `a` and `a/b`. No empty or unneeded directory, unlisted file, or other entry is admitted. These checks shall not depend on directory or archive enumeration order.

Because Clause 14 admits only lowercase ASCII paths, case variants and Unicode-equivalent variants reject as invalid paths instead of being resolved through a host-dependent collision rule.

Requirement identifiers: `JR-ENTRY-001` and `JR-COLLISION-001`.

## 18 Baseline resource envelope and ZIP Stage 5 processing

### 18.1 Baseline limits

The baseline resource limits are inclusive maxima:

| Resource | Maximum |
|---|---:|
| outer ZIP bytes | 536870912 |
| directory-projection entries below the selected root (`directoryEntryCount`) | 131072 |
| non-directory candidate entries (`memberCount`) | 4096 |
| one logical member's uncompressed octets | 67108864 |
| `claim-record` octets | 8388608 |
| total uncompressed logical-member octets | 268435456 |
| logical path segments | 32 |
| one path segment octets | 255 |
| complete logical path octets | 1024 |
| JSON array/object nesting depth | 128 |

Limits shall be enforced incrementally before unbounded allocation, decompression, recursion, or extraction. A value equal to a maximum is admitted; a value above it rejects. A conforming implementation of this baseline shall not silently impose a lower limit. A future separately identified profile may define another envelope without changing this baseline.

`directoryEntryCount` applies only to the directory projection. It excludes the
selected root and every ancestor outside that root and counts each observed
entry governed by Clause 15. The maximum is `4096 × 32`: it admits the largest
tree shape in which every one of the 4096 non-directory candidate entries has
a disjoint 32-segment physical path. Shared ancestor directories reduce the
count; they do not reduce the baseline maximum.

`memberCount` applies to both directory and ZIP projections and counts every
non-directory candidate entry before later name, type, duplication, collision,
or admission checks. In a directory projection, one non-directory observation
therefore increments both counters. Exceeding either counter shall terminate at
Stage 3 with `entry-count-exceeded` on the first observation that makes its
inclusive maximum false. Stage 4 defects already observed do not permit early
termination or incomplete traversal of otherwise traversable directories.

For the JSON nesting-depth limit, a root array or object has depth 1. Entering each directly nested array or object increases depth by 1. A scalar has depth 0 and does not increase the depth of its containing array or object. Object member names do not contribute to depth. The corpus resource identity `claimRecordJsonNestingDepth` applies this boundary to the claim record at representation Stage 6. The same numeric limit is applied to every later JSON member before its Part 2 parse or lift; a later-member excess is reported through the governing Part 2 problem and priority rather than a new companion-owned replay problem type.

Requirement identifier: `JR-RESOURCE-001`.

Clause 18.1 supplies common limits to both package-representation procedures
selected under 13.3; a resource that exists only in one procedure, such as
outer ZIP bytes, applies only to that procedure. Clauses 18.2 through 18.5
apply only when the caller has independently selected
`https://belgi.dev/ids/procedure/replay-package/zip-v1`. The directory procedure
remains governed by Clauses 15 and 17 together with the applicable common
limits in 18.1; it does not acquire ZIP header, STORE, DEFLATE, CRC-32, or
compressed-boundary semantics from the following subclauses.

### 18.2 Header-decidable preflight

After Stages 1 to 4 establish one complete valid entry set, the verifier shall
examine every entry's declared uncompressed size before decompressing member
data. If one or more declarations exceed the per-member maximum, processing
shall terminate with `member-size-exceeded`.

Otherwise, the verifier shall initialize aggregate `s` to zero and preserve
the invariant `0 <= s <= T`, where `T` is the aggregate maximum. For each next
declared size `d`, it shall reject with `total-size-exceeded` if
`d > T - s`; otherwise it shall set `s` to `s + d`. The verifier shall not
first form an arithmetic sum that can overflow. This
preflight covers the complete entry set because Stage 3 has already enforced
the entry-count limit. Clause 20 ordering applies to every defect established
during the preflight.

### 18.3 Canonical streaming order and counters

If the preflight succeeds, members shall be processed in ascending
lexicographic order of their validated raw ASCII physical-path octets. At the
first unequal position, the smaller unsigned octet sorts first; if one path is
an exact prefix of the other, the shorter path sorts first. Local-header order,
central-directory order, timestamps, host enumeration, logical-map insertion
order, and library iteration order shall not select the next member.

The verifier shall maintain exact non-negative counters for the current
member's produced octets and the aggregate produced octets. Before admitting
each next output octet, the verifier shall apply the following ordered steps:

1. if both counters equal their respective maxima, terminate with
   `member-size-exceeded`;
2. otherwise, if the member counter equals its maximum, terminate with
   `member-size-exceeded`;
3. otherwise, if the aggregate counter equals its maximum, terminate with
   `total-size-exceeded`; and
4. otherwise, admit the octet and increment both counters.

An equal member and aggregate threshold therefore selects
`member-size-exceeded`. Reaching a maximum by admitting an octet does not by
itself reject; rejection occurs only if another output octet is attempted.
Completion at exactly a maximum proceeds to the completed-stream checks in
18.4. An earlier aggregate threshold is terminal even if processing the
remainder of the current stream or a later stream could reveal a member
excess. After a terminal resource rejection, the verifier shall not continue
the current member or begin a later member.

STORE and DEFLATE shall use the same actual-output counters and threshold
rule. Method-specific knowledge of a STORE member's byte count shall not add a
header preflight beyond the declared-size preflight in 18.2 or select a
different primary result from an equivalent DEFLATE output trace.

### 18.4 Stream completion and exact boundary

A DEFLATE member shall contain exactly one raw RFC 1951 compressed data set in
the compressed-data byte interval declared by the matching ZIP headers. A
second concatenated data set, an unused trailing octet, a truncated or invalid
stream, failure to reach the final block within that interval, disagreement
between declared and actual uncompressed size, or CRC-32 disagreement shall
establish `member-stream-mismatch`.

Output may continue after the produced count first disagrees with the declared
uncompressed size only while it remains within the absolute member and
aggregate limits. If the stream attempts to produce a next octet while an
applicable counter already equals its maximum, the resource rejection shall be
terminal and shall outrank the pending size disagreement. If the stream
completes within both absolute limits, a declared-size, CRC-32, or
compressed-boundary disagreement shall terminate with
`member-stream-mismatch` before a later member is visited.

The procedure defines no compression-ratio result code or normative timeout.
The outer ZIP limit bounds compressed input, and the member and aggregate
limits bound produced output.

### 18.5 Terminality and priority scope

Clause 20 selects among defects established before this algorithm reaches its
defined terminal condition. It does not require exploration of unprocessed
compressed bytes or later members to discover latent defects. The complete
header-decidable preflight in 18.2 is performed before streaming and is not
shortened by archive enumeration order.

Requirement identifier: `JR-STAGE5-001`.

The operation-local corpus success code `within-limit` is governed by this clause for a value at or below its applicable maximum. It does not denote acceptance of a complete package.

## 19 Recovery and authority order

The package-representation procedure and the replay procedure in BELGI - Part 2, Clause 12, shall interleave in this order:

1. accept the independently trusted projection kind;
2. enforce the outer-byte limit;
3. boundedly enumerate and validate container framing and the entry count;
4. validate every raw or decoded name, node type, duplicate, and prefix collision without following or extracting entries;
5. establish one stable, bounded physical-path-to-exact-octet snapshot;
6. recover fixed physical member `claim-record.json` and obtain only the representation-domain bootstrap view needed to perform BELGI - Part 2, 12.2, step 1; Stage 6 shall not perform complete claim-record schema validation;
7. perform BELGI - Part 2, 12.2, steps 2 and 3 using the fixed package-integrity-manifest and package-integrity-anchor trusted roles; package fields shall not authorize their own bootstrap verifier;
8. perform BELGI - Part 2, 12.2, step 4 by completely validating the authenticated exact claim-record octets in accordance with Clause 11, using the independently fixed `claim-record` trusted role and its exact digest-bound schema graph;
9. only after step 4 succeeds, require a bijection between the authenticated member inventory and the physical map, and require all six bindings in 14.2;
10. continue BELGI - Part 2, 12.2, steps 5 to 14, applying the per-member, total, and JSON-depth limits before parsing or lifting each member; and
11. retain BELGI - Part 2, 13.7, failure priority wherever a Part 2 replay problem exists.

The bootstrap parser, claim-record digest verification, and complete step-4
validation shall observe the same immutable exact claim-record octets from the
Stage 5 snapshot. Stage 6 may perform the UTF-8 and byte-order-mark, complete
syntax, duplicate-name, Unicode-domain, and number-domain checks needed for a
deterministic view, recognize the top-level object, and extract only the
package-member, canonical-reference, manifest, anchor, integrity-binding, and
cross-binding material required by Part 2, steps 1 to 3. It shall not enforce
complete required-field coverage, unknown-property closure, required-root
completeness or uniqueness, dependency closure, profile or referenced-source
meaning, or any package-controlled schema authority. It shall not produce
semantic objects or authorize lifting.

The `invalid-claim-record-representation` result is available at Stage 6 only
for a representation-domain defect that prevents obtaining that bounded
bootstrap view. Complete-schema rejection after authentication is the Part 2,
step-4 problem `malformed-claim-record` with outcome class
`malformed-carrier`; it shall not be replaced by a representation result. A
physical path, filename, logical member name or package-supplied role, media
type, instance `$schema`, mutable registry lookup, package field or schema
designator, implementation default, guessed role, alias, or fallback shall not
select or replace the `claim-record` trusted role or exact schema graph.
External selection and source-digest verification of that graph may precede
claim-record authentication because their authority is independent; applying
the complete graph to the claim-record octets occurs only at Part 2, step 4.

Requirement identifier: `JR-RECOVERY-001`.

## 20 Representation result and deterministic priority

The representation procedure yields either one logical member map with Stage 8 result `complete` or one representation rejection. For simultaneous representation defects, the primary representation rejection shall be the earliest stage in the following table and then the first listed rejection code within that stage:

| Stage | Ordered draft-local result codes |
|---:|---|
| 1 | `outer-size-exceeded` |
| 2 | `malformed-container`, `unsupported-container-feature` |
| 3 | `entry-count-exceeded` |
| 4 | `invalid-entry-name`, `unsupported-entry-type`, `duplicate-entry`, `path-prefix-collision` |
| 5 | `member-size-exceeded`, `total-size-exceeded`, `member-stream-mismatch`, `package-mutated-during-read` |
| 6 | `missing-claim-record`, `claim-record-size-exceeded`, `invalid-claim-record-representation` |
| 7 | `physical-inventory-mismatch`, `fixed-role-binding-mismatch` |
| 8 | `complete` |

The result codes in this table form the named exact-edition-local compact
identifier vocabulary whose namespace identity is
(`https://belgi.dev/ids/companion/json-representation`,
`representation-result-code`). Within that namespace, a code shall be compared
as one exact string without case folding, Unicode normalization, whitespace
trimming, prefix expansion, or other normalization. No two meanings may share
one code. No later edition of this companion family shall reassign a code a
different meaning, and retirement or removal shall not make it available for
reassignment.

If the same code applies to more than one entry, the primary code remains determined; an optional diagnostic path does not affect conformance. Additional diagnostics may be retained but shall not change the primary stage or code. A Part 2 replay problem, when available, remains ordered by BELGI - Part 2, 13.7, and shall not be replaced by this table.

In particular, `invalid-claim-record-representation` does not denote complete
schema rejection of an authenticated claim record. Such a rejection is the
Part 2, 12.2, step-4 `malformed-claim-record` problem.

The table orders only defects established before the applicable terminal
condition. It does not require a verifier to continue a rejected stream or
visit a later member to search for a hypothetical higher-ranked defect. For
the ZIP procedure, the complete header-decidable Stage 5 preflight in 18.2
nevertheless examines the full validated entry set before streaming begins.

`member-stream-mismatch` means that STORE or bounded DEFLATE processing fails, produces an actual octet count different from the declared uncompressed size, produces a CRC-32 different from the declared value, or does not end exactly at the declared compressed-data boundary. A local-to-central field disagreement, an impossible record layout, or another defect knowable from headers and framing remains Stage 2 `malformed-container`.

Requirement identifiers: `JR-PROBLEM-001` and `JR-PRIORITY-001`.

## 21 Relocation equivalence

Two successful projections are equivalent if and only if they yield the same complete logical member map. Moving a directory root, changing ZIP entry order or ignored timestamp metadata, or converting between admitted directory and ZIP projections shall not change package identifiers, canonical references, integrity input octets, the recovered semantic tuple, the derived verdict, replay status, replay outcome, or ordered Part 2 problem identifiers. Host paths and container metadata shall not enter normative replay material.

Requirement identifier: `JR-RELOCATION-001`.

## 22 Replay-package representation corpus

The replay-package representation corpus for the `spec-0.5` Working Draft
family is the exact UTF-8 byte sequence of
`conformance/ReplayPackageRepresentation.v3.json`, with corpus role
`replay-package-representation`. It binds the exact `spec-0.4` predecessor
corpus and preserves every predecessor case, resource-limit row, priority row,
and equivalence-family object. It is selected only through the exact schema
inventory for this companion edition. That selection does not replace the
predecessor binding of a preserved claim and does not establish implementation
adoption.

The corpus contains isolated path and boundary vectors, abstract
directory-entry descriptors, exact ZIP archive octets, authenticated-inventory
binding vectors, priority families, relocation-equivalence families, and
allocation-free Stage 5 processing traces.

The `directoryEntryCount` resource has exact scalar cases immediately below,
at, and above its inclusive baseline maximum. A corresponding priority family
selects Stage 3 `entry-count-exceeded` ahead of Stage 4
`invalid-entry-name`. The corpus uses allocation-free scalar and priority
controls for this large boundary. Implementation adoption shall additionally
exercise actual hierarchical traversal, selected-root and ancestor exclusion,
invalid-prefix pruning, completion of otherwise traversable directories, and
enumeration-order independence; a flat corpus directory descriptor cannot
substitute for those implementation-owned observations.

Every case contains a unique `caseId`, one `family`, one operation-specific input, an exact expected result, and a non-empty `requirementIds` array referring to requirements in this document. Exact ZIP bytes are lowercase hexadecimal in `archiveHex`. Abstract directory descriptors are used for node kinds and mutation states that cannot be portably embedded in a JSON artifact. Resource-limit vectors state exact observed scalar values and do not require an implementation to allocate the represented resource during corpus-shape validation.

When present, `expected.logicalMap` is a JSON array ordered by ascending `logicalPath`. Each array item is a closed object containing exactly `logicalPath`, the portable logical member path, and `octetsHex`, the member's exact preserved octets encoded as even-length lowercase hexadecimal text. The array representation is the exact corpus encoding of the logical member map; JSON object member order within each item is not semantically significant.

The corpus operations isolate independently verifiable portions of the procedure:

- `portable-path-validate` evaluates 14.1;
- `logical-to-physical-map` evaluates 14.2;
- `directory-project` evaluates Clauses 15 and 17 through establishment of a stable physical snapshot;
- `zip-project` evaluates Clauses 16 and 17 through establishment of a stable physical snapshot;
- `resource-limit-check` evaluates one boundary in Clause 18;
- `recovery-binding-check` evaluates the fixed post-integrity inventory and role bindings in Clause 19;
- `stage-5-trace` evaluates the ZIP Stage 5 header preflight, canonical member
  order, actual-output counters, terminality, and completed-stream checks in
  Clause 18 from exact scalar observations without allocating the represented
  output;
  its input contains `memberMaximum`, `totalMaximum`, and an `entries` array in
  candidate enumeration order; each entry contains exactly `physicalPath`,
  `method`, `declaredUncompressedOctets`, `producedOctets`, `streamComplete`,
  `crcMatches`, and `compressedBoundaryExact`; and
- `priority-select` evaluates Clause 20 over an explicit set of detected representation defects.

For `stage-5-trace`, `memberMaximum` shall equal the inclusive baseline member
maximum `67108864`, and `totalMaximum` shall equal the inclusive baseline
aggregate maximum `268435456`. `entries` shall describe the complete entry set
of the selected ZIP projection already admitted through Stage 4, in candidate
enumeration order. Every entry shall have one unique physical path admitted by
Clause 14; array order shall not select processing order.

For each trace entry, `method` shall be exactly `STORE` or `DEFLATE`.
`declaredUncompressedOctets` is the non-negative uncompressed-size value in the
validated local and central headers. `producedOctets` is the non-negative count
of output octets that method processing would attempt before completion or
failure if no absolute resource terminal occurred; the scalar does not require
allocating those octets. `streamComplete` is true exactly when method
processing reaches its defined completion. `crcMatches` states whether CRC-32
over the complete produced output equals the validated declared CRC-32.
`compressedBoundaryExact` states whether the declared compressed-data interval
ends at the exact method boundary, including the single-data-set rule for
DEFLATE.

The completed-stream size, CRC-32, and boundary fields shall be consulted only
after all attempted output is admitted within the absolute limits. If a
resource terminal occurs first, fields describing later completion are not
consulted. If `streamComplete` is false, `crcMatches` and
`compressedBoundaryExact` shall both be false in the trace and are not
independent rejection selectors.

For `portable-path-validate` and `logical-to-physical-map`, an accepted isolated case has Stage 8 code `complete`. For `directory-project` and `zip-project`, an accepted isolated case has Stage 5 operation-local code `snapshot-established` and carries the exact projected `logicalMap`; that operation-local acceptance does not assert that package representation, Part 2 integrity recovery, or replay completed. For `resource-limit-check`, a value at or below the applicable maximum has operation-local code `within-limit` at the stage where Clause 20 places the corresponding over-limit rejection; it does not assert acceptance of a complete package. The `claimRecordJsonNestingDepth` vectors are claim-record-scoped and therefore use Stage 6 `invalid-claim-record-representation` above the maximum; they do not allocate a companion result for a later member. For `recovery-binding-check`, an accepted case has Stage 8 code `complete`. For `stage-5-trace`, an accepted isolated case has Stage 5 operation-local code `stage-5-complete`; it establishes only completion of the Stage 5 trace and does not assert execution or success of Stages 6 to 8. A `priority-select` case is rejected with the code selected from its explicit detected-defect set by Clause 20.

A `stage-5-trace` expected object additionally contains the complete canonical
`processingOrder`, the `visitedPaths` whose streams were begun before terminal
success or rejection, and `terminalCounters` containing exact
`memberOctets` and `totalOctets` values at that point. `processingOrder` shall
contain every physical path exactly once in the order defined by 18.3.
`visitedPaths` shall be the exact prefix of that order whose method processing
began, including the member in which a streaming terminal occurred. At a
header-preflight terminal it shall be empty. `memberOctets` shall equal the
octets admitted for the last visited member, or zero if none was visited;
`totalOctets` shall equal all output octets admitted before completion or the
terminal result. Both counters apply the inclusive maxima in Clause 18.

Every simultaneous-defect priority case names a corresponding isolated single-defect case for each asserted defect. Every relocation-equivalence family names successful projection cases with byte-identical expected logical maps. The three operation-local accepted codes are corpus controls rather than representation-procedure result codes and shall not be exposed as replay problems or outcomes.

Corpus operations and trace fields are conformance-fixture controls rather than
runtime APIs. Corpus result codes are draft-local conformance artifacts. They
do not define a Python or Go exception surface and do not evidence
implementation adoption. The corpus shall not override this document, the
schema inventory, the exact schemas, or Part 2 failure priority.

## 23 Conformance

The conformance classes defined by this companion are:

- BELGI JSON Representation-aware Producer;
- BELGI JSON Representation-aware Verifier; and
- BELGI Full JSON Representation Implementation.

A JSON Representation-aware Producer shall emit only representations admitted by the applicable requirements of Clauses 7 to 10 and, for replay packages, Clauses 13 to 21. A JSON Representation-aware Verifier shall apply the exact schema graph, procedures, authority order, limits, and deterministic rejection rules of those clauses without fallback or media-type self-selection. A Full JSON Representation Implementation shall conform as both producer and verifier.

A conformance statement shall identify the implementation, this document and
version, the class claimed, the exact companion and edition-selected
schema-inventory source bytes, every applicable edition-selected corpus, each
supported package-representation procedure, and the date of the statement.
Copying source or generated schema bytes without executing the applicable
procedures and corpora does not establish implementation adoption.

The Operational-Action overlay inventory and its corpus are not applicable
edition-selected material for a conformance statement under this clause.
Results from their evaluation may be reported separately only as
`part-5-working-draft` results; they shall not be used to satisfy a conformance
class, establish implementation adoption, or claim Part 5 promotion or
adoption.

## Annex A (informative) Security considerations

Duplicate-name acceptance can let different consumers evaluate different values from the same bytes. Silent number rounding can change identifiers, counters, or policy parameters. Schema self-selection can let untrusted content choose a weaker validator. Mutable or unresolved schema dependencies can change validation after a claim is preserved. Host-path interpretation, alias following, archive extraction, duplicate entries, prefix collisions, ZIP bombs, and mutation during reading can let ambient platform behavior or resource exhaustion alter the recovered package.

Clauses 7, 8, 10, 11, and 13 to 21 address these representation-level risks by requiring one strict input domain, caller-trusted role and projection selection, exact schema bytes, fail-closed conjunctive validation, portable names, bounded direct projection, stable snapshots, and deterministic rejection. They do not replace semantic evaluation, integrity verification, authorization policy, runtime isolation, or sole-capability enforcement.
