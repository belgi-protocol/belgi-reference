# Releasing the Python reference

The release workflow publishes one admitted source distribution and wheel. It
does not rebuild between TestPyPI, PyPI, and the GitHub prerelease.

## One-time operator setup

Create GitHub environments named exactly `testpypi` and `pypi`.

- Restrict both environments to deployments from the `main` branch only.
- Require an operator review on `pypi`. The TestPyPI environment may remain
  unprotected because PyPI is still downstream of an exact TestPyPI readback.
- Create an active repository tag ruleset for `v*` with update and deletion
  restricted and no bypass actor. The workflow rebinds the remote annotated
  tag object and its peeled commit immediately before every index upload and
  before GitHub release creation; the ruleset prevents the operator from
  normalizing tag movement into an accepted release practice.
- Configure one pending Trusted Publisher on TestPyPI and one on PyPI with
  owner `belgi-protocol`, repository `belgi-reference`, workflow
  `publish.yml`, and their matching environment name.

Do not store package-index API tokens in the repository or workflow.

## Candidate dispatch

Before creating a tag, require the `Verify` workflow to be green on the exact
`origin/main` commit. Create an annotated tag whose name is the Python version
prefixed with `v`; for the current alpha this is `v0.1.0a0`. The tag must point
to that same `origin/main` commit.

Run the `Publish` workflow from the `main` branch with:

- `release_tag`: `v0.1.0a0`
- `confirmation`: `publish belgi==0.1.0a0 from v0.1.0a0`

The workflow fails closed unless the dispatch ref, dispatch commit, annotated
tag commit, and current `origin/main` commit agree. It then builds one source
distribution from the tagged archive, builds two wheels independently from
that source distribution, admits one byte-identical wheel, and publishes the
same candidate artifact throughout.

After TestPyPI readback succeeds, inspect that job before approving the
protected `pypi` environment. PyPI readback must succeed before the workflow
creates the GitHub prerelease.

After any index upload, do not start a new dispatch or use **Re-run all jobs**.
If a downstream readback or release job fails, use **Re-run failed jobs** on
the same workflow run so the successful upload job is not repeated and the
retained candidate artifact continues downstream. If an upload job itself
fails after a partial upload, or the retained candidate artifact is no longer
available (the workflow requests 90 days), stop and prepare a new Python
version and annotated tag. Never move a published tag or reuse an index
version.

## Documentation successor

PyPI readback for `0.1.0a0` succeeded before the documentation successor stated
direct availability. `README.md` and `PACKAGE_README.md` remain byte-identical.
Updating these source files does not rewrite already-published `0.1.0a0`
metadata; never reuse an index version or move its tag to update prose.
