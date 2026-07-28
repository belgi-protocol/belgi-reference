# BELGI - Companion specification: Package integrity anchor verification

Date: 2026-07-21
Status: Working Draft
Stability: Draft
Version: 0.4
Depends on: BELGI - Part 1: Core semantic model; BELGI - Part 2: Claim carriers and replay package; BELGI - Part 3: Profiles and companion specifications
Publication status: Working Draft

## Foreword

BELGI is a multi-part specification family for preserved and replayable admission claims.

This document is a BELGI companion specification. It defines the exact-edition verification surface by which a package-integrity anchor authenticates a designated package-integrity manifest.

This document is a member of the coherent `spec-0.4` Working Draft family.
The exact `spec-0.3` source edition remains immutable and is not replaced by
this source.

## Introduction

BELGI - Part 2 requires a replay package to expose a package-integrity manifest and a package-integrity anchor, but it does not assign signer authorization policy or organizational trust policy.

BELGI - Part 3 reserves the extension point by which representation-specific validation constraints and machine-checkable verification surfaces may be fixed without reopening BELGI semantic authority or replay authority.

This companion specification uses that extension surface to fix the package-integrity-anchor verification method and the verification-key text grammar for this draft. It does not standardize a JSON Schema or another serialized carrier binding.

## 1 Scope

This document defines a BELGI companion specification for package-integrity-anchor verification.

This document defines:

- one exact-edition package-integrity-anchor verification method surface;
- one SHA-256 source-binding contract, verification-key grammar, signature encoding, and pure Ed25519 verification procedure for that method; and
- companion-specific conformance classes.

This document is applicable where replay depends on a package-integrity anchor to authenticate a designated package-integrity manifest.

This document does not define:

- signer authorization policy, trusted-signer registries, revocation policy, or organizational acceptance criteria for signers;
- profile condition vocabulary, evidence-kind vocabulary, trust-boundary vocabulary, or replay-policy refinements;
- representation-specific carrier schemas, JSON Schema dialects, or serialized field mappings; or
- one universal outer transport or package container format.

## 2 Normative references

The following documents are referred to in the text in such a way that some or all of their content constitute requirements of this document.

- BELGI - Part 1: Core semantic model, Version 0.4, 2026-07-21
- BELGI - Part 2: Claim carriers and replay package, Version 0.4, 2026-07-21
- BELGI - Part 3: Profiles and companion specifications, Version 0.4, 2026-07-21
- FIPS PUB 180-4, Secure Hash Standard
- RFC 4648, The Base16, Base32, and Base64 Data Encodings
- RFC 8032, Edwards-Curve Digital Signature Algorithm (EdDSA)

## 3 Terms and definitions

For the purposes of this document, the terms and definitions given in BELGI - Part 1, BELGI - Part 2, BELGI - Part 3, and the following apply.

### 3.1 package-integrity-anchor verification method identifier

stable opaque identifier naming one package-integrity-anchor verification
method with one fixed accepted set

### 3.2 manifest authentication input

exact preserved octets of the designated package-integrity manifest over which package-integrity-anchor verification is performed

### 3.3 verification-key binding surface

preserved verification-key text plus the immutable designator by which that exact preserved verification-key text is bound for replay

### 3.4 defining-source designator

immutable designator whose URI denotes one exact referenced source edition and whose digest binds the exact octets of that same source edition

## 4 Symbols and abbreviated terms

### 4.1 Symbols

- `A_enc`: the exact 32 public-key octets
- `A`: the Edwards25519 point decoded from `A_enc`
- `B`: the Edwards25519 base point defined by RFC 8032
- `k`: the Ed25519 challenge scalar
- `L`: the prime order of `B`, namely
  `2^252 + 27742317777372353535851937790883648493`
- `M`: the exact message octets
- `O`: the Edwards25519 identity point
- `R_enc`: the first 32 octets of the signature
- `R`: the Edwards25519 point decoded from `R_enc`
- `S_enc`: the final 32 octets of the signature
- `S`: the non-negative little-endian integer decoded from `S_enc`
- `[n]P`: scalar multiplication of point `P` by integer `n`
- `||`: octet-string concatenation

### 4.2 Abbreviated terms

- EdDSA: Edwards-curve Digital Signature Algorithm
- SHA-256: the SHA-256 hash function defined by FIPS PUB 180-4

## 5 Conventions and requirements language

The verbal forms used in this document are to be interpreted as in BELGI - Part 1: Core semantic model.

The statements in Clauses 5 to 11 are normative unless stated otherwise.

Stable local requirement identifiers beginning with `PIA-` label requirements
for traceability into machine-readable material. The `PIA-` prefix is reserved
to this companion, and a retired `PIA-*` requirement identifier shall never be
reused. An identifier is not a substitute for the requirement text.

This document owns only the exact-edition verification method and validation constraints fixed in Clauses 6 to 10. It does not alter the semantic authority of BELGI - Part 1, the replay authority of BELGI - Part 2, or the extension-governance authority of BELGI - Part 3.

## 6 Companion identity and declaration

### 6.1 Companion identifier and version designator

The companion identifier of this companion specification is:

`https://belgi.dev/ids/companion/package-integrity-anchor-verification`

The current draft version designator is:

`0.4`

The owning publisher or change controller of this companion specification is:

`belgi`

### 6.2 BELGI dependency declaration

This companion specification and the BELGI documents named in Clause 2 are
members of the coherent `spec-0.4` Working Draft family.

### 6.3 Reserved extension points served

This companion specification serves the following reserved extension point of BELGI - Part 3:

- 8.11 representation-specific schemas and serialization bindings.

This draft does not define condition identifiers, evidence-kind identifiers, trust-boundary vocabulary, environment-envelope vocabulary, or replay-policy refinements.

### 6.4 Machine-readable material

Clauses 7 to 10 fix the normative verification surface of this companion edition, and Clause 11 fixes its conformance classes. The JSON representation companion owns the canonical JSON schema and serialized field mapping for this surface. A separate clause-linked cryptographic corpus supplies examples and test vectors without becoming the first authority for the method or algorithms defined here.

The cryptographic corpus covers `PIA-METHOD-001`, `PIA-SOURCE-001`,
`PIA-DIGEST-001`, `PIA-KEY-001`, `PIA-BASE64-001`, `PIA-ED25519-001`, and
`PIA-FAIL-001`. The logical replay corpus named by Part 2, 12.6 covers
`PIA-TARGET-001`; target identity is not a cryptographic operation.

Operation names, result labels, and reason codes in that corpus are corpus-local controls. They do not define replay problems, replay outcomes, a normative failure taxonomy, or failure priority. The applicable requirement text in this document remains authoritative.

An implementation schema, carrier field mapping, corpus case, or serialization binding shall not override this document.

### 6.5 Compatibility statement

This `0.4` Working Draft follows exact `0.3` without rewriting or substituting
it. The predecessor identifier
`urn:belgi:companion:package-integrity-anchor-verification` identifies only the
older predecessor family editions and is not an alias for the identifier in
6.1.

The verification-method identifier
`https://belgi.dev/ids/verification-method/package-integrity/ed25519-detached-manifest`
names the accepted set defined by exact `spec-0.3`. It is deprecated with new
use disallowed. This edition allocates the distinct successor identifier
`https://belgi.dev/ids/verification-method/package-integrity/ed25519-detached-manifest-v2`
for the accepted set defined by Clause 8. A predecessor or successor relation
between those identifiers is discovery metadata only and creates no alias,
equivalence, fallback, normalization, migration, or replay substitution.

The signature-algorithm identifier
`https://belgi.dev/ids/algorithm/signature/ed25519` continues to identify the
pure Ed25519 primitive defined for BELGI by exact `spec-0.3`. Clause 8 changes
the verification method, not that algorithm assignment. This companion
specification declares no backward compatibility, forward compatibility, or
replay substitution with a predecessor edition.

## 7 General verification rules

### 7.1 Method identity rule

A package-integrity anchor interpreted under this companion specification shall carry both the stable verification-method identifier and the defining-source designator of the exact edition that defines that method.

The verification method shall not be inferred from media type, key format, signature length, implementation default, registry discovery, or local configuration.

### 7.2 Manifest-octet rule

The signature input governed by this companion specification shall be the exact preserved octets of the designated package-integrity manifest.

No alternate canonicalization, normalization, or lossy reconstruction of the package-integrity manifest shall be substituted for that input.

### 7.3 Verification-key binding rule

The verification key used by this companion specification shall be preserved as verification-key text within the package-integrity anchor.

The verification-key designator preserved in that anchor shall bind the exact preserved verification-key text encoded as UTF-8.

A key identifier, registry record, account identifier, certificate label, URL, local trust-store entry, or verifier default shall not by itself satisfy the verification-key binding rule.

### 7.4 Signature-algorithm rule

The package-integrity anchor shall carry both the stable signature-algorithm
identifier and the defining-source designator of the exact source that defines
that algorithm assignment.

That algorithm identifier names the pure Ed25519 primitive. It does not select
the verification method, its accepted set, its public-key validity predicate,
or its verification equation. Those method obligations are owned by the
stable verification-method identifier and exact method source required by
7.1 and fixed by Clause 8.

The stable algorithm identifier shall not substitute for the defining-source designator, and the defining-source designator shall not substitute for the stable algorithm identifier.

### 7.5 Anchor target-binding rule

The package-integrity anchor shall preserve the package identifier and the
designated package-integrity-manifest member as consistency bindings. After the
anchor authenticates the manifest and that manifest's binding authenticates the
claim record, each anchor value shall compare equal to the corresponding value
in that integrity-recovered claim record, and the manifest-member value shall
identify the exact manifest member authenticated under 7.2.

The comparison is exact after representation decoding. Trimming, case folding,
Unicode normalization, alias resolution, and inference from a filename,
location, media type, or registry entry are prohibited. These fields do not
select the manifest, verification method, algorithm, or verification key. A
mismatch shall fail closed under the Part 2 replay problem and priority rules.

Requirement identifier: `PIA-TARGET-001`.

### 7.6 Fail-closed rule

If a required stable method or algorithm identifier, defining-source designator, verification-key binding surface, designated manifest input, or signature value is missing, malformed, unknown, unsupported, prohibited, or inconsistent with the exact preserved material, replay shall fail closed.

## 8 Ed25519 detached manifest-signature verification

### 8.1 Verification method and identifiers

This companion defines exactly one package-integrity-anchor verification method:

`https://belgi.dev/ids/verification-method/package-integrity/ed25519-detached-manifest-v2`

The method uses exactly these algorithm identifiers:

```text
https://belgi.dev/ids/algorithm/digest/sha-256
https://belgi.dev/ids/algorithm/signature/ed25519
```

These strings are opaque stable identifiers and shall be compared as exact strings. A verifier shall not dereference them, follow redirects, infer meaning from path segments, case-fold, percent-normalize, or accept a URI variant.

The predecessor method identifier named in 6.5 does not identify this method
and shall not be emitted for new use under this edition.

Requirement identifier: `PIA-METHOD-001`.

### 8.2 Exact defining-source-byte bindings

The anchor shall carry the verification-method identifier in 8.1 separately
from the defining-source designator of the exact edition that defines that
method. It shall carry the Ed25519 algorithm identifier in 8.1 separately from
the defining-source designator of the exact source that defines the unchanged
pure Ed25519 algorithm assignment.

For this edition, the Ed25519 algorithm defining-source designator shall bind
the exact `spec-0.3` Package Integrity Anchor Verification source whose URI is:

`https://belgi.dev/specs/spec-0.3/sha256-e3fc0568fe6fec523e11a916978bca80b4b54b5a19f5a1b125c1093515ab9958/BELGI-Companion-Package-Integrity-Anchor-Verification.md`

and whose SHA-256 digest is
`e3fc0568fe6fec523e11a916978bca80b4b54b5a19f5a1b125c1093515ab9958`.
The method defining-source designator shall instead bind the exact source
edition of this document. Pairing the successor method identifier with the
predecessor method source, or pairing the Ed25519 algorithm identifier with a
different algorithm source, shall fail verification.

In each defining-source designator, its URI shall denote that exact referenced source edition and its digest shall bind the exact octets of the same source edition. A stable method or algorithm identifier is not an exact-source URI and shall not be placed in a defining-source designator whose digest covers different bytes.

Hashing a stable identifier string is not an exact-edition source binding and is prohibited. A matching identifier with a missing, mismatched, substituted, or unverifiable defining-source digest shall fail verification.

The verification-key designator instead designates and binds the exact verification-key text from the anchor, encoded as UTF-8, because that preserved text is the source being designated. Before package integrity succeeds, method and algorithm support remains an independently configured verifier capability; package-provided source or registry material cannot authorize its own bootstrap verifier.

Requirement identifier: `PIA-SOURCE-001`.

### 8.3 SHA-256

The serialized token `sha256`, when used by the immutable designators governed by this method, denotes SHA-256 exactly as specified by FIPS PUB 180-4 and by the stable identifier `https://belgi.dev/ids/algorithm/digest/sha-256`.

SHA-256 shall be applied to the named exact octet sequence. Its result is exactly 32 octets. Where this result is serialized as hexadecimal text, the text shall contain exactly 64 lowercase ASCII hexadecimal characters from `0` to `9` and `a` to `f`, with no prefix, separator, or whitespace.

The token `sha256` is a bootstrap serialization token allocated by this
companion family. It belongs to the named compact identifier vocabulary whose
namespace identity is
(`https://belgi.dev/ids/companion/package-integrity-anchor-verification`,
`immutable-designator-digest-algorithm-token`). Within that namespace it shall
be compared as one exact ASCII string without case folding, Unicode
normalization, whitespace trimming, prefix expansion, or other normalization.
No different meaning may receive the same token in that namespace. No later
edition of this companion family shall reassign `sha256` a different meaning,
and retirement or removal shall not make it available for reassignment.

This document does not claim that token as an IANA or other external registry allocation.

Requirement identifier: `PIA-DIGEST-001`.

### 8.4 Verification key

The verification-key text shall contain exactly 64 lowercase ASCII hexadecimal characters from `0` to `9` and `a` to `f`. Successive pairs, in preserved order, shall decode to exactly 32 raw octets of the Ed25519 public key.

No leading or trailing whitespace, prefix, separator, uppercase character, Base64 encoding, PEM encoding, JWK encoding, or other representation is permitted. The verification-key designator shall bind the exact preserved verification-key text encoded as UTF-8 under 8.2 and 8.3.

NOTE A hexadecimal decoder can accept uppercase characters while producing the
same 32 octets. Such decoder acceptance does not satisfy this clause: for
example, replacing any `a` to `f` character with its uppercase form makes the
preserved verification-key text nonconforming before Ed25519 verification.

Failure of the lexical grammar, decoded length, or exact key-text binding shall fail verification before signature acceptance.

Requirement identifier: `PIA-KEY-001`.

### 8.5 Signature encoding

The `signatureBase64` value shall encode exactly 64 signature octets using the standard Base64 alphabet and canonical encoding rules of RFC 4648, Section 4. Its exact lexical grammar is:

```regex
^(?:[A-Za-z0-9+/]{4}){21}[A-Za-z0-9+/][AQgw]==$
```

This expression is applied as a whole-string match. Its terminal `$` denotes
the absolute end of the string, not a position before a final line terminator.

The required `==` padding shall be present. Whitespace, Base64url alphabet characters, omitted or extra padding, alternative alphabets, and non-zero pad bits are prohibited. A verifier shall decode the text, require exactly 64 decoded octets, re-encode those octets using canonical RFC 4648 Base64, and require byte-for-byte equality with the preserved text. Schema matching alone is not sufficient.

Requirement identifier: `PIA-BASE64-001`.

### 8.6 Pure Ed25519 verification

The method identified in 8.1 uses pure Ed25519 as specified by RFC 8032.
Ed25519ctx and Ed25519ph are not admitted. The message is the exact preserved
octet sequence of the designated package-integrity manifest; no prehash,
context string, alternate canonicalization, normalization, or reconstruction
is applied. The complete accepted set in this clause belongs to that method;
it does not redefine the stable Ed25519 algorithm identifier.

The 32 public-key octets are `A_enc`. The 64 decoded signature octets are
`R_enc || S_enc`, where `R_enc` is the first 32 octets and `S_enc` is the
final 32 octets. `S` is the little-endian integer represented by `S_enc`. The
exact manifest octets are `M`.

`A_enc` and `R_enc` shall each decode to an Edwards25519 point using the
compressed-point decoding procedure in RFC 8032, 5.1.3. Each encoding shall be
canonical: re-encoding the decoded point using RFC 8032, 5.1.2 shall reproduce
the original 32 octets exactly. A decoding failure or an unequal re-encoding
shall fail verification.

The decoded public-key point `A` shall have exact order `L`. A verifier shall
therefore require both `A != O` and `[L]A = O`. A public key with an identity,
small-order, or mixed-order point shall fail verification. The scalar `S`
shall satisfy `0 <= S < L`.

Let `R` be the point decoded from `R_enc`, and let

```text
k = little-endian-integer(SHA-512(R_enc || A_enc || M)) mod L.
```

The signature shall be accepted only if the following uncofactored equation
holds:

```text
[S]B = R + [k]A.
```

The cofactored equation `[8][S]B = [8]R + [8][k]A` is not an alternative
acceptance path for this method. A verifier whose underlying library accepts a
wider set shall apply the checks in this clause and return failure for that
wider set. With `A` restricted to the prime-order subgroup, the selected
equation already forces every accepted `R` into that subgroup; a separate `R`
subgroup predicate does not change the accepted set.

The signature shall verify against the exact message and the 32 public-key octets decoded under 8.4.

Requirement identifier: `PIA-ED25519-001`.

### 8.7 Fail-closed verification and no fallback

A producer shall emit only the method and algorithms in 8.1. A verifier shall return failure for an unknown, unsupported, retired-for-new-use, prohibited, malformed, inconsistent, or non-verifying method, algorithm, key, signature, source binding, or message binding. A deprecated identifier is interpretable only where its exact defining edition permits the historical use.

Algorithm negotiation, suite fallback, successor substitution, “try another algorithm” behavior, and fallback among Ed25519, Ed25519ctx, and Ed25519ph are prohibited. A failed check shall not be retried under another method, algorithm, key representation, signature encoding, or message representation.

Part 2 maps these failures through the existing claim-record-integrity-recovery problem family; this companion does not define a second replay taxonomy.

Requirement identifier: `PIA-FAIL-001`.

## 9 Representation boundary

### 9.1 Carrier representation

This companion edition does not define a carrier schema, a JSON Schema dialect, or serialized field names for the package-integrity manifest or package-integrity anchor.

A conforming representation binding may define those surfaces, provided that it preserves the stable identifiers, exact manifest octets, verification-key text, signature value, and immutable designators required by Clauses 7 and 8 without changing their meaning. The JSON representation companion assigns `application/vnd.belgi.package-integrity-anchor+json` to the JSON representation of the anchor. That media type identifies representation format only and shall not select or authorize the method or algorithms in 8.1.

### 9.2 No schema substitution

An implementation-specific schema, filename, media type, package location, or local validator result shall not substitute for the verification procedure and fail-closed rules of Clauses 7 and 8.

## 10 Exact-edition dependency rule

If replay-relevant interpretation depends on this companion specification, the exact edition of this companion specification shall be identified and preserved in accordance with BELGI - Part 2 and BELGI - Part 3.

If replay-relevant interpretation depends on the verification method of Clause 8, the exact edition of this companion specification shall govern that interpretation.

## 11 Conformance

### 11.1 Conformance classes

The following conformance classes are defined:

- BELGI Package Integrity Anchor Verification-aware Producer;
- BELGI Package Integrity Anchor Verification-aware Verifier; and
- BELGI Full Package Integrity Anchor Verification Implementation.

### 11.2 BELGI Package Integrity Anchor Verification-aware Producer

An implementation conforms to this document as a BELGI Package Integrity Anchor Verification-aware Producer if it:

- emits the companion identifier of 6.1 exactly when replay-relevant interpretation depends on this companion specification;
- preserves the stable method and signature-algorithm identifiers separately from their exact defining-source designators;
- preserves the package and manifest-member consistency bindings required by 7.5;
- preserves package-integrity anchors only with the verification surface fixed by Clauses 7 to 9 when claiming conformance to this draft; and
- preserves the exact edition of this companion specification whenever replay-relevant interpretation depends on it.

### 11.3 BELGI Package Integrity Anchor Verification-aware Verifier

An implementation conforms to this document as a BELGI Package Integrity Anchor Verification-aware Verifier if it:

- identifies the exact edition of this companion specification from preserved material when replay depends on it;
- interprets the stable method, digest-algorithm, and signature-algorithm identifiers, their applicable exact source bindings, the verification-key text grammar, the canonical Base64 signature grammar, and the verification-key binding surface only according to this draft;
- applies FIPS PUB 180-4 SHA-256 and RFC 8032 pure Ed25519 as fixed by Clause 8;
- applies the 7.5 target-binding comparison only after claim-record integrity recovery and under the Part 2 replay order;
- applies the fail-closed rules of Clauses 7 and 8 to missing, malformed, unsupported, or inconsistent package-integrity-anchor verification material; and
- does not silently substitute another companion edition, another verification method, another signature algorithm, another verification key, local trust-store material, or registry material for replay.

### 11.4 BELGI Full Package Integrity Anchor Verification Implementation

An implementation conforms to this document as a BELGI Full Package Integrity Anchor Verification Implementation if it conforms to 11.2 and 11.3.

### 11.5 Conformance statement

A conformance statement claiming conformance to this document shall identify:

- the implementation;
- the document title;
- the document version;
- the conformance class claimed;
- the companion identifier of 6.1;
- the exact edition of this companion specification against which the claim is made; and
- the date of the statement.

## 12 Security considerations

Package-integrity-manifest substitution, signature-method substitution, algorithm downgrade, Ed25519 variant confusion, source-designator substitution, key substitution, key-encoding substitution, non-canonical Base64, malformed key or signature material, and silent local verifier defaults can all make a replay package appear authenticated when it is not.

This companion specification reduces those risks only when producers and verifiers preserve and enforce the stable method and algorithm identifiers, their exact defining-source-byte bindings, the verification-key binding surface, canonical signature encoding, and exact manifest octets fixed by this draft.

Verification-key substitution can arise when a key name, registry lookup, account label, certificate label, URL, local trust-store entry, verifier default, or alternate key encoding is treated as if it were the preserved verification-key text bound by immutable designator. Clauses 7.3, 7.6, 8.4, and 11.3 require one exact key grammar, exact preserved key binding, and fail-closed handling of inconsistent key material.

RFC 8032 permits verification equations with different accepted sets. Silent
selection by a cryptographic library can therefore make two replay verifiers
disagree on the same preserved bytes. Small-order or mixed-order public keys
can also satisfy an equation without representing a valid Ed25519 signer key.
Clause 8.6 removes both ambiguities by requiring a canonical exact-order public
key and one uncofactored acceptance equation.

Excluded reliance claim: this companion specification does not establish authorization, trust status, or organizational acceptance of any verified signer.

## 13 Privacy considerations

This companion specification does not require preservation of signer identity, operator identity, account identity, or other personal identifiers beyond the verification-key material needed for replay.

When preserved key material or related metadata incidentally contain personal data, applicable privacy obligations apply independently of this document.
