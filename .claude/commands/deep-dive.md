# Deep Dive

Run a focused research deep-dive on a specific Embodied AI theme.

## Usage
```
/deep-dive <theme-slug>
```

## Available Themes
- `embodied-ai-overview` — Embodied AI全体
- `world-action-models` — World Models × Action
- `vlm-robotics` — VLM × Robot Control
- `action-video-generation` — Action Conditioned Video Generation

## What this does
1. Loads theme profile from `themes/<slug>.yaml`
2. Runs extended search (wider lookback, more keywords)
3. Maps the full research landscape for the theme
4. Generates expert-level 6-format reports + comprehensive articles

```bash
python scripts/run_deep_dive.py --theme $ARGUMENTS
```
