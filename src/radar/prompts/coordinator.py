"""Coordinator system prompt builder."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from radar.theme_loader import ThemeProfile


def build_coordinator_prompt(theme: Optional[ThemeProfile], report_type: str) -> str:
    theme_section = theme.to_agent_context() if theme else ""
    today = datetime.utcnow().strftime("%Y-%m-%d")

    return f"""You are the Coordinator for the Embodied AI Radar system.
You act as a PI (Principal Investigator) directing a team of PhD student agents
to produce high-quality research monitoring reports.

## Your Role
Orchestrate the following pipeline in strict order:
1. **Monitor** — collect raw data (arXiv, Twitter/X, RSS feeds)
2. **Analyst** — score, rank, deduplicate, detect trends
3. **Writer** — generate reports in all 6 formats (3 Markdown + 3 HTML)
4. **Archivist** — persist results to radar.db

## Today
Date: {today}
Report Type: {report_type}
{theme_section}

## Pipeline Instructions

### Step 1: Delegate to Monitor
Pass the active theme context. Monitor returns a JSON array of raw items.

### Step 2: Delegate to Analyst
Pass Monitor's raw items + theme context.
Analyst returns: ranked_items[], trend_clusters[], alerts[], weekly_delta.

### Step 3: Delegate to Writer
Pass Analyst's structured data.
Writer generates all 6 report files + sub-theme articles if daily.
Save to correct paths under reports/.

### Step 4: Delegate to Archivist
Pass report paths + item list for persistence.
Archivist upserts all items to radar.db and logs the report.

## Output
After all steps complete, output a brief summary:
- Items collected
- Top 3 highlights
- Report file paths
- Any alerts triggered

## Quality Standards
- Every paper/tweet must include its source URL
- Reports must be publication-ready quality
- HTML reports must include Mermaid.js diagrams
- All content must be provided in both Japanese and English
"""


def build_daily_prompt(theme: Optional[ThemeProfile] = None) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"""Run the daily Embodied AI Radar digest for {today}.

1. Collect today's papers from arXiv (cs.RO, cs.AI, cs.LG, cs.CV)
2. Fetch tweets from the last 24 hours from watched accounts and keywords
3. Scan lab RSS feeds for new blog posts
4. Analyze and rank all items
5. Generate 6 report variants in reports/daily/{today}/
6. Generate 2-4 sub-theme articles based on today's highest-scoring topics
7. Log everything to radar.db

Focus on: Embodied AI, robot learning, VLA models, world models, humanoid robotics.
"""


def build_weekly_prompt(theme: Optional[ThemeProfile] = None) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    week = datetime.utcnow().strftime("%Y-W%W")
    return f"""Run the weekly Embodied AI Radar comprehensive report for {week}.

1. Aggregate all items from the past 7 days in radar.db
2. Identify major trends and breakthroughs of the week
3. Compare against the previous week (weekly_delta)
4. Generate comprehensive 6-format reports in reports/weekly/{week}/
5. Include trend charts (Mermaid diagrams), paper tables, researcher spotlights
6. Identify emerging research directions and open problems

Be thorough and academic in depth. This is the main weekly deliverable.
"""


def build_deep_dive_prompt(theme: ThemeProfile) -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"""Run a focused deep-dive on: **{theme.name}**

Theme: {theme.slug}
Date: {today}

1. Collect papers with extended lookback ({theme.sources.get('arxiv', {}).get('lookback_days', 7)} days)
2. Search for all key papers in the theme history (Semantic Scholar)
3. Map the research landscape: key papers, methods, benchmarks, researchers
4. Identify the frontier: what's solved vs. open problems
5. Generate expert-level 6-format reports in reports/deep-dives/{theme.slug}/{today}/

Technical depth: {theme.technical_depth}
Sections: {', '.join(theme.report_sections)}
"""
