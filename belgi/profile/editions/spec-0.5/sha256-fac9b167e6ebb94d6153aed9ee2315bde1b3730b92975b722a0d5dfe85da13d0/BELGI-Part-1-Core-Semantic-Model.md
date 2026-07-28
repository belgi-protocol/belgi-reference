# BELGI - Part 1: Core semantic model

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.5
Depends on: none
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is Part 1. It defines the core semantic model. Later parts define claim-carrier and replay-package rules, representation bindings, profiles, and companion extension rules without changing the semantic core fixed here.

## Introduction

Admission practice often preserves logs, comments, artifacts, or verdicts without preserving a single claim whose judged object, evidence state, and evaluator can be recovered and replayed as one semantic unit.

Passing checks, preserved artifacts, workflow events, or approval records can be useful operational evidence, but they do not by themselves fix a replayable admission claim. A replayable claim requires preservation of what was judged, what evidence state was made available, and what evaluator determined the verdict.

This document separates the semantic core, the preserved-claim layer, and the governance boundary. The semantic core determines verdict from a judged object, an evidence state, and an evaluator. The preserved-claim layer determines how those semantic objects are later recovered from preserved carriers. The governance boundary concerns evaluator selection, approval, and organizational reliance.

This document defines the semantic model for a replayable admission claim. It does not identify a claim with a stored verdict, with an artifact bundle, or with a bare semantic tuple alone.

This specification family is intended to comprise the following parts, under the general title _Admission claims_:

- Part 1: Core semantic model (this document);
- Part 2: Claim carriers and replay package;
- Part 3: Profiles and companion specifications; and
- Part 4: Software change admission profile.

The `spec-0.5` Working Draft family comprises Parts 1 to 4 and the six
companion specifications designated for that track in the edition source
inventory. A separately developed Part 5 operational-action profile is an
experimental working draft outside `spec-0.5`; it cannot be used to claim
conformance to this family edition.

Later parts extend the semantic core with carrier formats, replay packaging, domain profiles, and companion specifications. The semantic core fixed in this document is intended to remain stable across later parts.

Within this specification family, one implementation or party can produce or preserve carriers and another can later replay them or rely on the resulting verdict. Those role distinctions can matter operationally and architecturally, but they are not semantic sorts of the core model defined here.

This document fixes the semantic verdict as binary in order to keep the core admission result minimal and fail-closed. Richer statuses, diagnostics, confidence gradations, or operational outcomes may be preserved or declared elsewhere in this specification family, but they do not replace the semantic verdict fixed here.

This document treats evaluator identity extensionally so that replay depends on recovered decision behavior over judged objects and evidence states rather than on labels, implementation style, or declaration packaging alone. For the same reason, verdict is derived only by evaluator application and is not introduced as a separate preserved semantic primitive.

## 1 Scope

This document defines the core semantic model of an admission claim.

This document defines:

- the core semantic signature for judged objects, evidence states, and evaluators;
- the preserved-claim layer and the lifting relation;
- the relation between claim identity, evaluator identity, and replay;
- the minimum decomposition of the judged object;
- the semantic treatment of trust-boundary, governing-specification, and evidence-condition declarations when they participate in evaluator induction.

This document is applicable to admission systems that preserve a claim and later recover and replay the same semantic tuple from preserved carriers.

This document does not define:

- artifact schemas, field names, serialization rules, transport bindings, or storage mechanisms;
- replay-package closure, hashing, or storage rules;
- domain-specific condition vocabularies or failure taxonomies;
- organizational approval, policy, governance, or authorization for selecting an evaluator;
- workflow orchestration, multi-party voting, staged approval, or organizational escalation structures;
- admission-subject origination processes except insofar as preserved carriers later encode their results;
- whether a chosen evaluator satisfies external correctness, completeness, project, or organizational risk criteria.

A go verdict records the result of one evaluator applied to one judged object and one evidence state. It does not by itself assert correctness, safety, or fitness for purpose of the admission subject beyond the conditions declared in the relevant evaluator carrier.

## 2 Normative references

There are no normative references in this document.

## 3 Terms and definitions

For the purposes of this document, the following terms and definitions apply.

### 3.1 admission subject

proposed change, action, or other domain object submitted for one admission decision

### 3.2 reference context

semantic context recovered from preserved or replay-resolvable material and relative to which an admission subject is identified and judged

### 3.3 judged object

semantic object consisting of one admission subject and one reference context

### 3.4 evidence item

preserved item from which part of an evidence state is recovered

### 3.5 evidence state

semantic object representing the evidence made available to an evaluator for a judged object

### 3.6 evaluator

total binary decision function from judged objects and evidence states to verdicts

### 3.7 verdict

binary outcome obtained by applying an evaluator to a judged object and an evidence state

### 3.8 go

verdict value denoting admission relative to one evaluator

### 3.9 no-go

verdict value denoting non-admission relative to one evaluator

### 3.10 lifting

partial interpretation from preserved carrier to semantic object

### 3.11 preserved carrier

preserved representation from which a semantic object is recovered by lifting

### 3.12 judged-object carrier

preserved carrier from which a judged object is lifted

### 3.13 evidence-state carrier

preserved carrier from which an evidence state is lifted

### 3.14 evaluator carrier

preserved carrier from which an evaluator is lifted

### 3.15 declared go condition

condition declared within one evaluator carrier and bound to go determination under that evaluator carrier

### 3.16 fail-closed

property by which missing lift, invalid lift, or unsatisfied declared go condition does not support go

### 3.17 determining semantics

specification or rule set designated for a declared go condition and used to determine whether that condition is satisfied for a judged object and an evidence state

### 3.18 trust boundary

declared boundary constraining which sources, executions, or authorities contribute to one evaluator's determination scope

### 3.19 governing specification reference

declared reference to a specification or profile edition constraining one evaluator's determination semantics or scope

### 3.20 evidence-condition binding

declared relation by which preserved evidence is made relevant to evaluation of a declared go condition for one evaluator

### 3.21 semantic tuple

ordered triple of judged object, evidence state, and evaluator recovered from preserved carriers

### 3.22 admission claim

preserved designation of one judged-object carrier, one evidence-state carrier, and one evaluator carrier as the carriers from which the semantic tuple is recovered

### 3.23 constituent carrier

preserved carrier designated by an admission claim as one of the carriers from which the semantic tuple is recovered

### 3.24 claim identity

sameness relation for admission claims fixed in this document at the preserved-carrier level

### 3.25 replay

later recovery of a semantic tuple from preserved carriers through lifting

### 3.26 replayable claim

admission claim whose preserved carriers recover the same semantic tuple on repeated replay

### 3.27 undeclared ambient context

information not contained in preserved carriers yet used to determine a semantic tuple or verdict

### 3.28 immutable designator

identifier bound to exactly one referenced source edition by replay-verifiable content or integrity material rather than by mutable name, location, registry entry, or version label alone

## 4 Symbols and abbreviated terms

### 4.1 Symbols

For the purposes of this document, the following symbols apply.

| Symbol | Meaning |
| --- | --- |
| $\Sigma_{core}$ | core semantic signature |
| $J$ | set of judged objects |
| $E$ | set of evidence states |
| $F$ | set of evaluators |
| $V$ | verdict set $\{0,1\}$ |
| $\mathsf{AdmissionSubject}$ | set of admission subjects |
| $\mathsf{ReferenceContext}$ | set of reference contexts |
| $J_c$ | set of judged-object carriers |
| $E_c$ | set of evidence-state carriers |
| $F_c$ | set of evaluator carriers |
| $j_c$ | element of $J_c$ |
| $e_c$ | element of $E_c$ |
| $f_c$ | element of $F_c$ |
| $j$ | element of $J$ |
| $e$ | element of $E$ |
| $f$ | element of $F$ |
| $\lambda_J : J_c \rightharpoonup J$ | lifting from judged-object carriers to judged objects |
| $\lambda_E : E_c \rightharpoonup E$ | lifting from evidence-state carriers to evidence states |
| $\lambda_F : F_c \rightharpoonup F$ | lifting from evaluator carriers to evaluators |
| $Cond(f_c)$ | set of declared go conditions designated in evaluator carrier $f_c$ |
| $Sat(j,e,c)$ | satisfaction relation holding when judged object $j$ and evidence state $e$ satisfy declared go condition $c$ according to the determining semantics designated for $c$ |
| $\rightharpoonup$ | partial function |

### 4.2 Abbreviated terms

No abbreviated terms are listed in this document.

## 5 Conventions and requirements language

The family identifier of this Part is:

`https://belgi.dev/ids/specification/part-1`

The current draft version designator is `0.5`. The family identifier and
version designator do not by themselves identify the exact source bytes of
this edition; replay-relevant use requires an immutable designator bound to
one exact source edition.

In this document, "shall" denotes a requirement, "should" denotes a recommendation, "may" denotes permission, and "can" denotes possibility or capability.

The statements in Clauses 5 to 12 are normative unless stated otherwise.

The equality on $\mathsf{AdmissionSubject}$, $\mathsf{ReferenceContext}$, and $E$ is equality on those sets.

The equality on $J$ is componentwise equality induced by equality on $\mathsf{AdmissionSubject}$ and $\mathsf{ReferenceContext}$.

The equality on $F$ is extensional equality of total functions.

This clause fixes evaluator identity in the semantic model. It does not by itself define one runtime conformance procedure for proving universal equality over all $J \times E$.

When a proof artifact, conformance artifact, profile, or companion specification uses an evaluator equality witness instead of proving universal extensional equality over all $J \times E$, the artifact shall identify the witness basis and the claim boundary.

A finite-domain evaluator equality witness shall identify the proof domain before evaluation, the domain-selection rule or generator, the evaluator material to which the witness applies, and the result table over the selected domain.

A finite-domain evaluator equality witness shall not be described as universal evaluator equality unless the selected domain is the whole semantic domain over which the evaluator is defined.

Accordingly, references in this document to the "same" judged object, evidence state, evaluator, admission subject, or reference context are references to equality on the relevant set as fixed in this clause.

The verdict value $1$ denotes go and the verdict value $0$ denotes no-go.

## 6 Layering and semantic boundary

### 6.1 General

This document distinguishes:

- the semantic core;
- the preserved-claim layer;
- the governance boundary.

### 6.2 Semantic core

The semantic core contains judged objects, evidence states, evaluators, and verdicts derived by evaluator application.

At this layer, verdict is not a separately preserved semantic primitive.

The semantic core fixes only the objects and relations needed to state what admission decision was made.

### 6.3 Preserved-claim layer

The preserved-claim layer contains judged-object carriers, evidence-state carriers, evaluator carriers, and lifting from those carriers to semantic objects.

At this layer, the concern is not only that bytes or artifacts exist, but that they preserve sufficient content to recover the semantic tuple.

### 6.4 Governance boundary

Selection, approval, justification, or organizational authorization of an evaluator is outside the semantic model defined here.

This document therefore distinguishes the meaning of an evaluator from the reasons an organization had for relying on it.

### 6.5 Ambient-context exclusion

No semantic tuple or verdict defined by this document shall depend on undeclared ambient context.

Accordingly, repository history, local machine state, human recollection, mutable aliases, descriptive prose, or undeclared workflow convention do not determine semantic content unless they are explicitly incorporated into preserved carriers.

### 6.6 Profile and companion boundary

A conforming profile may identify domain-specific admission-subject and
reference-context material and define how that material induces the two
components of a judged object. A conforming profile or companion specification
may also specify identifier forms, condition kinds, condition taxonomies,
determining semantics, or evidence-condition-binding forms.

A conforming profile or companion specification shall not alter the equality fixed in Clause 5, the core semantic signature, the totality of evaluators, extensional evaluator identity, the fail-closed law, replay semantics, or preservation-relative claim identity fixed in this document.

### 6.7 Evaluator-related declarations

This document treats trust boundaries, governing specification references, and evidence-condition bindings as evaluator-related declarations.

This document does not introduce separate top-level semantic sorts for those declarations.

### 6.8 Conceptual flow

The conceptual flow fixed by this document is:

- preservation of judged-object, evidence-state, and evaluator carriers;
- lifting of those carriers into $j$, $e$, and $f$;
- derivation of verdict only as $f(j,e)$;
- replay as later recovery of the same semantic tuple.

This flow excludes verdict-only preservation as a sufficient account of a replayable admission claim.

## 7 Core semantic signature

### 7.1 Signature

The core semantic signature shall be:

$$
\Sigma_{core} = \langle J, E, F \rangle
$$

### 7.2 Verdict set

The verdict set shall be:

$$
V = \{0,1\}
$$

### 7.3 Evaluator space

Each evaluator $f$ in $F$ shall be a total function:

$$
f : J \times E \to V
$$

### 7.4 Derived verdict

For $j$ in $J$, $e$ in $E$, and $f$ in $F$, the semantic verdict shall be derived only as:

$$
v = f(j,e)
$$

### 7.5 No separate verdict primitive

The core semantic signature shall not introduce a fourth primitive sort for verdict records, verdict objects, or verdict carriers.

Within the semantic core, verdict is only the result of evaluator application.

## 8 Evaluator semantics

### 8.1 Extensional evaluator identity

For evaluators $f_1$ and $f_2$ in $F$:

Two evaluators are identical if and only if they yield the same verdict for every judged object in $J$ and every evidence state in $E$.

$$
f_1 = f_2 \iff \forall j \in J,\; \forall e \in E,\; f_1(j,e) = f_2(j,e)
$$

### 8.2 Declaration-sensitive distinctions

Differences among evaluator carriers do not by themselves create different evaluators.

Differences in trust boundary, governing specification reference, binding declarations, labels, or explanatory text change evaluator identity only when lifting yields a different verdict map.

### 8.3 Different carriers, same evaluator

Distinct evaluator carriers can lift to the same evaluator.

Evaluator identity and evaluator-carrier identity shall therefore remain distinct.

### 8.4 State-machine or abstract-machine realization

An implementation may realize an evaluator as a state machine, an abstract machine, a transition system, a rules engine, or another executable mechanism.

Such realization is semantically relevant in this document only through the total function in $F$ that it induces over judged objects and evidence states.

This document does not define lifecycle states, transition alphabets, or operational event sequencing for evaluator realization.

## 9 Preserved claims and lifting

### 9.1 Carrier domains

There shall exist sets $J_c$, $E_c$, and $F_c$ of judged-object carriers, evidence-state carriers, and evaluator carriers.

An admission claim shall designate one judged-object carrier $j_c$ in $J_c$, one evidence-state carrier $e_c$ in $E_c$, and one evaluator carrier $f_c$ in $F_c$ as its constituent carriers.

At replay time, an admission claim's designation of a constituent carrier shall retrieve the representation that was originally preserved. If it retrieves a different representation, the designated carrier is not recovered.

The form of the designation by which an admission claim refers to a constituent carrier, and the mechanisms for assuring content integrity across that designation, are outside the scope of this document.

### 9.2 Partial lifting

The preserved-claim layer shall be connected to the semantic core by the following partial functions:

$$
\lambda_J : J_c \rightharpoonup J
$$

$$
\lambda_E : E_c \rightharpoonup E
$$

$$
\lambda_F : F_c \rightharpoonup F
$$

A lift succeeds exactly when the relevant partial function is defined on the preserved carrier.

### 9.3 Recovered semantic tuple and verdict

If $\lambda_J(j_c)$, $\lambda_E(e_c)$, and $\lambda_F(f_c)$ are all defined, then the preserved claim recovers the semantic tuple:

$$
(j,e,f) = (\lambda_J(j_c), \lambda_E(e_c), \lambda_F(f_c))
$$

and the semantic verdict:

$$
v = f(j,e)
$$

If any of those lifts is undefined, no semantic tuple and no semantic verdict are recovered.

### 9.4 Claim identity

Claim identity shall be preservation-relative.

Two admission claims can recover the same semantic tuple and the same verdict and still remain distinct claims when their preserved carriers are distinct.

This document defines no weaker canonical identity relation than preservation-relative claim identity.

### 9.5 Non-owning preserved material

Preserved prose, labels, filenames, transport metadata, and other explanatory material that is not designated as part of a constituent carrier shall not determine the semantic tuple, the semantic verdict, or claim identity.

## 10 Core behavioral law

### 10.1 Judged-object decomposition

There shall exist sets $\mathsf{AdmissionSubject}$ and
$\mathsf{ReferenceContext}$ such that:

$$
J = \mathsf{AdmissionSubject} \times \mathsf{ReferenceContext}
$$

Each judged object $j$ in $J$ shall therefore contain one admission subject and
one reference context.

The admission subject identifies what is proposed for admission. The reference
context identifies the semantic context relative to which that subject is
interpreted and judged. A reference context can include an identified state,
target, environment, or other domain context, but it shall not depend on
undeclared ambient context.

Material belongs in the admission subject or reference context only when it
determines the identity or interpretation of that component. A fact shall not
belong to $J$ solely because it affects condition satisfaction or the verdict;
such a fact belongs to the evidence state or evaluator according to its
semantic role.

This document fixes the decomposition of judged objects into admission subject
and reference context. It does not further decompose either component.

### 10.2 Evidence-state reading

An evidence state is a semantic object made available to an evaluator.

This document does not fix the internal structure of $E$ and does not identify an evidence state with the bare existence of evidence items.

The preserved existence of evidence items by itself shall not determine satisfaction of a declared go condition.

### 10.3 Evaluator-carrier content

An evaluator carrier preserves material from which one evaluator is induced under this document.

Within that preserved material, this document identifies declared go conditions, trust boundaries, governing specification references, and evidence-condition bindings as evaluator-related declarations that can be semantically relevant to the fail-closed law.

Each declared go condition in $Cond(f_c)$ shall be designated by an identifier that is unique within that evaluator carrier.

This document does not require a particular identifier form. The form of that identifier shall be determined by the relevant carrier format or by a conforming profile or companion specification.

Those declarations affect evaluator identity only insofar as lifting changes the induced verdict map.

Trust boundaries, governing specification references, and evidence-condition bindings contribute to evaluator semantics only insofar as they affect the determining semantics of declared go conditions or the evaluation of $Sat(j,e,c)$.

This document does not define condition kinds, condition taxonomies, or binding-relation kinds. Those vocabularies are reserved to conforming profiles or companion specifications.

### 10.4 Binding relation

Evidence-condition binding shall be evaluator-relative.

The same preserved evidence items can participate in different bindings under different evaluator carriers.

Raw evidence does not bind itself.

### 10.5 Fail-closed law

This document does not define a universal satisfaction calculus for declared go conditions.

For each $c$ in $Cond(f_c)$, the relevant evaluator carrier shall designate the determining semantics of $Sat(j,e,c)$, either directly or by reference to a conforming profile or companion specification.

Where determining semantics are designated by reference, the reference shall identify an immutable designator and its resolution shall be determinable from preserved carrier material without undeclared ambient context.

An identifier whose resolution can change through registry update, network retrieval, local configuration, branch or tag movement, URL rewriting, or another mutable lookup shall not by itself satisfy this requirement.

Resolution of referenced determining semantics shall fail closed when the preserved material does not bind the exact referenced source edition or when the resolved material is inconsistent with that binding.

If $Cond(f_c)$ is empty, that evaluator carrier shall not support go.

If no determining semantics are designated for a declared go condition, that condition shall not support go.

If referenced determining semantics cannot be determined from preserved carrier material without undeclared ambient context, that condition shall not support go.

If $\lambda_F(f_c) = f$, then for every $j$ in $J$ and every $e$ in $E$:

$$
f(j,e) = 1 \Rightarrow \forall c \in Cond(f_c): Sat(j,e,c)
$$

### 10.6 Lift failure and support for go

If any of $\lambda_J(j_c)$, $\lambda_E(e_c)$, or $\lambda_F(f_c)$ is undefined, the preserved claim shall not support go.

## 11 Replay semantics

### 11.1 Replay object

Replay shall operate on preserved carriers rather than on a verdict field alone.

### 11.2 Successful replay

Replay is successful when repeated lifting of the same preserved carriers recovers the same semantic tuple:

$$
(j,e,f)
$$

Here, the "same semantic tuple" is determined by equality on $J$, $E$, and $F$ as fixed in Clause 5.

The same verdict then follows as a consequence of evaluator application.

This document fixes semantic equality of the recovered tuple.

This document does not define a general proof procedure for cross-implementation equivalence of replay results, any verdict-level interoperability obligation, or any exact-edition corpus or machine-checkable procedure for checking recovered-tuple renderings across implementations.

### 11.3 Replay failure

Replay fails when:

- a required preserved carrier cannot be read;
- a required lift is undefined;
- the retrieved representation of a designated constituent carrier differs from the originally preserved representation;
- repeated lifting recovers a different semantic tuple;
- undeclared ambient context is required to recover the tuple or verdict.

### 11.4 Replayable claim

An admission claim is replayable if and only if replay of the same preserved carriers recovers the same semantic tuple.

## 12 Conformance

### 12.1 Conformance classes

The following conformance classes are defined:

- BELGI Core Semantic Implementation;
- BELGI Replay Semantic Implementation.

### 12.2 BELGI Core Semantic Implementation

An implementation conforms to this document as a BELGI Core Semantic Implementation if:

- it represents the semantic core as $\Sigma_{core} = \langle J, E, F \rangle$ with each evaluator total from $J \times E$ to $V$;
- it treats judged objects in accordance with 10.1, such that $J = \mathsf{AdmissionSubject} \times \mathsf{ReferenceContext}$;
- it applies equality on $J$, $\mathsf{AdmissionSubject}$, $\mathsf{ReferenceContext}$, $E$, and $F$ in accordance with Clause 5;
- it does not allow a profile or companion specification to alter the equality fixed in Clause 5, the core semantic signature, the totality of evaluators, extensional evaluator identity, the fail-closed law, replay semantics, or preservation-relative claim identity;
- it treats an admission claim as a preserved designation of constituent carriers rather than as a bare verdict or a bare semantic tuple;
- it treats an admission claim as designating one constituent judged-object carrier, one constituent evidence-state carrier, and one constituent evaluator carrier;
- it recovers a semantic tuple only through defined lifting from $j_c$, $e_c$, and $f_c$;
- it derives semantic verdict only as $f(j,e)$ after successful lifting;
- it treats claim identity as preservation-relative and does not reduce claim identity to semantic-tuple identity;
- it does not allow preserved material not designated as part of a constituent carrier to determine the semantic tuple, the semantic verdict, or claim identity;
- it treats trust boundary, governing specification reference, and evidence-condition binding as evaluator-related declarations rather than as independent top-level semantic sorts;
- it treats trust boundary, governing specification reference, and evidence-condition binding as contributing to evaluator semantics only through the determining semantics of declared go conditions or the evaluation of $Sat(j,e,c)$;
- it requires each declared go condition to be uniquely identifiable within the relevant evaluator carrier;
- it determines satisfaction of each declared go condition only according to determining semantics designated by the relevant evaluator carrier or by a referenced conforming profile or companion specification;
- it does not treat family identifiers, version labels, registry entries, locators, or local resolver defaults as substitutes for immutable designators where referenced determining semantics are replay-relevant;
- it does not support go when an evaluator carrier designates no declared go conditions;
- it excludes undeclared ambient context from tuple and verdict determination;
- it fails closed when a required lift is undefined or when the retrieved representation of a designated constituent carrier differs from the originally preserved representation; and
- it fails closed when one or more declared go conditions are not satisfied.

NOTE Extensional evaluator identity remains part of the semantic model fixed by Clause 5 and protected by 12.2. Conformance review under this document is evaluated through preservation-relative tuple recovery and replay rather than through one runtime proof of universal evaluator equality over all $J \times E$.

### 12.3 BELGI Replay Semantic Implementation

An implementation conforms to this document as a BELGI Replay Semantic Implementation if:

- it conforms as a BELGI Core Semantic Implementation;
- it replays from preserved carriers;
- it recovers the same semantic tuple for replayable claims;
- it fails closed when replay cannot recover the same semantic tuple.

### 12.4 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- each conforming profile or companion specification on which the claim depends, including its immutable designator, or state that none is used;
- each referenced source used to fix determining semantics, including its immutable designator, or state that none is used;
- the date of the statement.

## 13 Security and trust considerations

This document's primary security and trust risks arise when replayable meaning is inferred from material other than the preserved carriers from which the semantic tuple is recovered. A preserved verdict, explanatory summary, or workflow trace can create the appearance of continuity while leaving the judged object, evidence state, or evaluator unrecoverable or semantically altered.

Ambient-context injection can arise when repository history, machine-local state, mutable aliases, human recollection, or undeclared workflow convention are allowed to participate in tuple or verdict recovery. Clauses 6.5, 9.5, and 11.3 exclude that pattern by keeping undeclared ambient context and non-owning preserved material from determining semantic content or successful replay.

Evaluator-substitution risk can arise when differences among evaluator carriers are treated as normatively significant without showing that lifting recovers a different verdict map, or when differently labelled carriers are treated as interchangeable without preserving extensional identity. Clauses 8.1 to 8.3 confine evaluator identity to the recovered total function over judged objects and evidence states.

Referenced-semantics substitution can arise when a registry entry, URL, version label, branch, tag, or local resolver result is treated as if it fixed the referenced source used to determine evaluator meaning. Clauses 10.5 and 12.2 require replay-verifiable exact-source binding and fail-closed handling of unresolved or inconsistent bindings.

Lift-manipulation or vacuous-satisfaction risk can arise when undefined lifts, missing determining semantics, or empty declared-go-condition sets are tolerated operationally as if they still supported go. Clauses 10.5 and 10.6 keep those cases fail-closed so that missing recovery or under-specified evaluator content cannot silently produce admission.

This document does not require preservation of personal identifiers. When preserved carriers incidentally contain personal data, applicable privacy obligations apply independently of this document.

This document does not define user-facing interfaces, locale-sensitive rendering, or natural-language presentation requirements. Accessibility and internationalization obligations therefore arise only in implementations or companion surfaces that present BELGI material to users.

Excluded reliance claim: this document preserves the meaning of one admission claim but does not establish external suitability, safety, or organizational acceptance of a recovered evaluator.
