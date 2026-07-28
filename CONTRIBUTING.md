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
python -m ruff format --check belgi tests/public_reference
python -m ruff check belgi tests/public_reference
python -m pyright
python -m build --wheel --outdir dist
export BELGI_WHEEL_PATH="$(
  python -c 'from pathlib import Path; wheels = list(Path("dist").glob("belgi-*.whl")); assert len(wheels) == 1; print(wheels[0].resolve())'
)"
python -m pytest -q tests/public_reference
```

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
