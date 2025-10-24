# Regime-Alert Service

Monitors a ticker universe for HMM regime changes and sends mobile alerts.

## Overview

This service:
- Pulls daily prices for a configured ticker universe
- Assigns each ticker a regime (Bull / Neutral / Bear) using 3-state HMM
- Detects regime changes vs. the prior run
- Sends webhook alerts when changes occur
- Runs twice daily on trading days (8:05 CT and 15:10 CT)
- Skips Sundays entirely

## Quick Start

### 1. Install Dependencies

```bash
cd regime_alert_service
pip install yfinance scikit-learn pandas numpy pytz requests
```

### 2. Configure Universe

Edit `config/universe.txt` with one ticker symbol per line:

```
APPS
ATUS
CSIQ
FUBO
...
```

### 3. Set Environment Variables

```bash
export ALERT_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export TIMEZONE="America/Chicago"  # Optional, defaults to CT
```

For Slack: Create an Incoming Webhook in your Slack workspace  
For IFTTT: Use IFTTT Webhooks service URL

### 4. Run the Service

```bash
python main.py
```

Or with options:

```bash
# Force alert even without changes
python main.py --force-alert

# Use custom universe file
python main.py --universe /path/to/custom_universe.txt

# Skip schedule checks (run immediately)
python main.py --skip-schedule-check
```

## Outputs

### Files Created

- `out/today_regimes.csv` - Current regimes for all symbols
  - Columns: symbol, last_price, regime, confidence, timestamp
  
- `out/changes.csv` - Regime changes detected (only when flips occur)
  - Columns: symbol, from_regime, to_regime, timestamp

- `out/run.log` - Run history with timestamps and stats

- `data/hmm_prev.json` - Persisted previous regimes for change detection

- `data/last_run.txt` - Date of last run (for duplicate prevention)

### Console Output

```
Starting regime detection at 2025-10-21T08:05:00

Wrote 10 regimes to out/today_regimes.csv
Wrote 2 changes to out/changes.csv
Alert sent: 2 changes

==================================================
REGIME SUMMARY
==================================================
Total symbols: 10
Bull: 4 | Neutral: 3 | Bear: 3
Changes detected: 2
==================================================

Completed in 12.34 seconds
```

### Webhook Alert Format

```
Regime changes:
ARQQ: Neutral → Bull
CSIQ: Bear → Neutral
```

## Regime Classification

### Primary Method: 3-State HMM

- Uses Gaussian Mixture Model on 6-9 months of daily returns
- 3 states labeled by mean return:
  - Lowest mean = **Bear**
  - Middle mean = **Neutral**
  - Highest mean = **Bull**
- Returns current state + confidence (0-1)

### Fallback Method: Moving Averages

If HMM fails (insufficient data, errors):
- Compares 20-day MA vs 50-day MA
- Classifies based on trend strength
- Returns regime with 0.5 confidence

## Scheduling

### Configured Run Times

- **08:05 CT** (pre-market)
- **15:10 CT** (near close)

### Guardrails

- Skips Sundays entirely
- Prevents duplicate runs on same day
- Lightweight API usage (no redundant downloads)

### Manual Override

Use `--skip-schedule-check` to run immediately regardless of schedule.

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ALERT_WEBHOOK_URL` | No | None | Slack/IFTTT webhook URL for alerts |
| `TIMEZONE` | No | `America/Chicago` | Timezone for scheduling |

If `ALERT_WEBHOOK_URL` is not set, alert text is printed to console instead.

## First Run Behavior

On first run:
- Creates all necessary folders (`config/`, `data/`, `out/`)
- Writes `today_regimes.csv` with current regimes
- Creates `hmm_prev.json` with initial state
- **Does not send alert** (no prior state to compare)

## Subsequent Runs

On subsequent runs:
- Compares new regimes against `hmm_prev.json`
- Writes `changes.csv` only if regime flips occur
- Sends webhook alert only if changes detected
- Updates `hmm_prev.json` with new state

## Testing Scenarios

### Test Sunday Skip

```bash
# Simulates Sunday (will skip)
python main.py
# Output: "Sunday - skipping"
```

### Test First Run

```bash
# Delete previous state
rm -f data/hmm_prev.json data/last_run.txt

python main.py --skip-schedule-check
# Output: No alert (first run, no prior state)
```

### Test Regime Change

```bash
# Manually edit data/hmm_prev.json to simulate previous different regime
# Then run:
python main.py --skip-schedule-check
# Output: Alert with regime changes
```

### Test Universe Changes

```bash
# Add new ticker to config/universe.txt
echo "TSLA" >> config/universe.txt

python main.py --skip-schedule-check
# Output: TSLA included in next run automatically
```

## Production Deployment

### Cron Schedule (Linux/Mac)

```cron
# Run twice daily on weekdays at 8:05 CT and 15:10 CT
5 8 * * 1-6 cd /path/to/regime_alert_service && python main.py
10 15 * * 1-6 cd /path/to/regime_alert_service && python main.py
```

### Windows Task Scheduler

Create two scheduled tasks:
- Trigger: Daily at 8:05 AM (skip Sunday)
- Trigger: Daily at 3:10 PM (skip Sunday)
- Action: Run `python main.py`

## Troubleshooting

### No Data Errors

If you see "No data for SYMBOL":
- Check if symbol is valid and actively traded
- Verify yfinance can access the data
- Symbol may be delisted or suspended

### Webhook Failures

If alerts aren't sending:
- Verify `ALERT_WEBHOOK_URL` is set correctly
- Test webhook URL with curl
- Check `out/run.log` for error messages

### HMM Fallback Warnings

If seeing frequent MA fallback usage:
- Symbol may not have 60+ days of data
- Consider increasing lookback period in `RegimeClassifier`

## Architecture

```
regime_alert_service/
├── main.py                 # Entry point with CLI
├── regime_service.py       # Main service logic
├── regime_classifier.py    # HMM + MA fallback
├── scheduler.py            # Timing and day checks
├── logger.py               # Run logging
├── config/
│   └── universe.txt        # Ticker symbols
├── data/
│   ├── hmm_prev.json      # Previous regimes
│   └── last_run.txt       # Last run date
└── out/
    ├── today_regimes.csv  # Current regimes
    ├── changes.csv        # Regime flips
    └── run.log            # Run history
```

## License

Internal use only.
