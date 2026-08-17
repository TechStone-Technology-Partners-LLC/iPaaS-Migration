# Trigger: scheduled_event / timer (Scheduled Recipe)

Fires the recipe on a recurring schedule. No input schema — the trigger provides a
`scheduled_at` timestamp datapill that downstream steps can reference.

---

## Complete Python Code

```python
from uuid import uuid4

TRIG = "clock"   # alias for this trigger

trigger = {
    "number": 0,
    "keyword": "trigger",
    "provider": "scheduled_event",
    "name": "timer",
    "as": TRIG,
    "uuid": str(uuid4()),
    "dynamicPickListSelection": {},
    "toggleCfg": {},
    "input": {
        "interval": "1",
        "interval_unit": "hours",
        "start_at": ""          # empty = start immediately when recipe is activated
    },
    "block": [...]
}
```

---

## interval_unit Options

| Value | Description |
|-------|-------------|
| `"minutes"` | Run every N minutes |
| `"hours"` | Run every N hours |
| `"days"` | Run every N days |

Minimum interval: 1 minute. Maximum practical interval: 7 days.

---

## Examples

```python
# Every 15 minutes
"input": {"interval": "15", "interval_unit": "minutes", "start_at": ""}

# Every 6 hours
"input": {"interval": "6", "interval_unit": "hours", "start_at": ""}

# Daily at a specific start time (ISO 8601 format)
"input": {"interval": "1", "interval_unit": "days", "start_at": "2026-01-01T08:00:00Z"}
```

---

## start_at

- Empty string `""` → recipe starts running immediately on activation.
- ISO 8601 datetime string → first run at that time; subsequent runs follow the interval.

---

## Accessing the scheduled_at Datapill

The timer trigger provides one output field: `scheduled_at` (ISO 8601 timestamp).

```python
def dp(provider, line, *path_parts):
    path = [{"path_element_type": "current_item"} if p == "*" else p for p in path_parts]
    pill = json.dumps({"pill_type": "output", "provider": provider, "line": line,
                       "path": path}).replace('"', '\\"')
    return "#{_dp('" + pill + "')}"

# Use the scheduled run time in a step input
dp("scheduled_event", TRIG, "scheduled_at")
```

---

## Config Entry

```python
config = [
    {"keyword": "application", "provider": "scheduled_event",
     "account_id": None, "skip_validation": False},
    # ... other providers ...
]
```

`scheduled_event` always uses `account_id: None`.

---

## Notes

- Scheduled recipes cannot accept external input — if you need to pass data at runtime,
  use a callable trigger instead.
- The first execution after activation may be delayed up to one interval unit.
- For testing, activate the recipe and use the "Run now" button in the Workato GUI to
  trigger an immediate run without waiting for the schedule.
