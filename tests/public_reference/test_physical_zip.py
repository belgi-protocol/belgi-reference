from __future__ import annotations

from pathlib import Path

from belgi.carrier.package.representation.contract import BASELINE_ENVELOPE
from belgi.substrate.io.bounded_zip.encode import encode_bounded_zip
from belgi.substrate.io.bounded_zip.model import BoundedZipLimits, ZipCompression

from .conftest import run_belgi, stdout_json


def _canonical_archive(directory: Path) -> bytes:
    return encode_bounded_zip(
        {
            member.name.encode("ascii"): member.read_bytes()
            for member in directory.iterdir()
            if member.is_file()
        },
        limits=BoundedZipLimits(
            archive_bytes=BASELINE_ENVELOPE.outer_zip_bytes,
            entry_count=BASELINE_ENVELOPE.member_count,
            member_bytes=BASELINE_ENVELOPE.member_bytes,
            total_member_bytes=BASELINE_ENVELOPE.total_member_bytes,
        ),
        compression=ZipCompression.DEFLATE,
    )


def test_canonical_zip_is_the_same_authoritative_replay(
    repository_root: Path,
    tmp_path: Path,
) -> None:
    directory = repository_root / "examples" / "finite-review-record"
    archive = tmp_path / "finite-review-record.zip"
    archive.write_bytes(_canonical_archive(directory))

    directory_process = run_belgi(
        "--json",
        "replay",
        str(directory),
        cwd=repository_root,
    )
    archive_process = run_belgi(
        "--json",
        "replay",
        str(archive),
        cwd=repository_root,
    )

    assert directory_process.returncode == archive_process.returncode == 0
    assert stdout_json(archive_process) == stdout_json(directory_process)


def test_non_zip_regular_file_is_a_typed_representation_rejection(
    repository_root: Path,
    tmp_path: Path,
) -> None:
    regular_file = tmp_path / "not-a-package"
    regular_file.write_bytes(b"not a ZIP archive")

    process = run_belgi(
        "--json",
        "replay",
        str(regular_file),
        cwd=repository_root,
    )

    assert process.returncode == 1
    document = stdout_json(process)
    assert document["status"] == "representation-rejected"
    assert document["representation"] == {
        "accepted": False,
        "result_code": "malformed-container",
        "stage": 2,
    }
    assert "Traceback" not in process.stderr
