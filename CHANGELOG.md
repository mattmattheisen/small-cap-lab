# Changelog

All notable changes to the Small-Cap Lab trading platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-10-28

### Added - Agent
- **Universe Management System (Option A - Simple)**: CSV-based ticker universe with filtering and prioritization
  - `config/universe_config.json`: Configuration with filters, ETF blocklist, max_tickers (350)
  - `data/universe.csv`: Master ticker list (~180 tickers seeded from screener + alert service)
  - `shared/universe_loader.py`: Core module for CSV reading, validation, filtering, sorting
  - Small Cap Screener integration: Universe sidebar with Priority checkbox, Reload button, N/M counter
  - Rationale: Centralized ticker management for consistent screening across app; preparation for Phase 2 OHLCV caching when Russell 2000 list added
  - Status: Implemented, tested
  - Components:
    - CSV filtering: min_price ($2), min_volume (200k), market cap range ($200M-$5B), exchange whitelist, ADR/ETF exclusion
    - Priority-based sorting: Fill max_tickers with A priority first, then B, then C
    - Auto-relax logic: Falls back to top 50 by volume if all tickers filtered out
    - Edge case handling: Creates default config if missing, shows warnings for missing CSV
    - Paste CSV helper: Optional sidebar tool for appending new tickers to universe
  - Schema: ticker, name, exchange, market_cap_musd, price, avg_vol_30d, sector, is_adr, is_etf, priority (A/B/C), source, notes
  - Testing: E2E test passed with 179 tickers loaded, screening completed with 26 results
  - Phase 2 (Deferred): OHLCV parquet caching with batch fetching and progress bars when full Russell 2000 list added

### Changed - Agent
- **SmallCapScreener Class**: Modified `__init__` to accept optional `universe` parameter
  - Falls back to universe_loader if no universe provided
  - Maintains backward compatibility with existing code
  - Status: Implemented

### Fixed - Agent
- **Pandas .str Accessor Bug**: Fixed "Can only use .str accessor with string values" error
  - Explicitly set dtype for string columns in CSV loading
  - Added string conversion and NaN handling before .str operations
  - Status: Resolved, tested

## [1.1.0] - 2025-10-24

### Added - Agent
- **Regime-Alert Service**: New standalone monitoring service for ticker regime changes (regime_alert_service/)
  - 3-state HMM regime classifier (Bull/Neutral/Bear) with MA fallback
  - Automatic regime change detection vs. previous run
  - Webhook alerts for Slack/IFTTT when regime flips occur
  - Scheduled runs: 8:05 CT (pre-market) and 15:10 CT (near close)
  - Sunday skip logic and duplicate run prevention
  - CSV outputs: today_regimes.csv and changes.csv
  - Persistent state tracking in data/hmm_prev.json
  - CLI support: --force-alert, --universe, --skip-schedule-check
  - Lightweight logging to out/run.log
  - Rationale: User requested autonomous monitoring service for regime transitions with mobile alerting
  - Status: Tested, production-ready
  - Components:
    - regime_classifier.py: HMM + MA fallback classification
    - regime_service.py: Main detection and alerting logic
    - scheduler.py: Trading day scheduling and guardrails
    - logger.py: Run history tracking
    - main.py: CLI entry point
    - test_service.sh: Comprehensive test suite
  - Configuration: config/universe.txt with 10 seed tickers (APPS, ATUS, CSIQ, FUBO, WOLF, ARQQ, SPIR, SES, SANA, JKS)
  - Environment variables: ALERT_WEBHOOK_URL, TIMEZONE (defaults to America/Chicago)

## [1.0.0] - 2025-10-21

### Added - Agent
- **CHANGELOG.md**: Created change management system following Keep a Changelog format
  - Rationale: Establish formal change tracking for multi-developer collaboration
  - Status: Implemented

### Removed - Agent
- **Sidebar User Manual Section**: Removed download button and section from sidebar (app.py lines 39-68)
  - Rationale: Button visibility issues in production; simplified sidebar UX
  - Status: Implemented, tested
- **Sidebar Data Refresh Section**: Removed refresh button and section from sidebar (app.py lines 39-68)
  - Rationale: Button visibility issues in production; simplified sidebar UX
  - Status: Implemented, tested

### Fixed - Agent
- **CSS Display Override Bug**: Removed `display: inline-block !important` from dark_terminal_styles.py
  - Rationale: CSS was breaking Streamlit's BaseWeb inline-flex layout, collapsing buttons to 0×0 pixels
  - Context: Attempted to force button visibility but inadvertently broke layout system
  - Status: Fixed, reverted to Streamlit defaults
- **Sidebar Collapse**: Added `transform: none !important` to prevent sidebar collapse
  - Status: Implemented

## [1.0.0-beta] - 2025-10-16

### Added - User/Agent
- **Dark Bloomberg Terminal Theme**: Complete UI transformation (dark_terminal_styles.py)
  - Dark color scheme (#1e1e1e background, #2a2a2a panels, sharp corners)
  - Professional data-dense layout optimized for trading
  - Removed all emojis and symbols from entire application
  - Monospace fonts for numeric values
  - Status: Production-ready, architect approved

### Changed - User
- **Project Rename**: MarkovSignals → Small-Cap Lab
  - Updated all references in app.py, replit.md, documentation
  - Verified transaction cost logic intact after rename
  - Status: Complete, verified

## [1.0.0-alpha] - 2025-10-15

### Added - User/Agent
- **Phase 1 Kelly Criterion Upgrade**: Advanced position sizing with transaction cost analysis (kelly_calculator.py)
  - Adaptive Kelly base factor: 0.15 with ATR-based volatility adjustment
  - Transaction cost estimation: spread, market impact, slippage
  - Net edge calculation: `net_edge = decayed_edge - tx_costs`
  - Edge decay function: `gross_edge × exp(-0.15 × holding_days)`
  - Regime transition detection with risk multipliers (STABLE=1.0, UNCERTAIN=0.75, TRANSITIONING=0.5)
  - Status: Fully integrated into live workflow (3 tabs: HMM Signals, Kelly Sizing, Combined Analytics)
- **Transaction Cost Functions**:
  - `calculate_transaction_costs()`: Estimates spread, impact, slippage in basis points
  - `calculate_net_edge()`: Subtracts costs from decayed edge, returns tradeable flag
  - Final filter: Sets Kelly=0 if net_edge ≤ 0
  - Status: Active in all Kelly calculations

### Changed - Agent
- **Kelly Summary Display**: Enhanced HMM tab card to show 8 metrics including net edge and transaction costs
  - Status: Implemented

## [0.9.0] - 2025-10-14

### Fixed - Agent
- **CSV Export Date Conversion Issue**: Small Cap Screener Excel date bug
  - Created separate `format_csv_export()` method for numeric CSV formatting
  - Score column exports as plain numbers instead of "7/10" text
  - Header changed to "Score (out of 10)" to prevent Excel misinterpretation
  - Status: Resolved

### Added - Agent
- **CSV Download Buttons**: Separate buttons for current and previous screening results
  - Status: Implemented

## [0.8.0] - 2025-10-13

### Changed - User/Agent
- **Major Feature Swap**: Replaced Sharpe Ratio analysis with Kelly Criterion position sizing
  - Hybrid win probability: HMM regime probabilities × historical win rates
  - Speedometer gauge visualization with 4 color-coded risk zones
  - Fractional Kelly support (Half Kelly 0.5x recommended)
  - Status: Production

### Fixed - Agent
- **Small Cap Screener Rotation**: Expanded universe to 200+ stocks with microsecond-based random seed
  - Status: Implemented

### Added - Agent
- **Data Caching System**: 1-hour TTL with manual refresh buttons
  - Toast notifications for all data refresh actions
  - Status: Active

## [0.7.0] - 2025-07-25

### Added - User/Agent
- **Candlestick Pattern Recognition**: Custom pattern detection integrated with HMM (pattern_utils.py)
  - Detects: Bullish/Bearish Engulfing, Morning/Evening Star, Hammer
  - Combined signal system: STRONG_BUY/STRONG_SELL when HMM + patterns align
  - Pattern analysis dashboard with 30-day history
  - Conflict detection: HOLD when HMM and patterns disagree
  - Status: Fully integrated, no external dependencies

## [0.6.0] - 2025-01-24

### Added - User/Agent
- **HMM Trading Signal Generator Integration**: Original user's HMM system (hmm_signal_generator.py)
  - 3-state regime classification (Bear, Sideways, Bull)
  - Feature engineering: returns, volatility, volume ratios, momentum, RSI
  - Gaussian Mixture Models as HMM approximation
  - Status: Core feature

### Added - Agent
- **Small Cap Stock Screener**: Advanced fundamental analysis tool (small_cap_screener.py)
  - Revenue/EPS growth filters, debt ratios, PEG ratios, volume requirements
  - 10-point scoring system
  - Status: Production-ready

### Fixed - Agent
- **yfinance Data Handling**: Resolved MultiIndex columns and data shape errors
  - Updated for modern yfinance API changes
  - Status: Stable

---

## Development Notes

### Active Components (Verified 2025-10-21)
- **Transaction Cost Integration**: ✅ Active in all Kelly calculations across 3 tabs
- **HMM Regime Detection**: ✅ Fully functional
- **Kelly Position Sizing**: ✅ With transaction costs and net edge filtering
- **Small Cap Screener**: ✅ 200+ stock universe with rotation
- **Dark Bloomberg Terminal Theme**: ✅ Production aesthetic

### Known Issues
- None currently tracked

### Rollback History
- **2025-10-21**: Removed sidebar buttons (User Manual, Data Refresh) due to persistent production visibility issues despite CSS fixes

---

## Change Management Protocol

**Before Making Changes:**
1. Read this CHANGELOG.md to check if similar changes were previously implemented or reverted
2. Verify no conflicts with existing functionality

**After Making Changes:**
1. Update this file with date, developer/initials, description, rationale, and status
2. Align Git commit message with changelog entry
3. Test changes before marking status as "Implemented"

**Status Values:**
- `Planned` - Scheduled but not started
- `In Progress` - Currently being implemented
- `Implemented` - Code written, not yet tested
- `Tested` - Verified working in development
- `Production` - Live and stable
- `Deprecated` - Marked for removal
- `Rolled Back` - Reverted due to issues
