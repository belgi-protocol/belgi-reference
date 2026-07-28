# BELGI - Part 4: Software change admission profile

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications; BELGI - Companion specification: Package integrity anchor verification
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is Part 4. It defines one generic BELGI profile for software change admission over repository-based software change workflows.

This document is a member of the coherent `spec-0.5` Working Draft family.
The exact `spec-0.4` source edition remains immutable and is not replaced by
this source.

## Introduction

Parts 1 to 3 fix the semantic core, the replay-package layer, and the extension-governance layer of BELGI.

Software change admission still requires domain choices that those parts intentionally leave open. A software admission claim needs a judged-object pattern for source changes, a vocabulary for evidence kinds, a way to classify evidence sources and execution contexts, and a profile-level rule for when environment differences matter to replay.

This document makes those choices at the generic software-change level. It is not tied to one forge, one repository host, one build system, one CI system, one programming language, or one deployment platform.

This document also keeps the boundary with Parts 1 to 3 explicit. It does not reopen the semantic core, replace the replay package, or define representation-specific schemas. It fixes only the profile-level vocabulary and constraints needed to use BELGI for software change admission.

This document specifies one BELGI software-change profile for verdict replay. It is not an attestation framework, a generic provenance framework, or a registry for external supply-chain ecosystems, although preserved provenance or attestation records may appear as evidence under the constraints of this profile.

This document states profile-level vocabulary, declaration, and conformance obligations. It does not by itself supply a general proof calculus for cross-implementation equivalence over all claims using this profile.

This Working Draft also defines one finite, language-neutral
review-record evaluator. That evaluator is a bounded Part 4 determining
semantics source; it does not add a carrier schema, a replay-procedure token,
or a verdict-level interoperability declaration.

## 1 Scope

This document defines a BELGI profile for software change admission.

This document defines:

- the profile identity and dependency declaration for this profile;
- the judged-object pattern for software change proposals and baseline revisions;
- a minimum evidence vocabulary for software change admission;
- a minimum condition vocabulary for software change admission;
- trust-boundary and environment-envelope vocabulary for software change admission;
- evidence-condition binding relation kinds for software change admission;
- replay-policy refinements for software change admission;
- one finite review-record evaluator over closed logical records and
  exact-edition-local declaration parameters; and
- Part 4 conformance classes.

This document is applicable to preserved admission claims about software changes whose proposal, baseline, evidence, evaluator declarations, and replay dependencies are intended to be preserved and replayed under BELGI.

This document does not define:

- one repository-hosting service, one workflow engine, one CI system, one programming language, or one deployment platform;
- an attestation framework, generic provenance framework, or generic registry for external supply-chain ecosystems;
- one universal set of mandatory go conditions for every software project;
- live operational-action admission, live command execution authorization, or runtime interception of tool calls or API calls;
- representation-specific schemas, serialization bindings, or machine-readable schema dialects;
- a new carrier role, schema role, generic replay procedure, or global
  identifier allocation;
- organizational approval policy, staffing policy, merge authority, or release authority; or
- whether a particular evaluator, profile, or software project satisfies organizational acceptance criteria.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.5, 2026-07-21
- BELGI - Companion specification: Package integrity anchor verification, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in BELGI - Part 1, BELGI - Part 2, BELGI - Part 3, and the following apply.

### 3.1 software change proposal

proposed modification to one or more source-controlled software artifacts intended for evaluation against one baseline revision

### 3.2 baseline revision

identified source revision against which a software change proposal is interpreted

### 3.3 source state

identified preserved or recoverable software source snapshot used to determine either the proposal, the baseline, or both

### 3.4 evidence artifact

Part 1 evidence item preserved as a result, record, or statement from which part of an evidence state for software change admission is recovered

### 3.5 evidence source class

profile-defined class identifying the kind of source or execution context from which one evidence artifact or judged-object dependency originates

### 3.6 execution environment

software or platform context in which relevant build, test, analysis, or review-support activity is performed

### 3.7 required condition

declared go condition that a conforming evaluator carrier using this profile treats as in scope for supporting admission of the relevant claim

### 3.8 exact evidence reference

replay-relevant designation identifying one preserved evidence artifact or one replay-relevant member from which that evidence artifact is recovered

### 3.9 decisive binding

declared evidence-condition binding with identifier `belgi.software-change.binding.satisfies` that designates evidence required as input to the determining semantics of one declared condition

### 3.10 required evidence

evidence designated by the decisive bindings and replay-relevant interpretation rules as necessary to determine whether a required condition is satisfied for the relevant claim

### 3.11 environment envelope

declared set of replay-relevant environment facts by which evidence production, evidence interpretation, evaluator induction, or verdict derivation can depend on repository, execution-environment, platform, toolchain, dependency-state, configuration-input, or comparable context

### 3.12 finite review-record evaluator

Part 4 evaluator selected by the exact-source and declaration constraints of
12.6, induced from evaluator-carrier declarations under 9.5, 10.8, and 11.5,
and applied to judged objects and evidence states independently induced under
7.5 and 8.5

## 4 Symbols and abbreviated terms

### 4.1 Symbols

No symbols are listed in this document.

### 4.2 Abbreviated terms

| Abbreviation | Meaning |
| --- | --- |
| CI | continuous integration |

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 15 are normative unless stated otherwise.

This document owns only the profile-level vocabulary and constraints defined in Clauses 6 to 12. It does not alter the semantic authority of Part 1, the replay authority of Part 2, or the extension-governance authority of Part 3.

## 6 Profile identity and declaration

### 6.1 Profile identifier and version designator

The profile identifier of this profile is:

`https://belgi.dev/ids/profile/software-change-admission`

The current draft version designator is:

`0.5`

The owning publisher or change controller of this profile is:

`belgi`

The compact identifier tokens defined by this profile are partitioned into the
following named vocabularies:

```text
evidence-kind | condition | boundary-participation | authority-level |
evidence-source-class | environment-envelope |
evidence-condition-binding-kind | evaluator-declaration-parameter |
replay-policy | review-decision
```

The namespace identity of each vocabulary is the ordered pair of the profile
identifier in 6.1 and the vocabulary name above. Within each namespace, tokens
shall be compared as exact strings without case folding, Unicode normalization,
whitespace trimming, prefix expansion, or other normalization. No two meanings
may share one token in the same namespace. Once assigned, a token shall not be
reassigned a different meaning by a later edition of this profile family, and
retirement or removal shall not make it available for reassignment. Each token
remains subordinate to its exact defining edition and is not globally reusable
without its named namespace and exact-edition context.

Stable local requirement identifiers beginning with `P4-FE-` label the finite
evaluator requirements in this source for traceability into machine-readable
material. The `P4-FE-` prefix is reserved to this Part family, and a retired
`P4-FE-*` requirement identifier shall never be reused. A requirement
identifier is structural traceability metadata: it is not a semantic selector
and shall not substitute for its requirement text or the exact determining
source required by 12.6.

### 6.2 BELGI dependency declaration

This profile, the BELGI Parts, and the companion specification named in Clause
2 are members of the coherent `spec-0.5` Working Draft family.

### 6.3 Selected companions

This `0.5` Working Draft selects the Package integrity anchor verification
companion in the same coherent `spec-0.5` family as a mandatory companion
specification. A claim using that companion shall
preserve its exact materialized edition by immutable designator; the family
reference in Clause 2 is not a substitute for that replay binding.

A replay-relevant evaluator using this profile may additionally depend on exact editions of companion specifications in accordance with BELGI - Part 3, 12.2, provided that those dependencies are declared and preserved in accordance with BELGI - Part 2, 9.6.

Clause 10.4 states the conditions under which CI-originated material may be authoritative under this profile.

NOTE The mandatory companion selected in this clause governs the exact-edition package-integrity-anchor verification surface required by BELGI - Part 2. When Clause 10.4 is relied upon to treat CI-originated material as authoritative, an additional exact-edition CI-oriented companion or other BELGI normative dependency can also become operationally necessary for that claim.

### 6.4 Reserved extension points used

This profile uses the following reserved extension points of BELGI - Part 3:

- 8.2 judged-object carrier vocabulary and constraints;
- 8.3 evidence vocabulary and evidence kinds;
- 8.4 condition vocabulary;
- 8.5 trust-boundary vocabulary;
- 8.7 evidence-condition binding kinds;
- 8.8 environment-envelope vocabulary;
- 8.9 evaluator declaration parameter vocabulary;
- 8.10 replay-policy refinements.

### 6.5 Compatibility statement

This `0.5` Working Draft succeeds exact `0.4`. This profile declares no
backward compatibility, forward compatibility, or replay substitution with
its predecessor.

BELGI - Part 3, Clause 10 defines no successor-edition compatibility classes for the current draft family.

### 6.6 Mandatory and optional profile declarations

For replay-relevant material governed by this draft, the material shall make explicit, at minimum:

- preservation or resolution of one software change proposal and one baseline revision as required by Clause 7;
- each exact-edition governing or determining-semantics source on which replay-relevant interpretation depends;
- the evidence vocabulary used for the claim, as required by Clause 8; and
- the condition vocabulary, trust-boundary vocabulary, environment-envelope vocabulary, and decisive evidence-condition binding material used for the claim, as required by Clauses 9 to 11.

When a producer or verifier makes a Part 4 conformance claim, the claim material shall also make explicit:

- use of the profile identifier in 6.1;
- the exact edition of this profile by immutable designator in accordance with BELGI - Part 3, 12.2 and BELGI - Part 2, 9.6;
- the exact edition of the mandatory companion selected in 6.3;
- each exact-edition companion source on which replay-relevant interpretation depends; and
- one replay policy defined by Clause 12.

The replay-relevant material may additionally make explicit:

- additional evidence kinds that do not contradict Clause 8;
- additional condition identifiers that do not contradict Clause 9; and
- additional replay-relevant parameters that do not contradict Clauses 9 to 12.

### 6.7 Interoperability status

This profile edition does not declare verdict-level interoperability under BELGI - Part 2, 12.5 or BELGI - Part 3, 9.8.

Implementations using this profile remain subject to the replay conformance requirements of BELGI - Part 2, 12.4. They shall not present implementation-local corpora, procedures, report projections, or diagnostic material as a cross-implementation verdict-agreement obligation of this profile edition.

### 6.8 Reference-validation material

Reference implementations may publish implementation-local corpora, procedures, report projections, and worked examples for regression validation. Such material is not conformance material of this profile edition and does not establish independent-implementation agreement.

Clause 12.9 identifies finite reference-validation material for the evaluator
defined by 12.6 and 12.7. That material has the same non-conformance and
non-interoperability status.

## 7 Judged-object profile

### 7.1 General

For this profile, the judged object is one software change proposal plus one baseline revision.

The software change proposal induces the Part 1 admission subject. The baseline revision induces the Part 1 reference context. These are the two components of the judged object; this profile does not introduce another top-level semantic input sort.

The mapping shall be deterministic from replay-relevant material. Admission subjects under this profile are equal exactly when the proposal identifiers, recovered proposed-change semantics, and any declared identity-bearing repository or source namespaces assigned to the proposal are equal. Reference contexts are equal exactly when the baseline revision identities, resolved source states, and any declared identity-bearing repository or source namespaces assigned to the baseline are equal. A difference in any participating value makes the corresponding component unequal; a carrier or wrapper difference that changes none of those values does not change the judged object.

### 7.2 Proposal constraints

A conforming judged-object carrier using this profile shall preserve or resolve, at minimum:

- one proposal identifier;
- one baseline revision identifier; and
- replay-relevant material from which the proposed software change relative to the baseline revision is determined.

The judged-object carrier may preserve a patch set, a merge-request snapshot, a tree delta, a preserved source snapshot, or another equivalent representation.

### 7.3 Baseline-revision constraints

A baseline revision under this profile shall identify one source state by stable revision identifier, digest-bound source snapshot, tree identifier, archive identifier, or another immutable source-state designator.

If the baseline revision is represented indirectly, the replay package shall preserve replay-relevant material from which it is resolved under the declared replay policy.

### 7.4 Source-state recovery boundary

Proposal recovery and baseline recovery under this profile shall not depend on undeclared repository state, mutable branch heads, late external checkout against floating references, or other undeclared ambient context.

Any repository identity, source-control namespace, or equivalent source context needed to identify or interpret the software change proposal or baseline revision shall participate in the corresponding judged-object component. An environment-envelope declaration shall not substitute for that component material.

Whether such context participates in admission-subject identity, reference-context identity, or both, and its semantic projection, shall be fixed by this profile or by an exact-edition governing or determining-semantics source declared under 6.6. It shall not be selected by implementation-local convention.

### 7.5 Finite review-record judged-object subset

Judged-object lifting under this exact Part 4 finite logical-record mapping
shall process the judged-object carrier independently of the evaluator carrier
and its condition declarations. Generic content-location and source recovery
shall complete under 7.2 to 7.4 and BELGI - Part 2 before the following logical
records are induced:

```text
ProposalRecord {
  proposalIdentifier: non-empty exact string,
  proposedSourceStateIdentifier: non-empty exact string
}

BaselineRecord {
  baselineRevisionIdentifier: non-empty exact string,
  baselineSourceStateIdentifier: non-empty exact string
}
```

The `ProposalRecord` induces the Part 1 admission subject. Two admission
subjects in this finite subset are equal exactly when both corresponding
members are equal under the exact-string rule of 9.5. The `BaselineRecord`
induces the Part 1 reference context. Two reference contexts in this finite
subset are equal exactly when both corresponding members are equal under that
same rule.

Each record is closed. A missing or extra member, a null or wrong-type member,
an empty string, or an attempted coercion makes $\lambda_J$ undefined. The
source-state identifiers are equality keys only after the source-recovery
obligations of 7.2 to 7.4 have completed; an identifier shall not substitute
for recovery of the source state it identifies.

This induction-failure rule applies to resolved carrier material governed by
the finite logical-record mapping. It shall not turn an already valid judged
object in $J$ outside this finite subset into a lift failure. The evaluator of
12.7 returns verdict `0` for such a valid judged object only after all three
lifts succeed and replay reaches evaluator application.

Requirement identifier: `P4-FE-002`. This identifier governs the closed
judged-object records in this subclause and the closed evidence record in 8.5.

## 8 Evidence vocabulary and evidence-state constraints

### 8.1 General

This profile defines the following minimum local compact evidence-kind tokens for software change admission.

### 8.2 Minimum evidence kinds

| Evidence kind identifier | Meaning |
| --- | --- |
| `belgi.software-change.evidence.build-result` | preserved result of a build or packaging activity |
| `belgi.software-change.evidence.test-result` | preserved result of automated test execution |
| `belgi.software-change.evidence.coverage-result` | preserved result expressing exercised code or behavior coverage |
| `belgi.software-change.evidence.static-analysis-result` | preserved result of static security, quality, or defect analysis |
| `belgi.software-change.evidence.dependency-analysis-result` | preserved result of dependency, vulnerability, or policy analysis |
| `belgi.software-change.evidence.review-record` | preserved human or automated review statement or decision record |
| `belgi.software-change.evidence.provenance-record` | preserved provenance, attestation, or origin record for replay-relevant activity or artifacts |
| `belgi.software-change.evidence.environment-record` | preserved record describing the execution environment relevant to evidence interpretation |

A conforming use of this profile may define or use additional evidence kinds only when they do not contradict BELGI - Part 1, BELGI - Part 2, BELGI - Part 3, or this profile.

### 8.3 Evidence-state sufficiency

A conforming evidence-state carrier using this profile shall preserve replay-relevant content identifying one or more evidence artifacts of the kinds defined in 8.2 or additional kinds that do not contradict Clause 8, from which the evidence state is constructed.

### 8.4 Negative evidence and absence of evidence

Evidence showing that a declared condition does not hold shall be preserved as evidence of the relevant kind rather than omitted from the preserved evidence state.

Absence of required evidence shall not be treated as satisfaction of a declared condition.

### 8.5 Finite review evidence record

Evidence-state lifting under this exact Part 4 source shall process the
evidence-state carrier independently of the evaluator carrier and its
bindings. Every evidence item is keyed by one arbitrary non-empty exact
evidence identifier.

When any evidence item declares evidence kind
`belgi.software-change.evidence.review-record`, its resolved source shall
induce exactly the following closed logical record:

```text
ReviewRecord {
  reviewIdentifier: non-empty exact string,
  proposalIdentifier: non-empty exact string,
  proposedSourceStateIdentifier: non-empty exact string,
  baselineRevisionIdentifier: non-empty exact string,
  baselineSourceStateIdentifier: non-empty exact string,
  decision: accepted | rejected
}
```

The `decision` member tokens `accepted` and `rejected` are exact-edition-local
compact identifiers in the `review-decision` vocabulary named by 6.1. Their
meanings are the accepted and rejected review outcomes used by
`reviewPolicySatisfied` in 12.7.

The evidence kind is declared outside the resolved `ReviewRecord`; the record
shall not contain a redundant payload kind. It shall also contain no reviewer
identity, timestamp, freshness value, or self-authored participation or
authority field. A missing or extra member, a null or wrong-type member, an
empty identity string, an attempted coercion, or a decision other than the
exact token `accepted` or `rejected` makes $\lambda_E$ undefined. Every such
review item shall also satisfy the declaration-parameter grammar of 9.5.

An evidence item whose evidence kind is another token defined by 8.2, or by an
applicable exact-edition source governing evidence-state lifting, remains valid
evidence without being interpreted as a `ReviewRecord`. An evidence item whose
evidence-kind token has no such exact owning source makes $\lambda_E$
undefined.

Only after $\lambda_E$ has independently induced the evidence state does the
evaluator of 12.7 look up the common decisive evidence identifier from 11.5.
If that identifier is absent, finite evaluation succeeds with verdict `0`. A
successfully induced unbound auxiliary evidence item, including a well-formed
unbound review record, is ignored by the finite evaluator and cannot repair,
replace, or change the bound item. Generic representation validity alone does
not excuse a malformed item that declares the exact Part 4 review-record kind;
such an item makes $\lambda_E$ undefined even when no evaluator binding
references it.

The requirement identifier for this subclause is `P4-FE-002` as declared in
7.5.

## 9 Condition vocabulary and evaluator-declaration constraints

### 9.1 General

This profile defines the following generic local compact condition tokens for software change admission.

Use of this profile does not require every evaluator to use every identifier in 9.2.

### 9.2 Generic condition identifiers

| Condition identifier | Meaning |
| --- | --- |
| `belgi.software-change.condition.change-basis-resolved` | the proposal and the baseline are identified by replay-relevant material from which replay resolves the source states under the declared replay policy |
| `belgi.software-change.condition.required-evidence-present` | the evidence required by the declared bindings is present and interpretable |
| `belgi.software-change.condition.build-policy-satisfied` | build or packaging results satisfy the declared policy for admission |
| `belgi.software-change.condition.test-policy-satisfied` | automated test results satisfy the declared policy for admission |
| `belgi.software-change.condition.coverage-policy-satisfied` | coverage results satisfy the declared coverage policy for admission |
| `belgi.software-change.condition.review-policy-satisfied` | preserved review material satisfies the declared policy for admission |
| `belgi.software-change.condition.dependency-policy-satisfied` | dependency-related results satisfy the declared policy for admission |
| `belgi.software-change.condition.analysis-policy-satisfied` | static or comparable analysis results satisfy the declared policy for admission |
| `belgi.software-change.condition.environment-compatibility-satisfied` | the declared environment envelope is compatible with the evidence and evaluator material relied on for admission |

### 9.3 Required evaluator declarations

A conforming evaluator carrier using this profile shall:

- declare `belgi.software-change.condition.change-basis-resolved`;
- declare `belgi.software-change.condition.required-evidence-present`;
- declare at least one additional go condition: either another identifier from 9.2, excluding `belgi.software-change.condition.change-basis-resolved` and `belgi.software-change.condition.required-evidence-present`, or an exact-edition companion condition identifier whose meaning refines, and does not contradict, one of the identifiers in 9.2;
- if preserved evidence material or evaluator material carries replay-relevant environment-envelope terms or an environment-equivalence basis under Clause 10, declare `belgi.software-change.condition.environment-compatibility-satisfied`;
- declare the parameters, thresholds, rule references, or severity criteria required to interpret each declared condition;
- declare the decisive evidence-condition bindings by which each required condition is satisfied under this draft's evaluator rules; and
- in accordance with BELGI - Part 2, 9.6 and BELGI - Part 3, 12.2, declare any exact-edition companion, governing, or determining-semantics source on which replay-relevant interpretation depends.

An exact-edition companion condition identifier shall not be used under this profile unless that exact-edition companion specification explicitly identifies the identifier in 9.2 whose meaning it refines.

### 9.4 Condition-set selection rule

This profile defines no scoped-exception kind and no condition-suspension surface.

Policy variation under this profile shall be expressed only by:

- selection of the declared condition set;
- selection of exact-edition companion condition identifiers that refine identifiers in 9.2; and
- declaration of the parameters, thresholds, rule references, or severity criteria required to interpret those declared conditions.

A conforming evaluator carrier under this profile shall not suspend or waive `belgi.software-change.condition.change-basis-resolved`, `belgi.software-change.condition.required-evidence-present`, or any other declared condition through a separate exception mechanism.

### 9.5 Finite evaluator declaration-parameter vocabulary

This profile defines the following exact-edition-local compact tokens in the
`evaluator-declaration-parameter` vocabulary for the finite review-record
evaluator:

| Parameter identifier | Meaning |
| --- | --- |
| `belgi.software-change.parameter.evidence-source-class` | classifies the preserved source regime of one evidence item |
| `belgi.software-change.parameter.boundary-participation` | declares whether one evidence source class participates in evaluator reliance |
| `belgi.software-change.parameter.authority-level` | declares the authority level of one included evidence source class |

At the induced logical level, every evidence item that declares the exact Part
4 review-record kind shall have exactly one declaration parameter. Its
parameter identifier shall be
`belgi.software-change.parameter.evidence-source-class`, and its value shall be
exactly one evidence-source-class token defined by 10.3. A missing, duplicate,
unknown, or wrong-type parameter, an unknown source-class token, or any
additional parameter makes $\lambda_E$ undefined. A recognized 10.3 source
class other than `belgi.software-change.source.review-system` is valid but
cannot satisfy the finite evaluator; if referenced decisively, it therefore
yields verdict `0`.

Each of the three declared conditions selected by 12.6 shall have an exactly
empty parameter array. Every decisive binding admitted by 11.5 shall also have
an exactly empty parameter array. A non-empty array in either location makes
$\lambda_F$ undefined.

Raw evidence shall not declare its own boundary participation or authority
level. Those declarations belong only to the evaluator-carrier trust-boundary
map and are constrained by 10.8.

Every token and identity governed by the finite evaluator shall be compared,
after representation decoding, as an exact sequence of Unicode scalar values.
Case folding, Unicode normalization, whitespace trimming, URI or path
normalization, prefix expansion, platform-specific name rules, and
implementation aliases are prohibited. Tokens in the
`belgi.reference-profile.parameter.*` family are not aliases for the three
parameter identifiers defined here and shall not be imported into this
vocabulary.

These rules constrain the logical values admitted by the existing generic
carrier structures. They define no serialized field, representation schema,
schema role, registry entry, or procedure token.

Requirement identifier: `P4-FE-003`. This identifier governs this parameter
grammar and the trust-declaration grammar in 10.8.

## 10 Trust-boundary and environment-envelope profile

### 10.1 General

This profile requires explicit declaration of both trust-boundary material and environment-envelope material whenever those declarations participate in evidence interpretation, evaluator induction, or replay.

Where preserved evidence material or evaluator material carries replay-relevant environment-envelope terms or an environment-equivalence basis under this clause, the evaluator carrier shall declare `belgi.software-change.condition.environment-compatibility-satisfied` in accordance with 9.3.

### 10.2 Boundary participation and authority levels

#### 10.2.1 Boundary participation

| Boundary participation identifier | Meaning |
| --- | --- |
| `belgi.software-change.boundary-participation.included` | may participate in evaluator determination for the claim and shall therefore be assigned an authority level under 10.2.2 |
| `belgi.software-change.boundary-participation.excluded` | lies outside evaluator reliance for the claim |

#### 10.2.2 Authority levels for included material

| Authority level identifier | Meaning |
| --- | --- |
| `belgi.software-change.authority.authoritative` | may be relied upon directly by the evaluator for one or more declared conditions |
| `belgi.software-change.authority.non-authoritative` | may be preserved or examined but does not satisfy conditions by itself |

### 10.3 Evidence-source classes

| Evidence source class identifier | Meaning |
| --- | --- |
| `belgi.software-change.source.repository-system` | source regime supplying repository state, repository object identity, or repository-hosted material |
| `belgi.software-change.source.review-system` | source regime supplying preserved review material |
| `belgi.software-change.source.ci-execution` | automated execution regime producing build, test, coverage, or analysis evidence |
| `belgi.software-change.source.artifact-store` | source regime supplying replay-relevant artifact custody, digest-bound artifact identity, or artifact-origin linkage |
| `belgi.software-change.source.dependency-advisory-service` | source regime supplying dependency, vulnerability, or policy intelligence |
| `belgi.software-change.source.developer-workspace` | local interactive workspace outside controlled automation |
| `belgi.software-change.source.external-analysis-service` | external hosted analysis or scanning regime |

### 10.4 Boundary-participation and authority rules

A conforming evaluator carrier using this profile shall assign every replay-relevant evidence source or execution context:

- one evidence source class from 10.3 or one evidence source class defined by an exact-edition companion whose meaning refines, and does not contradict, one of the classes in 10.3; and
- one boundary-participation identifier from 10.2.1.

If the assigned boundary participation is `belgi.software-change.boundary-participation.included`, the carrier shall also assign one authority level from 10.2.2.

A companion source-material-role identifier shall not replace the generic evidence source class required by the first bullet. Such an identifier may be declared only in addition to that generic class.

A declared evidence source class under 10.3 classifies the preserved source regime that gives the material its replay-relevant meaning. The last upload, download, export, retrieval, or attachment hop shall not by itself determine that class.

Material attached, uploaded, exported, or otherwise transported into the replay package that still preserves one of the source regimes of 10.3 shall be classified by that preserved regime. Material that does not preserve the replay-relevant identifiers required by the applicable authority rule for another source regime in this clause may be preserved under this profile only with boundary participation `belgi.software-change.boundary-participation.excluded`.

Material assigned boundary participation `belgi.software-change.boundary-participation.excluded` shall not be used as a decisive evaluator binding and shall not otherwise affect determination of a declared condition.

Material whose declared evidence source class is `belgi.software-change.source.repository-system` shall not be authoritative unless replay-relevant material preserves repository identity and at least one immutable repository object identifier, revision identifier, or source-state identifier sufficient to recover the asserted repository fact.

Material whose declared evidence source class is `belgi.software-change.source.review-system` shall not be authoritative unless replay-relevant material preserves stable review object identity and the replay-relevant decision state on which the asserted review fact depends.

Material whose declared evidence source class is `belgi.software-change.source.artifact-store` shall not be authoritative unless replay-relevant material preserves digest-bound artifact identity and origin linkage from which replay determines the asserted custody, retrieval, or artifact-origin fact.

Material whose declared evidence source class is `belgi.software-change.source.dependency-advisory-service` shall not be authoritative unless replay-relevant material preserves the advisory source or dataset identity and the advisory, vulnerability, dependency, or package anchor on which the asserted dependency-advisory fact depends.

Material whose declared evidence source class is `belgi.software-change.source.developer-workspace` shall not be authoritative for `belgi.software-change.condition.build-policy-satisfied`, `belgi.software-change.condition.test-policy-satisfied`, `belgi.software-change.condition.coverage-policy-satisfied`, `belgi.software-change.condition.analysis-policy-satisfied`, or `belgi.software-change.condition.dependency-policy-satisfied` under this profile.

Material whose declared evidence source class is `belgi.software-change.source.ci-execution` shall not be authoritative for `belgi.software-change.condition.build-policy-satisfied`, `belgi.software-change.condition.test-policy-satisfied`, `belgi.software-change.condition.coverage-policy-satisfied`, `belgi.software-change.condition.analysis-policy-satisfied`, `belgi.software-change.condition.dependency-policy-satisfied`, or comparable automated-admission conditions unless replay-relevant material depends on an exact-edition CI-oriented companion or other BELGI normative dependency. That dependency shall be preserved in accordance with BELGI - Part 2 and shall fix the CI run identity, workflow-definition identity, immutable source reference, artifact-origin linkage, and relevant CI environment-envelope material.

Dashboard badges, check-run conclusions, job summaries, aggregate statuses, artifact URLs, filenames, cache keys, storage locations, or package member names shall not by themselves make CI-originated or artifact-store material authoritative under this clause.

NOTE The companion family identified by `https://belgi.dev/ids/companion/ci-trust-boundary-vocabulary` defines CI-specific source-material-role and environment-envelope terms. A claim that depends on those terms binds an exact companion edition under 6.6.

Material whose declared evidence source class is `belgi.software-change.source.external-analysis-service` shall not be authoritative unless replay-relevant material preserves the analyzer or service identity and the analysis run, scan, report, finding, or other result identity on which the asserted analysis fact depends.

### 10.5 Environment-envelope minimum content

This profile defines the following generic local compact environment-envelope tokens.

| Environment-envelope identifier | Meaning |
| --- | --- |
| `belgi.software-change.environment.repository-identity` | identifies the repository, source-control namespace, or equivalent source context relevant to evidence interpretation or evaluator induction |
| `belgi.software-change.environment.execution-environment-identity` | identifies the execution environment instance or class relevant to evidence production or evaluator induction |
| `belgi.software-change.environment.platform-identity` | identifies the operating-system, platform, architecture, or comparable platform facts relevant to the claim |
| `belgi.software-change.environment.toolchain-identity` | identifies the runtime, compiler, interpreter, package manager, build tool, or comparable toolchain facts relevant to the claim |
| `belgi.software-change.environment.dependency-state-identity` | identifies the dependency set, lock state, resolved dependency graph, or comparable dependency facts relevant to the claim |
| `belgi.software-change.environment.configuration-input-identity` | identifies configuration, policy, secret-independent input, or comparable replay-relevant inputs that can affect condition evaluation |

An environment envelope under this profile shall declare relevance by membership. An identifier present in the envelope is declared relevant to the claim. An identifier omitted from the envelope is declared not relevant to the claim.

For every identifier declared relevant, the environment envelope shall preserve or resolve the corresponding exact environment fact. The permitted identifiers are:

- `belgi.software-change.environment.repository-identity`;
- `belgi.software-change.environment.execution-environment-identity`;
- `belgi.software-change.environment.platform-identity`;
- `belgi.software-change.environment.toolchain-identity`;
- `belgi.software-change.environment.dependency-state-identity`; and
- `belgi.software-change.environment.configuration-input-identity`.

An identifier declared not relevant shall not be used to interpret evidence, induce the evaluator, determine condition satisfaction, or derive the verdict. If replay-relevant material depends on an identifier omitted from the environment envelope, replay under this profile shall fail closed.

Environment-envelope material of 10.5 shall not be replay-relevant for claim evaluation under this profile unless the evaluator carrier declares `belgi.software-change.condition.environment-compatibility-satisfied`.

If preserved evidence material or evaluator material carries environment-envelope terms or an environment-equivalence basis while that condition is undeclared, this draft's evaluator rules shall fail closed and the claim shall not support go under this profile.

### 10.6 Environment-equivalence rule

Differences in environment facts for identifiers declared relevant under 10.5 shall be treated as replay-relevant.

Such differences shall not be treated as equivalent by silence.

If a producer or verifier treats such differences as equivalent for a declared condition, the basis for that equivalence shall be declared in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2.

### 10.7 Hidden-context prohibition

A conforming evaluator carrier using this profile shall not rely on undeclared repository state, undeclared runner state, undeclared toolchain defaults, undeclared dependency sources, or undeclared external-service responses to interpret evidence, induce the evaluator, determine condition satisfaction, or derive the verdict.

### 10.8 Finite evaluator trust declaration

The trust-boundary map of a finite review-record evaluator shall use only exact
evidence-source-class tokens from 10.3 as keys. An entry relevant to a bound
evidence item is the entry whose key equals that item's declared source class
under 9.5. Absence of such an entry makes
`requiredEvidencePresent` false under 12.7; it does not authorize inference of
a default boundary or authority value.

Each present entry shall have exactly one of these two ordered parameter
arrays:

```text
[
  boundary-participation = included,
  authority-level = authoritative | non-authoritative
]

[
  boundary-participation = excluded
]
```

The parameter identifiers shall be the exact identifiers in 9.5. The values
shall be the corresponding exact tokens from 10.2. An included entry shall
contain the boundary-participation parameter first and exactly one authority
parameter second. An excluded entry shall contain only the
boundary-participation parameter and shall contain no authority parameter.

An unknown map key, parameter identifier, or parameter value; a missing,
duplicate, extra, reordered, or wrong-type parameter; an included entry without
exactly one authority parameter; or an excluded entry with an authority
parameter makes $\lambda_F$ undefined. The evidence item does not assign any
of these evaluator-owned trust declarations.

The requirement identifier for this subclause is `P4-FE-003` as declared in
9.5.

## 11 Evidence-condition binding relation kinds

### 11.1 General

This profile defines the following local compact evidence-condition binding-kind tokens.

For this draft's evaluator rules, `belgi.software-change.binding.satisfies` is the only decisive evaluator binding kind.

`belgi.software-change.binding.supports` and `belgi.software-change.binding.refutes` may be preserved as descriptive carrier or diagnostic material, but they are not decisive binding kinds under this draft and shall not by themselves affect whether a declared condition holds.

### 11.2 Binding relation kinds

| Binding relation kind identifier | Meaning |
| --- | --- |
| `belgi.software-change.binding.satisfies` | designates the evidence artifact as required input to the determining semantics by which the condition is evaluated; the identifier alone does not establish that the condition holds |
| `belgi.software-change.binding.supports` | records a diagnostic assertion that the evidence artifact contributes to the condition without making the artifact a decisive input under this profile |
| `belgi.software-change.binding.refutes` | records a diagnostic assertion that the evidence artifact counts against the condition without making the artifact a decisive input under this profile |

### 11.3 Binding completeness rule

For each required condition, a conforming evaluator carrier using this profile shall define at least one decisive binding with identifier `belgi.software-change.binding.satisfies` to one or more declared evidence kinds, one or more exact evidence references, or both.

A required condition with no applicable decisive `belgi.software-change.binding.satisfies` binding shall not support go under this profile.

### 11.4 Parameter and threshold rule

If satisfaction of a condition under this draft's evaluator rules depends on thresholds, allowlists, deny lists, severity floors, policy identifiers, or other replay-relevant parameters, those parameters shall be declared in replay-relevant evaluator material or exact-edition referenced sources preserved in accordance with BELGI - Part 2.

### 11.5 Finite evaluator decisive-binding grammar

For the finite review-record evaluator, bindings that purport to affect its
three declared conditions shall be grouped only under the exact condition
identifiers selected by 12.6. Under each condition there may be zero or exactly
one decisive binding with kind
`belgi.software-change.binding.satisfies`. Each present decisive binding shall
contain exactly one evidence identifier and the exactly empty parameter array
required by 9.5.

All present decisive bindings shall designate the same evidence identifier.
When all three conditions have one such binding, that identifier is the common
decisive evidence reference used by 8.5 and 12.7. More than one decisive
binding under a condition, more than one evidence identifier in a decisive
binding, a decisive binding under another condition key, inconsistent targets
among present decisive bindings, or a non-empty decisive-binding parameter
array makes $\lambda_F$ undefined.

The binding kinds `belgi.software-change.binding.supports` and
`belgi.software-change.binding.refutes` may be preserved as descriptive
material. They never supply a decisive evidence reference and shall not affect
$Sat$ or the verdict. A binding-kind token not defined by 11.2 and not owned by
an applicable exact-edition source declared under 6.6 makes $\lambda_F$
undefined; another recognized non-decisive binding kind remains irrelevant to
this finite evaluator.

If any required condition has no applicable decisive binding, including when
it has only descriptive bindings, evaluator induction may still succeed. The
condition is false under 12.7 and the total evaluator returns verdict `0`.
Missing decisive input is therefore not a new lift-failure classification.

Requirement identifier: `P4-FE-004`. This identifier governs this binding
grammar and the condition semantics and total evaluator in 12.7.

## 12 Replay-policy refinements

### 12.1 General

This profile defines one local compact replay-policy token for software change admission.

### 12.2 Record-check replay

`belgi.software-change.replay.record-check` is satisfied when:

- all required carriers parse successfully;
- all replay-relevant references resolve within the replay package;
- all integrity bindings required by BELGI - Part 2 verify successfully;
- the lifting procedures of BELGI - Part 2 succeed; and
- replay yields one derived verdict in accordance with BELGI - Part 1, 7.4.

### 12.3 No additional replay-policy refinement

This profile defines no replay-policy refinement beyond `belgi.software-change.replay.record-check` for this version `0.5` Working Draft.

Source-state reconstruction requirements remain governed by Clause 7, the declared condition set of Clause 9, and the source-state recovery boundary of 7.4 rather than by a second replay-policy identifier.

### 12.4 Replay-policy declaration

A replay package making a Part 4 conformance claim shall declare `belgi.software-change.replay.record-check`.

That replay-policy declaration shall be preserved as replay-relevant material in the evaluator carrier.

If evidence interpretation or evaluator induction depends on the environment envelope of Clause 10, the replay package shall preserve the environment-envelope material on which the declared replay policy depends.

### 12.5 Operational-risk boundary

Operational risk introduced, removed, widened, narrowed, or otherwise controlled by a software change may be evaluated under this profile only as evidence or evaluator material concerning the software change proposal against its baseline revision.

This profile shall not treat a live operational action request, live deployment request, live tool call, live infrastructure API call, or comparable runtime operation as the judged object unless that request is represented as a software change proposal governed by Clause 7.

Profiles or companion specifications that evaluate live operational-action admission shall use the extension framework of BELGI - Part 3 without reusing this profile as a runtime-action profile.

### 12.6 Finite evaluator selection and exact source authority

The finite review-record evaluator shall be selected only when all of the
following conditions hold:

1. generic carrier and package processing applicable before evaluator
   induction has succeeded, including complete authenticated claim-record
   validation under BELGI - Part 2, 12.2, steps 1 to 10;
2. the evaluator declares exactly these three go conditions and no others:
   - `belgi.software-change.condition.change-basis-resolved`;
   - `belgi.software-change.condition.required-evidence-present`; and
   - `belgi.software-change.condition.review-policy-satisfied`;
3. each of those conditions contains the exactly empty parameter array
   required by 9.5 and designates the same immutable exact source consisting
   of the bytes of this Part 4 `0.5` Working Draft source as its determining
   semantics;
4. that exact source has resolved and has satisfied every applicable exact
   integrity and representation constraint; and
5. the evaluator declares replay policy
   `belgi.software-change.replay.record-check` as one exact string.

The digest-bound exact Part 4 source, rather than the condition set by itself,
supplies the procedure in 12.7. A requirement identifier, corpus operation,
case label, filename, media type, schema identifier, registry result,
implementation default, alias, or fallback shall not select or replace that
source. Selection shall not be inferred from similar tokens or carrier shape.

When a carrier is evaluated as a candidate for this finite source, a missing,
extra, or substituted condition, an absent or inconsistent determining-source
designator, a non-empty condition parameter array, or a different replay
policy makes $\lambda_F$ undefined. An evaluator governed by other exact Part
4 determining semantics may be valid Part 4 material but is outside this
finite evaluator surface; no implementation fallback or inference is
permitted.

This selection adds no schema, schema role, schema-inventory entry, registry
entry, global identifier, or replay-procedure token. The generic
`judged-object`, `evidence-state`, and `evaluator` carrier roles remain the
only carrier roles used by this procedure.

Requirement identifier: `P4-FE-001`.

### 12.7 Finite condition semantics and total evaluator

For a fixed finite declaration admitted by 12.6 and 11.5, the following is the
language-neutral condition procedure. `review` denotes the common referenced
item only when `requiredEvidencePresent` is true.

```text
requiredEvidencePresent(j, e, declaration) =
    all three conditions have the same applicable decisive evidence reference
    and the referenced evidence item exists
    and the item has evidence kind
        belgi.software-change.evidence.review-record
    and the item has the closed ReviewRecord of 8.5
    and its declared source class is
        belgi.software-change.source.review-system
    and the source-class trust entry has boundary participation
        belgi.software-change.boundary-participation.included
    and that entry has authority
        belgi.software-change.authority.authoritative

changeBasisResolved(j, e, declaration) =
    requiredEvidencePresent(j, e, declaration)
    and review.proposalIdentifier == j.proposalIdentifier
    and review.proposedSourceStateIdentifier
        == j.proposedSourceStateIdentifier
    and review.baselineRevisionIdentifier == j.baselineRevisionIdentifier
    and review.baselineSourceStateIdentifier
        == j.baselineSourceStateIdentifier

reviewPolicySatisfied(j, e, declaration) =
    requiredEvidencePresent(j, e, declaration)
    and review.decision == accepted

f(j, e) = 1 iff
    changeBasisResolved(j, e, declaration)
    and requiredEvidencePresent(j, e, declaration)
    and reviewPolicySatisfied(j, e, declaration)
otherwise 0
```

For the three condition identifiers in 12.6, $Sat(j,e,c)$ shall equal,
respectively, `changeBasisResolved`, `requiredEvidencePresent`, and
`reviewPolicySatisfied` above. `supports` and `refutes` bindings and
successfully induced unbound auxiliary evidence shall not affect any of those
predicates.

The induced evaluator is total on the complete Part 1 domain $J \times E$.
After a semantic tuple has been recovered, it returns verdict `0` for every
input for which the conjunction above is not true, including a valid judged
object outside the finite subset of 7.5. A
false condition, missing decisive input, absent referenced evidence item,
recognized but non-matching evidence kind or source class, excluded or
non-authoritative source, rejected review, or identity mismatch is a derived
no-go verdict rather than an undefined evaluator.

The requirement identifier for this subclause is `P4-FE-004` as declared in
11.5.

### 12.8 Failure, priority, and ambient-context boundary

The finite evaluator shall preserve the following lift-versus-verdict
classifications. A row prescribing a verdict assumes that all three lifts are
otherwise defined and replay reaches evaluator application.

| Defect or state | Required result |
| --- | --- |
| malformed generic representation or carrier | existing Part 2 carrier or representation failure; no finite evaluation |
| unavailable or digest-mismatched exact Part 4 determining source | existing Part 2 dependency or source-resolution failure; no verdict |
| malformed closed `ProposalRecord` or `BaselineRecord` | $\lambda_J$ undefined; no verdict |
| any exact review-record item with a malformed closed `ReviewRecord` or invalid finite evidence parameter grammar | $\lambda_E$ undefined; no verdict, whether or not that item is bound |
| any evidence-kind token without an applicable exact owning source | $\lambda_E$ undefined; no verdict, whether or not that item is bound |
| finite declaration with invalid condition, determining-source, trust, or decisive-binding grammar | $\lambda_F$ undefined; no verdict |
| no decisive binding, or only `supports` or `refutes` bindings | successful finite evaluation; verdict `0` |
| referenced evidence item absent | successful finite evaluation; verdict `0` |
| decisively referenced, recognized non-review evidence kind | successful finite evaluation; verdict `0` |
| rejected review | successful finite evaluation; verdict `0` |
| any one or more of the four identity comparisons is false | successful finite evaluation; verdict `0` |
| recognized 10.3 source class other than `belgi.software-change.source.review-system` | successful finite evaluation; verdict `0` |
| applicable trust entry absent, excluded, or included and non-authoritative | successful finite evaluation; verdict `0` |
| successfully induced unbound auxiliary evidence | ignored; it cannot affect the verdict |
| cached-verdict disagreement | retain the derived verdict and emit only the existing Part 2 `cached-verdict-mismatch` warning |
| earlier package, cryptographic, complete authenticated claim-record, generic schema, integrity, or closure defect | the earlier owner and Part 2 priority govern; finite evaluation is not performed |

Complete authenticated claim-record validation shall occur before source
resolution and semantic lifting. No finite-evaluator case shall bypass or
reorder BELGI - Part 2, 12.2, and an earlier failure shall not be masked by a
later finite-evaluator result. This profile defines no new replay outcome
class, problem type, warning type, stage, or priority rule for these cases.

The finite evaluator shall not read a clock, current time, freshness service,
mutable branch, live review system, environment default, or undeclared
external state. A clock, freshness, timestamp-policy, or comparable attempted
declaration on an exact Part 4 review-record evidence item or finite evaluator
declaration is outside the closed parameter grammar; its presence makes the
corresponding evidence or evaluator induction undefined. A future
time-sensitive procedure shall preserve its decisive fact in $E$ and bind
another exact determining source rather than reading ambient time.

Requirement identifier: `P4-FE-005`.

### 12.9 Finite reference-validation material

`conformance/SoftwareChangeFiniteEvaluator.v1.json` is clause-linked finite
reference-validation material for requirements `P4-FE-001` through
`P4-FE-006`. It identifies already decoded finite carrier inputs and, solely
for the totality boundary in 12.7, an explicitly pre-induced Part 1 judged
object outside the finite record subset. It also contains expected records and
corpus-local operation and diagnostic labels for testing the procedure. The
pre-induced witness is not a carrier-lifting rule. This material does not
define a carrier schema, schema role, representation binding, procedure token,
selector, replay outcome, problem type, warning type, or failure priority.

The result for each case shall be derived from its input and the requirements
of this document. Case order, expected outcome or verdict fields, diagnostic
prose, filenames, and corpus-local identifiers shall not supply evaluator
authority. Reordering cases or replacing expected fields shall not change the
result derived from an unchanged input.

This material is not a finite verdict-interoperability corpus under BELGI -
Part 3, 9.8. Its existence, use, or successful execution does not establish
cross-implementation agreement, implementation adoption, or conformance to
this Working Draft source. The digest-bound exact Part 4 source remains the sole
owner of the finite evaluator meaning.

Requirement identifier: `P4-FE-006`.

## 13 Conformance

### 13.1 Conformance classes

The following conformance classes are defined:

- BELGI Software Change Admission Producer;
- BELGI Software Change Admission Verifier; and
- BELGI Full Part 4 Implementation.

### 13.2 BELGI Software Change Admission Producer

An implementation conforms to this document as a BELGI Software Change Admission Producer if it:

- conforms to BELGI - Part 1: Core semantic model as a BELGI Core Semantic Implementation in accordance with Part 1, 12.2;
- conforms to BELGI - Part 2: Claim carriers and replay package as a BELGI Replay Package Producer in accordance with Part 2, 14.3;
- conforms to BELGI - Part 3: Profiles and companion specifications as a BELGI Profile-aware Producer in accordance with Part 3, 13.4;
- conforms to BELGI - Companion specification: Package integrity anchor verification as a BELGI Package Integrity Anchor Verification-aware Producer in accordance with that companion specification, Clause 11.2;
- uses the profile identifier of 6.1 for claims produced under this profile;
- preserves the exact edition of the mandatory companion selected in 6.3;
- preserves judged-object material in accordance with Clause 7;
- preserves evidence material in accordance with Clause 8;
- preserves evaluator declarations in accordance with Clauses 9 to 11;
- preserves optional exact-edition companion dependencies only when replay-relevant interpretation depends on them;
- declares `belgi.software-change.replay.record-check` for every claim produced under this profile; and
- does not treat a produced claim as conforming to this profile unless its replay package satisfies `belgi.software-change.replay.record-check`.

NOTE Producer conformance cites BELGI - Part 1, 12.2 rather than BELGI - Part 1, 12.3 because BELGI - Part 2, 14.3 already requires preservation of the replay-relevant content, closure, projection, and integrity material needed for replay. Replay success is determined by the replay verifier.

### 13.3 BELGI Software Change Admission Verifier

An implementation conforms to this document as a BELGI Software Change Admission Verifier if it:

- conforms to BELGI - Part 1: Core semantic model as a BELGI Replay Semantic Implementation in accordance with Part 1, 12.3;
- conforms to BELGI - Part 2: Claim carriers and replay package as a BELGI Replay Verifier in accordance with Part 2, 14.4;
- conforms to BELGI - Part 3: Profiles and companion specifications as a BELGI Profile-aware Verifier in accordance with Part 3, 13.5;
- conforms to BELGI - Companion specification: Package integrity anchor verification as a BELGI Package Integrity Anchor Verification-aware Verifier in accordance with that companion specification, Clause 11.3;
- recognizes the profile identifier of 6.1;
- interprets the vocabulary and constraints of Clauses 7 to 12 only according to the exact edition of this profile and any exact-edition companion dependencies identified for the claim;
- verifies the exact edition of the mandatory companion selected in 6.3 before treating a claim as conforming under this profile;
- verifies that the claim declares and satisfies `belgi.software-change.replay.record-check` before treating the claim as conforming under this profile;
- applies fail-closed semantics to missing required declarations, missing required bindings, missing required parameters, and unresolved replay-relevant dependencies under this profile; and
- does not treat undeclared environment-envelope material, undeclared environment equivalence, descriptive `belgi.software-change.binding.supports` or `belgi.software-change.binding.refutes` material, or material assigned boundary participation `belgi.software-change.boundary-participation.excluded` as decisive evaluator bindings or otherwise as affecting declared conditions under this profile.

### 13.4 BELGI Full Part 4 Implementation

An implementation conforms to this document as a BELGI Full Part 4 Implementation if it conforms to 13.2 and 13.3 and conforms to BELGI - Companion specification: Package integrity anchor verification as a BELGI Full Package Integrity Anchor Verification Implementation in accordance with that companion specification, Clause 11.4.

### 13.5 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- the exact edition of BELGI - Part 1 used as semantic authority, or the immutable designator from which that exact edition is identified;
- the profile identifier of 6.1;
- the exact edition of this profile against which the claim is made, or the immutable designator from which that exact edition is identified;
- the exact edition of the mandatory companion selected in 6.3;
- each optional exact-edition companion dependency on which replay-relevant interpretation under this profile depends, or state that no optional companion dependency is used;
- support for the mandatory replay policy `belgi.software-change.replay.record-check`; and
- the date of the statement.

## 14 Security considerations

Software change admission is vulnerable to under-specified baselines, undeclared repository context, environment drift, dependency drift, substituted evidence, non-authoritative local results, and post hoc reinterpretation of automated or human-produced records.

This profile reduces those risks only when producers and verifiers preserve and enforce the judged-object pattern, the declared evidence kinds, the trust boundary, the environment envelope, the decisive binding declarations, and the mandatory replay policy used for the claim.

Excluded reliance claim: this profile does not establish authority, correctness, or suitability of CI output, review material, generated analysis output, or any particular tool. It makes only the reliance surface explicit and replayable.

Attestation-shape substitution can arise when a preserved provenance record, CI assertion, workflow record, or other origin statement is treated as authoritative merely because it is an attestation-shaped artifact. Clauses 8.2, 10.4, and 12 keep such material subordinate to declared evidence kind, boundary participation, authority level, exact-edition dependencies, and replay-policy requirements.

CI summary substitution and artifact-origin substitution can arise when badges, check-run conclusions, job summaries, artifact URLs, filenames, cache keys, storage paths, or package colocation are treated as if they established underlying report content, workflow identity, source identity, or producing-run linkage. Clause 10.4 requires replay-relevant CI and artifact-origin facts rather than presentation or storage coincidences.

## 15 Privacy considerations

This profile does not require preservation of developer identity, reviewer identity, or other personal identifiers unless such material is replay-relevant to a declared condition.

Persistent identifiers preserved only for operational convenience can create cross-claim correlation that is unnecessary for replay.

Applicable privacy obligations for personal data incidentally preserved in replay-relevant material apply independently of this profile.

Repository identifiers, revision identifiers, workflow identifiers, CI run identifiers, artifact-origin linkages, review-system references, and other operational metadata can also create cross-claim correlation or metadata-leakage risk when preserved more broadly than replay requires.

This document does not define user-facing interfaces, locale-sensitive rendering, or natural-language presentation requirements. Accessibility and internationalization obligations therefore arise only in implementations, repository surfaces, CI surfaces, review surfaces, or companion surfaces that present BELGI material to users.
