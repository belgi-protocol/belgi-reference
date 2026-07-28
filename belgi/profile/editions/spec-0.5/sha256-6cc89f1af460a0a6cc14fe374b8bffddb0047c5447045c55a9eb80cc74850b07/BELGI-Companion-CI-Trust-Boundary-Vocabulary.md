# BELGI - Companion specification: CI trust-boundary vocabulary

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications; BELGI - Part 4: Software change admission profile
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is a BELGI companion specification. It defines reusable continuous-integration-oriented trust-boundary and environment-envelope vocabulary for use with BELGI profiles and evaluator carriers.

## Introduction

BELGI - Part 3 reserves the extension points at which profiles and companion specifications may add domain-specific vocabulary without reopening the semantic authority of BELGI - Part 1 or the replay authority of BELGI - Part 2.

This document uses that extension surface for continuous-integration-mediated software admission. It fixes exact-edition-local compact identifier vocabularies and minimum meanings for CI-oriented source-material roles and CI-oriented environment-envelope declarations that can affect replay-relevant evaluator meaning.

This document is intentionally vendor-neutral at the semantic layer. It does not make any one CI platform, runner product, workflow language, provenance format, artifact store, repository host, or credential model normative. Profiles and evaluator declarations may bind this vocabulary to concrete systems or equivalent processes, but those bindings remain external to the meanings fixed here.

## 1 Scope

This document defines a BELGI companion specification for CI-oriented trust-boundary vocabulary.

This document defines:

- CI-oriented source-material-role identifiers;
- CI-oriented environment-envelope identifiers; and
- companion-specific conformance classes.

This document is applicable where a BELGI profile or replay-relevant evaluator material uses CI-oriented trust-boundary or environment-envelope vocabulary.

This document does not define:

- one mandatory CI platform, one mandatory provenance format, one mandatory artifact store, or one mandatory repository host;
- one universal trust policy for all CI-originated evidence;
- condition identifiers, evidence-kind identifiers, binding relation kinds, or replay-policy refinements;
- representation-specific schemas, serialization bindings, or machine-readable schema dialects; or
- one reference profile for CI-mediated admission.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.5, 2026-07-21
- BELGI - Part 4: Software change admission profile, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in BELGI - Part 1, BELGI - Part 2, BELGI - Part 3, BELGI - Part 4, and the following apply.

### 3.1 CI source-material-role identifier

term identifier naming one CI-oriented role of preserved source material defined by this companion specification

### 3.2 CI environment-envelope identifier

term identifier naming one replay-relevant CI environment fact defined by this companion specification

### 3.3 immutable source reference

repository reference that denotes one fixed source state rather than a moving branch tip or other mutable selector

### 3.4 artifact-origin linkage

replay-relevant linkage by which a preserved artifact or report is connected to the specific CI run and source reference that produced it

### 3.5 attested CI run

CI run whose run identity, workflow-definition identity, immutable source reference, and artifact-origin linkage are preserved or resolved by replay-relevant material from which replay determines those facts under the applicable BELGI profile

## 4 Symbols and abbreviated terms

### 4.1 Symbols

No symbols are listed in this document.

### 4.2 Abbreviated terms

CI continuous integration

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 13 are normative unless stated otherwise.

This document owns only the companion vocabulary fixed in Clauses 6 to 10. It does not alter the semantic authority of BELGI - Part 1, the replay authority of BELGI - Part 2, or the extension-governance authority of BELGI - Part 3.

## 6 Companion identity and declaration

### 6.1 Companion identifier and version designator

The companion identifier of this companion specification is:

`https://belgi.dev/ids/companion/ci-trust-boundary-vocabulary`

The current draft version designator is:

`0.5`

The owning publisher or change controller of this companion specification is:

`belgi`

The compact identifier tokens defined by this companion are partitioned into
the named vocabularies `source-material-role` and `environment-envelope`. The
namespace identity of each vocabulary is the ordered pair of the companion
identifier in 6.1 and that vocabulary name.

Within each namespace, tokens shall be compared as exact strings without case
folding, Unicode normalization, whitespace trimming, prefix expansion, or other
normalization. No two meanings may share one token in the same namespace. Once
assigned, a token shall not be reassigned a different meaning by a later
edition of this companion family, and retirement or removal shall not make it
available for reassignment. Each token remains subordinate to its exact
defining edition and is not globally reusable without its named namespace and
exact-edition context.

### 6.2 BELGI dependency declaration

This companion specification and the BELGI Parts named in Clause 2 are members
of the coherent `spec-0.5` Working Draft family.

### 6.3 Reserved extension points served

This companion specification serves the following reserved extension points of BELGI - Part 3:

- 8.5 trust-boundary vocabulary; and
- 8.8 environment-envelope vocabulary.

This draft does not define condition identifiers, evidence-kind identifiers, binding relation kinds, replay-policy refinements, evaluator-parameter identifiers, or representation-specific schemas.

### 6.4 Machine-readable material

This draft defines no separate machine-readable declaration material beyond the local compact identifier tokens and meanings fixed by this draft.

### 6.5 Compatibility statement

This `0.5` Working Draft succeeds exact `0.4`. This companion specification
declares no backward compatibility, forward compatibility, or replay
substitution with its predecessor.

## 7 General vocabulary rules

### 7.1 No authority-by-identifier rule

The identifiers defined by this companion specification do not by themselves assign boundary participation or authority level to a source or environment.

Those declarations shall be made by the applicable BELGI profile or replay-relevant evaluator declaration.

### 7.2 Attested-run rule

If replay-relevant evaluator material uses this companion specification in a way that treats CI-originated material as authoritative on the basis of an attested CI run, the replay-relevant material shall preserve or resolve, at minimum:

- the CI run identity;
- the workflow-definition identity;
- the immutable source reference; and
- the artifact-origin linkage for each preserved artifact or report relied on for the claim.

### 7.3 Immutable-source-reference rule

A moving branch tip, mutable tag, mutable environment label, or other mutable selector shall not by itself satisfy an immutable source reference.

### 7.4 No implicit artifact-origin-binding rule

An artifact, report, or cached result shall not be treated as originating from a particular CI run merely because it appears in the same storage location, package, job summary, or workflow namespace.

An artifact URL, download path, cache key, storage bucket, filename, package member name, or job/workflow namespace shall not by itself establish artifact-origin linkage.

Artifact-origin linkage shall be made explicit wherever replay-relevant interpretation depends on it.

### 7.5 No summary-only substitution rule

Dashboard badges, aggregate pass or fail statuses, job summaries, and comparable summary-only material shall not by themselves determine the meaning of CI-originated evidence when replay depends on underlying report content, workflow identity, source identity, or artifact-origin linkage.

Status-summary material may support diagnostics, but it shall not replace the underlying report content, workflow-definition identity, source-reference identity, artifact-origin linkage, or environment-envelope facts on which evaluator meaning depends.

### 7.6 No silent environment-equivalence rule

Differences in workflow definition, runner platform, runner image, trigger context, toolchain state, or other CI environment facts shall not be treated as equivalent by silence whenever those differences can affect evidence production, evidence interpretation, evaluator induction, or verdict derivation.

## 8 CI source-material-role vocabulary

### 8.1 General

This companion specification defines the following CI-oriented source-material-role identifiers.

### 8.2 Source-material-role identifiers

| Source-material-role identifier | Meaning |
| --- | --- |
| `belgi.ci.source.run-record` | preserved CI control-plane or execution source material identifying one CI run, without implying that all facts required for an attested CI run are preserved |
| `belgi.ci.source.run-attestation` | preserved CI-originated or CI-bound source material from which replay determines the run identity, workflow-definition identity, immutable source reference, and artifact-origin linkage for the relevant run |
| `belgi.ci.source.workflow-definition` | preserved source material fixing the workflow, pipeline, reusable workflow, step script, or comparable CI execution definition used for the run |
| `belgi.ci.source.runner-environment-record` | preserved source material describing the CI execution environment in which the relevant workflow steps ran |
| `belgi.ci.source.artifact-origin-record` | preserved source material establishing artifact-origin linkage for a preserved artifact or report relied on by the claim |
| `belgi.ci.source.status-summary` | preserved CI status, badge, conclusion, or aggregate result summary that does not by itself preserve the full underlying report semantics |

### 8.3 Source-material-role interpretation rules

The identifiers of 8.2 classify the replay-relevant role of preserved CI source material. They supplement, and do not replace, the generic evidence source class or execution-context class required by an applicable BELGI profile.

When used with BELGI - Part 4: Software change admission profile, Version 0.5, 2026-07-21, Clauses 10.2 to 10.4:

- `belgi.ci.source.run-record`, `belgi.ci.source.run-attestation`, `belgi.ci.source.workflow-definition`, `belgi.ci.source.runner-environment-record`, and `belgi.ci.source.status-summary` shall be declared only in addition to the generic Part 4 evidence source class `belgi.software-change.source.ci-execution`;
- `belgi.ci.source.artifact-origin-record` shall be declared only in addition to the generic source class of the source from which the linkage record originates, typically `belgi.software-change.source.ci-execution` or `belgi.software-change.source.artifact-store`; and
- the generic Part 4 source class controls trust-boundary classification, while the identifier of 8.2 states the CI-specific role of the preserved source material.

`belgi.ci.source.run-attestation` shall not be used unless replay over the preserved replay-relevant material determines the facts listed in 7.2.

Replay-relevant material designated as `belgi.ci.source.workflow-definition` shall include reusable workflow material, imported step definitions, generated execution definitions, or comparable external execution logic whenever those materials can affect the meaning of the evidence.

`belgi.ci.source.artifact-origin-record` shall identify the producing run and the produced artifact or report by replay-relevant material from which replay determines the artifact-origin linkage whenever artifact-origin linkage is relied on for the claim.

`belgi.ci.source.status-summary` may be preserved as supporting or diagnostic material, but it shall not by itself establish the more specific source role of `belgi.ci.source.run-attestation` or `belgi.ci.source.artifact-origin-record`.

## 9 CI environment-envelope vocabulary

### 9.1 General

This companion specification defines the following CI-oriented environment-envelope identifiers.

### 9.2 Environment-envelope identifiers

| Environment-envelope identifier | Meaning |
| --- | --- |
| `belgi.ci.environment.run-identity` | identifies the CI run instance relevant to the preserved evidence or report |
| `belgi.ci.environment.workflow-definition-identity` | identifies the workflow or pipeline definition relevant to the preserved evidence or report |
| `belgi.ci.environment.source-reference-identity` | identifies the immutable source reference used for the run |
| `belgi.ci.environment.runner-platform-identity` | identifies the operating-system, platform, architecture, or comparable execution-platform facts relevant to the run |
| `belgi.ci.environment.runner-image-identity` | identifies the runner image, runner template, container image, or comparable execution image used for the run |
| `belgi.ci.environment.toolchain-state-identity` | identifies the compiler, interpreter, package-manager, action, plugin, or comparable toolchain state relevant to evidence production or interpretation |
| `belgi.ci.environment.trigger-context-identity` | identifies the trigger source, trigger input, event type, or comparable invocation context relevant to the run |

### 9.3 Environment-envelope interpretation rules

`belgi.ci.environment.source-reference-identity` shall denote one fixed source state and shall not be satisfied by a moving branch tip or other mutable selector alone.

`belgi.ci.environment.workflow-definition-identity` shall be preserved or resolved whenever workflow configuration, reusable workflow material, imported execution logic, or generated execution definitions can affect the meaning of the evidence or the evaluator.

`belgi.ci.environment.runner-platform-identity`, `belgi.ci.environment.runner-image-identity`, and `belgi.ci.environment.toolchain-state-identity` shall be preserved or resolved whenever differences in those facts can affect evidence production, evidence interpretation, evaluator induction, or verdict derivation.

`belgi.ci.environment.trigger-context-identity` shall be preserved or resolved whenever trigger source or trigger inputs can affect workflow selection, workflow behavior, proposal scope, baseline scope, or evidence meaning.

## 10 Profile-use constraints

### 10.1 General

A BELGI profile or replay-relevant evaluator declaration using this companion specification shall preserve the meanings of the identifiers defined in Clauses 8 and 9.

When used with BELGI normative text that already defines generic source classes or generic environment-envelope content, the identifiers of Clauses 8 and 9 shall supplement those generic declarations as CI-specific source-material roles or environment refinements and shall not contradict or replace them.

### 10.2 CI authoritative-use constraints

If CI-originated material is classified as authoritative for build, test, analysis, dependency, provenance, or comparable automated-admission conditions, replay-relevant material shall preserve or resolve the CI source-material-role and environment-envelope material needed for replay to determine:

- the run identity;
- the workflow-definition identity;
- the immutable source reference; and
- the artifact-origin linkage for each preserved artifact or report on which the condition meaning depends.

Summary-only material, storage colocation, artifact download location, package member naming, or CI namespace membership shall not by itself satisfy those facts.

### 10.3 Summary-only restriction

Material designated only as `belgi.ci.source.status-summary` shall not by itself satisfy a declared go condition whose meaning depends on underlying result content, workflow identity, source identity, or artifact-origin linkage.

### 10.4 Exact-edition dependency rule

If replay-relevant interpretation depends on this companion specification, the exact edition of this companion specification shall be identified and preserved in accordance with BELGI - Part 2 and BELGI - Part 3.

## 11 Conformance

### 11.1 Conformance classes

The following conformance classes are defined:

- BELGI CI Trust-Boundary Vocabulary-aware Producer;
- BELGI CI Trust-Boundary Vocabulary-aware Verifier; and
- BELGI Full CI Trust-Boundary Vocabulary Implementation.

For the purposes of this clause, production support for an identifier means the capability to emit at least one instance that satisfies every applicable requirement of Clauses 7 to 10. Verification support means the capability to accept such a conforming instance and fail closed on an instance that violates an applicable requirement of Clauses 7 to 10.

### 11.2 BELGI CI Trust-Boundary Vocabulary-aware Producer

An implementation conforms to this document as a BELGI CI Trust-Boundary Vocabulary-aware Producer if it:

- has production support for at least one identifier defined by Clauses 8 or 9;
- when emitting an identifier defined by Clauses 8 or 9, uses that identifier exactly as defined by this draft;
- preserves or resolves the replay-relevant CI facts required by Clauses 7 to 10 whenever it emits identifiers whose meanings depend on those facts;
- does not treat mutable source selectors, summary-only CI material, or unbound artifacts as if they satisfied stronger identifiers defined by this draft; and
- preserves the exact edition of this companion specification whenever replay-relevant interpretation depends on it.

### 11.3 BELGI CI Trust-Boundary Vocabulary-aware Verifier

An implementation conforms to this document as a BELGI CI Trust-Boundary Vocabulary-aware Verifier if it:

- has verification support for at least one identifier defined by Clauses 8 or 9;
- identifies the exact edition of this companion specification from preserved material when replay depends on it;
- interprets the identifiers defined by Clauses 8 and 9 only according to the meanings fixed by this draft and any exact-edition replay-relevant narrowing that does not contradict this draft;
- fails closed when replay-relevant CI facts needed to interpret an identifier from Clauses 8 or 9 are missing, unresolved, contradictory, or non-authoritative under the applicable BELGI profile or evaluator declaration; and
- does not silently substitute another companion edition or another identifier for replay.

### 11.4 BELGI Full CI Trust-Boundary Vocabulary Implementation

An implementation conforms to this document as a BELGI Full CI Trust-Boundary Vocabulary Implementation if it conforms to 11.2 and 11.3.

### 11.5 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- the companion identifier of 6.1;
- the exact edition of this companion specification against which the claim is made;
- a non-empty set of supported identifiers from Clauses 8 and 9, with production support, verification support, or both stated for each identifier; and
- the date of the statement.

A statement that all identifiers are supported shall be made only when the claimed implementation has the stated production or verification support for every identifier in Clauses 8 and 9.

## 12 Profile and evaluator guidance

### 12.1 General

This clause is informative.

Profiles and evaluator declarations commonly use this companion specification to refine generic CI-related source classes or environment-envelope material defined elsewhere in BELGI.

Typical uses include distinguishing status summaries from artifact-origin records, distinguishing run records from attested runs, and making workflow-definition identity or runner-image identity explicit where replay depends on them.

### 12.2 Non-substitution reminder

This companion specification does not replace an applicable BELGI profile, governing specification, determining-semantics source, or other evaluator-defining source.

It provides only vocabulary for talking about CI trust-boundary and environment facts within those larger semantic structures.

## 13 Security considerations

CI-oriented admission is vulnerable to mutable source selectors presented as fixed source states, workflow-definition substitution, runner-environment drift, artifact substitution, summary-only evidence presented as decisive, and post hoc reinterpretation of CI records whose exact edition or producing context is not preserved.

This companion specification reduces ambiguity only when producers and verifiers preserve and enforce the replay-relevant CI facts and exact-edition bindings needed to interpret the identifiers defined here.

Artifact-origin substitution can arise when an artifact URL, filename, cache key, storage location, package member name, or workflow namespace is treated as proof of the producing CI run. Clauses 7.4, 8.3, and 10.2 require explicit producing-run and produced-artifact linkage.

Excluded reliance claim: this companion specification does not establish authority, correctness, or suitability of any one CI platform, runner, workflow engine, provenance format, or artifact store.

## 14 Privacy considerations

This companion specification does not require preservation of developer identity, reviewer identity, CI account identity, or other personal identifiers.

When CI records, workflow metadata, or provenance material incidentally contain personal data, applicable privacy obligations apply independently of this companion specification.
