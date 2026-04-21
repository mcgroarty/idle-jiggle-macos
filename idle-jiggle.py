#!/usr/bin/env python3
"""
idle-jiggle.py - One-shot idle timer reset when idle > threshold.

Prevents idle detection by sending a synthetic fn keypress
after a configurable period of inactivity.  Does nothing while
you're actively using the system.  This prevents wobble or other
artifacts while actively using the system.

Usage modes:

Use in a busy loop from your shell scripts for tasks that you
want to complete before power saving kicks in. Call it all you
like.

Run from crontab every few minutes during desired hours, e.g.
staying alive over lunch on workdays:
  */2 12-13 * * 1-5 /usr/local/bin/idle-jiggle.py

No external dependencies - uses ioreg and osascript via subprocess.


Note: osascript needs Accessibility permissions in
  System Settings > Privacy & Security > Accessibility

You'll be prompted by macOS if you haven't set them yet.
"""

import argparse
import re
import subprocess
import sys

IDLE_THRESHOLD = 120  # seconds (2 minutes)
#IDLE_THRESHOLD = 300  # seconds (5 minutes)


def check_accessibility():
    """Check that the calling process has Accessibility permissions."""
    result = subprocess.run(
        [
            "/usr/bin/osascript",
            "-e",
            'tell application "System Events" to get name of first process',
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            "Error: Accessibility permission required.\n"
            "Grant access to the calling process (e.g. Terminal, iTerm2, cron)\n"
            "in System Settings > Privacy & Security > Accessibility.",
            file=sys.stderr,
        )
        sys.exit(1)


def get_idle_seconds():
    """Return seconds since last keyboard/mouse input via ioreg."""
    try:
        out = subprocess.check_output(
            ["/usr/sbin/ioreg", "-c", "IOHIDSystem", "-d", "4"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        return 0

    for line in out.splitlines():
        if "HIDIdleTime" in line:
            match = re.search(r"=\s*(\d+)", line)
            if match:
                return int(match.group(1)) // 1_000_000_000
    return 0


def nudge():
    """Send a synthetic fn keypress (key code 63) to reset the idle timer."""
    subprocess.run(
        [
            "/usr/bin/osascript",
            "-e",
            'tell application "System Events" to key code 63',
        ],
        stderr=subprocess.DEVNULL,
    )


def main():
    parser = argparse.ArgumentParser(description="Reset idle timer when idle")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    check_accessibility()

    idle = get_idle_seconds()

    if args.verbose:
        print(f"Idle: {idle}s (threshold: {IDLE_THRESHOLD}s)")

    if idle > IDLE_THRESHOLD:
        if args.verbose:
            print("Nudging")
        nudge()
    else:
        if args.verbose:
            print("Active - no nudge")


if __name__ == "__main__":
    main()
