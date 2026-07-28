# Finite review-record example authority

The positive package in `../finite-review-record/` is the exact static output
of the specification repository's
`tests/software_change_finite/package_builder.py::build_finite_signed_package`
for the active `spec-0.5` graph. The public reference wheel does not include
that builder or any signing orchestration.

The verification key is carried by `package-integrity-anchor`:

```text
verificationKeyText =
bb45714fb373da495b94928d1f6631a4818b067c9a57236affe91b174b732a22

verificationKeyDesignator.uri =
https://belgi.dev/keys/test/authenticated-claim-record.pub

verificationKeyDesignator.digest =
sha256:7e898c3d531818ece8bd264606016419858559223e030564721fc9ddba716839
```

This deterministic key identifies only a public interoperability fixture. It
is not a deployment trust root.

The determining Part 4 member is `part-4-determining-semantics`:

```text
sha256:89727ba59e10f493a130ab5a6ff32916860c20f9d4ea6617b6d2722dcf34b574
```

`../finite-review-record-tampered/` preserves the positive anchor and manifest
but changes exactly one byte in `proposed-source-state`, at zero-based offset
75, from `0x65` (`e`) to `0x75` (`u`). It is intentionally not re-signed and
must fail member-integrity verification before semantic lifting.

## Go verifier recipe

With sibling public checkouts named `belgi-reference/` and
`belgi-verifier-go/`, run the following from the `belgi-verifier-go/` root.
The `REFERENCE_ROOT` path names the sibling Python-reference checkout that owns
the static examples:

```sh
REFERENCE_ROOT=../belgi-reference
jq '.verificationKeyDesignator' \
  "$REFERENCE_ROOT/examples/finite-review-record/package-integrity-anchor" \
  > /tmp/belgi-example-key-designator.json
GOWORK=off go build -o /tmp/belgi-replayobserve ./cmd/replayobserve

/tmp/belgi-replayobserve \
  --packet-root testdata/spec-0.5 \
  --directory "$REFERENCE_ROOT/examples/finite-review-record" \
  --verification-key-text bb45714fb373da495b94928d1f6631a4818b067c9a57236affe91b174b732a22 \
  --verification-key-designator /tmp/belgi-example-key-designator.json

/tmp/belgi-replayobserve \
  --packet-root testdata/spec-0.5 \
  --directory "$REFERENCE_ROOT/examples/finite-review-record-tampered" \
  --verification-key-text bb45714fb373da495b94928d1f6631a4818b067c9a57236affe91b174b732a22 \
  --verification-key-designator /tmp/belgi-example-key-designator.json
```

The positive observation exits `0`; the intentional tamper exits `2`.
