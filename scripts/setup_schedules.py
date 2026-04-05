#!/usr/bin/env python3
"""Register durable RemoteTrigger cron schedules for the Embodied AI Radar.

Schedules are in Toronto time (ET = UTC-5 / EDT = UTC-4).
Toronto 7:00 AM EDT = 11:00 UTC
Toronto 7:00 AM EST = 12:00 UTC

We use 11:00 UTC (covers EDT / summer time).
"""
import sys
from pathlib import Path

# These triggers are registered via Claude Code's RemoteTrigger mechanism.
# Run this script inside a Claude Code session to register the schedules.

TRIGGERS = [
    {
        "name": "radar-daily-digest",
        "cron": "0 11 * * *",   # 7:00 AM EDT (Toronto)
        "prompt": (
            "Run the Embodied AI Radar daily digest. "
            "Change to /Users/undgro03/work/embodied-ai-radar and execute: "
            "python scripts/run_daily.py --theme embodied-ai-overview"
        ),
        "description": "Daily Embodied AI Radar digest at 7 AM Toronto time",
    },
    {
        "name": "radar-weekly-report",
        "cron": "0 11 * * 1",   # Monday 7:00 AM EDT
        "prompt": (
            "Run the Embodied AI Radar weekly comprehensive report. "
            "Change to /Users/undgro03/work/embodied-ai-radar and execute: "
            "python scripts/run_weekly.py --theme embodied-ai-overview"
        ),
        "description": "Weekly Embodied AI Radar report every Monday at 7 AM Toronto time",
    },
    {
        "name": "radar-alert-check",
        "cron": "0 */4 * * *",   # Every 4 hours
        "prompt": (
            "Check for high-impact Embodied AI research alerts. "
            "Change to /Users/undgro03/work/embodied-ai-radar and execute: "
            "python scripts/run_daily.py --alerts-only"
        ),
        "description": "High-impact paper alert check every 4 hours",
    },
]


def print_trigger_info():
    print("\n📅 Embodied AI Radar — Schedule Configuration")
    print("=" * 56)
    for t in TRIGGERS:
        print(f"\n  Name:   {t['name']}")
        print(f"  Cron:   {t['cron']}")
        print(f"  Desc:   {t['description']}")
    print("\n" + "=" * 56)
    print("\nTo register these triggers, run this script inside a Claude Code")
    print("session with RemoteTrigger access, or use the /schedule command:\n")
    for t in TRIGGERS:
        print(f"  /schedule create \"{t['name']}\" \"{t['cron']}\" \"{t['prompt'][:60]}...\"")
    print()


if __name__ == "__main__":
    print_trigger_info()

    # When running inside Claude Code with RemoteTrigger available,
    # the actual registration is handled by the agent via RemoteTrigger tool.
    # This script serves as documentation and can be extended for API-based registration.
    print("[setup] Trigger definitions printed. Register via Claude Code /schedule command.")
