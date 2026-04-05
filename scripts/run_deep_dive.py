#!/usr/bin/env python3
"""Run a focused deep-dive on a specific Embodied AI theme."""
import asyncio
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@click.command()
@click.option("--theme", required=True, help="Theme slug (e.g. vla-models)")
def main(theme: str):
    """Run a focused deep-dive on a specific theme."""
    from radar.orchestrator import run_deep_dive
    from radar.theme_loader import list_themes

    available = list_themes()
    if theme not in available:
        print(f"[radar] Unknown theme: {theme}")
        print(f"[radar] Available: {', '.join(available)}")
        sys.exit(1)

    print(f"[radar] Starting deep-dive — theme: {theme}")
    asyncio.run(run_deep_dive(theme))


if __name__ == "__main__":
    main()
