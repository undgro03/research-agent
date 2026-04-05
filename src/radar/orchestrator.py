"""Main orchestrator — wires theme profiles to subagents and drives the pipeline."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

from radar.theme_loader import ThemeProfile
from radar.prompts.coordinator import (
    build_coordinator_prompt,
    build_daily_prompt,
    build_weekly_prompt,
    build_deep_dive_prompt,
)

load_dotenv()

AGENTS_DIR = Path(__file__).parent.parent.parent / ".claude" / "agents"


def _load_agent_md(name: str) -> str:
    path = AGENTS_DIR / f"{name}.md"
    if path.exists():
        return path.read_text()
    return f"You are the {name} subagent for the Embodied AI Radar."


async def run_daily(theme_slug: str = "embodied-ai-overview") -> None:
    theme = ThemeProfile.load(theme_slug)
    await _run_pipeline(
        task_prompt=build_daily_prompt(theme),
        theme=theme,
        report_type="daily",
    )


async def run_weekly(theme_slug: str = "embodied-ai-overview") -> None:
    theme = ThemeProfile.load(theme_slug)
    await _run_pipeline(
        task_prompt=build_weekly_prompt(theme),
        theme=theme,
        report_type="weekly",
    )


async def run_deep_dive(theme_slug: str) -> None:
    theme = ThemeProfile.load(theme_slug)
    await _run_pipeline(
        task_prompt=build_deep_dive_prompt(theme),
        theme=theme,
        report_type="deep_dive",
    )


async def _run_pipeline(
    task_prompt: str,
    theme: Optional[ThemeProfile],
    report_type: str,
) -> None:
    """Execute the Monitor → Analyst → Writer → Archivist pipeline."""
    client = anthropic.Anthropic()
    system_prompt = build_coordinator_prompt(theme, report_type)
    theme_context = theme.to_agent_context() if theme else ""

    # Build the full prompt with subagent delegation instructions
    full_prompt = f"""{task_prompt}

{theme_context}

## Subagent Instructions

Use the Agent tool to delegate to each subagent in order:

### 1. Monitor Agent
<monitor_instructions>
{_load_agent_md('monitor')}
</monitor_instructions>

### 2. Analyst Agent
<analyst_instructions>
{_load_agent_md('analyst')}
</analyst_instructions>

### 3. Writer Agent
<writer_instructions>
{_load_agent_md('writer')}
</writer_instructions>

### 4. Archivist Agent
<archivist_instructions>
{_load_agent_md('archivist')}
</archivist_instructions>
"""

    print(f"\n{'='*60}")
    print(f"Embodied AI Radar — {report_type.upper()}")
    if theme:
        print(f"Theme: {theme.name}")
    print(f"{'='*60}\n")

    # For now, run as a standard Claude API call
    # In production this uses claude-agent-sdk with subagent delegation
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": full_prompt}],
    )

    result = response.content[0].text
    print(result)
    return result
