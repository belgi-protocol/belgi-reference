# Versioning

The Python distribution and the BELGI specification family have independent
version lines. The distribution version is the PEP 440 value in
`pyproject.toml`; a replay package selects its governing exact specification
edition separately.

This repository is an alpha research reference. A release identifies one
implementation snapshot and its bounded, documented replay and conformance
surfaces. It does not publish or version the BELGI specification, claim general
BELGI conformance, establish production readiness, or promise a stable Python
import API.

Before `1.0`, command grammar, output documents, installed data, and importable
modules may change between releases. Observable incompatible changes must be
called out and use a new distribution version. Published artifacts are
immutable: a changed artifact advances the PEP 440 version instead of replacing
existing bytes.

Specification changes, including normative identifiers, schemas, and edition
lifecycle, follow the separate policy in
[`belgi-protocol/belgi-spec`](https://github.com/belgi-protocol/belgi-spec).
Updating this implementation's selected or supported edition requires an
explicit implementation change and does not create a mutable `latest` alias.
