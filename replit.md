# small-cap lab - HMM & Kelly Criterion Analysis

## Overview

This is a comprehensive trading platform built with Streamlit that combines Hidden Markov Model (HMM) regime detection with Kelly Criterion position sizing. The application provides traders and analysts with advanced tools for market regime identification, optimal position sizing recommendations, candlestick pattern confirmation, and small cap stock screening.

## Recent Changes

**October 21, 2025 - Sidebar Cleanup:**
- **Removed User Manual section** - Download button removed from sidebar
- **Removed Data Refresh section** - Refresh button removed from sidebar
- **Simplified sidebar** - Screening Criteria now appears at top of sidebar without clutter

**October 16, 2025 - Dark Bloomberg Terminal UI Transformation:**
- **Complete Dark Theme Implementation**: Transformed entire UI to professional Dark Bloomberg Terminal aesthetic
- **Dark Color Scheme**: Consistent dark backgrounds throughout
  - Body background: #1e1e1e (deep charcoal)
  - Panel backgrounds: #2a2a2a (dark gray)
  - Borders: #404040 (medium gray)
  - Text: #e0e0e0 (light gray)
- **Zero Emojis Achievement**: Removed ALL emojis and symbols from entire application
  - Removed page icon emoji, Kelly warning emojis, HMM regime icons
  - Removed checkmarks, crosses, arrows, multiplication symbols from displays
  - Python verification confirms zero emoji characters in codebase
- **Professional Design Elements**:
  - Sharp corners throughout (border-radius: 0 everywhere)
  - Gray buttons (#2a2a2a) - no colorful accent buttons
  - Monospace fonts (Consolas/Monaco/Courier New) for all numeric values
  - Data-dense layout optimized for trading professionals
- **Dark Charts**: All Plotly visualizations converted to dark theme
  - Dark backgrounds with light text for readability
  - HMM regime charts, Kelly speedometer gauge, Combined Analytics
- **Tab Reorganization**: Small Cap Screener → HMM Trading Signals → Kelly Position Sizing → Combined Analytics
- **Status Bar**: Added bottom status bar showing timestamp and data source
- **Architect Approved**: Final review confirmed production-ready Dark Bloomberg Terminal aesthetic
- **CSS Module**: Created dark_terminal_styles.py for centralized theme management

**October 15, 2025 (AM - Phase 1 Kelly Criterion):**
- **Phase 1 Kelly Criterion Upgrade - Advanced Position Sizing**: Implemented sophisticated Kelly calculator with transaction cost analysis and adaptive volatility-based sizing
- **Adaptive Kelly Base Factor**: Reduced to conservative 0.15 base with ATR-based volatility adjustment using formula: base * (confidence/100) * min(1.0, 0.05/atr_pct), capped at 0.25
- **Transaction Cost Analysis**: Comprehensive cost estimation including spread cost (from daily price range), market impact (position size vs volume), and slippage
- **Net Edge Calculation**: Implemented edge decay function: gross_edge * exp(-0.15 * holding_days) - transaction_costs, with automatic filtering to only recommend positions where net_edge > 0
- **Regime Transition Detection**: Added market state analysis with risk multipliers:
  - STABLE: Normal conditions, multiplier 1.0 (default)
  - UNCERTAIN: Low confidence (probability spread < 0.2), multiplier 0.75
  - TRANSITIONING: High volatility (>3 regime changes in last 10 periods), multiplier 0.5
- **Enhanced UI Displays**: Added Transaction Costs & Edge Analysis section showing all cost components, gross edge, net edge with tradeable indicators (✅/❌), and ATR metrics
- **Kelly Summary Enhancements**: Expanded HMM tab Kelly card to show 8 metrics including net edge, transaction costs, and regime transition warnings
- **Test Validation**: Verified with AEIS (STABLE), SOFI (TRANSITIONING), and ARRY (STABLE) - all metrics displaying correctly
- **Backup Created**: Saved previous version as kelly_calculator_backup_v1.py before major changes

**October 14, 2025:**
- **CSV Export Fix**: Resolved Excel date conversion issue in Small Cap Screener
- Created separate `format_csv_export()` method for proper numeric CSV formatting
- Score column now exports as plain numbers (7, 6, 5) instead of "7/10" text
- Changed header to "Score (out of 10)" to prevent Excel date misinterpretation
- All numeric columns (Market Cap, percentages, ratios) now export as pure numbers
- Added dedicated CSV download buttons for both current and previous screening results

**October 13, 2025:**
- **Major Update**: Replaced Sharpe Ratio analysis with Kelly Criterion position sizing calculator
- Implemented hybrid win probability calculation using HMM regime probabilities and historical win rates
- Added speedometer gauge visualization with 4 color-coded risk zones (Green/Yellow/Orange/Red)
- Integrated Kelly summary card in HMM results tab for quick position sizing recommendations
- Added data caching with 1-hour TTL and refresh buttons to prevent stale data issues
- Updated Combined Analytics tab to display Kelly metrics instead of Sharpe ratios
- Kelly calculator integrates seamlessly with HMM regime detection for optimal position sizing
- Fractional Kelly support (Half Kelly 0.5x recommended for conservative trading)
- Fixed Small Cap Screener rotation: expanded universe to 200+ stocks with microsecond-based random seed
- Added toast notifications for all data refresh actions

**July 25, 2025:**
- Successfully integrated custom candlestick pattern recognition into HMM Trading Signal Generator
- Added detection for high-information patterns: Bullish/Bearish Engulfing, Morning/Evening Star, Hammer
- Created combined signal system that enhances HMM regime detection with pattern confirmation
- Enhanced UI displays STRONG_BUY/STRONG_SELL when both HMM and patterns align
- Added pattern analysis dashboard showing current patterns and 30-day history
- Implemented conflict detection - shows HOLD when HMM and patterns disagree (for safety)
- Custom pattern detection built without external dependencies for reliability

**January 24, 2025:**
- Successfully integrated user's original HMM Trading Signal Generator with existing Sharpe Ratio Calculator
- Fixed yfinance data handling issues (MultiIndex columns and data shape errors)
- Updated both components to handle modern yfinance API changes
- Added comprehensive Small Cap Stock Screener with advanced fundamental analysis
- Screener includes revenue/EPS growth filters, debt ratios, PEG ratios, volume requirements
- All features now working smoothly with real market data
- Platform provides seamless tabbed interface for all analysis tools

## User Preferences

Preferred communication style: Simple, everyday language.

## Change Management Protocol

**Required Workflow:**
1. **Before Changes**: Read CHANGELOG.md to verify no similar changes were previously implemented or reverted
2. **After Changes**: Update CHANGELOG.md with date, developer/initials, description, rationale, and status
3. **Commit Alignment**: Ensure Git commit messages mirror changelog entries for traceability

**Format**: Keep a Changelog (https://keepachangelog.com/en/1.0.0/)

**Status Values**: Planned, In Progress, Implemented, Tested, Production, Deprecated, Rolled Back

## System Architecture

The application follows a modular, single-page web application architecture built on Streamlit:

- **Frontend**: Streamlit-based web interface with tabbed navigation
- **Backend Logic**: Python modules for HMM signal generation and Kelly Criterion calculations
- **Data Source**: Yahoo Finance API for real-time market data
- **Visualization**: Plotly for interactive charts and speedometer gauges
- **ML Component**: Scikit-learn Gaussian Mixture Models for regime detection
- **Caching**: 1-hour TTL data caching with manual refresh capabilities

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and UI orchestration
- **Architecture**: Tab-based interface with four main sections:
  - HMM Trading Signals with Kelly Summary
  - Kelly Position Sizing with Speedometer Gauge
  - Combined Analytics (HMM + Kelly)
  - Small Cap Stock Screener
- **Session Management**: Uses Streamlit session state for component persistence
- **Caching**: Implements @st.cache_data with 1-hour TTL to prevent stale data

### 2. HMM Signal Generator (`hmm_signal_generator.py`)
- **Purpose**: Market regime detection using Hidden Markov Models with candlestick pattern enhancement
- **Technology**: Gaussian Mixture Models from scikit-learn as HMM approximation
- **Features**: 
  - 3-state regime classification (Bear, Sideways, Bull)
  - Feature engineering (returns, volatility, volume ratios, momentum, RSI)
  - Signal generation based on regime transitions
  - **Enhanced**: Candlestick pattern integration for signal confirmation
  - **Combined Signals**: STRONG_BUY/STRONG_SELL when HMM + patterns align

### 3. Kelly Criterion Calculator (`kelly_calculator.py`)
- **Purpose**: Optimal position sizing based on win probability and risk/reward ratios
- **Technology**: Kelly Criterion formula with hybrid probability calculation
- **Features**:
  - Hybrid win probability using HMM regime probabilities × historical win rates
  - Win/Loss ratio calculation from regime average returns
  - Fractional Kelly support (0.5x Half Kelly recommended)
  - Speedometer gauge visualization with 4 color-coded risk zones:
    - Green (0-25%): Conservative
    - Yellow (25-50%): Optimal/Moderate
    - Orange (50-75%): Aggressive
    - Red (75-100%): Very Aggressive/Danger
  - Position size recommendations based on portfolio value and stop loss
  - Integration with HMM regime detection for dynamic position sizing

### 4. Pattern Recognition (`pattern_utils.py`)
- **Purpose**: Custom candlestick pattern detection and signal combination
- **Technology**: Custom algorithms without external dependencies
- **Features**:
  - Bullish/Bearish Engulfing pattern detection
  - Morning Star and Evening Star reversal patterns
  - Hammer pattern recognition
  - Pattern frequency analysis and history tracking
  - HMM + pattern signal combination logic

### 5. Utilities (`utils.py`)
- **Purpose**: Common helper functions
- **Functions**:
  - Data formatting (percentages, numbers)
  - Date validation
  - Data cleaning and preprocessing
  - Trading day calculations

## Data Flow

1. **Data Acquisition**: Yahoo Finance API fetches market data (cached for 1 hour)
2. **Feature Engineering**: Raw price/volume data transformed into technical indicators
3. **Model Processing**: 
   - HMM: Features fed to Gaussian Mixture Model for regime classification
   - Kelly: Win probabilities calculated from HMM regime stats × historical win rates
4. **Position Sizing**: Kelly Criterion calculates optimal position size based on:
   - Hybrid win probability from HMM regimes
   - Win/Loss ratio from regime returns
   - Portfolio value and stop loss parameters
   - Fractional Kelly multiplier (default 0.5x)
5. **Visualization**: 
   - HMM: Regime charts with price overlays
   - Kelly: Speedometer gauge with color-coded risk zones
   - Combined: Integrated analytics dashboard
6. **User Interaction**: Real-time parameter adjustment with instant recalculation

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **yfinance**: Yahoo Finance data retrieval
- **pandas/numpy**: Data manipulation and numerical computing
- **plotly**: Interactive visualization
- **scikit-learn**: Machine learning (Gaussian Mixture Models)

### Data Dependencies
- **Yahoo Finance**: Primary data source for stock prices, volumes, and market data
- **Risk-free Rate**: Hardcoded 10-year Treasury approximation (4.5%)

## Deployment Strategy

The application is designed for Replit deployment with the following characteristics:

- **Single-file Entry**: `app.py` serves as the main entry point
- **No Database Required**: All data is fetched real-time from external APIs
- **Stateless Design**: No persistent data storage needed
- **Resource Efficient**: Uses caching through Streamlit's session state
- **Scalable**: Modular design allows easy feature additions

### Deployment Considerations
- Requires internet access for Yahoo Finance API calls
- Memory usage scales with data range and number of assets analyzed
- No authentication or user management required
- All computations happen server-side with client-side visualization

The architecture prioritizes simplicity and modularity, making it easy to extend with additional features while maintaining clean separation of concerns between data processing, analysis, and presentation layers.