# BELGI - Part 2: Claim carriers and replay package

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is Part 2. It defines the carrier-side obligations needed to preserve, recover, and replay the semantic tuple fixed by Part 1. Later parts define profiles and companion specifications that can constrain carrier content or replay obligations without changing the semantic authority of Part 1.

This document is a member of the coherent `spec-0.5` Working Draft family.
The exact `spec-0.4` source edition remains immutable and is not replaced by
this source.

## Introduction

Part 1 fixes the semantic core of an admission claim and defines the abstract lifting functions from preserved carriers into the semantic tuple.

This document defines the preserved claim record, replay package, carrier minimum content, replay-relevant projection, package closure, integrity binding, lifting procedure shape, replay report, and replay problem taxonomy needed to operationalize that core.

This document does not redefine semantic tuple identity, evaluator identity, or claim identity. It defines the carrier-side conditions under which the preserved carriers of one admission claim can be replayed without undeclared ambient context.

This document specifies replay-package obligations for later recovery of one semantic tuple and one derived verdict from preserved material. It is not an attestation framework for issuing, transporting, or validating third-party claims about external build events, supply-chain steps, or artifact provenance, although such material may be preserved as auxiliary or replay-relevant package members when another BELGI normative text makes it replay-relevant.

This document states operational replay requirements and failure conditions. It does not by itself supply a general proof calculus for replay determinism or cross-implementation evaluator equivalence.

Carrier formats may vary only when replay-relevant meaning remains fixed by the preserved replay-relevant content recovered under this document. A replay package is conforming only when every replay-relevant dependency needed for replay is preserved, designated, integrity-bound, and recoverable from the package itself.

## 1 Scope

This document defines the claim carriers and replay package for BELGI admission claims.

This document defines:

- the preserved claim record and replay package model;
- the minimum content of judged-object, evidence-state, and evaluator carriers;
- replay-relevant projection and package closure;
- canonical references and integrity bindings;
- the parse, resolve, and induce stages of lifting;
- the replay procedure;
- replay reports, outcome classes, and replay problem taxonomy; and
- Part 2 conformance classes.

This document is applicable to preserved admission claims intended to support deterministic replay of the semantic tuple and derived verdict defined by Part 1.

This document does not define:

- the semantic core fixed by Part 1;
- an attestation framework for issuing, transporting, or validating third-party claims about external build events, supply-chain steps, or artifact provenance;
- machine-readable schema dialects or representation-specific bindings;
- domain-specific condition taxonomies, trust-boundary vocabularies, or governing-specification vocabularies;
- identifier-family, registry, compatibility, alias, or deprecation rules for profiles, companions, or domain-specific vocabularies;
- one universal outer transport, storage container, or archive syntax;
- one universal canonicalization algorithm or digest algorithm for all media types; or
- whether a recovered evaluator satisfies external correctness or organizational acceptance criteria.

## 2 Normative references

The following document is referred to in the text in such a way that some or all of its content constitutes requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the following terms and definitions apply.

### 3.1 package identifier

designator that identifies one replay package

### 3.2 package member

preserved byte sequence designated by the claim record as belonging to one replay package

### 3.3 replay package

preserved closure unit containing one claim record and all replay-relevant members needed to replay one admission claim

### 3.4 claim record

preserved root record that operationalizes the designation of constituent carriers for one admission claim and identifies the replay-relevant members and dependencies of the replay package

### 3.5 root designator

designation in the claim record identifying the package member that serves as the required carrier root for one semantic sort

### 3.6 replay-relevant member

package member whose preserved content can affect package closure, integrity verification, lifting, recovery of the semantic tuple, or derivation of the verdict

### 3.7 package closure

property by which every replay-relevant dependency needed for replay resolves to a replay-relevant member of the same replay package

### 3.8 dependency declaration

designation in the claim record that one package member depends on another package member for replay-relevant purposes

### 3.9 auxiliary member

package member preserved for explanation, provenance, convenience, or audit support but not required to establish replayability

### 3.10 replay-relevant projection

deterministic selection of the content of a package member that can affect package closure, integrity verification, lifting, recovery of the semantic tuple, or derivation of the verdict

### 3.11 canonical reference

stable package-internal identifier used by the claim record to designate one package member

### 3.12 canonical representation

deterministic representation of a replay-relevant projection used for integrity verification or equality-preserving comparison

### 3.13 integrity binding

verifiable binding between a canonical reference and either the exact preserved octets of its package member or the canonical representation of its replay-relevant projection

### 3.14 parse stage

lifting stage that reads preserved replay-relevant material as preserved and determines whether that material is syntactically well-formed for the procedure being applied

### 3.15 resolve stage

lifting stage that determines the replay-relevant dependencies, referenced sources, or designated members needed by the procedure and binds them without undeclared ambient context

### 3.16 induce stage

lifting stage that determines exactly one semantic object from successfully parsed and resolved replay-relevant material

### 3.17 open replay package

replay package that does not satisfy package closure

### 3.18 replay outcome class

primary classification of the result of one replay attempt

### 3.19 replay problem

structured record describing one detected anomaly during package reading, integrity verification, dependency resolution, lifting, or replay

### 3.20 replay report

structured result of one replay attempt, including replay status, replay outcome class, and zero or more replay problems

### 3.21 package-integrity manifest

preserved claim-record-integrity-recovery package member carrying the integrity bindings by which the replay-relevant members of one replay package are verified

### 3.22 package-integrity anchor

preserved claim-record-integrity-recovery package member that authenticates one designated package-integrity manifest by detached signature over its exact preserved octets

### 3.23 claim-record-integrity-recovery member

package member preserved to recover claim-record integrity before claim-record contents are treated as authoritative, without becoming replay-relevant solely by that use

## 4 Symbols and abbreviated terms

### 4.1 Symbols

For the purposes of this document, the following symbols apply.

| Symbol | Meaning |
| --- | --- |
| $R_{pkg}$ | replay package |
| $C_{rec}$ | claim record |
| $m$ | package member |
| $proj(m)$ | replay-relevant projection of package member $m$ |
| $canon(m)$ | canonical representation of $proj(m)$, when defined |

### 4.2 Abbreviated terms

No abbreviated terms are listed in this document.

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 15 are normative unless stated otherwise.

References in this document to the same semantic tuple or the same verdict are references to the equality conventions fixed by Part 1, Clause 5.

The repeated-execution rule of 12.4 is a minimum operational replay requirement for one implementation. Cross-implementation verdict agreement is governed by 12.5 when a conforming profile declares verdict-level interoperability.

The claim record, replay package, canonical references, integrity bindings, and replay reports defined by this document are carrier-side mechanisms. They do not alter the semantic authority of Part 1.

## 6 Layering and carrier boundary

### 6.1 General

The family identifier of this part is:

`https://belgi.dev/ids/specification/part-2`

The current draft version designator is `0.5`. The family identifier and
version designator do not by themselves identify exact source bytes.
Replay-relevant use requires an immutable designator whose URI denotes one
exact source edition and whose digest binds the exact octets of that same
source edition.

Stable local requirement identifiers beginning with `P2-` label requirements
for traceability into machine-readable material. The `P2-` prefix is reserved
to this Part family, and a retired `P2-*` requirement identifier shall never be
reused. A requirement identifier is not a substitute for its requirement text.

This document distinguishes:

- the semantic core fixed by Part 1;
- the claim-carrier and replay-package layer fixed by this document; and
- the profile and companion layer reserved for later BELGI parts.

### 6.2 Semantic authority

Part 1 remains the semantic authority for judged objects, evidence states, evaluators, verdicts, replayability, and claim identity.

This document operationalizes preservation and replay without redefining those semantic categories.

### 6.3 Replay package as closure unit

The replay package is the preserved closure unit for replay.

Successful replay shall depend on the preserved replay package rather than on a cached verdict, display summary, or undeclared repository state.

### 6.4 Non-owning preserved material

Labels, display-oriented summaries, filenames, transport metadata, cached verdicts, undeclared signatures, attestations, and other explanatory or convenience material may be preserved as auxiliary members.

Auxiliary members shall not determine package closure, lifting, semantic tuple recovery, derived verdict, or claim identity unless another BELGI normative text explicitly makes them replay-relevant.

The package-integrity manifest and package-integrity anchor required in accordance with 10.2 are claim-record-integrity-recovery members, and the replay verifier shall apply 10.3 to them.

### 6.5 Claim identity boundary

This document does not reduce claim identity to claim-record identity, replay-package identity, or semantic-tuple identity.

A change to replay-relevant package material after preservation creates a new preserved claim instance; it does not mutate the identity of the already preserved claim.

### 6.6 External specification boundary

When replay depends on profiles, companions, governing specifications, determining-semantics sources, or other referenced sources, this document requires only that replay-relevant dependencies and immutable designators be preserved and enforced where replay depends on them.

This document does not define the compatibility policy, registry policy, alias policy, deprecation policy, or publication policy for those referenced sources.

## 7 Replay package model

### 7.1 General

A replay package shall contain exactly one claim record.

A replay package shall preserve exactly one required root carrier of each semantic sort:

- one judged-object carrier root;
- one evidence-state carrier root; and
- one evaluator carrier root.

Each required root carrier shall be preserved as one package member.

A replay package may also preserve additional replay-relevant members, claim-record-integrity-recovery members, and auxiliary members.

### 7.2 Claim record minimum content

The claim record shall preserve, at minimum:

- one package identifier;
- one root designator for the judged-object carrier;
- one root designator for the evidence-state carrier;
- one root designator for the evaluator carrier;
- an inventory of package members;
- a replay-relevant, claim-record-integrity-recovery, or auxiliary classification for each package member;
- a canonical reference for each replay-relevant member;
- one designated package-integrity manifest member classified as claim-record-integrity-recovery that preserves the integrity bindings for all replay-relevant members of the replay package, including the claim record;
- one designated package-integrity anchor member classified as claim-record-integrity-recovery;
- the dependency declarations among replay-relevant members; and
- the stable identifiers and immutable defining-source designators required elsewhere in this document for replay-relevant referenced sources, methods, and algorithms.

The claim record may also preserve:

- cached verdicts;
- notes;
- provenance summaries; and
- implementation-specific auxiliary fields.

### 7.3 Root-designation rules

The claim record shall designate exactly one root package member for each required carrier role.

Each required root designator shall designate a package member contained in the same replay package.

One package member shall not satisfy more than one required carrier role.

### 7.4 Member inventory rules

Every package member shall be designated in the claim record.

Every replay-relevant member shall have exactly one canonical reference within the replay package.

Canonical references shall be unique within the replay package.

### 7.5 Cached verdict rule

If a cached verdict is preserved, it shall be treated as auxiliary derived material.

A cached verdict shall not determine replayability, semantic tuple recovery, the derived verdict, or claim identity.

## 8 Carrier minimum requirements

### 8.1 General

Each required carrier shall preserve replay-relevant content from which the corresponding lifting function of Part 1, 9.2 is defined when replay succeeds.

If a required carrier depends on additional replay-relevant members, those members shall be designated in the claim record and included in package closure.

### 8.2 Judged-object carrier

A judged-object carrier shall preserve replay-relevant content from which exactly one admission subject and exactly one reference context are determined.

If admission-subject or reference-context material is not preserved directly in the judged-object carrier, the judged-object carrier or the claim record shall designate the replay-relevant package members on which judged-object lifting depends.

### 8.3 Evidence-state carrier

An evidence-state carrier shall preserve replay-relevant content from which the evidence state made available to the evaluator is induced.

If the evidence state depends on separate evidence members, the evidence-state carrier or the claim record shall designate those members and their package membership by dependency declaration.

This document does not prohibit preservation of an evidence-state carrier whose bound-evidence set is empty.

The preserved existence of auxiliary evidence labels or summaries shall not by itself satisfy this clause.

### 8.4 Evaluator carrier

An evaluator carrier shall preserve replay-relevant content from which one evaluator is induced under Part 1.

At minimum, the evaluator carrier or the replay-relevant members designated for it shall preserve the declared go conditions.

If evaluator induction depends on additional evaluator-declaration material designated by a conforming profile or companion specification, the evaluator carrier or the replay-relevant members designated for it shall also preserve that material.

This document does not prohibit preservation of an evaluator carrier whose declared go conditions are empty.

An evaluator carrier that preserves no declared go conditions shall not support go under Part 1, 10.5.

This document does not prohibit preservation of empty sets of other designated evaluator-declaration material when the evaluator carrier designates none.

If evaluator induction depends on profiles, companions, determining-semantics sources, or other evaluator-defining material designated by immutable designator under Part 1, 10.5, the replay package shall preserve replay-relevant package members corresponding to that material.

### 8.5 Claim record as designation owner

The claim record is the package member that operationalizes the designation form left abstract in Part 1, 9.1.

The claim record shall not be treated as a semantic carrier of judged object, evidence state, or evaluator in place of the required root carriers.

## 9 Replay-relevant projection and package closure

### 9.1 Replay-relevant projection

Each replay-relevant member shall have a replay-relevant projection.

The replay-relevant projection of a member shall include all preserved content of that member that can affect:

- package closure;
- integrity verification;
- parsing;
- dependency resolution;
- induction of a semantic object;
- recovery of the semantic tuple; or
- derivation of the verdict.

The replay-relevant projection shall exclude auxiliary content that cannot affect those results.

### 9.2 Default projection rule

If no narrower replay-relevant projection is designated for a replay-relevant member, the replay-relevant projection of that member shall be the exact preserved octet sequence of that member.

For each required root carrier, the replay-relevant projection shall be the exact preserved octet sequence of that root carrier.

### 9.3 Narrower projection rule

If a replay package designates a replay-relevant projection narrower than the exact preserved octets of a replay-relevant member other than a required root carrier, the claim record shall identify the projection rule by both its stable identifier and an immutable designator of the exact source edition that defines that rule.

The stable identifier and immutable defining-source designator shall be
serialized independently. Either both shall be present or both shall be absent.

A designated projection rule shall be deterministic.

A replay verifier shall not treat a designated narrower projection as authoritative unless it can verify, from preserved material, that the preserved replay-relevant projection is the result of that designated projection rule applied to the preserved member. If it cannot do so, replay shall fail closed.

### 9.4 Canonical representation rule

If integrity verification or comparison is performed over a canonical representation of a replay-relevant projection of a replay-relevant member other than a required root carrier rather than over exact preserved octets, the applicable package-integrity-manifest binding shall identify the canonicalization rule by both its stable identifier and an immutable designator of the exact source edition that defines that rule.

Both canonicalization fields shall be present for a canonical-projection
binding. Neither shall be present for an exact-preserved-octets binding.

A replay verifier shall not treat a designated canonicalization rule as authoritative unless it can verify that rule over the preserved replay-relevant projection. If it cannot do so, replay shall fail closed.

### 9.5 Closure requirement

A replay package shall be closed with respect to all replay-relevant dependencies needed for replay.

### 9.6 Exact closure rule

For every replay-relevant dependency declared from one replay-relevant member to another member:

- the target member shall be contained in the same replay package;
- the target member shall be designated in the claim record;
- the target member shall have a canonical reference;
- the target member shall have an integrity binding when required by 10.2; and
- the target member shall be classified as a replay-relevant member when it satisfies 3.6.

If a replay-relevant dependency corresponds to a profile, companion, governing specification, determining-semantics source, or other referenced source, the claim record shall also preserve the immutable designator of that source.

For such a dependency, a package-local canonical reference, locator, family identifier, version label, registry entry, or local resolver result shall not substitute for the immutable designator of the referenced source.

### 9.7 Prohibited open-package patterns

No replay-relevant dependency shall resolve through:

- undeclared ambient context;
- mutable external content;
- floating aliases;
- mutable branch heads; or
- late retrieval from outside the replay package.

If any replay-relevant dependency requires one of those patterns, the replay package is open.

### 9.8 Immutability of the replay-relevant subset

The replay-relevant subset of a replay package shall be immutable for the purposes of replay.

Any mutation of a replay-relevant member, canonical reference, integrity binding, projection rule, or canonicalization rule after preservation invalidates replay of that replay package.

## 10 Canonical references and integrity bindings

### 10.1 Canonical references

Every replay-relevant member shall have exactly one canonical reference within the replay package.

A canonical reference shall:

- designate exactly one replay-relevant member;
- remain stable within the replay package; and
- be usable by dependency declarations, integrity bindings, and replay reports to identify that member.

A canonical reference is package-local.

A canonical reference shall not be treated as a global identifier for a referenced source or as a substitute for an immutable designator.

### 10.2 Package-integrity manifest and integrity binding minimum content

Every replay-relevant member shall have at least one integrity binding preserved in the designated package-integrity manifest.

The claim record shall identify exactly one package-integrity manifest member from which the integrity bindings applicable to the replay-relevant members of the replay package are recovered.

The package-integrity manifest shall preserve at least one integrity binding for every replay-relevant member, including the claim record.

The integrity binding applicable to the claim record shall bind the exact preserved octets of the claim record.

The package-integrity manifest used only to bind replay-relevant members shall be classified as a claim-record-integrity-recovery member rather than as a replay-relevant or auxiliary member.

The claim record shall identify exactly one package-integrity anchor member that authenticates the exact preserved octets of the designated package-integrity manifest.

The designated package-integrity anchor shall identify the verification method by both its stable method identifier and an immutable designator of the exact source edition that defines that method.

The designated package-integrity anchor shall also identify the signature algorithm by both its stable algorithm identifier and immutable defining-source designator, and shall preserve the verification-key binding surface required for that verification method.

The package-integrity anchor used only to authenticate the designated package-integrity manifest shall be classified as a claim-record-integrity-recovery member rather than as a replay-relevant or auxiliary member.

The package-integrity anchor shall carry the package identifier and designated
package-integrity-manifest member as consistency bindings. After claim-record
integrity recovery, each value in the anchor shall equal the corresponding
value in the integrity-recovered claim record, and the manifest-member value in
both shall designate the same package member whose exact manifest octets were
authenticated. Comparison shall be exact, without trimming, case folding,
Unicode normalization, alias resolution, or inference from a filename,
location, media type, or registry entry. Neither anchor field shall select the
manifest or authorize bootstrap verification.

Requirement identifier: `P2-ANCHOR-TARGET-001`.

This document therefore requires a verifiable signer surface for the designated package-integrity manifest.

This document does not by itself define signer authorization policy, trusted-signer registries, revocation policy, or acceptance criteria for particular signers.

An integrity binding applicable to a required root carrier shall bind the exact preserved octets of that required root carrier.

An integrity binding preserved in the package-integrity manifest shall preserve, at minimum:

- the canonical reference of the member to which it applies;
- the stable identifier of the digest algorithm used;
- the immutable designator of the exact referenced source edition that fixes that algorithm;
- the bound value; and
- whether the bound object is the exact preserved octets of the member or the canonical representation of its replay-relevant projection.

### 10.3 Integrity verification

A conforming replay verifier shall verify the package-integrity anchor according to the exact-edition verification method designated by that anchor, over the exact preserved octets of the designated package-integrity manifest, shall then verify the integrity binding applicable to the claim record as recovered from that manifest, and shall then completely validate that authenticated exact claim-record representation in accordance with 12.2, step 4, before treating anything preserved in the claim record as authoritative, including root designators, dependency declarations, canonical references, projection rules, and canonicalization rules.

Preliminary use of claim-record fields to locate the designated package-integrity manifest member and package-integrity anchor member is a bootstrap use only. That preliminary use shall not authorize lifting, package-closure success, semantic tuple recovery, derived-verdict calculation, or replay success until claim-record integrity recovery and complete claim-record validation have succeeded.

A replay verifier shall not use claim-record root designations, dependency declarations, canonical references, projection rules, canonicalization rules, profile bindings, companion bindings, or referenced-source bindings to select or interpret semantic content before the exact claim record has both passed claim-record integrity recovery and been completely validated.

Package-integrity-anchor verification has an external bootstrap boundary. Before package integrity succeeds, a replay verifier shall select only stable verification-method and algorithm identifiers that the verifier independently supports, require their exact defining-source designators, and apply any operator trust policy independently of package-provided material. A profile, companion specification, registry entry, referenced source, or other package-provided byte sequence shall not authorize the package-integrity anchor that is required to authenticate that byte sequence first. Only after anchor verification, claim-record integrity recovery, and complete step-4 validation succeed may integrity-bound exact-edition source bytes govern the later dependency-resolution and lifting stages for which they are declared.

A conforming replay verifier shall verify the integrity binding of every other replay-relevant member as recovered from the designated package-integrity manifest before replay is reported as successful.

If the claim record, the designated package-integrity manifest, the designated package-integrity anchor, or another replay-relevant member fails integrity verification or required anchor verification, replay shall fail.

### 10.4 Algorithm and method identification

This document does not require one universal digest algorithm or one universal canonicalization algorithm for all replay-relevant members.

Any digest algorithm, projection rule, or canonicalization rule used for replay-relevant purposes shall be governed by a stable identifier assigned by its defining specification and by the immutable designator of the exact referenced source edition that fixes it. The carrier shall preserve the two values in separate fields. Each shall be validated independently, and the exact designated source shall assign the selected identifier the selected meaning.

The stable identifier is an opaque exact string. It shall not be inferred from
the designator URI, the designator digest-algorithm token, a registry path, a
media type, a filename, an implementation default, or another field. The
defining-source designator shall not be inferred from the stable identifier.
In particular, a designator's `sha256` digest-algorithm token identifies the
operation that binds the defining source bytes; it does not identify the
digest algorithm applied to a replay-package member.

An algorithm name, media type, registry entry, implementation default, local configuration value, or version label shall not by itself identify a replay-relevant digest algorithm, projection rule, canonicalization rule, or package-integrity-anchor verification method.

The designated package-integrity anchor shall preserve separate stable identifiers and immutable defining-source designators for the verification method and signature algorithm used for package-integrity-manifest authentication. A stable-identifier URI paired with a digest of different defining-source bytes is not a valid immutable designator.

A conforming profile may designate mandatory algorithms or methods for a particular domain, provided that it does not weaken this clause.

Requirement identifier: `P2-RULE-BINDING-001`. This identifier governs the
paired stable-identifier and exact defining-source-designator requirements in
9.3, 9.4, 10.2, and 10.4.

## 11 Lifting procedures

### 11.1 General procedure shape

This document operationalizes the abstract lifting functions of Part 1, 9.2 by decomposing each lifting procedure into three stages:

1. parse;
2. resolve; and
3. induce.

For a fixed replay package, the procedures implementing $\lambda_J$, $\lambda_E$, and $\lambda_F$ shall be deterministic.

Here, deterministic means that for fixed preserved input and fixed replay-relevant referenced material, repeated execution of the same stage yields the same result or the same failure.

When a lifting defect could be classified at more than one stage, the earliest stage whose preconditions are not satisfied shall govern classification of that defect.

### 11.2 Judged-object lifting

The procedure implementing $\lambda_J$ shall:

1. parse the judged-object carrier root member;
2. resolve every replay-relevant dependency needed to determine the admission subject and the reference context; and
3. induce one judged object in $J$.

If any stage fails, $\lambda_J$ is undefined for that replay package.

### 11.3 Evidence-state lifting

The procedure implementing $\lambda_E$ shall:

1. parse the evidence-state carrier root member;
2. resolve every replay-relevant dependency needed to determine the evidence state; and
3. induce one evidence state in $E$.

If any stage fails, $\lambda_E$ is undefined for that replay package.

### 11.4 Evaluator lifting

The procedure implementing $\lambda_F$ shall:

1. parse the evaluator carrier root member;
2. resolve every replay-relevant dependency needed to determine evaluator content, including any required profile, companion, governing-specification, determining-semantics, or other designated evaluator-defining material; and
3. induce one evaluator in $F$.

If any stage fails, $\lambda_F$ is undefined for that replay package.

### 11.5 Lift success criterion

A replay attempt shall treat lifting as successful only when $\lambda_J$, $\lambda_E$, and $\lambda_F$ are all defined for the same replay package.

## 12 Replay procedure

### 12.1 General

Replay shall begin from the claim record and replay package rather than from a cached verdict alone.

The stable identifier of the replay procedure defined by this clause is:

`https://belgi.dev/ids/procedure/replay/part-2`

The identifier is opaque and shall be compared as an exact string. It does not identify one exact edition by itself. An invocation that depends on this procedure shall bind the identifier to the immutable designator of the exact Part 2 source edition that defines the procedure. A media type, filename, registry result, implementation default, or package-provided selector shall not select or replace that binding.

### 12.2 Required replay steps

A conforming replay verifier shall perform the following steps:

1. read the claim record far enough to identify the package members, the canonical references, the designated package-integrity manifest member, and the designated package-integrity anchor member;
2. verify that the claim record identifies a package-integrity manifest and a package-integrity anchor applicable to the claim record;
3. perform claim-record integrity recovery before any lifting begins as follows:
   a. verify that the package-integrity anchor's stable method and algorithm identifiers match independently supported values, verify their exact defining-source designators, and apply that exact-edition method over the exact preserved octets of the designated package-integrity manifest;
   b. parse the designated package-integrity manifest;
   c. validate the stable digest-algorithm identifier and exact defining-source designator in the claim-record integrity binding, then apply that selected algorithm and verify the binding over the exact preserved claim-record octets; and
   d. after the claim record is integrity-recovered, verify the package identifier and package-integrity-manifest member cross-bindings required by 10.2 against the manifest package member actually consumed by substeps 3 a to 3 c;
4. completely validate the exact preserved claim-record representation whose octets were verified in substep 3 c, under every applicable independently selected exact representation constraint;
5. verify that exactly one required root designator is present for each required carrier role;
6. verify that every designated root member exists in the replay package;
7. verify the uniqueness of canonical references for replay-relevant members;
8. verify package closure;
9. verify that the designated package-integrity manifest preserves an integrity binding for every replay-relevant member other than the claim record itself;
10. validate every applicable digest-algorithm, projection-rule, and canonicalization-rule identifier/designator pair, then verify integrity bindings for replay-relevant members other than the claim record itself from the designated package-integrity manifest;
11. execute the parse, resolve, and induce stages of the procedures implementing $\lambda_J$, $\lambda_E$, and $\lambda_F$ in accordance with Clause 11;
12. if all three lifts succeed, derive the verdict as $f(j,e)$ in accordance with Part 1, 7.4;
13. classify the replay result; and
14. emit a replay report.

Steps 1 to 4 shall observe one immutable exact claim-record byte sequence from
one stable package snapshot. Step 1 processing shall be limited to the
representation-domain processing required to obtain a deterministic bounded
bootstrap view, recognition of the top-level representation, and extraction
only of the package identifier, package members, canonical references,
manifest and anchor designations, claim-record integrity binding, and
cross-binding values required by steps 1 to 3. It shall not enforce complete
required-field coverage,
unknown-property closure, required-root completeness or uniqueness, dependency
closure, profile or referenced-source meaning, or package-controlled schema
authority. It shall not produce semantic objects or authorize lifting. Failure
to obtain that bounded bootstrap view is governed by step 1.

At step 4, the verifier shall apply the complete exact representation graph
selected for the claim record independently of the package. When the JSON
representation companion applies, the trusted role shall be externally fixed
as `claim-record`, the exact digest-bound schema graph selected for that role
shall be applied, and the exact octets used by substep 3 c shall be the octets
validated. An instance `$schema`, physical path or filename, logical member
name, package-supplied member role, media type, mutable registry lookup,
package field, schema designator, implementation default, guessed role, alias,
or fallback shall not select, replace, or relax that trusted role or graph.
Failure at step 4 shall yield `malformed-claim-record` with outcome class
`malformed-carrier`. No processing governed by a later step, or by a
representation stage ordered after step 4, shall be performed after that
failure.

Requirement identifier: `P2-CLAIM-VALIDATION-001`.

### 12.3 Cached verdict mismatch

If a cached verdict is preserved and differs from the derived verdict, the replay verifier shall report a warning and shall ignore the cached verdict for all semantic purposes.

### 12.4 Replay failure rule

Replay shall fail if package reading, integrity verification, complete authenticated claim-record validation, package closure, or required lifting fails.

If repeated execution of the same replay procedure over the same replay package by the same implementation yields different recovered semantic tuples or different derived verdicts, replay shall fail.

This repeated-execution rule is a minimum operational failure detector for one implementation. Cross-implementation verdict agreement is governed by 12.5 when a conforming profile declares verdict-level interoperability.

### 12.5 Verdict-level interoperability

When a conforming profile declares verdict-level interoperability, two conforming implementations of that profile that both successfully replay the same replay package under that profile shall derive the same verdict.

If two such implementations derive different verdicts from the same replay package under that profile, at least one implementation is non-conforming with respect to the declaring profile.

This clause does not require one general proof procedure for cross-implementation equivalence of semantic tuples or evaluators. It defines the profile-activated verdict agreement obligation.

NOTE The clauses, declaration material, exact-edition artifacts, and machine-checkable procedures by which a profile declares and satisfies that obligation are defined by BELGI - Part 3.

### 12.6 Replay-procedure conformance corpus

`conformance/ReplayProcedure.v2.json` is the clause-linked logical corpus for
the replay procedure. It has corpus role `replay-procedure` and identifies the
exact Part 2 `0.5` Working Draft source to which its cases apply. It binds the
exact `spec-0.4` `ReplayProcedure.v1.json` predecessor and preserves all of its
cases and requirement links. Its cases operate on
already decoded logical fields and explicit verification observations; they do
not select a JSON schema, package container, cryptographic library, or
implementation diagnostic.

Operation `rule-source-binding-validate` requires independent stable-identifier
and exact-source-designator values and records whether the designated source is
available, digest-valid, and assigns that identifier the selected rule meaning.
It exercises `P2-RULE-BINDING-001` without defining an identifier or rule that
the prose does not define.

Operation `claim-record-integrity-recovery` supplies the ordered observations
for 12.2, step 3, together with the two claim-record identities, the two anchor
identities, and the actual manifest member. A rejected case records the one
primary problem type, outcome class, and governing substep required by this
document. Corpus-local operation, state, and case identifiers do not create
normative replay vocabulary.

Operation `authenticated-claim-record-validate` supplies ordered logical
observations through 12.2, step 4 and selected later steps, including whether
complete validation was performed over the authenticated bytes using the
independently trusted claim-record graph. Its cases expose the governing
step, problem type, outcome class, and terminal boundary without substituting
those observations for exact-byte representation, digest, or signature
evidence. Corpus-local authority and latent-defect labels are not schema
selectors or replay vocabulary.

Operation `replay-report-package-identifier-select` supplies exactly
`step1BootstrapComplete`, `candidatePackageIdentifier`, `terminalStep`,
`anchorPackageIdentifier`, and `sourcePackageIdentifierHint`. The operation
selects only the package identifier availability state required by 13.1. A
complete Step 1 requires a string candidate with length at least one and
selects that exact candidate for every later terminal step: `2`, `3a`, `3b`,
`3c`, `3d`, `4` through `14`, or `successful-replay`. Candidate validity is
the non-empty string constraint; the operation performs no trimming or other
normalization. An incomplete Step 1 requires a null corpus candidate and
selects the language-neutral unavailable state at terminal step `1`. Anchor
values and source hints are ignored string-or-null observations. Their content,
including whitespace-only content, neither replaces the Step 1 result nor
causes rejection. The terminal step classifies the observation but does not
alter the selected value.
The expected result exposes `packageIdentifierAvailable` and, only when true,
the exact `packageIdentifier`. Malformed Step 1 state combinations reject with
the corpus-local reason `invalid-step-1-package-identifier-state`. The reason
is a fixture control, not replay vocabulary.

An issued edition that includes this corpus shall bind its exact bytes by
immutable designator. The corpus does not override this document and does not
by itself establish implementation adoption or conformance.

## 13 Replay reports and problem taxonomy

### 13.1 Replay report minimum content

A replay report shall contain, at minimum:

- `status`;
- `outcomeClass`;
- `packageIdentifier`;
- `problems`; and
- `warnings`.

If replay is successful, the replay report shall also contain the derived verdict.

The language-neutral value of `packageIdentifier` shall be exactly one of:

- the exact non-empty package identifier yielded by successful completion of
  the complete atomic bounded bootstrap view in 12.2, step 1; or
- unavailable when step 1 fails before that complete view and its non-empty
  package identifier have both been obtained.

Step 1 is atomic for this purpose. A package identifier observed by partial
parsing does not survive a later step-1 failure. A physical-container value,
adapter hint, filename, path, caller default, implementation sentinel, anchor
value, or other value outside the complete Step 1 view shall not supply the
report field.

After Step 1 succeeds, the replay report shall retain the exact claim-record
package identifier for a failure at step 2 or any later step. The value remains
an unauthenticated candidate until claim-record integrity recovery completes;
its presence in the report does not assert authenticity. In particular, a
step-3-d package identifier mismatch shall report the claim-record value, not
the anchor value or a source hint.

The candidate is non-empty when its representation-domain string length is at
least one. A verifier shall preserve it exactly and shall not trim whitespace,
normalize Unicode, case-fold, or apply an identifier-specific rewrite when
selecting the report value.

A successful replay report shall contain the recovered non-empty package
identifier. The unavailable state is permitted only for a non-replayable
report. A text token such as `unavailable`, `<unknown-package>`, an empty
string, or any other sentinel shall not encode the unavailable state.

Requirement identifier: `P2-REPORT-IDENTITY-001`.

### 13.2 Replay status

The replay status shall be exactly one of:

- `replayable`; or
- `non-replayable`.

### 13.3 Replay outcome classes

The minimum replay outcome classes are:

| Outcome class | Meaning |
| --- | --- |
| `successful-replay` | replay completed without package-reading failure, integrity failure, complete authenticated claim-record validation failure, closure failure, or lift failure, and yielded one semantic tuple and one derived verdict in accordance with Part 1, 7.4; warnings such as `cached-verdict-mismatch` do not by themselves change this outcome class |
| `malformed-carrier` | replay failed because the claim record, a required carrier member, or a required claim-record-integrity-recovery member could not be parsed as preserved, or because the authenticated exact claim record could not be completely validated under its applicable representation requirements |
| `unresolved-reference` | replay failed because a replay-relevant dependency could not be resolved within the replay package |
| `integrity-failure` | replay failed because the claim record or another replay-relevant member did not satisfy its integrity binding |
| `lift-failure` | replay failed because parse and dependency resolution completed but one or more lifting procedures were undefined |
| `ambient-context-required` | replay failed because successful replay would require undeclared ambient context or mutable external content |
| `non-replayable-claim` | replay failed because the preserved package does not satisfy the replay preconditions claimed for it |

The minimum replay outcome classes are exact-edition-local compact identifier
tokens in the `replay-outcome-class` vocabulary.

A conforming profile or implementation shall not assign a different meaning to a minimum replay outcome class defined by this document.

### 13.4 Replay problem minimum content

A replay problem shall contain, at minimum:

- `type`;
- `title`;
- `detail`.

A replay problem shall contain `relatedReference` if and only if the related package member has a canonical reference.

### 13.5 Minimum replay problem types

The minimum replay problem types are:

- `malformed-claim-record`;
- `claim-record-integrity-binding-missing`;
- `claim-record-integrity-binding-mismatch`;
- `claim-record-integrity-recovery-failure`;
- `claim-record-integrity-recovery-malformed`;
- `missing-required-root`;
- `duplicate-root-designation`;
- `missing-required-member`;
- `duplicate-canonical-reference`;
- `integrity-binding-missing`;
- `integrity-binding-source-failure`;
- `integrity-binding-mismatch`;
- `out-of-closure-dependency`;
- `unresolved-dependency`;
- `carrier-parse-failure`;
- `carrier-resolve-failure`;
- `induce-failure`;
- `ambient-context-required`; and
- `non-deterministic-lift`.

The minimum replay problem types shall govern replay stages and replay outcome classes as follows:

| Problem type | Governing replay step | Governing outcome class |
| --- | --- | --- |
| `malformed-claim-record` | step 1 or step 4 | `malformed-carrier` |
| `claim-record-integrity-binding-missing` | step 2 | `non-replayable-claim` |
| `claim-record-integrity-binding-mismatch` | step 3 | `integrity-failure` |
| `claim-record-integrity-recovery-failure` | step 3 | `integrity-failure` |
| `claim-record-integrity-recovery-malformed` | step 3 | `malformed-carrier` |
| `missing-required-root` | step 5 | `non-replayable-claim` |
| `duplicate-root-designation` | step 5 | `non-replayable-claim` |
| `missing-required-member` | step 6 | `non-replayable-claim` |
| `duplicate-canonical-reference` | step 7 | `non-replayable-claim` |
| `out-of-closure-dependency` | step 8 | `non-replayable-claim` |
| `unresolved-dependency` | step 8 | `unresolved-reference` |
| `ambient-context-required` | step 8 or step 11 resolve | `ambient-context-required` |
| `integrity-binding-missing` | step 9 | `non-replayable-claim` |
| `integrity-binding-source-failure` | step 10 | `integrity-failure` |
| `integrity-binding-mismatch` | step 10 | `integrity-failure` |
| `carrier-parse-failure` | step 11 parse | `malformed-carrier` |
| `carrier-resolve-failure` | step 11 resolve | `unresolved-reference` |
| `induce-failure` | step 11 induce | `lift-failure` |
| `non-deterministic-lift` | 12.4 repeated execution | `non-replayable-claim` |

In the package-integrity manifest and required package-integrity anchor model, `claim-record-integrity-binding-missing` includes failure to designate the required package-integrity manifest or required package-integrity anchor, failure to recover either designated member from the replay package, or failure to recover the claim-record integrity binding from the designated package-integrity manifest.

In the package-integrity manifest and required package-integrity anchor model, `claim-record-integrity-binding-mismatch` includes actual digest or signature disagreement after the applicable method, algorithm, source, key, and representation material has been parsed and selected successfully.

In the package-integrity manifest and required package-integrity anchor model, `claim-record-integrity-recovery-failure` includes an unknown, unsupported, retired-for-new-use, prohibited, or inconsistent stable method or algorithm identifier; a missing, mismatched, substituted, or unavailable exact defining-source binding; prohibited downgrade or fallback; or another failure to apply the designated package-integrity anchor or manifest when the failure is neither missing designation, malformed representation, nor an actual digest or signature mismatch.

It also includes disagreement between either consistency binding in the
package-integrity anchor and the corresponding value in the
integrity-recovered claim record, or disagreement between their designated
manifest-member value and the manifest member actually authenticated.

In the package-integrity manifest and required package-integrity anchor model, `claim-record-integrity-recovery-malformed` includes a missing required identifier/designator pair in the manifest, a syntactically malformed identifier or defining-source designator, malformed verification key or signature encoding, or another failure to parse the designated package-integrity anchor or designated package-integrity manifest as preserved.

`integrity-binding-source-failure` includes an unknown, unsupported,
retired-for-new-use, prohibited, inconsistent, substituted, unavailable, or
unverifiable stable identifier or exact defining-source designator for a
digest algorithm, projection rule, or canonicalization rule used at step 10.
It does not denote an actual bound-value disagreement after successful rule
selection; that remains `integrity-binding-mismatch`.

The minimum replay problem types are exact-edition-local compact identifier
tokens in the `replay-problem-type` vocabulary.

A conforming profile or implementation shall not assign a different meaning to a minimum replay problem type defined by this document.

Profiles may define more specific replay problem types.

Profiles shall not redefine the meanings of the minimum replay outcome classes or the minimum replay problem types, and shall not collapse the minimum replay outcome classes or the minimum replay problem types into fewer classes.

### 13.6 Warning types

The replay report may contain warnings.

This document defines at minimum the following warning type:

- `cached-verdict-mismatch`.

The replay-status values in 13.2, replay-outcome-class values in 13.3,
replay-problem-type values in 13.5, and replay-warning-type values in 13.6
form four named compact identifier vocabularies. Their namespace identities are
respectively:

- (`https://belgi.dev/ids/specification/part-2`, `replay-status`);
- (`https://belgi.dev/ids/specification/part-2`, `replay-outcome-class`);
- (`https://belgi.dev/ids/specification/part-2`, `replay-problem-type`); and
- (`https://belgi.dev/ids/specification/part-2`, `replay-warning-type`).

Within each namespace, a token shall be compared as one exact string without
case folding, Unicode normalization, whitespace trimming, prefix expansion, or
other normalization. No two meanings may share one token in the same
namespace. Once assigned, a token shall not be reassigned a different meaning
by a later edition of this Part family, and retirement or removal shall not make
it available for reassignment. A token is not globally reusable without its
named namespace and exact defining edition.

### 13.7 Failure priority

If more than one replay failure is detected, the replay verifier shall report as the replay outcome class the failure whose governing replay step is earliest in the 13.5 mapping and that prevents successful replay.

When a problem type maps to more than one governing replay step in 13.5, the governing replay step shall be the step at which that problem was actually detected.

Within step 3, substeps a through d in 12.2 are ordered. A failure in an earlier
substep is primary over a cross-binding mismatch in substep d. Complete
claim-record validation is not performed after such a failure. A failure at
step 4 is primary over a JSON physical-inventory failure or any failure governed
by steps 5 to 14, and those later checks are not performed after the step 4
failure. Within step 10,
identifier/designator pair selection precedes application of the selected rule;
an `integrity-binding-source-failure` is therefore primary over an actual
bound-value comparison that cannot validly be performed.

Additional replay problems may also be reported.

## 14 Conformance

### 14.1 Conformance classes

The following conformance classes are defined:

- BELGI Carrier Producer;
- BELGI Replay Package Producer;
- BELGI Replay Verifier; and
- BELGI Full Part 2 Implementation.

### 14.2 BELGI Carrier Producer

An implementation conforms to this document as a BELGI Carrier Producer if it produces one or more required carriers whose replay-relevant content satisfies the carrier minimum requirements of Clause 8 and the corresponding lifting procedures of Clause 11.

### 14.3 BELGI Replay Package Producer

An implementation conforms to this document as a BELGI Replay Package Producer if it:

- produces replay packages satisfying Clause 7;
- preserves the carrier minimum requirements of Clause 8 and the corresponding lifting procedures of Clause 11;
- enforces replay-relevant projection and package closure in accordance with Clause 9; and
- provides canonical references, package-integrity manifests, integrity bindings, and the required package-integrity anchors in accordance with Clause 10.

### 14.4 BELGI Replay Verifier

An implementation conforms to this document as a BELGI Replay Verifier if it:

- applies the replay procedure of Clause 12;
- completely validates the authenticated exact claim record at 12.2, step 4, before consuming claim-record authority in any later replay step;
- applies the replay report and problem taxonomy of Clause 13;
- ignores cached verdicts for semantic purposes; and
- does not treat open replay packages or integrity-failing replay packages as replayable.

### 14.5 BELGI Full Part 2 Implementation

An implementation conforms to this document as a BELGI Full Part 2 Implementation if it conforms to 14.2, 14.3, and 14.4.

### 14.6 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- the exact edition of BELGI - Part 1 used as semantic authority, or the immutable designator from which that exact edition is identified;
- each immutable designator of profile, companion, governing-specification, determining-semantics, or other replay-relevant referenced source on which replay-package production or replay verification depends, or state that none is used;
- for each identified profile that declares verdict-level interoperability, the immutable designators required by that profile's interoperability declaration; and
- the date of the statement.

## 15 Transport and storage neutrality

This document defines the logical replay package and the carrier-side requirements for replay.

This document does not require one outer transport, one archive format, or one storage topology.

A conforming implementation may serialize a replay package as a directory tree, archive, object bundle, or other preserved container, provided that:

- the claim record is preserved as one package member;
- package members preserve their authoritative octet sequences exactly;
- canonical references remain stable within the replay package; and
- the container does not defeat the closure, integrity, or replay requirements of this document.

A representation companion may allocate a media type and a stable container-procedure identifier. A media type identifies representation format only; it shall not select the replay procedure, container procedure, trusted package role, schema role, profile, companion, algorithm, or verification method.

## 16 Security and trust considerations

This document's main security and trust risks arise at the preserved-package boundary. A replay package can appear complete or authoritative while omitting replay-relevant dependencies, mutating replay-relevant members, substituting projection or digest methods, or inviting consumers to rely on cached verdicts and presentation material instead of replay.

Closure violations and replay-package tampering can arise when replay-relevant dependencies resolve through mutable external content, floating aliases, branch heads, omitted members, or other late retrieval outside the preserved package. Clauses 7 to 9 require explicit designation, replay-relevant classification, exact closure, and immutability of the replay-relevant subset so that replay does not depend on undeclared external state.

Integrity bypass and algorithm-substitution risk can arise when a replay-relevant member is accepted without verified binding, or when stable identifiers and exact defining-source designators are collapsed, or when digest, projection, canonicalization, and verification methods are inferred implicitly at replay time. Clauses 10.2 to 10.4 require integrity bindings and separate validation of the stable identifiers and exact defining-source designators that govern them.

Claim-record bootstrap substitution can arise when unverified claim-record fields are used as authority for root selection, dependency interpretation, semantic lifting, profile binding, or replay success before the designated package-integrity manifest and package-integrity anchor have recovered claim-record integrity. Clause 10.3 confines preliminary claim-record use to the integrity-recovery bootstrap.

Auxiliary-material substitution can arise when cached verdicts, summaries, filenames, undeclared signatures, or other auxiliary material are treated as if they determined replayability or the derived verdict. Clauses 6.4, 7.5, 10.2, 10.3, 12, and 13 keep those forms auxiliary, place the package-integrity manifest and package-integrity anchor in the dedicated claim-record-integrity-recovery class, and require the replay procedure and replay report taxonomy to govern the reported result.

This document requires that a conforming replay package expose a verifiable signer surface through the required package-integrity anchor. It does not, by itself, determine which signers are authorized, trusted, or acceptable for any organizational reliance decision.

This document does not require preservation of personal identifiers. When replay-relevant carriers or package members incidentally contain personal data, applicable privacy obligations apply independently of this document.

Replay-package identifiers, canonical references, package-integrity anchors, signer surfaces, and auxiliary metadata can create correlation or metadata-leakage risk when reused across packages or transport contexts. Clauses 6.4, 7.2, 7.5, and 10.1 to 10.3 limit authoritative material to what replay requires and keep cached verdicts, summaries, and other auxiliary material from silently widening disclosure. Data minimization, pseudonymization, transport confidentiality, and disclosure policy remain implementation, profile, or companion obligations.

This document does not define user-facing interfaces, locale-sensitive rendering, or natural-language presentation requirements. Accessibility and internationalization obligations therefore arise only in implementations or companion surfaces that present BELGI material to users.

Excluded reliance claim: this document preserves and verifies replayable carrier material but does not establish organizational acceptance criteria for a recovered evaluator, replay package, or successful replay result.
