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


class TestGitignoreManagement:
    """Tests for cpc-managed .gitignore section."""

    def test_creates_gitignore_when_missing(self, tmp_path: Path) -> None:
        """If no .gitignore exists, create one with just the cpc section."""
        from cpc.linker import update_gitignore

        target = tmp_path / "project"
        target.mkdir()

        update_gitignore(
            target=target,
            rule_files=["universal-coding-review.md", "universal-coding-security.md"],
            skill_names=["cpc-init"],
        )

        gitignore = target / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "# cpc:start" in content
        assert "# cpc:end" in content
        assert ".claude/rules/universal-coding-review.md" in content
        assert ".claude/rules/universal-coding-security.md" in content
        assert ".claude/skills/cpc-init" in content
        assert ".claude/.cpc.manifest.json" in content

    def test_appends_to_existing_gitignore(self, tmp_path: Path) -> None:
        """If .gitignore exists without cpc markers, append the section."""
        from cpc.linker import update_gitignore

        target = tmp_path / "project"
        target.mkdir()
        gitignore = target / ".gitignore"
        gitignore.write_text("node_modules/\n.env\n")

        update_gitignore(
            target=target,
            rule_files=["typescript-web-types.md"],
            skill_names=[],
        )

        content = gitignore.read_text()
        assert content.startswith("node_modules/\n.env\n")
        assert ".claude/rules/typescript-web-types.md" in content
        assert "# cpc:start" in content

    def test_replaces_existing_cpc_section(self, tmp_path: Path) -> None:
        """If .gitignore has cpc markers, replace only that section."""
        from cpc.linker import update_gitignore

        target = tmp_path / "project"
        target.mkdir()
        gitignore = target / ".gitignore"
        gitignore.write_text(
            "node_modules/\n"
            "# cpc:start (managed by cpc — do not edit)\n"
            ".claude/rules/old-rule.md\n"
            ".claude/.cpc.manifest.json\n"
            "# cpc:end\n"
            ".env\n"
        )

        update_gitignore(
            target=target,
            rule_files=["new-rule.md"],
            skill_names=["vibesec"],
        )

        content = gitignore.read_text()
        assert "node_modules/" in content
        assert ".env" in content
        assert "old-rule.md" not in content
        assert ".claude/rules/new-rule.md" in content
        assert ".claude/skills/vibesec" in content

    def test_preserves_user_content_outside_markers(self, tmp_path: Path) -> None:
        """Content before and after cpc markers must be untouched."""
        from cpc.linker import update_gitignore

        target = tmp_path / "project"
        target.mkdir()
        gitignore = target / ".gitignore"
        gitignore.write_text(
            "# My stuff\nnode_modules/\n"
            "# cpc:start (managed by cpc — do not edit)\n"
            ".claude/rules/old.md\n"
            ".claude/.cpc.manifest.json\n"
            "# cpc:end\n"
            "# More stuff\n.env\n"
        )

        update_gitignore(
            target=target,
            rule_files=["new.md"],
            skill_names=[],
        )

        content = gitignore.read_text()
        assert content.startswith("# My stuff\nnode_modules/\n")
        assert content.endswith("# More stuff\n.env\n")

    def test_idempotent_gitignore_update(self, tmp_path: Path) -> None:
        """Running update_gitignore twice produces the same result."""
        from cpc.linker import update_gitignore

        target = tmp_path / "project"
        target.mkdir()

        args = dict(target=target, rule_files=["a.md", "b.md"], skill_names=["s1"])
        update_gitignore(**args)
        first = (target / ".gitignore").read_text()
        update_gitignore(**args)
        second = (target / ".gitignore").read_text()
        assert first == second


class TestFlutterAppProfile:
    """Tests for the flutter-app profile resolution."""

    def test_flutter_app_profile_exists(self) -> None:
        from cpc.config import load_config

        config = load_config()
        assert "flutter-app" in config.profiles

    def test_flutter_app_profile_rules(self) -> None:
        from cpc.config import RuleSet, load_config

        config = load_config()
        profile = config.profiles["flutter-app"]
        assert RuleSet("universal-coding") in profile.rules
        assert RuleSet("flutter-app") in profile.rules

    def test_flutter_app_profile_skills(self) -> None:
        from cpc.config import load_config

        config = load_config()
        profile = config.profiles["flutter-app"]
        assert "flutter-interface-design" in profile.skills

    def test_flutter_app_rules_discoverable(self) -> None:
        from cpc.config import discover_rules, load_config

        config = load_config()
        profile = config.profiles["flutter-app"]
        rules = discover_rules(profile.rules)
        for rule_set in profile.rules:
            assert len(rules[rule_set]) > 0, f"No files found for rule set: {rule_set}"

    def test_flutter_interface_design_skill_resolvable(self) -> None:
        from cpc.config import load_config, resolve_skill

        config = load_config()
        skill_dir = resolve_skill("flutter-interface-design", config.skill_sources)
        assert skill_dir is not None
        assert (skill_dir / "SKILL.md").exists()


class TestGodotCsharpProfile:
    """Tests for the godot-csharp profile and its path-scoped rule sets."""

    NEW_SETS = ("csharp-core", "godot-csharp", "python-tools")

    def test_godot_csharp_profile_rules(self) -> None:
        from cpc.config import RuleSet, load_config

        profile = load_config().profiles["godot-csharp"]
        assert profile.rules == [
            RuleSet("universal-coding"),
            RuleSet("csharp-core"),
            RuleSet("godot-csharp"),
            RuleSet("python-tools"),
        ]

    def test_godot_csharp_rules_discoverable(self) -> None:
        from cpc.config import discover_rules, load_config

        profile = load_config().profiles["godot-csharp"]
        rules = discover_rules(profile.rules)
        for rule_set in profile.rules:
            assert len(rules[rule_set]) > 0, f"No files found for rule set: {rule_set}"

    def test_each_new_set_has_a_review_gate(self) -> None:
        from cpc.config import RULES_DIR

        for rule_set in self.NEW_SETS:
            review = RULES_DIR / rule_set / f"{rule_set}-review.md"
            text = review.read_text()
            assert "## Verification Commands" in text
            assert "```bash" in text

    def test_review_rules_are_not_path_scoped(self) -> None:
        """The gate must always be in context, so review files carry no frontmatter."""
        from cpc.config import RULES_DIR

        for rule_set in self.NEW_SETS:
            review = RULES_DIR / rule_set / f"{rule_set}-review.md"
            assert not review.read_text().startswith("---")

    def test_path_scoped_frontmatter_parses(self) -> None:
        """Claude Code loads a rule unconditionally if its frontmatter doesn't parse."""
        import yaml

        from cpc.config import RULES_DIR

        for rule_set in self.NEW_SETS:
            for path in sorted((RULES_DIR / rule_set).glob("*.md")):
                text = path.read_text()
                if not text.startswith("---\n"):
                    continue
                header = text.split("---\n", 2)[1]
                data = yaml.safe_load(header)
                assert isinstance(data, dict), path.name
                assert set(data) == {"paths"}, path.name
                assert isinstance(data["paths"], list) and data["paths"], path.name
                assert all(isinstance(p, str) for p in data["paths"]), path.name


class TestMultiProfileManifest:
    """Tests for multi-profile manifest format."""

    def test_save_and_load_multi_profile_manifest(self, tmp_path: Path) -> None:
        from cpc.config import load_manifest, save_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli", "flutter-app"])
        manifest = load_manifest(target)

        assert manifest is not None
        assert manifest.profiles == ["python-cli", "flutter-app"]

    def test_load_legacy_single_profile_manifest(self, tmp_path: Path) -> None:
        """Old manifests with 'profile' string migrate to 'profiles' list."""
        import json

        target = tmp_path / "project"
        claude_dir = target / ".claude"
        claude_dir.mkdir(parents=True)

        manifest_path = claude_dir / ".cpc.manifest.json"
        manifest_path.write_text(json.dumps({
            "source": "/some/path",
            "profile": "python-cli",
            "rules": ["universal-coding", "python-cli"],
            "skills": ["cpc-init"],
            "installed": "2026-01-01",
        }))

        from cpc.config import load_manifest
        manifest = load_manifest(target)

        assert manifest is not None
        assert manifest.profiles == ["python-cli"]

    def test_save_empty_profiles_deletes_manifest(self, tmp_path: Path) -> None:
        from cpc.config import load_manifest, save_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli"])
        assert load_manifest(target) is not None

        save_manifest(target, [])
        assert load_manifest(target) is None


class TestResolveProfiles:

    def test_union_of_two_profiles(self) -> None:
        from cpc.config import RuleSet, load_config, resolve_profiles

        config = load_config()
        rule_sets, skill_names = resolve_profiles(
            ["python-cli", "flutter-app"], config
        )

        # Both should contribute their rules
        assert RuleSet("universal-coding") in rule_sets
        assert RuleSet("python-cli") in rule_sets
        assert RuleSet("flutter-app") in rule_sets
        # No duplicates
        assert rule_sets.count(RuleSet("universal-coding")) == 1

        # Both should contribute their skills
        assert "cpc-audit" in skill_names
        assert "flutter-interface-design" in skill_names
        # No duplicates
        assert skill_names.count("cpc-audit") == 1

    def test_unknown_profile_errors(self) -> None:
        from cpc.config import load_config, resolve_profiles

        config = load_config()
        with pytest.raises(KeyError):
            resolve_profiles(["nonexistent"], config)


class TestMultiProfileInstall:
    """Tests for additive multi-profile installation."""

    def test_additive_install_preserves_existing(self, tmp_path: Path) -> None:
        """Installing a second profile keeps the first profile's symlinks."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install universal (simulating first profile)
        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Install union of both (simulating additive install)
        result = install_profile(
            target=target,
            rule_sets=[UNIVERSAL, TYPESCRIPT_WEB],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        rules = target / ".claude" / "rules"
        assert (rules / "universal-coding-review.md").is_symlink()
        assert (rules / "typescript-web-types.md").is_symlink()
        assert len(result.cleaned) == 0

    def test_duplicate_profile_not_added_twice(self, tmp_path: Path) -> None:
        """Re-installing same profile doesn't duplicate in manifest."""
        from cpc.config import save_manifest, load_manifest

        target = tmp_path / "project"
        target.mkdir()

        save_manifest(target, ["python-cli"])
        manifest = load_manifest(target)
        assert manifest is not None

        # Simulate what install does: append if not present
        profiles = list(manifest.profiles)
        if "python-cli" not in profiles:
            profiles.append("python-cli")

        assert profiles == ["python-cli"]


class TestMultiProfileUninstall:

    def test_uninstall_one_of_two_profiles(self, tmp_path: Path) -> None:
        """Uninstalling one profile keeps the other's symlinks."""
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        # Install both profiles' rules (union)
        install_profile(
            target=target,
            rule_sets=[UNIVERSAL, TYPESCRIPT_WEB],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        # Sync with only UNIVERSAL (simulating uninstall of typescript-web profile)
        result = install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        rules = target / ".claude" / "rules"
        assert (rules / "universal-coding-review.md").is_symlink()
        assert not (rules / "typescript-web-types.md").exists()
        assert len(result.cleaned) == 1

    def test_uninstall_last_profile_cleans_everything(self, tmp_path: Path) -> None:
        """Uninstalling the last profile removes all symlinks and manifest."""
        from cpc.config import load_manifest, save_manifest
        from cpc.linker import install_profile

        rules_dir = _create_source_rules(tmp_path)
        target = _create_target(tmp_path)

        install_profile(
            target=target,
            rule_sets=[UNIVERSAL],
            skill_dirs=[],
            rules_dir=rules_dir,
        )
        save_manifest(target, ["python-cli"])

        # Sync with empty sets (simulating uninstall of last profile)
        result = install_profile(
            target=target,
            rule_sets=[],
            skill_dirs=[],
            rules_dir=rules_dir,
        )

        save_manifest(target, [])
        assert load_manifest(target) is None
        assert len(result.cleaned) == 2

    def test_uninstall_nonexistent_profile(self, tmp_path: Path) -> None:
        """Uninstalling a profile not in the manifest is detected."""
        from cpc.config import save_manifest, load_manifest

        target = tmp_path / "project"
        target.mkdir()
        save_manifest(target, ["python-cli"])
        manifest = load_manifest(target)
        assert manifest is not None
        assert "flutter-app" not in manifest.profiles

    def test_clean_gitignore_removes_cpc_section(self, tmp_path: Path) -> None:
        """_clean_gitignore removes the cpc section from .gitignore."""
        from cpc.linker import _clean_gitignore

        target = tmp_path / "project"
        target.mkdir()
        gitignore = target / ".gitignore"
        gitignore.write_text(
            "node_modules/\n"
            "\n"
            "# cpc:start (managed by cpc — do not edit)\n"
            ".claude/rules/foo.md\n"
            ".claude/.cpc.manifest.json\n"
            "# cpc:end\n"
            ".env\n"
        )

        _clean_gitignore(target)

        content = gitignore.read_text()
        assert "cpc:start" not in content
        assert "cpc:end" not in content
        assert "node_modules/" in content
        assert ".env" in content


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
