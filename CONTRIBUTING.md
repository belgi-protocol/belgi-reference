# Contributing

This repository is a research reference implementation for bounded BELGI
replay and conformance surfaces. It is not a production verification boundary,
a general BELGI conformance implementation, or a stable Python library API.

Before proposing a change, identify the affected command, artifact, exact
edition, or implementation check. Keep a pull request focused on one coherent
behavior or documentation objective, state any observable compatibility
effect, and include a fail-closed regression when changing verification
behavior.

Normative language, identifiers, schemas, and edition changes belong in
[`belgi-protocol/belgi-spec`](https://github.com/belgi-protocol/belgi-spec).
This repository may implement an exact specification edition, but it must not
create competing normative meaning.

Run the candidate checks from the repository root:

```sh
python -m ruff format --check belgi tests/public_reference .github/scripts
python -m ruff check belgi tests/public_reference .github/scripts
python -m pyright
python -m pyright .github/scripts
python -m build --wheel --no-isolation --outdir dist
export BELGI_WHEEL_PATH="$(
  python - <<'PY'
from pathlib import Path

wheels = list(Path("dist").glob("belgi-*.whl"))
if len(wheels) != 1:
    raise SystemExit(f"expected one wheel, found {len(wheels)}")
print(wheels[0].resolve())
PY
)"
python -m pytest -q tests/public_reference
```

`README.md` owns the shared repository and package introduction.
`PACKAGE_README.md` is its byte-identical packaging projection; the public
reference tests reject drift between them.

Release artifacts follow a stricter path than an ordinary contribution. The
tag workflow builds one source distribution from the exact tag, builds two
independent wheels from that same source distribution, admits their exact
inventories and metadata, and publishes the admitted bytes without rebuilding.
The operator sequence and one-time index setup are in
[`RELEASING.md`](RELEASING.md).

Do not add product orchestration, signing authority, network fallback,
production policy, or mutable edition aliases to the reference distribution.
Tests should prove observable behavior, a resource or trust boundary, an
independently derived relation, or an exact public artifact property.

Contributions are licensed under Apache License 2.0 and use the Developer
Certificate of Origin. Sign off each commit with:

```text
Signed-off-by: Your Name <you@example.com>
```

The sign-off certifies that you have the right to submit the contribution under
the repository's license terms.
