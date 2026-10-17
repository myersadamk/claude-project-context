"""Validate all agent definition files in agents/ have correct frontmatter."""
import re
from pathlib import Path

import yaml
import pytest

AGENTS_DIR = Path(__file__).parent.parent / "agents"

VALID_MODELS = {"opus", "sonnet", "haiku"}
VALID_EFFORTS = {"max", "high", "medium", "low"}
REQUIRED_FIELDS = {"name", "description", "model", "effort"}

# Agents that must NOT have Write, Edit, or NotebookEdit in their tools list
READ_ONLY_AGENTS = {
    "research-max",
    "research-high",
    "review-code-high",
    "review-spec-low",
    "git-ops-low",
    "git-ops-high",
}

WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}


def parse_frontmatter(path: Path) -> dict:
    content = path.read_text()
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        pytest.fail(f"{path.name}: missing or malformed frontmatter delimiters")
    return yaml.safe_load(match.group(1))


AGENT_FILES = sorted(p for p in AGENTS_DIR.glob("*.md") if p.stem != "README")


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_agent_is_not_empty(path: Path) -> None:
    assert path.stat().st_size > 0, f"{path.name} is empty"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_required_frontmatter_fields(path: Path) -> None:
    fm = parse_frontmatter(path)
    missing = REQUIRED_FIELDS - fm.keys()
    assert not missing, f"{path.name}: missing fields {missing}"


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_name_matches_filename(path: Path) -> None:
    fm = parse_frontmatter(path)
    assert fm["name"] == path.stem, (
        f"{path.name}: name '{fm['name']}' does not match filename stem '{path.stem}'"
    )


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_valid_model(path: Path) -> None:
    fm = parse_frontmatter(path)
    assert fm["model"] in VALID_MODELS, (
        f"{path.name}: model '{fm['model']}' not in {VALID_MODELS}"
    )


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_valid_effort(path: Path) -> None:
    fm = parse_frontmatter(path)
    assert fm["effort"] in VALID_EFFORTS, (
        f"{path.name}: effort '{fm['effort']}' not in {VALID_EFFORTS}"
    )


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_read_only_agents_have_no_write_tools(path: Path) -> None:
    # Guard is intentional: non-read-only agents have no tools field so they
    # would pass this check vacuously. Skip them — this test is only meaningful
    # for agents that are supposed to be restricted.
    if path.stem not in READ_ONLY_AGENTS:
        pytest.skip("not a read-only agent")
    fm = parse_frontmatter(path)
    # tools field presence is enforced separately by test_read_only_agents_declare_tools_field
    raw = fm.get("tools", [])
    if isinstance(raw, str):
        tools = {t.strip() for t in raw.split(",")}
    else:
        tools = set(raw)
    forbidden = tools & WRITE_TOOLS
    assert not forbidden, (
        f"{path.name}: read-only agent has write tools {forbidden}"
    )


@pytest.mark.parametrize("path", AGENT_FILES, ids=lambda p: p.stem)
def test_read_only_agents_declare_tools_field(path: Path) -> None:
    """Read-only agents must declare a tools field — omitting it grants full access."""
    if path.stem not in READ_ONLY_AGENTS:
        pytest.skip("not a read-only agent")
    fm = parse_frontmatter(path)
    assert "tools" in fm, (
        f"{path.name}: read-only agent must declare tools field to restrict access"
    )


def test_all_12_agents_exist() -> None:
    expected = {
        "general-max", "general-high", "general-med", "general-low",
        "coding-high", "coding-med",
        "research-max", "research-high",
        "review-code-high", "review-spec-low",
        "git-ops-low", "git-ops-high",
    }
    found = {p.stem for p in AGENT_FILES if p.stem != "README"}
    missing = expected - found
    assert not missing, f"Missing agent files: {missing}"
