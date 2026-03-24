# idle-jiggle-macos

Prevents macOS idle detection (e.g. sleep, screen lock) by sending a synthetic **fn** keypress after a configurable period of inactivity. Does nothing while you're actively using the system, so there's no cursor wobble or other artifacts.

## How it works

1. Reads the system idle time via `ioreg` (`IOHIDSystem` / `HIDIdleTime`).
2. If idle time exceeds the threshold (default **120 seconds**), sends a synthetic `fn` key code 63 press through `osascript` / System Events.
3. If you're still active, it exits without doing anything.

## Usage

```bash
# One-shot check (e.g. from a shell script)
./idle-jiggle.py

# Verbose output
./idle-jiggle.py -v

# Crontab - stay alive over lunch on workdays
*/2 12-13 * * 1-5 /usr/local/bin/idle-jiggle.py
```

## Requirements

- **macOS** - uses `ioreg` and `osascript` (no external dependencies).
- **Accessibility permissions** - `osascript` needs access in  
  *System Settings → Privacy & Security → Accessibility*.  
  macOS will prompt you on first run if not already granted.

## License

See [LICENSE](LICENSE).
