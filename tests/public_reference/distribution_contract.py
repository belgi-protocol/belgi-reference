from __future__ import annotations

UNSHIPPED_REFERENCE_MODULE_DESTINATIONS = frozenset(
    {
        "belgi/carrier/package/claim_record.py",
        "belgi/carrier/package/closure.py",
        "belgi/carrier/package/drafts.py",
        "belgi/carrier/package/members.py",
        "belgi/carrier/package/model.py",
        "belgi/carrier/package/representation/logical_map.py",
        "belgi/carrier/package/representation/zip.py",
        "belgi/profile/acquisition.py",
        "belgi/profile/companions/identifier_registry/__init__.py",
        "belgi/profile/companions/identifier_registry/conformance/__init__.py",
        "belgi/profile/companions/identifier_registry/conformance/corpus.py",
        "belgi/profile/companions/identifier_registry/conformance/entry_lifecycle.py",
        "belgi/profile/companions/identifier_registry/conformance/evaluation.py",
        "belgi/profile/companions/identifier_registry/conformance/model.py",
        (
            "belgi/profile/companions/identifier_registry/conformance/"
            "snapshot_governance.py"
        ),
        "belgi/profile/companions/identifier_registry/conformance/use_authority.py",
        "belgi/profile/companions/identifier_registry/conformance/validation.py",
        "belgi/profile/reference_profile/defaults.py",
        "belgi/profile/reference_profile/judged/carrier/projection.py",
        "belgi/replay/package_source/structured.py",
        "belgi/replay/procedure/exceptions.py",
        "belgi/replay/procedure/installed.py",
        "belgi/replay/procedure/selection.py",
        "belgi/substrate/ed25519_signing.py",
        "belgi/substrate/io/windows/mutation.py",
        "belgi/substrate/terminal.py",
    }
)
UNSHIPPED_CRYPTO_CAPABILITIES = frozenset(
    {
        "ed25519_public_key_hex",
        "generate_ed25519_private_key",
        "load_ed25519_private_key",
        "sign_ed25519_payload",
    }
)
ALLOWED_REFERENCE_CARRIER_PACKAGE_MODULES = frozenset(
    {
        "belgi/carrier/package/__init__.py",
        "belgi/carrier/package/names.py",
        "belgi/carrier/package/representation/__init__.py",
        "belgi/carrier/package/representation/binding.py",
        "belgi/carrier/package/representation/contract.py",
        "belgi/carrier/package/representation/paths.py",
    }
)
PRIVATE_KEY_IMPLEMENTATION_MARKERS = (
    b"Ed25519PrivateKey",
    b"from_private_bytes",
    b".sign(",
)

__all__ = [
    "ALLOWED_REFERENCE_CARRIER_PACKAGE_MODULES",
    "PRIVATE_KEY_IMPLEMENTATION_MARKERS",
    "UNSHIPPED_CRYPTO_CAPABILITIES",
    "UNSHIPPED_REFERENCE_MODULE_DESTINATIONS",
]
