# Robotics AI Radar — Project Memory

## Purpose
Automated research monitoring system for the Robotics/Embodied AI field.
Modeled as: PI (user) assigning tasks to PhD student (Claude).

The system monitors X (Twitter) for breaking news, tracks arXiv and major lab publications daily, generates structured research reports (Markdown + HTML/CSS consulting-style), and supports focused deep-dives on specific themes.

## Agent Roles
- **Coordinator** (main session): orchestrates the pipeline, delegates all leaf work
- **Monitor** (subagent): data collection only — arXiv, X/Twitter, RSS, lab pages
- **Analyst** (subagent): scoring, ranking, trend detection — uses claude-opus-4-6
- **Writer** (subagent): report generation in 6 formats — uses claude-sonnet-4-6
- **Archivist** (subagent): SQLite persistence — uses claude-haiku-4-5

## Key Directories
- `themes/` — YAML profiles driving each deep-dive (extend `_base.yaml`)
- `reports/daily/` — daily digests (YYYY-MM-DD/)
- `reports/weekly/` — weekly reports (YYYY-WNN/)
- `reports/deep-dives/<theme>/` — per-theme deep-dive reports
- `data/radar.db` — SQLite memory store
- `data/feeds.yaml` — lab RSS feeds, X accounts, paper sources with links
- `.claude/agents/` — subagent definition files
- `src/radar/` — Python package
- `templates/` — HTML/CSS report templates

## Report Formats (6 variants per run)
1. `report_ja.md` — Markdown, Japanese
2. `report_en.md` — Markdown, English
3. `report_bilingual.md` — Markdown, Japanese + English
4. `report_ja.html` — HTML/CSS consulting-style with Mermaid diagrams, Japanese
5. `report_en.html` — HTML/CSS consulting-style with Mermaid diagrams, English
6. `report_bilingual.html` — HTML/CSS consulting-style, bilingual

Plus daily sub-theme articles (`articles/<slug>/YYYY-MM-DD.md` + `.html`).

## Theme Profiles
All themes extend `themes/_base.yaml`. Available themes:
- `embodied-ai-overview` — Embodied AI全体 (main theme)
- `world-action-models` — World Models × Action
- `vlm-robotics` — VLM × ロボット制御
- `action-video-generation` — Action Conditioned Video Generation

To add a new theme: create `themes/<slug>.yaml` with `extends: _base`.

## Scheduling (Toronto Time / ET)
- Daily digest: 7:00 AM ET → `python scripts/run_daily.py`
- Weekly report: Monday 7:00 AM ET → `python scripts/run_weekly.py`
- Alert check: every 4 hours → `python scripts/run_daily.py --alerts-only`
- To register: `python scripts/setup_schedules.py`

## Database (data/radar.db)
Tables: `items`, `trend_snapshots`, `reports`, `alerts`, `articles`
Items deduplicated by sha256(source+url). Pruned after 90 days.

## API Keys
See `.env` / `.env.example`:
- `ANTHROPIC_API_KEY`
- `TWITTER_BEARER_TOKEN` — X API v2, read-only monitoring

## Running
```bash
uv sync
python scripts/init_db.py
python scripts/setup_schedules.py

python scripts/run_daily.py
python scripts/run_weekly.py
python scripts/run_deep_dive.py --theme vla-models
```

Slash commands: `/daily`, `/weekly`, `/deep-dive <theme>`
