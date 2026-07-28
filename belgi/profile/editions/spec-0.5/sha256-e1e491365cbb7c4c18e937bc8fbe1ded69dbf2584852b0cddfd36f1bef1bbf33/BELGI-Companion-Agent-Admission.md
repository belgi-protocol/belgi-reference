# BELGI - Companion specification: Agent admission vocabulary

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications; BELGI - Part 4: Software change admission profile
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is a BELGI companion specification. It defines reusable agent-admission condition, evidence-kind, source-material-role, environment-envelope, and evaluator-parameter vocabulary for use with BELGI profiles and evaluator carriers.

## Introduction

BELGI - Part 3 reserves the extension points at which profiles and companion specifications may add domain-specific vocabulary without reopening the semantic authority of BELGI - Part 1 or the replay authority of BELGI - Part 2.

This document uses that extension surface for preserved agent-decision admission. It fixes exact-edition-local compact identifier vocabularies and minimum meanings for replay over preserved agent-decision evidence.

This document is intentionally not a live-agent execution replay specification. It does not make any model provider, prompt renderer, tool runner, orchestration loop, external API, or stochastic execution environment normative. It defines vocabulary and fail-closed constraints for deterministic verdict replay over preserved artifacts.

## 1 Scope

This document defines a BELGI companion specification for agent-admission vocabulary.

This document defines:

- agent-admission condition identifiers;
- agent-admission evidence-kind identifiers;
- agent-admission source-material-role identifiers;
- agent-admission environment-envelope identifiers;
- agent-admission evaluator-parameter identifiers; and
- companion-specific conformance classes.

This document is applicable where a BELGI profile or replay-relevant evaluator material uses preserved agent-decision evidence to support a software-admission verdict.

This document does not define:

- live model invocation or replay;
- prompt rendering semantics;
- tool execution semantics;
- one mandatory model provider, agent framework, tool protocol, policy format, or orchestration runtime;
- one universal agent-correctness criterion;
- one representation-specific carrier schema or serialization binding; or
- verdict-level interoperability for a profile by itself.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.5, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.5, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.5, 2026-07-21
- BELGI - Part 4: Software change admission profile, Version 0.5, 2026-07-21

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in BELGI - Part 1, BELGI - Part 2, BELGI - Part 3, BELGI - Part 4, and the following apply.

### 3.1 agent-decision record

preserved evidence material describing one agent-produced admission decision or recommendation

### 3.2 tool-use summary

preserved evidence material summarizing tool calls, tool results, or tool-use facts relied on by an agent-decision record

### 3.3 agent-admission condition identifier

term identifier naming one agent-admission condition defined by this companion specification

### 3.4 agent-admission evidence-kind identifier

term identifier naming one agent-admission evidence kind defined by this companion specification

### 3.5 agent-admission source-material-role identifier

term identifier naming one agent-admission role of preserved source material defined by this companion specification

### 3.6 agent-admission environment-envelope identifier

term identifier naming one replay-relevant agent-admission environment fact defined by this companion specification

### 3.7 agent-admission evaluator-parameter identifier

term identifier naming one replay-relevant evaluator parameter defined by this companion specification

## 4 Symbols and abbreviated terms

### 4.1 Symbols

No symbols are listed in this document.

### 4.2 Abbreviated terms

No abbreviated terms are listed in this document.

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 13 are normative unless stated otherwise.

This document owns only the companion vocabulary and constraints fixed in Clauses 6 to 12. It does not alter the semantic authority of BELGI - Part 1, the replay authority of BELGI - Part 2, the extension-governance authority of BELGI - Part 3, or the software-change profile authority of BELGI - Part 4.

## 6 Companion identity and declaration

### 6.1 Companion identifier and version designator

The companion identifier of this companion specification is:

`https://belgi.dev/ids/companion/agent-admission`

The current draft version designator is:

`0.5`

The owning publisher or change controller of this companion specification is:

`belgi`

The compact identifier tokens defined by this companion are partitioned into
the named vocabularies `condition`, `evidence-kind`, `source-material-role`,
`environment-envelope`, and `evaluator-parameter`. The namespace identity of
each vocabulary is the ordered pair of the companion identifier in 6.1 and that
vocabulary name.

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
- 8.4 condition vocabulary;
- 8.5 trust-boundary vocabulary;
- 8.8 environment-envelope vocabulary; and
- 8.9 evaluator declaration parameter vocabulary.

This draft does not define binding relation kinds, replay-policy refinements, representation-specific schemas, or machine-checkable conformance corpora.

### 6.4 Machine-readable material

This draft defines no separate machine-readable declaration material beyond the local compact identifier tokens and meanings fixed by this draft.

### 6.5 Compatibility statement

This `0.5` Working Draft succeeds exact `0.4`. This companion specification
declares no backward compatibility, forward compatibility, or replay
substitution with its predecessor.

## 7 General vocabulary rules

### 7.1 Preserved-evidence rule

The identifiers defined by this companion specification apply to preserved agent-admission evidence. They do not require, authorize, or replay live model execution.

### 7.2 No authority-by-agent rule

An artifact shall not be treated as authoritative merely because it was produced by an agent, model, assistant, workflow, or tool runner.

Boundary participation, authority level, accepted decision values, required tool-use facts, and policy identity shall be made explicit by the applicable BELGI profile, evaluator declaration, or exact-edition referenced source.

### 7.3 Exact dependency rule

If replay-relevant interpretation depends on this companion specification, the exact edition of this companion specification shall be identified and preserved in accordance with BELGI - Part 2 and BELGI - Part 3.

If replay-relevant interpretation depends on a model identity, policy identity, tool-set identity, prompt-template identity, or external determining-semantics source, that material shall be exact-edition identified or otherwise preserved as replay-relevant material in accordance with BELGI - Part 2.

### 7.4 No hidden stochastic replay rule

A verifier shall not infer satisfaction of an agent-admission condition by re-running a live model, live tool, mutable agent policy, mutable prompt template, or external service unless a later BELGI specification explicitly defines such replay and exact-edition constraints.

### 7.5 Summary-only restriction

Summary-only agent status, natural-language approval text, chat transcript fragments, or dashboard labels shall not by themselves determine the meaning of an agent-admission condition when replay depends on underlying decision evidence, tool-use evidence, policy identity, or environment facts.

## 8 Agent-admission condition vocabulary

### 8.1 General

This companion specification defines the following agent-admission condition identifiers.

### 8.2 Condition identifiers

| Condition identifier | Meaning |
| --- | --- |
| `belgi.agent-admission.condition.agent-decision-accepted` | preserved agent-decision evidence satisfies the declared outcome policy for the agent decision under the selected profile and companion exact editions |
| `belgi.agent-admission.condition.tool-use-recorded` | preserved evidence contains the declared minimum tool-use summary material required by the evaluator declaration |

### 8.3 Condition interpretation rules

`belgi.agent-admission.condition.agent-decision-accepted` shall be interpreted through replay-relevant outcome-policy declaration material. The accepted decision values, evidence bindings, minimum counts, and any threshold-like constraints shall be explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2.

`belgi.agent-admission.condition.tool-use-recorded` shall be interpreted through replay-relevant evidence-presence declaration material. The required evidence kind, source constraints, binding relation, and minimum count shall be explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2.

The condition identifiers of 8.2 do not by themselves fix:

- one mandatory agent framework;
- one mandatory agent decision format;
- one mandatory tool-use trace format;
- one mandatory prompt template;
- one mandatory policy language; or
- one mandatory model provider.

Those matters shall be made explicit by the applicable profile or evaluator declaration when replay-relevant.

### 8.4 Fail-closed interpretation

If replay-relevant material using one of the condition identifiers in 8.2 omits a required policy identity, accepted decision value, evidence binding, tool-use requirement, model identity, prompt-template identity, or tool-set identity needed for interpretation, that condition shall not support go.

If required agent-decision evidence or tool-use evidence is absent, unresolved, non-authoritative under the selected profile, or not interpretable under the declared replay-relevant rules, that condition shall not support go.

## 9 Agent-admission evidence-kind vocabulary

### 9.1 General

This companion specification defines the following agent-admission evidence-kind identifiers.

### 9.2 Evidence-kind identifiers

| Evidence-kind identifier | Meaning |
| --- | --- |
| `belgi.agent-admission.evidence.agent-decision-record` | preserved record or equivalent preserved result describing an agent-produced admission decision or recommendation |
| `belgi.agent-admission.evidence.tool-use-summary` | preserved record or equivalent preserved result describing tool-use facts relied on by an agent-decision record |

### 9.3 Evidence-kind interpretation rules

An agent-decision record shall not be treated as accepted merely because it contains favorable natural-language text. The replay-relevant accepted decision value or outcome rule shall be explicit in evaluator material or in an exact-edition referenced source.

A tool-use summary shall not be treated as complete merely because a tool name, URL, or transcript label appears in preserved material. The replay-relevant tool-use requirement shall be explicit in evaluator material or in an exact-edition referenced source.

## 10 Agent-admission source and environment vocabulary

### 10.1 Source-material-role identifiers

This companion specification defines the following agent-admission source-material-role identifiers.

| Source-material-role identifier | Meaning |
| --- | --- |
| `belgi.agent-admission.source.agent-output-record` | preserved source material containing the agent output, decision, or recommendation used by the evaluator |
| `belgi.agent-admission.source.tool-trace-record` | preserved source material containing tool-call or tool-result facts used by the evaluator |
| `belgi.agent-admission.source.policy-record` | preserved source material identifying or defining the admission policy used to interpret the agent-decision evidence |

### 10.2 Environment-envelope identifiers

This companion specification defines the following agent-admission environment-envelope identifiers.

| Environment-envelope identifier | Meaning |
| --- | --- |
| `belgi.agent-admission.environment.agent-model-identity` | identifies the model, model family, model snapshot, or equivalent agent model identity relevant to preserved agent-decision evidence |
| `belgi.agent-admission.environment.agent-policy-identity` | identifies the policy, policy edition, policy rule set, or equivalent policy identity relevant to preserved agent-decision evidence |
| `belgi.agent-admission.environment.agent-tool-set-identity` | identifies the tool set, tool catalog, tool permission set, or equivalent tool-set identity relevant to preserved agent-decision evidence |
| `belgi.agent-admission.environment.agent-prompt-template-identity` | identifies the prompt template, system instruction set, prompt bundle, or equivalent prompt-template identity relevant to preserved agent-decision evidence |

### 10.3 Source and environment interpretation rules

The identifiers of 10.1 and 10.2 classify replay-relevant roles and facts. They do not by themselves establish trust, authority, correctness, or completeness.

When a condition in 8.2 depends on an agent model identity, policy identity, tool-set identity, or prompt-template identity, the corresponding environment-envelope fact shall be preserved or resolved by replay-relevant material.

Mutable aliases, provider product names, branch names, prompt labels, dashboard titles, policy names, tool names, or model nicknames shall not by themselves satisfy the identifiers of 10.2.

## 11 Agent-admission evaluator-parameter vocabulary

### 11.1 General

This companion specification defines the following replay-relevant evaluator-parameter identifiers.

### 11.2 Evaluator-parameter identifiers

| Evaluator-parameter identifier | Meaning |
| --- | --- |
| `belgi.agent-admission.parameter.accepted-decision-value` | identifies the decision value, outcome value, or equivalent normalized value accepted by `belgi.agent-admission.condition.agent-decision-accepted` |
| `belgi.agent-admission.parameter.require-tool-use-summary` | identifies whether and how tool-use summary material is required by `belgi.agent-admission.condition.tool-use-recorded` |

### 11.3 Parameter-usage rules

`belgi.agent-admission.parameter.accepted-decision-value` shall be made explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2 when `belgi.agent-admission.condition.agent-decision-accepted` is used and the accepted value is not otherwise fixed by the selected profile declaration.

`belgi.agent-admission.parameter.require-tool-use-summary` shall be made explicit in replay-relevant evaluator material or in exact-edition referenced sources preserved in accordance with BELGI - Part 2 when `belgi.agent-admission.condition.tool-use-recorded` is used and the tool-use requirement is not otherwise fixed by the selected profile declaration.

## 12 Profile-use constraints

### 12.1 General

A BELGI profile, evaluator declaration, or replay verifier using this companion specification shall preserve the meanings of the identifiers defined in Clauses 8 to 11.

### 12.2 No silent narrowing or widening

A profile or evaluator declaration shall not silently narrow or widen the meaning of an agent-admission condition identifier, evidence-kind identifier, source-material-role identifier, environment-envelope identifier, or evaluator-parameter identifier defined by this companion specification.

If narrower meaning is required, the profile or evaluator declaration shall make that narrowing explicit by exact-edition referenced rules that do not contradict this companion specification.

### 12.3 Excluded agent-execution claims

Use of this companion specification shall not be presented as proof that an agent made a correct decision, that a live model execution is reproducible, or that a model provider, tool, prompt, or policy is authoritative or suitable for external reliance.

This companion specification supports deterministic replay over preserved admission evidence. It does not validate external suitability of the agent that produced that evidence.

## 13 Conformance

### 13.1 Conformance classes

The following conformance classes are defined:

- BELGI Agent Admission Vocabulary-aware Producer;
- BELGI Agent Admission Vocabulary-aware Verifier; and
- BELGI Full Agent Admission Vocabulary Implementation.

For the purposes of this clause, production support for an identifier means the capability to emit at least one instance that satisfies every applicable requirement of Clauses 7 to 12. Verification support means the capability to accept such a conforming instance and fail closed on an instance that violates an applicable requirement of Clauses 7 to 12.

### 13.2 BELGI Agent Admission Vocabulary-aware Producer

An implementation conforms to this document as a BELGI Agent Admission Vocabulary-aware Producer if it:

- has production support for at least one identifier defined by Clauses 8 to 11;
- when emitting an identifier defined by Clauses 8 to 11, uses that identifier exactly as defined by this draft;
- makes explicit any replay-relevant accepted decision value, evidence binding, tool-use requirement, policy identity, model identity, prompt-template identity, or tool-set identity needed to interpret the emitted identifier;
- preserves the exact edition of this companion specification whenever replay-relevant interpretation depends on it; and
- does not treat omitted replay-relevant parameters or environment facts as if they were satisfied by default.

### 13.3 BELGI Agent Admission Vocabulary-aware Verifier

An implementation conforms to this document as a BELGI Agent Admission Vocabulary-aware Verifier if it:

- has verification support for at least one identifier defined by Clauses 8 to 11;
- identifies the exact edition of this companion specification from preserved material when replay depends on it;
- interprets the identifiers defined by Clauses 8 to 11 only according to the meanings fixed by this draft and any exact-edition replay-relevant narrowing that does not contradict this draft;
- fails closed when replay-relevant parameters, environment facts, source material, or evidence needed to interpret an identifier from Clauses 8 to 11 are missing, unresolved, or contradictory; and
- does not silently substitute live model execution, another companion edition, another source identifier, or another condition identifier for replay.

### 13.4 BELGI Full Agent Admission Vocabulary Implementation

An implementation conforms to this document as a BELGI Full Agent Admission Vocabulary Implementation if it conforms to 13.2 and 13.3.

### 13.5 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- the companion identifier of 6.1;
- the exact edition of this companion specification against which the claim is made;
- a non-empty set of supported identifiers from Clauses 8 to 11, with production support, verification support, or both stated for each identifier; and
- the date of the statement.

A statement that all identifiers are supported shall be made only when the claimed implementation has the stated production or verification support for every identifier in Clauses 8 to 11.

## 14 Security considerations

Agent-admission vocabulary is vulnerable to live-execution substitution, prompt drift, policy drift, model alias drift, tool-set drift, incomplete tool traces, summary-only approvals, transcript cherry-picking, and authority-by-agent confusion.

This companion specification reduces ambiguity only when producers and verifiers preserve and enforce the replay-relevant parameters, environment facts, source material, evidence bindings, and exact-edition dependencies needed to interpret the identifiers defined here.

Excluded reliance claim: this companion specification does not establish authority, correctness, or suitability of any agent, model, prompt, policy, tool, orchestration framework, or provider.

## 15 Privacy considerations

This companion specification does not require preservation of user identity, developer identity, reviewer identity, model-provider account identity, prompt text, or conversation content except where selected profile or evaluator material makes such content replay-relevant.

When agent-admission evidence, prompts, transcripts, tool outputs, or policy records incidentally contain personal data, applicable privacy obligations apply independently of this companion specification.
