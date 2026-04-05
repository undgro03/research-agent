#!/usr/bin/env python3
"""Run the daily Embodied AI Radar digest."""
import asyncio
import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@click.command()
@click.option("--theme", default="embodied-ai-overview", help="Theme slug")
@click.option("--alerts-only", is_flag=True, help="Only check for high-impact alerts")
def main(theme: str, alerts_only: bool):
    """Run the daily Embodied AI Radar digest."""
    from radar.orchestrator import run_daily

    if alerts_only:
        print("[radar] Running alerts-only check...")
        # TODO: lightweight alert check
        return

    print(f"[radar] Starting daily digest — theme: {theme}")
    asyncio.run(run_daily(theme))


if __name__ == "__main__":
    main()
