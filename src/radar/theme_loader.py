"""Theme profile loader — reads YAML, resolves inheritance, injects agent context."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

THEMES_DIR = Path(__file__).parent.parent.parent / "themes"


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base (override wins on conflict)."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key == "extends":
            continue
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class ThemeProfile:
    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def load(cls, slug_or_path: str) -> "ThemeProfile":
        path = Path(slug_or_path)
        if not path.suffix:
            path = THEMES_DIR / f"{slug_or_path}.yaml"
        if not path.is_absolute():
            path = THEMES_DIR / path

        data = yaml.safe_load(path.read_text())

        if "extends" in data:
            base_data = yaml.safe_load((THEMES_DIR / "_base.yaml").read_text())
            data = _deep_merge(base_data, data)

        return cls(data)

    @property
    def name(self) -> str:
        return self._data.get("name", "Unknown")

    @property
    def slug(self) -> str:
        return self._data.get("slug", "unknown")

    @property
    def description(self) -> str:
        return self._data.get("description", "")

    @property
    def sources(self) -> dict:
        return self._data.get("sources", {})

    @property
    def labs(self) -> list[dict]:
        return self._data.get("labs", [])

    @property
    def twitter_accounts(self) -> list[str]:
        return self._data.get("twitter_accounts", [])

    @property
    def researchers(self) -> dict:
        return self._data.get("researchers", {})

    @property
    def technical_depth(self) -> str:
        return self._data.get("technical_depth", "medium")

    @property
    def report_sections(self) -> list[str]:
        return self._data.get("report_sections", [])

    @property
    def alert_thresholds(self) -> dict:
        return self._data.get("alert_thresholds", {})

    @property
    def mcp_servers(self) -> list[str]:
        return self._data.get("mcp_servers", [])

    @property
    def sub_themes(self) -> list[str]:
        return self._data.get("sub_themes", [])

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_agent_context(self) -> str:
        """Structured string injected into each subagent's system prompt."""
        arxiv_kw = self.sources.get("arxiv", {}).get("keywords", [])
        twitter_kw = self.sources.get("twitter", {}).get("keywords", [])
        focus_researchers = self.researchers.get("focus", []) if isinstance(self.researchers, dict) else []

        lab_lines = []
        for lab in self.labs[:15]:  # top 15
            if isinstance(lab, dict):
                links = lab.get("links", {})
                link_str = " | ".join(f"{k}: {v}" for k, v in list(links.items())[:2])
                lab_lines.append(f"  - {lab['name']} ({link_str})")
            else:
                lab_lines.append(f"  - {lab}")

        return f"""
## Active Theme: {self.name}
{self.description}

### arXiv Search Keywords
{chr(10).join(f'  - {k}' for k in arxiv_kw)}

### Twitter/X Keywords
{chr(10).join(f'  - {k}' for k in twitter_kw)}

### Watched Labs & Companies
{chr(10).join(lab_lines)}

### Focus Researchers
{chr(10).join(f'  - {r}' for r in focus_researchers)}

### Technical Depth: {self.technical_depth}
### Report Sections: {', '.join(self.report_sections)}
### Alert Thresholds: {self.alert_thresholds}
"""

    def to_dict(self) -> dict:
        return self._data


def list_themes() -> list[str]:
    return [
        p.stem for p in THEMES_DIR.glob("*.yaml") if p.stem != "_base"
    ]
