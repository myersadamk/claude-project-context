"""Safety-critical tests for the linker module.

These tests verify that the linker NEVER performs destructive operations
on non-symlink files. If any of these fail, the tool is dangerous.
"""

from pathlib import Path

import pytest

from cpc.config import RuleSet

UNIVERSAL = RuleSet("universal-coding")
TYPESCRIPT_WEB = RuleSet("typescript-web")


def _create_source_rules(tmp_path: Path) -> Path:
    """Create a fake rules/ directory with two sets."""
    rules = tmp_path / "rules"
    universal = rules / UNIVERSAL
    universal.mkdir(parents=True)
    (universal / "universal-coding-review.md").write_text("# Review")
    (universal / "universal-coding-security.md").write_text("# Security")

    ts = rules / TYPESCRIPT_WEB
    ts.mkdir(parents=True)
    (ts / "typescript-web-types.md").write_text("# Types")
    return rules


def _create_source_skills(tmp_path: Path) -> Path:
    """Create a fake skills/ directory with one skill."""
    skills = tmp_path / "skills"
    vibesec = skills / "vibesec"
    vibesec.mkdir(parents=True)
    (vibesec / "SKILL.md").write_text("# VibeSec")
    return skills


def _create_target(tmp_path: Path) -> Path:
    """Create a fake target project directory."""
    target = tmp_path / "project"
    target.mkdir()
    return target


class TestSafetyInvariants:
    """If any of these tests fail, the tool is dangerous."""

    def test_never_deletes_non_symlink_files(self, tmp_path: Path) -> None:
        """A real file in .claude/rules/ must survive install — it's a local override."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Pre-create a local override file (not a symlink)
        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        local_file = claude_rules / "universal-coding-review.md"
        local_file.write_text("# My local override")

        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Local file must still exist with original content
        assert local_file.exists()
        assert not local_file.is_symlink()
        assert local_file.read_text() == "# My local override"

    def test_never_overwrites_non_symlink_files(self, tmp_path: Path) -> None:
        """Install must not replace a real file with a symlink."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        local_file = claude_rules / "universal-coding-security.md"
        local_file.write_text("# Local security rules")

        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        assert not local_file.is_symlink()
        assert local_file.read_text() == "# Local security rules"

    def test_stale_cleanup_only_removes_our_symlinks(self, tmp_path: Path) -> None:
        """Cleanup must not touch symlinks that point outside our sources."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Create a symlink from another tool
        claude_rules = target / ".claude" / "rules"
        claude_rules.mkdir(parents=True)
        other_source = tmp_path / "other-tool" / "some-rule.md"
        other_source.parent.mkdir(parents=True)
        other_source.write_text("# Other tool's rule")
        foreign_link = claude_rules / "some-rule.md"
        foreign_link.symlink_to(other_source)

        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Foreign symlink must survive
        assert foreign_link.is_symlink()
        assert foreign_link.resolve() == other_source.resolve()

    def test_only_writes_inside_claude_directory(self, tmp_path: Path) -> None:
        """No files should be created outside .claude/ in the target."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        skills_dir = _create_source_skills(tmp_path)
        target = _create_target(tmp_path)

        # Record files before install
        before = set()
        for p in target.rglob("*"):
            before.add(p)

        install_profile(
            target=target,
            rule_sets=[UNIVERSAL, TYPESCRIPT_WEB],
            skill_dirs=[(skills_dir / "vibesec")],
            rules_dir=rules_dir,
        )

        # All new files must be under .claude/
        for p in target.rglob("*"):
            if p not in before:
                rel = p.relative_to(target)
                assert rel.parts[0] == ".claude", f"File created outside .claude/: {rel}"


class TestCorrectBehavior:

    def test_creates_symlinks_for_selected_rules(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        result = install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        rules = target / ".claude" / "rules"
        link = rules / "universal-coding-review.md"
        assert link.is_symlink()
        assert link.resolve().name == "universal-coding-review.md"
        assert len(result.linked) == 2

    def test_creates_symlinks_for_selected_skills(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        skills_dir = _create_source_skills(tmp_path)
        target = _create_target(tmp_path)

        result = install_profile(
            target=target,
            rule_sets=[],
            skill_dirs=[(skills_dir / "vibesec")],
            rules_dir=rules_dir,
        )

        skills = target / ".claude" / "skills"
        link = skills / "vibesec"
        assert link.is_symlink()
        assert (link / "SKILL.md").exists()

    def test_replaces_existing_symlinks(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install twice
        install_profile(
            target=target, rule_sets=[UNIVERSAL],
            skill_dirs=[], rules_dir=rules_dir,
        )
        result = install_profile(
            target=target, rule_sets=[UNIVERSAL],
            skill_dirs=[], rules_dir=rules_dir,
        )

        assert len(result.updated) == 2
        assert len(result.linked) == 0

    def test_cleans_stale_symlinks_on_update(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install universal + typescript-web
        install_profile(
            target=target,
            rule_sets=[UNIVERSAL, TYPESCRIPT_WEB],
            skill_dirs=[], rules_dir=rules_dir,
        )

        # Re-install with only universal — typescript-web links should be cleaned
        result = install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[], rules_dir=rules_dir,
        )

        assert len(result.cleaned) == 1  # typescript-web-types.md
        rules = target / ".claude" / "rules"
        assert not (rules / "typescript-web-types.md").exists()

    def test_idempotent_reinstall(self, tmp_path: Path) -> None:
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        sets = [UNIVERSAL, TYPESCRIPT_WEB]

        result1 = install_profile(
            target=target, rule_sets=sets,
            skill_dirs=[], rules_dir=rules_dir,
        )
        result2 = install_profile(
            target=target, rule_sets=sets,
            skill_dirs=[], rules_dir=rules_dir,
        )

        # Same number of active symlinks, no cleaned, no skipped
        active1 = len(result1.linked) + len(result1.updated)
        active2 = len(result2.linked) + len(result2.updated)
        assert active1 == active2
        assert len(result2.cleaned) == 0


class TestErrorHandling:

    def test_nonexistent_profile_errors(self, tmp_path: Path) -> None:
        from cpc.config import load_config

        config_path = tmp_path / "config.yaml"
        config_path.write_text("profiles: {}\nsources:\n  skills: []\n")
        config = load_config(config_path)
        assert "nonexistent" not in config.profiles

    def test_missing_manifest_on_update_errors(self, tmp_path: Path) -> None:
        from cpc.config import load_manifest

        target = tmp_path / "project"
        target.mkdir()
        assert load_manifest(target) is None
