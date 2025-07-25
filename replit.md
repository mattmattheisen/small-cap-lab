# Trading Platform - HMM & Sharpe Analysis

## Overview

This is a comprehensive trading platform built with Streamlit that combines Hidden Markov Model (HMM) regime detection with Sharpe ratio analysis. The application provides traders and analysts with advanced tools for market regime identification and risk-adjusted performance analysis.

## Recent Changes

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
- **Backend Logic**: Python modules for HMM signal generation and Sharpe ratio calculations
- **Data Source**: Yahoo Finance API for real-time market data
- **Visualization**: Plotly for interactive charts and graphs
- **ML Component**: Scikit-learn Gaussian Mixture Models for regime detection

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and UI orchestration
- **Architecture**: Tab-based interface with three main sections:
  - HMM Trading Signals
  - Sharpe Ratio Analysis  
  - Combined Analytics
- **Session Management**: Uses Streamlit session state for component persistence

### 2. HMM Signal Generator (`hmm_signal_generator.py`)
- **Purpose**: Market regime detection using Hidden Markov Models
- **Technology**: Gaussian Mixture Models from scikit-learn as HMM approximation
- **Features**: 
  - 3-state regime classification (Bear, Sideways, Bull)
  - Feature engineering (returns, volatility, volume ratios, momentum, RSI)
  - Signal generation based on regime transitions

### 3. Sharpe Calculator (`sharpe_calculator.py`)
- **Purpose**: Risk-adjusted performance analysis
- **Features**:
  - Portfolio Sharpe ratio calculations
  - Multi-asset portfolio support
  - Risk-free rate integration (default: 4.5% 10-year Treasury)
  - Performance metrics calculation

### 4. Utilities (`utils.py`)
- **Purpose**: Common helper functions
- **Functions**:
  - Data formatting (percentages, numbers)
  - Date validation
  - Data cleaning and preprocessing
  - Trading day calculations

## Data Flow

1. **Data Acquisition**: Yahoo Finance API fetches market data
2. **Feature Engineering**: Raw price/volume data transformed into technical indicators
3. **Model Processing**: 
   - HMM: Features fed to Gaussian Mixture Model for regime classification
   - Sharpe: Returns calculated for portfolio performance analysis
4. **Visualization**: Results rendered through Plotly charts in Streamlit interface
5. **User Interaction**: Real-time parameter adjustment through Streamlit widgets

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