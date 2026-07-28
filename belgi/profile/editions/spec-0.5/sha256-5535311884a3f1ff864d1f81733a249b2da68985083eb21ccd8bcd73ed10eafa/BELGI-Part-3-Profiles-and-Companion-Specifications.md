# BELGI - Part 3: Profiles and companion specifications

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Companion specification: Identifier and registry governance
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is Part 3. It defines the extension discipline for profiles and companion specifications used with Parts 1 and 2.

## Introduction

Part 1 fixes the semantic core of an admission claim. Part 2 fixes the claim-carrier and replay-package obligations needed to preserve and replay that core.

Real admission systems still need domain-specific vocabularies, constraints, parameterizations, and reusable declaration material. Without a separate extension discipline, such material can silently redefine evaluator meaning, reopen claim identity, weaken replay, or add hidden semantic inputs.

This document defines the extension governance needed to prevent that drift. It reserves the extension points at which profiles and companion specifications may add or constrain domain-specific content. It also fixes exact edition binding, initial-edition publication discipline, controlled identifier and registry boundaries, publication rules, and Part 3 conformance.

This document specifies BELGI extension governance for verdict replay. It is not an attestation framework, an attestation-profile registry, or a generic extension registry for external supply-chain or provenance ecosystems, although profiles and companion specifications may reference such material when another BELGI normative text makes it replay-relevant.

This document states governance, exact-edition, and conformance obligations. It does not by itself supply a general proof calculus for semantic equivalence across profile editions, companion editions, or implementations.

This document allows growth at the domain edge without reopening the semantic authority of Part 1 or the replay authority of Part 2.

## 1 Scope

This document defines the profile and companion-specification framework for BELGI.

This document defines:

- the profile and companion-specification model;
- the extension boundary between Parts 1 and 2 and later domain-specific material;
- the reserved extension points available to profiles and companion specifications;
- the protected core and prohibited redefinitions;
- versioning and initial-edition publication rules;
- identifier and term rules;
- the boundary between exact defining artifacts and identifier-registry governance;
- publication and dependency rules; and
- Part 3 conformance classes.

This document is applicable to BELGI extensions that constrain or supplement judged-object carriers, evidence-state carriers, evaluator carriers, replay verification, or replay reporting without changing the semantic core fixed by Part 1 or the replay obligations fixed by Part 2.

This document does not define:

- the semantic signature, behavioral law, or replay semantics fixed by Part 1;
- the carrier minimum requirements, closure rules, integrity rules, lifting rules, replay procedure, or replay taxonomy fixed by Part 2;
- an attestation framework, attestation-profile registry, or generic extension registry for external supply-chain or provenance ecosystems;
- any specific domain profile, any specific companion specification, or any specific representation-specific schema;
- a mutable central registry or mandatory online publication service as replay authority; or
- whether a profile, companion specification, or evaluator satisfies external correctness or organizational acceptance criteria.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Companion specification: Identifier and registry governance, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the following terms and definitions apply.

### 3.1 extension point

explicit location in the BELGI family at which a profile or companion specification may add or constrain domain-specific content

### 3.2 profile

normative BELGI extension specification selecting or constraining one coherent set of domain-specific declarations, vocabularies, and mandatory choices at reserved extension points without redefining the semantics of Part 1 or the replay obligations of Part 2

### 3.3 companion specification

supporting specification referenced by a profile or by replay-relevant evaluator material to define domain-specific vocabulary, rules, or declaration material at one or more reserved extension points

### 3.4 profile family

stable lineage of profile editions treated as one evolving profile line under common change control

### 3.5 companion-specification family

stable lineage of companion editions treated as one evolving companion line under common change control

### 3.6 profile identifier

stable identifier for one profile family

### 3.7 companion identifier

stable identifier for one companion-specification family

### 3.8 version designator

publisher-controlled identifier distinguishing one edition of a profile or companion specification from another

### 3.9 exact edition binding

binding of a replay-relevant dependency to one exact profile or companion edition fixed by immutable designator

### 3.10 compatibility statement

publisher-declared statement that no predecessor compatibility declaration applies for an initial published edition under the current BELGI draft family

### 3.11 profile closure

property by which all profile and companion material required to interpret replay-relevant declarations is identified exactly and without undeclared assumptions

### 3.12 extension term

term defined by a profile or companion specification at a reserved extension point

### 3.13 term identifier

stable machine-usable identifier for one machine-readable extension term defined by a profile or companion specification

### 3.14 deprecated identifier

identifier whose assigned meaning is retained while new normative use is discouraged or disallowed in accordance with its governing registry event

## 4 Symbols and abbreviated terms

### 4.1 Symbols

No symbols are listed in this document.

### 4.2 Abbreviated terms

No abbreviated terms are listed in this document.

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 14 are normative unless stated otherwise.

The family identifier of this Part is:

`https://belgi.dev/ids/specification/part-3`

The current draft version designator is:

`0.5`

This document owns extension governance. The Identifier and registry governance companion owns identifier allocation, registry lifecycle, registry snapshots, and registry change control. Neither document owns the semantic authority of Part 1 or the replay-package authority of Part 2.

Profile identifiers, companion identifiers, version designators, term identifiers, replay outcome class identifiers, and replay problem type identifiers are identifiers. Human-readable titles, labels, names, or short names are not sufficient for normative identification unless this document or another BELGI normative text explicitly states otherwise.

## 6 Layering and extension boundary

### 6.1 General

This document distinguishes:

- the semantic core fixed by Part 1;
- the claim-carrier and replay-package layer fixed by Part 2; and
- the extension-governance layer fixed by this document.

### 6.2 Authority priority

Part 1 remains the semantic authority for judged objects, evidence states, evaluators, verdicts, claim identity, and replay semantics.

Part 2 remains the authority for claim records, replay packages, closure, canonical references, integrity bindings, lifting procedure shape, replay procedure, replay reports, replay outcome classes, and replay problem types.

Profiles and companion specifications are subordinate to Parts 1 and 2 for those matters.

### 6.3 Exact edition boundary

When replay depends on any profile, companion specification, governing specification, determining-semantics source, or other referenced source, its exact edition shall be fixed by immutable designator and preserved in accordance with Parts 1 and 2.

A family identifier, version designator, registry entry, discovery result, short name, floating alias, mutable locator, local installation path, branch, or tag is not sufficient for replay-relevant identification.

### 6.4 Profile closure boundary

A preserved claim that depends on a profile or companion specification has profile closure only when all replay-relevant profile and companion material required for lifting or replay is identified exactly and can be resolved without undeclared assumptions.

### 6.5 Non-authoritative labels and discovery metadata

Titles, labels, examples, presentation text, short names, and predecessor or successor references can assist human understanding or discovery.

Those forms shall not determine core BELGI meaning, replay success, replay outcome class, replay problem type, or exact edition identity.

No such form creates an alias, identifier equivalence, or replay substitution rule.

## 7 Profile and companion model

### 7.1 General

A profile stabilizes one interoperable selection over the open BELGI extension surface.

A companion specification contributes reusable domain material at one or more reserved extension points.

A profile may select one or more companion specifications and impose narrower constraints over them.

### 7.2 Profile minimum content

A profile shall identify, at minimum:

- one profile identifier;
- one version designator;
- one title and one scope statement;
- the BELGI part editions on which it depends;
- the exact companion editions it selects, if any;
- the reserved extension points it uses;
- the evaluator-declaration families it activates, if any;
- the mandatory and optional declarations it introduces or constrains;
- for an initial published edition under the current BELGI draft family, a statement that no predecessor compatibility declaration applies; and
- its own conformance requirements.

### 7.3 Companion-specification minimum content

A companion specification shall identify, at minimum:

- one companion identifier;
- one version designator;
- one title and one scope statement;
- the reserved extension points it serves;
- the declaration material, vocabularies, or term identifiers it defines;
- the machine-readable material required for its replay-relevant use, if any;
- for an initial published edition under the current BELGI draft family, a statement that no predecessor compatibility declaration applies; and
- its own conformance requirements.

### 7.4 Dependency and reference rules

If a profile depends on a companion specification, governing specification, or other referenced source for replay-relevant meaning, that dependency shall be declared explicitly and by exact edition.

If a profile or companion specification refers to a specific clause, table, figure, or annex of another specification for replay-relevant meaning, the reference shall be dated and clause-specific.

### 7.5 Publication rule

A replay-relevant profile or companion specification shall publish:

- human-readable normative text from which its declared meaning is determined; and
- machine-readable declaration material usable at its declared extension points, where replay-relevant use depends on such material.

A replay-relevant profile or companion specification shall be published in a form that permits construction of an immutable designator for its exact published edition in accordance with Parts 1 and 2.

### 7.6 Profile closure rule

A profile shall identify all replay-relevant profile material on which interpretation of an evaluator carrier or replay verifier depends, so that application of the profile does not require undeclared profile assumptions.

The same requirement applies when replay-relevant evaluator material references a companion specification without profile mediation.

## 8 Reserved extension points

### 8.1 General

Only the extension points listed in 8.2 to 8.11 are open to profile-level or companion-level extension under BELGI.

When a profile or companion specification activates evaluator-declaration material beyond the declared go conditions preserved under Part 2, 8.4, it shall do so only through one or more of 8.4 to 8.9.

### 8.2 Judged-object correspondence, carrier vocabulary, and constraints

A profile or companion specification may define domain-specific carrier vocabularies, identifiers, or constraints for admission subjects and reference contexts.

A profile using domain-specific judged-object terms shall state which domain material induces the admission subject and which domain material induces the reference context. That correspondence shall be deterministic from replay-relevant material and shall state the membership and component-equality consequences of the mapping.

Every fact that changes judged-object identity shall participate in one or both declared components. A profile shall not make judged-object identity depend on undeclared ambient context or introduce a third top-level semantic input sort.

An evaluator activated by a profile shall be total on the Part 1 domain. For a judged object outside the profile's declared subset, the evaluator shall return no-go unless the profile normatively fixes another total behavior.

A parse, resolution, or induction failure is governed by Part 2 and makes the corresponding lifting function undefined; it shall not be represented as a valid judged object outside the profile subset. Conversely, a valid judged object outside that subset shall not make an evaluator partial.

A companion specification may supply vocabulary or constraints used by the correspondence, but the profile remains responsible for defining the correspondence.

Such definitions shall remain subordinate to the judged-object model fixed by Part 1 and the judged-object-carrier obligations fixed by Part 2.

### 8.3 Evidence vocabulary and evidence kinds

A profile or companion specification may define evidence kinds, evidence-source categories, source-material-role vocabularies, and evidence-state carrier vocabularies or constraints.

Such definitions shall remain subordinate to the evidence-state role fixed by Part 1 and the evidence-state-carrier obligations fixed by Part 2.

### 8.4 Condition vocabulary

A profile or companion specification may define condition types, condition parameters, and related evaluator-declaration vocabularies used by evaluator carriers.

Condition vocabulary remains evaluator-declaration material. It does not create a new semantic sort.

### 8.5 Trust-boundary vocabulary

A profile or companion specification may define trust-boundary categories, source classes, source-material-role vocabularies, execution classes, or exclusion classes.

Trust-boundary vocabulary remains evaluator-declaration material. It does not create a new semantic sort.

### 8.6 Governing-specification reference vocabulary

A profile or companion specification may define vocabulary or rules used to identify governing specifications, determining-semantics sources, or related normative dependencies.

Governing-specification reference vocabulary remains evaluator-declaration material. It does not create a new semantic sort.

### 8.7 Evidence-condition binding kinds

A profile or companion specification may define evidence-condition binding relation kinds and the meaning of those relation kinds.

Evidence-condition binding vocabulary remains evaluator-declaration material. It does not create a new semantic sort.

### 8.8 Environment-envelope vocabulary

A profile or companion specification may define environment-envelope declarations or execution-context vocabularies used by evaluator carriers.

Environment-envelope material remains evaluator-declaration material. It does not create a new semantic sort.

Concrete context used to identify an admission subject or reference context is governed by 8.2 and shall not be moved into the evaluator solely because it describes an environment. If one fact independently participates in judged-object identity and evaluator meaning, each role and its replay-relevant binding shall be explicit.

### 8.9 Evaluator declaration parameter vocabulary

A profile or companion specification may define parameter vocabularies used to constrain or interpret evaluator-carrier declarations.

Evaluator declaration parameter vocabulary remains evaluator-declaration material. It does not create a new semantic sort.

### 8.10 Replay-policy refinements

A profile may define stricter replay validation rules, more specific replay problem types, or outcome subclasses, provided that the minimum replay outcome classes and minimum replay problem types of Part 2 remain available and unchanged in meaning.

### 8.11 Representation-specific schemas and serialization bindings

A profile or companion specification may define representation-specific carrier schemas, claim-record schemas, replay-report schemas, serialization bindings, validation constraints, machine-checkable conformance-corpus schemas, or machine-checkable conformance-procedure bindings for the carriers and package material governed by Parts 1 and 2.

Such definitions shall remain subordinate to Parts 1 and 2 and shall not introduce a new semantic sort, a new semantic verdict, or a new replay authority outside the reserved BELGI extension surface.

## 9 Protected core and prohibited redefinitions

### 9.1 General

Profiles and companion specifications shall not refound the BELGI core.

### 9.2 No new semantic sort or verdict

A profile or companion specification shall not:

- add a new top-level semantic input sort;
- add a third semantic verdict value; or
- introduce a new preserved semantic primitive that replaces evaluator application as the source of verdict.

### 9.3 Protected semantic and replay identities

A profile or companion specification shall not redefine:

- extensional evaluator identity;
- claim identity;
- the same semantic tuple recovered by replay; or
- replayable claim.

### 9.4 Protected Part 2 semantics

A profile or companion specification shall not:

- remove a required carrier role;
- remove a required lifting stage;
- redefine replay package closure;
- suppress required integrity verification;
- redefine the minimum replay outcome classes of Part 2; or
- redefine the minimum replay problem types of Part 2.

### 9.5 No undeclared semantic dependency

A profile or companion specification shall not make lifting, replay success, replay classification, or derived verdict depend on:

- undeclared ambient context;
- mutable external content;
- floating aliases;
- mutable branch heads;
- late retrieval outside the declared replay rules; or
- hidden default profile selection.

### 9.6 No prose-only or presentation-only semantics

A profile or companion specification shall not assign indispensable semantic work to comments, filenames, presentation text, examples, or labels unless that material is itself an identified referenced source bound by exact edition.

### 9.7 Extension non-interference rule

An optional or unrecognized extension term shall not by its absence, non-recognition, or omission:

- convert no-go into go;
- convert a non-replayable claim into a replayable claim; or
- silently redefine a term defined by Part 1, Part 2, or Part 3.

### 9.8 Verdict-level interoperability declaration

A profile may declare verdict-level interoperability.

A profile may declare verdict-level interoperability only for a stated class of replay packages whose replay-relevant carrier vocabularies, declaration material, referenced semantics, exact-edition dependencies, and replay-policy refinements are all identified by the declaring profile edition.

A profile that declares verdict-level interoperability shall identify the clauses, declarations, companion dependencies, or referenced sources by which that obligation is satisfied.

A profile that declares verdict-level interoperability shall also identify, by exact edition:

- one finite verdict-interoperability corpus; and
- one machine-checkable conformance procedure by which implementations are tested against that corpus.

These declared corpora and machine-checkable procedures are conformance artifacts. They do not by themselves prove general evaluator equivalence outside the declared exact-edition surface.

Non-declared conformance material, including diagnostic corpora, experimental procedures, example fixtures, recovered-tuple rendering aids, and implementation-local test surfaces, shall not satisfy this verdict-level interoperability declaration unless it is identified by the exact selected profile edition under this clause.

A profile shall not claim the verdict-level interoperability obligation of BELGI - Part 2, 12.5 if decisive verdict agreement criteria remain outside the declared exact-edition surface.

A profile that does not declare verdict-level interoperability remains subject to BELGI - Part 2, 12.4 and shall not claim the cross-implementation verdict agreement obligation of BELGI - Part 2, 12.5.

## 10 Initial-edition publication statement and replay substitution

### 10.1 General

An initial published profile edition or companion edition under the current BELGI draft family shall state that no predecessor compatibility declaration applies.

The current BELGI draft family defines no successor-edition compatibility classes and no machine-readable compatibility governance beyond that initial-edition publication statement.

Any publication-time compatibility language under this draft family does not by itself authorize replay substitution.

### 10.2 Replay substitution rule

A consumer shall not replace an exact bound edition with another edition merely because both editions belong to the same family.

Replay shall use the exact edition fixed by immutable designator and preserved in accordance with Part 2.

The initial-edition publication statement of this draft family and any future publication-time compatibility language can support authoring or publication context outside replay. They shall not be interpreted as silent permission to replay against a different exact edition.

Governance review, publication validation, and any future compatibility governance are declaration-time or publication-time controls. They do not by themselves add a replay step or substitute for the replay authority of Part 2.

## 11 Identifier and term rules

### 11.1 Profile and companion identifiers

A profile identifier and a companion identifier shall be publisher-controlled HTTPS identifiers conforming to the Identifier and registry governance companion.

A BELGI-owned profile identifier or companion identifier shall use the prefix `https://belgi.dev/ids/`. A non-BELGI publisher shall use an absolute HTTPS identifier under that publisher's documented change control unless the governing BELGI specification explicitly requires another registered identifier scheme.

An identifier shall be compared as one opaque exact string. A consumer shall not dereference it, follow a redirect, infer meaning from its path, case-fold it, percent-normalize it, or accept a URI variant as equal.

Once published, a profile identifier or companion identifier shall not be reassigned to a different family.

### 11.2 Version designators and exact edition references

Every published profile edition and every published companion edition shall have one explicit version designator.

For replay-relevant purposes, family identifier and version designator support publication and discovery. They are not substitutes for exact edition binding where Parts 1 and 2 require immutable designators of referenced sources.

An immutable designator used for replay-relevant exact-edition binding shall denote exactly one referenced source edition, shall not be reassigned to different content or a different edition, and shall remain stable for the replay-relevant lifetime of claims that depend on it.

A registry entry, publication URL, package name, local resolver result, branch, tag, or version label shall not by itself satisfy replay-relevant exact-edition binding.

If discovery or registry material resolves to content inconsistent with the preserved immutable designator, replay shall fail closed rather than substitute the discovered material.

A profile or companion specification may restrict the permitted immutable-designator schemes for its domain, provided that the restriction does not weaken BELGI - Parts 1 and 2.

### 11.3 Term identifiers

A profile or companion specification that defines machine-readable extension terms shall assign each such term one term identifier.

A globally reusable term identifier shall satisfy the controlled-identifier and exact-comparison rules of 11.1 and shall be allocated under the Identifier and registry governance companion.

A profile or companion may instead define an exact-edition-local compact term token in accordance with the Identifier and registry governance companion, Clause 7.5. The defining document shall name the vocabulary whose namespace is paired with its family identifier and shall fix exact comparison, within-namespace collision prevention, and family-line non-reassignment. Such a token remains subordinate to the exact defining edition, shall not be treated as globally reusable, and need not appear in the global registry.

If a later specification externalizes a local compact token as a globally reusable identifier, it shall allocate a new controlled HTTPS identifier. It shall not silently promote, prefix, map, or alias the local token.

A term identifier shall remain stable within the defining family.

For replay-relevant use, a term identifier shall not have a different meaning in any other exact edition that can be selected by the same evaluator carrier or replay verifier, whether that edition belongs to the same family or a different family.

A term identifier shall be opaque. Human-readable names can change without changing the term identifier.

### 11.4 Lifecycle and predecessor or successor metadata

A profile or companion specification may identify deprecated or retired identifiers and may publish predecessor or successor references for discovery.

A deprecated or retired identifier shall retain its own assigned meaning, shall not be reassigned, and shall not be made an alias for another identifier. A retired identifier shall not be used for new normative material. New use of a deprecated identifier is governed by its exact deprecation event and the exact defining edition.

Predecessor or successor references, short names, migration tables, and redirects are discovery metadata only. They shall not authorize equivalence, fallback, normalization, or replay substitution.

### 11.5 Identifier and registry governance companion boundary

The BELGI - Companion specification: Identifier and registry governance defines the allocation process, minimum registration-entry shape, closed lifecycle vocabulary, collision rules, immutable registry snapshots, modification procedure, conflict review, and appeal procedure for BELGI-controlled identifiers and registry values.

Every meaning-bearing registry entry shall identify one exact defining artifact by immutable designator and one stable Clause locator. The defining artifact and identified Clause own meaning. A registry entry, summary, corpus case, publication route, or mutable web response shall not repeat, replace, widen, or narrow that meaning.

Registry snapshots are immutable exact-edition artifacts. A mutable latest route may support discovery, new-authoring policy, or current security notice, but it shall not determine replay meaning, replace preserved exact material, or authorize successor, predecessor, or alias substitution.

A registry snapshot is replay-relevant only when an owning exact BELGI specification declares that exact snapshot to be replay-relevant and it is preserved in accordance with Parts 1 and 2. By default, replay-relevant material binds the exact defining artifact directly rather than the whole registry snapshot.

The registry companion, registry artifacts, and this Part are members of one coherent draft family. A semantic document shall not embed a same-family registry-snapshot digest that would create a content-digest cycle. The external registry inventory binds registry artifacts after the coherent source bytes are closed.

Signer-key compromise and signer-key revocation are trust-profile and operator-policy concerns. They do not alter identifier allocation status, algorithm meaning, verification-method meaning, or the cryptographic result of signature verification.

## 12 Publication and dependency rules

### 12.1 General

Profile and companion publication shall make replay-relevant dependencies explicit.

### 12.2 Exact dependency declaration

If replay-relevant interpretation depends on a profile, companion specification, governing specification, determining-semantics source, or other referenced source, that dependency shall be declared by exact edition.

### 12.3 External specifications

A profile or companion specification may reference material published outside the BELGI family.

If such material is replay-relevant, the profile or companion specification shall reference it with exact-edition and locator information from which the replay package can preserve its immutable designator in accordance with Part 2.

### 12.4 Change-control visibility

A profile or companion specification shall identify the owning publisher or other change controller responsible for issuing new editions.

## 13 Conformance

### 13.1 Conformance classes

The following conformance classes are defined:

- BELGI Profile Specification;
- BELGI Companion Specification;
- BELGI Profile-aware Producer;
- BELGI Profile-aware Verifier;
- BELGI Full Part 3 Implementation; and
- BELGI Full Implementation.

For the purposes of 13.4 and 13.5, a replay-relevant companion dependency referenced without profile mediation is governed by the same producer and verifier obligations that apply to replay-relevant profile dependencies.

### 13.2 BELGI Profile Specification

A specification conforms to this document as a BELGI Profile Specification if it:

- satisfies the profile requirements of Clause 7;
- uses only the reserved extension points of Clause 8;
- does not violate the prohibitions of Clause 9;
- if it declares verdict-level interoperability, does so in accordance with 9.8;
- if it declares verdict-level interoperability, publishes each exact-edition corpus and each machine-checkable conformance procedure required by 9.8;
- for an initial published edition, states that no predecessor compatibility declaration applies in accordance with Clause 10;
- allocates and uses identifiers in accordance with Clause 11 and the Identifier and registry governance companion; and
- follows the identifier and publication rules of Clauses 11 and 12.

### 13.3 BELGI Companion Specification

A specification conforms to this document as a BELGI Companion Specification if it:

- satisfies the companion-specification requirements of Clause 7;
- uses only the reserved extension points of Clause 8;
- does not violate the prohibitions of Clause 9;
- for an initial published edition, states that no predecessor compatibility declaration applies in accordance with Clause 10;
- allocates and uses identifiers in accordance with Clause 11 and the Identifier and registry governance companion; and
- follows the identifier and publication rules of Clauses 11 and 12.

### 13.4 BELGI Profile-aware Producer

An implementation conforms to this document as a BELGI Profile-aware Producer if it:

- preserves the exact profile and companion dependencies on which its replay-relevant declarations depend;
- emits only extension terms and declarations authorized by the selected profile and companion editions; and
- does not rely on hidden default profile selection or undeclared profile assumptions.

### 13.5 BELGI Profile-aware Verifier

An implementation conforms to this document as a BELGI Profile-aware Verifier if it:

- identifies exact profile and companion editions from preserved material;
- applies only the semantics declared by those exact editions;
- treats registry, discovery, publication, and local resolver material as discovery aids only unless that material is itself exact-edition replay-relevant material preserved in accordance with Parts 1 and 2;
- when a selected profile declares verdict-level interoperability, interprets that declaration only according to the clauses, declarations, companion dependencies, referenced sources, and conformance artifacts identified by the exact selected profile edition;
- does not claim conformance to that profile's verdict-level interoperability declaration unless it also satisfies each exact-edition corpus and each machine-checkable conformance procedure identified by that profile;
- does not silently substitute a different edition for replay; and
- rejects or fails closed on extension material that violates Clause 9 or lacks exact replay-relevant identification.

### 13.6 BELGI Full Part 3 Implementation

An implementation conforms to this document as a BELGI Full Part 3 Implementation if it conforms to 13.4 and 13.5.

### 13.7 BELGI Full Implementation

An implementation conforms to the BELGI family as a BELGI Full Implementation if it:

- conforms to BELGI - Part 1: Core semantic model as a BELGI Replay Semantic Implementation in accordance with Part 1, 12.3;
- conforms to BELGI - Part 2: Claim carriers and replay package as a BELGI Full Part 2 Implementation in accordance with Part 2, 14.5; and
- conforms to this document as a BELGI Full Part 3 Implementation in accordance with 13.6.

### 13.8 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the specification or implementation;
- the document title;
- the document version;
- the conformance class claimed;
- each profile identifier and companion identifier on which the claim depends;
- whether any identified profile declares verdict-level interoperability;
- for each identified profile that declares verdict-level interoperability, the exact editions of each finite corpus and each machine-checkable conformance procedure by which that declaration is satisfied;
- for a claim of BELGI Full Implementation, the exact editions of BELGI Parts 1, 2, and 3 against which the claim is made;
- each exact edition or immutable designator required for replay-relevant use, or state that none is used;
- each exact registry snapshot made replay-relevant by the governing exact specifications, or state that none is used; and
- the date of the statement.

## 14 Security and trust considerations

Profiles and companion specifications create extension-integrity risks. Hidden upgrades, reused identifiers, undeclared dependencies, mutable external references, identifier-equivalence confusion, and presentation text carrying silent semantics can all cause replay divergence while preserved material remains syntactically continuous.

This document reduces those risks by requiring exact edition binding, explicit extension points, stable identifiers, explicit no-predecessor publication statements for initial editions, and fail-closed handling of undeclared or incompatible extension material.

Identifier-equivalence confusion can arise when short names, predecessor or successor references, family identifiers, redirects, normalized URI forms, or mutable locators are treated as if they were exact replay-relevant identifiers. Clauses 6, 10, and 11 prevent that by separating discovery metadata from exact string identity and exact edition binding.

Dependency confusion can arise when two different publishers issue materially different companion specifications under similar titles, labels, or discovery paths. Clauses 7, 11, and 12 require exact identification, change-control visibility, and reference precision for replay-relevant use.

Registry poisoning can arise when a registry, mutable latest view, discovery service, package index, local resolver, branch, tag, or publication URL supplies a different profile, companion, corpus, procedure, or determining-semantics source than the one bound by preserved replay-relevant material. Clauses 6.3, 10.2, 11.2, 11.5, 12, and 13.5 keep discovery separate from replay authority and require fail-closed handling of inconsistent exact-edition material.

Compatibility substitution can arise when family membership or publication-time compatibility language is treated as replay substitution permission. Clause 10 keeps that material from being interpreted as silent permission to replay against a different exact edition.

Interoperability-declaration substitution can arise when a declared verdict-interoperability corpus or machine-checkable conformance procedure is silently replaced, widened, or interpreted under a different exact edition. Clauses 9.8, 12, and 13 require exact-edition identification and fail-closed handling of that material for replay-relevant use.

Presentation-text substitution can arise when examples, prose, or filenames are allowed to carry indispensable meaning outside the identified replay-relevant sources. Clauses 6 and 9 prohibit that pattern.

This document does not require preservation of personal identifiers. When replay-relevant profile material, companion material, or extension vocabularies incidentally contain personal data, applicable privacy obligations apply independently of this document.

Profile identifiers, companion identifiers, dependency locators, publication metadata, and change-controller information can create correlation or metadata-leakage risk when reused across claims, packages, or transport contexts. Clauses 6, 11, and 12 confine normative authority to exact-edition identified sources and keep discovery or publication material from silently widening replay-relevant disclosure. Data minimization, pseudonymization, transport confidentiality, and disclosure policy remain obligations outside this document.

This document does not define user-facing interfaces, locale-sensitive rendering, or natural-language presentation requirements. Accessibility and internationalization obligations therefore arise only in implementations, registries, or companion surfaces that present BELGI material to users.

Excluded reliance claim: this document does not establish external suitability, safety, or organizational acceptance of a profile, companion specification, or evaluator.
