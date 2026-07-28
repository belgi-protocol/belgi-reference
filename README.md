# BELGI Python reference

`belgi` is the bounded Python reference distribution for replaying finite
software-change review records and checking the exact installed conformance
surface.

This alpha distribution targets the exact `spec-0.5` Working Draft material
packaged with the wheel. It is a research/reference artifact, not a production
admission controller.

## Install and inspect

Python 3.11 or newer is required.

```bash
python -m pip install .
python -c "import belgi; print(belgi.__version__)"
belgi --help
```

To inspect exact candidate bytes, install the local wheel by its full path:

```bash
python -m pip install ./dist/belgi-0.1.0a0-py3-none-any.whl
```

Package-index availability is established by the exact version page and the
release readback, not by this README. If version `0.1.0a0` is present on PyPI
and its published bytes have passed that readback, install it with:

```bash
python -m pip install "belgi==0.1.0a0"
```

Otherwise, use the source or admitted local-wheel commands above.

The only promised Python import is `belgi.__version__`. All other Python
modules are implementation detail.

The command surface is deliberately small:

```text
belgi [--json] replay PATH
belgi [--json] conformance
```

`PATH` must be a physical directory or a ZIP archive. Reads are bounded and
authenticated against the selected package-representation procedure before
semantic lifting. Replay emits the authoritative replay report; a cached
verdict in the record is never replay authority.

## Static examples

The source distribution contains two static records:

```bash
belgi --json replay examples/finite-review-record
belgi --json replay examples/finite-review-record-tampered
```

The first is the exact static finite Part 4 `record-check` package and replays
successfully. The second differs by one byte in its bound proposed source-state
member and is rejected for an integrity-binding mismatch before semantic
lifting. These examples are fixed bytes, not output from a packaged builder or
signing workflow.

An installed wheel also places both examples under
`share/belgi/examples/` in the installation prefix.

## Conformance

```bash
belgi --json conformance
```

The JSON result separates:

- `normative_corpora`: exact JSON representation, replay-package
  representation, and package-integrity crypto corpora;
- `implementation_checks`: the exact finite Part 4 evaluator validation.

An implementation check is not presented as a normative or
cross-implementation conformance claim.

## Exit status

| Code | Meaning |
|---:|---|
| 0 | Replay or conformance succeeded. |
| 1 | The package was rejected, replay failed, or a conformance mismatch was observed. |
| 2 | Command usage or physical path kind was unsupported. |
| 3 | I/O, installation, or integration failed. |

Expected invalid input is reported without a traceback. Use root `--json` for
one machine-readable document.

## Scope boundary

This wheel contains the Part 1–4 reference execution path, the six selected
companion specifications, exact resources, and minimum substrate required for
replay and conformance. It does not ship the product application,
operational-action or Part 5 surfaces, cloud/IaC integrations, console, MCP
transport, policy/PEP integration, admission orchestration, package builders,
or signing orchestration.

The reference validates the supplied record under its exact packaged editions.
It does not prove that evidence was honestly produced, establish deployment or
CI provenance, control external writes, provide a sandbox, or make a production
security claim.

Project sources:

- [Python reference](https://github.com/belgi-protocol/belgi-reference)
- [Specification](https://github.com/belgi-protocol/belgi-spec)
- [Technical report](https://github.com/belgi-protocol/belgi-spec/blob/main/TECHNICAL-REPORT.md)
- [Reproducibility guide](https://github.com/belgi-protocol/belgi-spec/blob/main/REPRODUCIBILITY.md)
