# Trading Platform - HMM & Kelly Criterion Analysis

## Overview

This is a comprehensive trading platform built with Streamlit that combines Hidden Markov Model (HMM) regime detection with Kelly Criterion position sizing. The application provides traders and analysts with advanced tools for market regime identification, optimal position sizing recommendations, candlestick pattern confirmation, and small cap stock screening.

## Recent Changes

**October 13, 2025:**
- **Major Update**: Replaced Sharpe Ratio analysis with Kelly Criterion position sizing calculator
- Implemented hybrid win probability calculation using HMM regime probabilities and historical win rates
- Added speedometer gauge visualization with 4 color-coded risk zones (Green/Yellow/Orange/Red)
- Integrated Kelly summary card in HMM results tab for quick position sizing recommendations
- Added data caching with 1-hour TTL and refresh buttons to prevent stale data issues
- Updated Combined Analytics tab to display Kelly metrics instead of Sharpe ratios
- Kelly calculator integrates seamlessly with HMM regime detection for optimal position sizing
- Fractional Kelly support (Half Kelly 0.5x recommended for conservative trading)

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