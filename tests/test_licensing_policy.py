"""Guard against accidentally conflating program, font, and upstream-data licenses."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_version_scoped_licenses_present_in_packages():
    manifest = json.loads((ROOT / "family/package-manifest.json").read_text(encoding="utf-8"))
    expected = {
        "LICENSE", "LICENSE-GPL-2.0.txt", "LICENSE-APACHE-2.0.txt",
        "LICENSING.md", "V1-APACHE-GRANT.md", "FONT-LICENSE-V2PLUS.md",
        "NOTICE.md", "assets/fonts/source/CJKVI-IDS-COPYING.txt",
        "family/data/UNICODE-LICENSE.txt",
    }
    assert expected <= set(manifest["source_files"])
    assert expected <= set(manifest["licenses"])
    assert all((ROOT / path).is_file() for path in expected)


def test_grant_scope_does_not_revoke_historic_rights():
    policy = (ROOT / "LICENSING.md").read_text(encoding="utf-8")
    assert "GPL-2.0-only OR AGPL-3.0-only" in policy
    assert "v1.0.0" in policy.lower()
    assert "Apache-2.0" in policy
    assert "retroactively" in policy
    assert "Third-party" in policy
    font_eula = (ROOT / "FONT-LICENSE-V2PLUS.md").read_text(encoding="utf-8")
    assert "explicitly issued" in font_eula
    assert "previously" in font_eula
    assert "CJKVI" in font_eula


def test_generated_font_license_points_to_versioned_policy():
    builder = (ROOT / "family/font_builder.py").read_text(encoding="utf-8")
    assert "Singleline JP Font Commercial License" in builder
    assert "blob/main/LICENSING.md" in builder


def test_new_font_license_allows_real_embedding_but_prohibits_standalone_distribution():
    eula = (ROOT / "FONT-LICENSE-V2PLUS.md").read_text(encoding="utf-8")
    assert "## 3. Permitted integration and distribution with finished products" in eula
    assert "desktop/mobile applications and games" in eula
    assert "self-hosted webfonts" in eula
    assert "technical accessibility alone" in eula
    assert "## 4. Prohibited standalone redistribution" in eula
    assert "unchanged, renamed, converted, subsetted, or modified" in eula
    assert "Encryption, DRM, obfuscation, or other anti-extraction measures are not required" in eula
    assert "does not restrict the additional **Apache-2.0 grant" in eula
    assert "previously granted" in eula
    assert "include installable/usable font binaries as part of redistributable applications" not in eula
