# BELGI - Companion specification: Python condition vocabulary

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications; BELGI - Part 4: Software change admission profile
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is a BELGI companion specification. It defines reusable Python-oriented condition, evidence-kind, and evaluator-parameter vocabulary for use with BELGI profiles and evaluator carriers.

## Introduction

BELGI - Part 3 reserves the extension points at which profiles and companion specifications may add domain-specific vocabulary without reopening the semantic authority of BELGI - Part 1 or the replay authority of BELGI - Part 2.

This document uses that extension surface for Python-oriented software change admission. It fixes exact-edition-local compact identifier vocabularies and minimum meanings for Python-specific admission conditions, Python-specific evidence kinds, and Python-specific evaluator parameters.

This document is intentionally tool-neutral at the semantic layer. It does not make any one linter, type checker, test runner, coverage tool, dependency auditor, lock resolver, repository host, or CI platform normative. Profiles and evaluator declarations may bind this vocabulary to concrete tools or equivalent processes, but those bindings remain external to the meanings fixed here.

## 1 Scope

This document defines a BELGI companion specification for Python-oriented software change admission vocabulary.

This document defines:

- Python-specific condition identifiers;
- Python-specific evidence-kind identifiers;
- Python-specific evaluator-parameter identifiers; and
- companion-specific conformance classes.

This document is applicable where a BELGI profile or replay-relevant evaluator material uses Python-oriented condition, evidence, or parameter vocabulary.

This document does not define:

- one mandatory Python toolchain, one mandatory package manager, one mandatory build backend, or one mandatory CI platform;
- one universal satisfaction algorithm for every Python condition;
- representation-specific schemas, serialization bindings, or machine-readable schema dialects;
- trust-boundary vocabulary; or
- one reference profile for Python admission.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.5, 2026-07-21
- BELGI - Part 4: Software change admission profile, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in BELGI - Part 1, BELGI - Part 2, BELGI - Part 3, BELGI - Part 4, and the following apply.

### 3.1 Python condition identifier

term identifier naming one Python-oriented admission condition defined by this companion specification

### 3.2 Python evidence-kind identifier

term identifier naming one Python-oriented evidence kind defined by this companion specification

### 3.3 Python evaluator-parameter identifier

term identifier naming one replay-relevant evaluator parameter defined by this companion specification

## 4 Symbols and abbreviated terms

### 4.1 Symbols

No symbols are listed in this document.

### 4.2 Abbreviated terms

No abbreviated terms are listed in this document.

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 13 are normative unless stated otherwise.

This document owns only the companion vocabulary and constraints fixed in Clauses 6 to 11. It does not alter the semantic authority of BELGI - Part 1, the replay authority of BELGI - Part 2, or the extension-governance authority of BELGI - Part 3.

## 6 Companion identity and declaration

### 6.1 Companion identifier and version designator

The companion identifier of this companion specification is:

`https://belgi.dev/ids/companion/python-condition-vocabulary`

The current draft version designator is:

`0.5`

The owning publisher or change controller of this companion specification is:

`belgi`

The compact identifier tokens defined by this companion are partitioned into
the named vocabularies `condition`, `evidence-kind`, and `evaluator-parameter`.
The namespace identity of each vocabulary is the ordered pair of the companion
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

- 8.3 evidence vocabulary and evidence kinds;
- 8.4 condition vocabulary; and
- 8.9 evaluator declaration parameter vocabulary.

This draft does not define trust-boundary vocabulary, environment-envelope vocabulary, replay-policy refinements, binding relation kinds, or representation-specific schemas.

### 6.4 Machine-readable material

This draft defines no separate machine-readable declaration material beyond the local compact identifier tokens and meanings fixed by this draft.

### 6.5 Compatibility statement

This `0.5` Working Draft succeeds exact `0.4`. This companion specification
declares no backward compatibility, forward compatibility, or replay
substitution with its predecessor.

## 7 General vocabulary rules

### 7.1 Tool-neutrality rule

The meanings of the identifiers defined by this companion specification are semantic meanings. They are not fixed by the brand name, executable name, output filename, or report syntax of any one tool.

### 7.2 External tool binding rule

If a profile or evaluator declaration uses this companion specification to support interpretation across more than one concrete tool or report form, it shall explicitly identify the concrete tools, equivalent processes, or accepted report forms by which the identifiers of Clauses 8 to 10 are interpreted.

### 7.3 Parameter visibility rule

If satisfaction or non-satisfaction of a condition defined by this companion specification depends on thresholds, scopes, dependency-set selection, interpreter constraints, environment assumptions, or other replay-relevant parameters, those parameters shall be made explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2.

### 7.4 Trust-boundary dependency rule

If replay-relevant interpretation of a condition identifier in 8.2 depends on whether preserved evidence is included as authoritative, included as non-authoritative, or excluded, the applicable BELGI profile or replay-relevant evaluator declaration shall identify the trust-boundary vocabulary and the boundary-participation and authority declarations by which that dependence is determined.

For software-change admission under BELGI - Part 4, Version 0.5, 2026-07-21, Clauses 9.3 and 10.2 to 10.4, use of a condition identifier in 8.2 shall depend on an exact-edition profile or other BELGI normative text that fixes the boundary-participation and authority declarations under which the relevant Python evidence is interpreted.

### 7.5 No implicit binding-kind rule

This companion specification does not define evidence-condition binding relation kinds.

A profile or evaluator declaration using this companion specification shall use only binding relation kinds permitted by the applicable BELGI profile or other applicable BELGI normative text.

## 8 Python condition vocabulary

### 8.1 General

This companion specification defines the following Python-oriented condition identifiers.

### 8.2 Condition identifiers

| Condition identifier | Meaning |
| --- | --- |
| `belgi.python.condition.lint-clean` | authoritative Python lint evidence indicates no finding at or above the declared failure threshold within the declared scope |
| `belgi.python.condition.tests-pass` | authoritative Python test evidence indicates successful completion of the declared test scope with no failing test case relevant to that scope |
| `belgi.python.condition.coverage-threshold-met` | authoritative Python coverage evidence indicates measured coverage at or above the declared minimum threshold within the declared scope |
| `belgi.python.condition.type-check-pass` | authoritative Python static type-analysis evidence indicates no finding at or above the declared failure threshold within the declared scope |
| `belgi.python.condition.dependency-audit-pass` | authoritative Python dependency-audit evidence indicates no finding at or above the declared severity floor for the declared dependency set |
| `belgi.python.condition.lock-resolution-clean` | authoritative Python lock or dependency-resolution evidence indicates successful resolution of the declared dependency graph under the declared interpreter and environment constraints |

### 8.3 Condition interpretation rules

When used with BELGI - Part 4: Software change admission profile, Version 0.5, 2026-07-21, Clauses 9.2 and 9.3, the condition identifiers of 8.2 refine the following generic Part 4 condition identifiers.

| Python condition identifier | Generic Part 4 condition identifier |
| --- | --- |
| `belgi.python.condition.lint-clean` | `belgi.software-change.condition.analysis-policy-satisfied` |
| `belgi.python.condition.tests-pass` | `belgi.software-change.condition.test-policy-satisfied` |
| `belgi.python.condition.coverage-threshold-met` | `belgi.software-change.condition.coverage-policy-satisfied` |
| `belgi.python.condition.type-check-pass` | `belgi.software-change.condition.analysis-policy-satisfied` |
| `belgi.python.condition.dependency-audit-pass` | `belgi.software-change.condition.dependency-policy-satisfied` |
| `belgi.python.condition.lock-resolution-clean` | `belgi.software-change.condition.dependency-policy-satisfied` |

The condition identifiers of 8.2 do not by themselves fix:

- one mandatory concrete tool;
- one mandatory output format;
- one mandatory failure threshold;
- one mandatory analysis scope; or
- one mandatory dependency-selection method.

Those matters shall be made explicit by the applicable profile or evaluator declaration when replay-relevant.

### 8.4 Fail-closed interpretation

If replay-relevant material using one of the condition identifiers in 8.2 omits a parameter required for its interpretation, that condition shall not support go.

If required evidence for one of the condition identifiers in 8.2 is absent, unresolved, non-authoritative, or not interpretable under the declared replay-relevant rules, that condition shall not support go.

## 9 Python evidence-kind vocabulary

### 9.1 General

This companion specification defines the following Python-oriented evidence-kind identifiers.

### 9.2 Evidence-kind identifiers

| Evidence-kind identifier | Meaning |
| --- | --- |
| `belgi.python.evidence.lint-report` | preserved report or equivalent preserved result describing Python lint or static style findings |
| `belgi.python.evidence.test-report` | preserved report or equivalent preserved result describing Python test execution outcomes |
| `belgi.python.evidence.coverage-report` | preserved report or equivalent preserved result describing measured Python coverage and the scope to which it applies |
| `belgi.python.evidence.type-check-report` | preserved report or equivalent preserved result describing Python static type-analysis findings |
| `belgi.python.evidence.dependency-audit-report` | preserved report or equivalent preserved result describing vulnerability, policy, or dependency-audit findings for Python dependencies |
| `belgi.python.evidence.lock-resolution-report` | preserved report or equivalent preserved result describing the success or failure of Python dependency or lock resolution under declared constraints |

### 9.3 Evidence-kind interpretation rules

Human-readable summaries, badges, dashboard statuses, or cached pass/fail indicators shall not by themselves determine the meaning of an evidence-kind identifier defined in 9.2 when replay depends on the underlying report content.

If a profile or evaluator declaration accepts more than one concrete report form for the same evidence-kind identifier, that acceptance shall be made explicit.

## 10 Python evaluator-parameter vocabulary

### 10.1 General

This companion specification defines the following replay-relevant evaluator-parameter identifiers.

### 10.2 Evaluator-parameter identifiers

| Evaluator-parameter identifier | Meaning |
| --- | --- |
| `belgi.python.parameter.analysis-scope` | identifies the file set, package set, test selection, module set, or other declared scope to which a Python condition applies |
| `belgi.python.parameter.failure-threshold` | identifies the finding level, rule level, or failure criterion at or above which a Python condition is unsatisfied |
| `belgi.python.parameter.coverage-minimum` | identifies the minimum coverage threshold required for `belgi.python.condition.coverage-threshold-met` |
| `belgi.python.parameter.dependency-set-designator` | identifies the dependency set, lock scope, extras selection, or comparable dependency universe to which a dependency-related condition applies |
| `belgi.python.parameter.interpreter-constraint` | identifies the Python interpreter version or version range relevant to the condition or evidence interpretation |
| `belgi.python.parameter.environment-constraint` | identifies the declared operating-system, platform, architecture, or runtime constraint relevant to Python condition interpretation |

### 10.3 Parameter-usage rules

`belgi.python.parameter.coverage-minimum` shall be made explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2 when `belgi.python.condition.coverage-threshold-met` is used.

`belgi.python.parameter.dependency-set-designator` shall be made explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2 when `belgi.python.condition.dependency-audit-pass` or `belgi.python.condition.lock-resolution-clean` is used and the applicable evaluator meaning depends on a selected dependency set rather than on the whole resolved dependency graph.

`belgi.python.parameter.analysis-scope`, `belgi.python.parameter.failure-threshold`, `belgi.python.parameter.interpreter-constraint`, and `belgi.python.parameter.environment-constraint` shall be made explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2 whenever omission of the parameter would leave the condition meaning under-specified for replay.

## 11 Profile-use constraints

### 11.1 General

A BELGI profile, evaluator declaration, or replay verifier using this companion specification shall preserve the meanings of the identifiers defined in Clauses 8 to 10.

### 11.2 No silent narrowing or widening

A profile or evaluator declaration shall not silently narrow or widen the meaning of a Python condition identifier, evidence-kind identifier, or evaluator-parameter identifier defined by this companion specification.

If narrower meaning is required, the profile or evaluator declaration shall make that narrowing explicit by exact-edition referenced rules that do not contradict this companion specification.

### 11.3 Exact-edition dependency rule

If replay-relevant interpretation depends on this companion specification, the exact edition of this companion specification shall be identified and preserved in accordance with BELGI - Part 2 and BELGI - Part 3.

## 12 Conformance

### 12.1 Conformance classes

The following conformance classes are defined:

- BELGI Python Condition Vocabulary-aware Producer;
- BELGI Python Condition Vocabulary-aware Verifier; and
- BELGI Full Python Condition Vocabulary Implementation.

For the purposes of this clause, production support for an identifier means the capability to emit at least one instance that satisfies every applicable requirement of Clauses 7 to 11. Verification support means the capability to accept such a conforming instance and fail closed on an instance that violates an applicable requirement of Clauses 7 to 11.

### 12.2 BELGI Python Condition Vocabulary-aware Producer

An implementation conforms to this document as a BELGI Python Condition Vocabulary-aware Producer if it:

- has production support for at least one identifier defined by Clauses 8 to 10;
- when emitting an identifier defined by Clauses 8 to 10, uses that identifier exactly as defined by this draft;
- makes explicit any replay-relevant tool binding, threshold, scope, dependency-set selection, interpreter constraint, or environment constraint needed to interpret the emitted identifier;
- preserves the exact edition of this companion specification whenever replay-relevant interpretation depends on it; and
- does not treat omitted replay-relevant parameters as if they were satisfied by default.

### 12.3 BELGI Python Condition Vocabulary-aware Verifier

An implementation conforms to this document as a BELGI Python Condition Vocabulary-aware Verifier if it:

- has verification support for at least one identifier defined by Clauses 8 to 10;
- identifies the exact edition of this companion specification from preserved material when replay depends on it;
- interprets the identifiers defined by Clauses 8 to 10 only according to the meanings fixed by this draft and any exact-edition replay-relevant narrowing that does not contradict this draft;
- fails closed when replay-relevant parameters or evidence needed to interpret an identifier from Clauses 8 to 10 are missing, unresolved, or contradictory; and
- does not silently substitute another companion edition or another identifier for replay.

### 12.4 BELGI Full Python Condition Vocabulary Implementation

An implementation conforms to this document as a BELGI Full Python Condition Vocabulary Implementation if it conforms to 12.2 and 12.3.

### 12.5 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- the companion identifier of 6.1;
- the exact edition of this companion specification against which the claim is made;
- a non-empty set of supported identifiers from Clauses 8 to 10, with production support, verification support, or both stated for each identifier; and
- the date of the statement.

A statement that all identifiers are supported shall be made only when the claimed implementation has the stated production or verification support for every identifier in Clauses 8 to 10.

## 13 Security considerations

Python-oriented admission vocabulary is vulnerable to tool substitution, incomplete execution presented as success, summary-only evidence, threshold drift, scope drift, dependency-set ambiguity, interpreter mismatch, and environment mismatch.

This companion specification reduces ambiguity only when producers and verifiers preserve and enforce the replay-relevant parameters and exact-edition bindings needed to interpret the identifiers defined here.

Excluded reliance claim: this companion specification does not establish authority, correctness, or suitability of any one Python tool, report format, or execution environment.

## 14 Privacy considerations

This companion specification does not require preservation of developer identity, reviewer identity, or other personal identifiers.

When Python-oriented evidence, reports, or evaluator parameters incidentally contain personal data, applicable privacy obligations apply independently of this companion specification.
