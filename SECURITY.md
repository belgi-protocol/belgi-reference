# Security Policy

Report suspected vulnerabilities privately through GitHub's private
vulnerability-reporting or Security Advisory interface for
`belgi-protocol/belgi-reference`. Do not open a public issue or pull request
with exploit details, secrets, private keys, personal data, or confidential
packages.

If that interface is unavailable, report privately at security@belgi.dev.

Include the affected revision and Python version, the smallest safe reproducer,
the observed exit status, and whether the issue involves package integrity,
signature verification, source binding, archive or path handling, resource
bounds, or an incorrect replay result.

This project is a research reference implementation. It is not represented as
a production security boundary, a general conformance implementation, or a
substitute for an adopter's threat model. Reports of fail-open behavior,
authentication or integrity bypass, path traversal, verification confusion,
and resource exhaustion are nevertheless in scope.

Non-sensitive correctness and documentation defects may use public issues.
Specification ambiguities or proposed normative changes belong in
[`belgi-protocol/belgi-spec`](https://github.com/belgi-protocol/belgi-spec).
