# Daily Digest

Run the Embodied AI Radar daily digest.

Executes the full Monitor → Analyst → Writer → Archivist pipeline for today.
Generates 6 report formats + sub-theme articles.

```bash
python scripts/run_daily.py $ARGUMENTS
```

If `$ARGUMENTS` contains a theme slug (e.g., `vla-models`), run for that theme.
Otherwise, run for `embodied-ai-overview`.
