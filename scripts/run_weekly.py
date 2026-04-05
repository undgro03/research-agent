#!/usr/bin/env python3
"""Run the weekly Embodied AI Radar comprehensive report."""
import asyncio
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@click.command()
@click.option("--theme", default="embodied-ai-overview", help="Theme slug")
def main(theme: str):
    """Run the weekly comprehensive report."""
    from radar.orchestrator import run_weekly

    print(f"[radar] Starting weekly report — theme: {theme}")
    asyncio.run(run_weekly(theme))


if __name__ == "__main__":
    main()
