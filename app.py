"""
Comprehensive Trading Platform
Combining HMM Regime Detection with Sharpe Ratio Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from hmm_signal_generator import HMMSignalGenerator
from sharpe_calculator import SharpeCalculator
from small_cap_screener import SmallCapScreener
from utils import format_percentage, format_number, validate_date_range

# Page configuration
st.set_page_config(
    page_title="Trading Platform - HMM & Sharpe Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Header
    st.title("Advanced Trading Platform")
    st.markdown("**Hidden Markov Model Regime Detection + Professional Sharpe Ratio Analysis**")
    
    # Sidebar - User Manual Download
    with st.sidebar:
        st.markdown("### 📖 User Manual")
        
        try:
            with open("USER_MANUAL.md", "r") as f:
                manual_content = f.read()
            
            st.download_button(
                label="📥 Download User Manual",
                data=manual_content,
                file_name="Trading_Platform_User_Manual.md",
                mime="text/markdown",
                help="Download the complete user manual for this trading platform"
            )
            st.markdown("---")
        except Exception as e:
            st.error(f"Unable to load manual: {e}")
    
    # Initialize session state
    if 'hmm_generator' not in st.session_state:
        st.session_state.hmm_generator = HMMSignalGenerator()
    if 'sharpe_calculator' not in st.session_state:
        st.session_state.sharpe_calculator = SharpeCalculator()
    if 'small_cap_screener' not in st.session_state:
        st.session_state.small_cap_screener = SmallCapScreener()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["HMM Trading Signals", "📊 Sharpe Ratio Analysis", "🔬 Combined Analytics", "🔍 Small Cap Screener"])
    
    with tab1:
        hmm_trading_signals()
    
    with tab2:
        sharpe_ratio_analysis()
    
    with tab3:
        combined_analytics()
    
    with tab4:
        small_cap_screener()

def hmm_trading_signals():
    """HMM Trading Signals Tab"""
    st.header("Markov Chain Trading Signals")
    
    st.info("Advanced regime detection using Hidden Markov Models. You control position sizing and risk management based on high-quality market regime signals.")
    
    # Sidebar inputs for HMM
    with st.sidebar:
        st.subheader("📊 HMM Analysis Settings")
        
        symbol = st.text_input(
            "Stock Symbol:",
            value="SOFI",
            help="Enter any valid stock ticker"
        ).upper()
        
        lookback_days = st.slider(
            "Analysis Period (Days):",
            min_value=100,
            max_value=800,
            value=252,
            help="Number of trading days to analyze"
        )
        
        confidence_threshold = st.slider(
            "Signal Confidence Threshold:",
            min_value=0.5,
            max_value=0.9,
            value=0.7,
            step=0.05,
            help="Minimum confidence required for BUY/SELL signals"
        )
    
    # Analysis button
    if st.button("🚀 Generate HMM Signal", type="primary", key="hmm_analyze"):
        try:
            with st.spinner(f"Analyzing {symbol} market regimes..."):
                # Download data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(lookback_days * 1.8))
                
                data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                
                if data is None or data.empty:
                    st.error(f"❌ No data available for {symbol}")
                    return
                
                if data is None or len(data) < 100:
                    st.error(f"❌ Insufficient data for {symbol}. Need at least 100 days.")
                    return
                
                # Store data in session state for combined analytics
                st.session_state.hmm_data = data
                st.session_state.hmm_symbol = symbol
                
                # Initialize HMM
                hmm = st.session_state.hmm_generator
                
                # Prepare features
                features = hmm.prepare_features(data)
                
                # Fit model and get predictions
                states, probabilities = hmm.fit_model(features)
                
                # Get current state
                current_regime = states[-1]
                current_confidence = probabilities[-1].max()
                
                # Analyze regimes
                regime_stats = hmm.analyze_regimes(features, states, probabilities)
                
                # Generate signal with candlestick pattern enhancement
                signal_info = hmm.generate_signal(current_regime, current_confidence, regime_stats, data)
                
                # Store results in session state
                st.session_state.hmm_results = {
                    'signal_info': signal_info,
                    'regime_stats': regime_stats,
                    'states': states,
                    'probabilities': probabilities,
                    'features': features,
                    'data': data
                }
                
                # Display results
                display_hmm_results(signal_info, regime_stats, data, states, features)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def display_hmm_results(signal_info, regime_stats, data, states, features):
    """Display HMM analysis results with candlestick patterns"""
    
    # Check if we have enhanced signal with patterns
    has_patterns = signal_info.get('combined_signal') is not None
    
    if has_patterns:
        # Display combined signal prominently
        combined = signal_info['combined_signal']
        action = combined['action']
        combined_strength = combined['strength']
        
        # Enhanced signal box
        if 'STRONG_BUY' in action:
            st.success(f"🟢 **{action}** - Strength: {combined_strength}/10")
        elif 'STRONG_SELL' in action:
            st.error(f"🔴 **{action}** - Strength: {combined_strength}/10")
        elif 'WEAK_BUY' in action:
            st.info(f"🔵 **{action}** - Strength: {combined_strength}/10")
        elif 'WEAK_SELL' in action:
            st.warning(f"🟠 **{action}** - Strength: {combined_strength}/10")
        else:
            st.warning(f"🟡 **{action}** - Strength: {combined_strength}/10")
        
        # Show reasoning
        if combined.get('reasoning'):
            for reason in combined['reasoning']:
                st.info(f"💡 {reason}")
    
    else:
        # Original HMM-only signal display
        signal = signal_info['signal']
        strength = signal_info['strength']
        
        if signal == 'BUY':
            st.success(f"🟢 **{signal}** Signal - Strength: {strength}/10")
        elif signal == 'SELL':
            st.error(f"🔴 **{signal}** Signal - Strength: {strength}/10")
        else:
            st.warning(f"🟡 **{signal}** Signal - Strength: {strength}/10")
    
    # Pattern Information Section
    if has_patterns:
        pattern_signal = signal_info.get('pattern_signal', {})
        pattern_summary = signal_info.get('pattern_summary', {})
        
        st.subheader("📊 Candlestick Pattern Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pattern_text = pattern_signal.get('tag', 'None')
            pattern_dir = pattern_signal.get('dir', 0)
            if pattern_dir == 1:
                st.metric("Current Pattern", f"🟢 {pattern_text}")
            elif pattern_dir == -1:
                st.metric("Current Pattern", f"🔴 {pattern_text}")
            else:
                st.metric("Current Pattern", "No Pattern")
        
        with col2:
            total_patterns = pattern_summary.get('total_patterns', 0)
            st.metric("Patterns (30d)", total_patterns)
        
        with col3:
            bullish_count = pattern_summary.get('bullish_count', 0)
            st.metric("Bullish Patterns", bullish_count)
        
        with col4:
            bearish_count = pattern_summary.get('bearish_count', 0)
            st.metric("Bearish Patterns", bearish_count)
        
        # Recent patterns
        if pattern_summary.get('recent_patterns'):
            with st.expander("📋 Recent Pattern History (Last 30 Days)"):
                recent_df = pd.DataFrame(pattern_summary['recent_patterns'])
                if not recent_df.empty:
                    recent_df['date'] = pd.to_datetime(recent_df['date']).dt.strftime('%Y-%m-%d')
                    st.dataframe(recent_df[['date', 'pattern', 'direction']], use_container_width=True)
    
    # Component Analysis
    regime = signal_info['regime']
    confidence = signal_info['confidence']
    
    st.subheader("🔬 Signal Components")
    
    col1, col2, col3 = st.columns(3)
    
    # Current regime info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Regime", f"{regime} {st.session_state.hmm_generator.regime_icons.get(list(st.session_state.hmm_generator.regime_names.keys())[list(st.session_state.hmm_generator.regime_names.values()).index(regime)], '')}")
    
    with col2:
        st.metric("Confidence", f"{confidence:.1f}%")
    
    with col3:
        if has_patterns and signal_info.get('combined_signal'):
            st.metric("Combined Strength", f"{signal_info['combined_signal']['strength']}/10")
        else:
            st.metric("Signal Strength", f"{signal_info['strength']}/10")
    
    # Regime Statistics
    st.subheader("📊 Regime Analysis")
    
    regime_df = pd.DataFrame([
        {
            'Regime': f"{stats['icon']} {stats['name']}",
            'Days': stats['days'],
            'Percentage': f"{stats['percentage']:.1f}%",
            'Avg Return': f"{stats['avg_return']:.2f}%",
            'Volatility': f"{stats['volatility']:.2f}%",
            'Persistence': f"{stats['persistence']:.1f}%"
        }
        for stats in regime_stats.values()
    ])
    
    st.dataframe(regime_df, use_container_width=True)
    
    # Price chart with regime overlay
    st.subheader("📈 Price History with Regime Detection")
    
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=data.index[-len(states):],
        y=data['Close'].iloc[-len(states):],
        mode='lines',
        name='Price',
        line=dict(color='black', width=2)
    ))
    
    # Add regime background colors
    for i, regime in enumerate(states):
        color = st.session_state.hmm_generator.regime_colors[regime]
        if i < len(states) - 1:
            fig.add_vrect(
                x0=data.index[-len(states):][i],
                x1=data.index[-len(states):][i+1],
                fillcolor=color,
                opacity=0.2,
                layer="below",
                line_width=0
            )
    
    fig.update_layout(
        title="Stock Price with Market Regime Detection",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def sharpe_ratio_analysis():
    """Sharpe Ratio Analysis Tab"""
    st.header("📊 Professional Sharpe Ratio Calculator")
    
    st.info("The Sharpe ratio measures risk-adjusted returns by comparing portfolio returns to the risk-free rate, divided by portfolio volatility. Higher values indicate better risk-adjusted performance.")
    
    # Method selection
    method = st.selectbox(
        "Choose calculation method:",
        ["Portfolio Builder", "Manual Input"],
        help="Select how you want to calculate the Sharpe ratio"
    )
    
    if method == "Portfolio Builder":
        portfolio_builder_interface()
    else:
        manual_input_interface()

def portfolio_builder_interface():
    """Portfolio Builder interface"""
    st.subheader("🏗️ Portfolio Builder")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Portfolio input
        num_assets = st.number_input("Number of assets:", min_value=1, max_value=10, value=2)
        
        symbols = []
        weights = []
        
        for i in range(num_assets):
            col_symbol, col_weight = st.columns([2, 1])
            
            with col_symbol:
                symbol = st.text_input(f"Asset {i+1} Symbol:", value="AAPL" if i == 0 else "GOOGL" if i == 1 else "", key=f"symbol_{i}")
                symbols.append(symbol.upper())
            
            with col_weight:
                weight = st.number_input(f"Weight %:", min_value=0.0, max_value=100.0, 
                                       value=50.0 if num_assets == 2 else 100.0/num_assets, key=f"weight_{i}")
                weights.append(weight / 100.0)
        
        # Date range
        col_start, col_end = st.columns(2)
        
        with col_start:
            start_date = st.date_input(
                "Start Date:",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        
        with col_end:
            end_date = st.date_input(
                "End Date:",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Risk-free rate
        risk_free_rate = st.number_input(
            "Risk-Free Rate (%):",
            value=st.session_state.sharpe_calculator.risk_free_rate * 100,
            min_value=0.0,
            max_value=10.0,
            format="%.2f",
            help="Current 10-year Treasury rate is auto-loaded"
        )
    
    with col2:
        st.subheader("⚖️ Portfolio Summary")
        
        # Validation
        total_weight = sum(weights)
        valid_symbols = all(symbol.strip() for symbol in symbols)
        
        if abs(total_weight - 1.0) > 0.01:
            st.error(f"⚠️ Weights sum to {total_weight:.1%}, must equal 100%")
        elif not valid_symbols:
            st.error("⚠️ Please enter all stock symbols")
        else:
            st.success("✅ Portfolio is valid")
            
            # Display portfolio
            portfolio_df = pd.DataFrame({
                'Symbol': symbols,
                'Weight': [f"{w:.1%}" for w in weights]
            })
            st.table(portfolio_df)
    
    # Calculate button
    if st.button("🚀 Calculate Sharpe Ratio", type="primary", key="sharpe_calc"):
        if valid_symbols and abs(total_weight - 1.0) <= 0.01:
            try:
                with st.spinner("Downloading data and calculating..."):
                    results = st.session_state.sharpe_calculator.calculate_simple_sharpe(
                        symbols, weights, 
                        start_date.strftime('%Y-%m-%d'), 
                        end_date.strftime('%Y-%m-%d'),
                        risk_free_rate / 100
                    )
                
                # Store results for combined analytics
                st.session_state.sharpe_results = results
                st.session_state.sharpe_symbols = symbols
                st.session_state.sharpe_weights = weights
                
                display_sharpe_results(results, symbols, weights)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Please fix portfolio issues before calculating")

def manual_input_interface():
    """Manual input interface"""
    st.subheader("✏️ Manual Input")
    
    st.info("Use this method when you already know your portfolio's return and volatility. Perfect for analyzing existing investment statements or theoretical portfolios.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        portfolio_return = st.number_input(
            "Annual Portfolio Return (%):",
            value=12.0,
            min_value=-50.0,
            max_value=100.0,
            format="%.2f",
            help="Your portfolio's annual return percentage"
        )
        
        portfolio_volatility = st.number_input(
            "Annual Portfolio Volatility (%):",
            value=18.0,
            min_value=0.1,
            max_value=100.0,
            format="%.2f",
            help="Standard deviation of your portfolio returns"
        )
    
    with col2:
        risk_free_rate = st.number_input(
            "Risk-Free Rate (%):",
            value=st.session_state.sharpe_calculator.risk_free_rate * 100,
            min_value=0.0,
            max_value=10.0,
            format="%.2f",
            help="Current 10-year Treasury rate"
        )
        
        st.markdown("### 📊 Quick Examples")
        if st.button("Conservative Portfolio"):
            st.session_state.manual_return = 8.0
            st.session_state.manual_vol = 12.0
        if st.button("Aggressive Portfolio"):
            st.session_state.manual_return = 15.0
            st.session_state.manual_vol = 25.0
    
    if st.button("🚀 Calculate Sharpe Ratio", type="primary", key="manual_sharpe"):
        try:
            results = st.session_state.sharpe_calculator.calculate_manual_sharpe(
                portfolio_return / 100,
                portfolio_volatility / 100,
                risk_free_rate / 100
            )
            
            display_manual_sharpe_results(results)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def display_sharpe_results(results, symbols, weights):
    """Display Sharpe calculation results"""
    st.subheader("📊 Sharpe Analysis Results")
    
    # Main Sharpe ratio display
    sharpe = results['sharpe_ratio']
    rating, color = st.session_state.sharpe_calculator.get_sharpe_rating(sharpe)
    
    st.markdown(f"## Sharpe Ratio: {format_number(sharpe, 3)}")
    st.markdown(f"**Rating: {rating}**")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Annual Return",
            value=format_percentage(results['annual_return']),
            help="Annualized portfolio return"
        )
    
    with col2:
        st.metric(
            label="Annual Volatility", 
            value=format_percentage(results['annual_volatility']),
            help="Annualized standard deviation"
        )
    
    with col3:
        st.metric(
            label="Max Drawdown",
            value=format_percentage(results['max_drawdown']),
            help="Largest peak-to-trough decline"
        )
    
    with col4:
        st.metric(
            label="Win Rate",
            value=format_percentage(results['win_rate']),
            help="Percentage of positive trading days"
        )
    
    # Performance chart
    st.subheader("📈 Portfolio Performance")
    
    fig = go.Figure()
    
    # Cumulative returns
    dates = results['cumulative_returns'].index
    fig.add_trace(go.Scatter(
        x=dates,
        y=(results['cumulative_returns'] - 1) * 100,
        mode='lines',
        name='Portfolio',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title="Cumulative Returns (%)",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Benchmark comparison
    st.subheader("🏆 Benchmark Comparison")
    benchmark_text = st.session_state.sharpe_calculator.get_benchmark_comparison(sharpe)
    st.text(benchmark_text)
    
    # Additional info
    st.info(f"""
    **Calculation Details:**
    • Portfolio: {', '.join(f'{s} ({w:.1%})' for s, w in zip(symbols, weights))}
    • Risk-Free Rate: {format_percentage(results['risk_free_rate'])}
    • Observations: {results['num_observations']} trading days
    • Total Return: {format_percentage(results['total_return'])}
    """)

def display_manual_sharpe_results(results):
    """Display manual calculation results"""
    st.subheader("📊 Manual Sharpe Results")
    
    # Main Sharpe ratio display
    sharpe = results['sharpe_ratio']
    rating, color = st.session_state.sharpe_calculator.get_sharpe_rating(sharpe)
    
    st.markdown(f"## Sharpe Ratio: {format_number(sharpe, 3)}")
    st.markdown(f"**Rating: {rating}**")
    
    # Calculation breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Portfolio Return",
            value=format_percentage(results['portfolio_return'])
        )
    
    with col2:
        st.metric(
            label="Portfolio Volatility",
            value=format_percentage(results['portfolio_volatility'])
        )
    
    with col3:
        st.metric(
            label="Risk-Free Rate",
            value=format_percentage(results['risk_free_rate'])
        )

def combined_analytics():
    """Combined Analytics Tab"""
    st.header("🔬 Combined HMM & Sharpe Analytics")
    
    if 'hmm_results' not in st.session_state or 'sharpe_results' not in st.session_state:
        st.warning("Please run both HMM Trading Signals and Sharpe Ratio Analysis first to see combined analytics.")
        return
    
    st.success("Analyzing combined HMM regime detection with risk-adjusted performance metrics...")
    
    # Get stored results
    hmm_results = st.session_state.hmm_results
    sharpe_results = st.session_state.sharpe_results
    
    # Combined metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Signal",
            hmm_results['signal_info']['signal'],
            f"Strength: {hmm_results['signal_info']['strength']}/10"
        )
    
    with col2:
        st.metric(
            "Portfolio Sharpe",
            format_number(sharpe_results['sharpe_ratio'], 3),
            "Risk-Adjusted Return"
        )
    
    with col3:
        st.metric(
            "Signal Confidence",
            f"{hmm_results['signal_info']['confidence']:.1f}%",
            f"Regime: {hmm_results['signal_info']['regime']}"
        )
    
    # Regime-specific performance analysis
    st.subheader("📊 Regime-Specific Risk Analysis")
    
    # Calculate regime-specific Sharpe ratios if we have overlapping data
    try:
        analyze_regime_performance(hmm_results, sharpe_results)
    except Exception as e:
        st.warning(f"Unable to calculate regime-specific metrics: {str(e)}")
    
    # Combined visualization
    st.subheader("📈 Integrated Analysis Dashboard")
    
    # Create combined chart
    fig = go.Figure()
    
    # Add HMM data if available
    if 'data' in hmm_results:
        hmm_data = hmm_results['data']
        states = hmm_results['states']
        
        # Price with regime overlay
        fig.add_trace(go.Scatter(
            x=hmm_data.index[-len(states):],
            y=hmm_data['Close'].iloc[-len(states):],
            mode='lines',
            name='Price',
            line=dict(color='black', width=2),
            yaxis='y1'
        ))
        
        # Add regime background
        hmm_generator = st.session_state.hmm_generator
        for i, regime in enumerate(states):
            if i < len(states) - 1:
                color = hmm_generator.regime_colors[regime]
                fig.add_vrect(
                    x0=hmm_data.index[-len(states):][i],
                    x1=hmm_data.index[-len(states):][i+1],
                    fillcolor=color,
                    opacity=0.2,
                    layer="below",
                    line_width=0
                )
    
    # Add Sharpe portfolio performance if available
    if 'cumulative_returns' in sharpe_results:
        fig.add_trace(go.Scatter(
            x=sharpe_results['cumulative_returns'].index,
            y=(sharpe_results['cumulative_returns'] - 1) * 100,
            mode='lines',
            name='Portfolio Returns (%)',
            line=dict(color='blue', width=2),
            yaxis='y2'
        ))
    
    # Update layout for dual y-axis
    fig.update_layout(
        title="Combined HMM Regime Detection & Portfolio Performance",
        xaxis_title="Date",
        yaxis=dict(title="Stock Price ($)", side="left"),
        yaxis2=dict(title="Portfolio Returns (%)", side="right", overlaying="y"),
        hovermode='x unified',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

def analyze_regime_performance(hmm_results, sharpe_results):
    """Analyze performance by regime"""
    
    # Get regime statistics
    regime_stats = hmm_results['regime_stats']
    
    # Display regime analysis
    st.markdown("**Regime Performance Summary:**")
    
    for regime_id, stats in regime_stats.items():
        with st.expander(f"{stats['icon']} {stats['name']} Regime Analysis"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Days in Regime", stats['days'])
                st.metric("Persistence", f"{stats['persistence']:.1f}%")
            
            with col2:
                st.metric("Average Return", f"{stats['avg_return']:.2f}%")
                st.metric("Volatility", f"{stats['volatility']:.2f}%")
            
            with col3:
                # Calculate regime-specific risk metrics
                if stats['volatility'] > 0:
                    regime_sharpe = stats['avg_return'] / stats['volatility']
                    st.metric("Regime Sharpe*", f"{regime_sharpe:.2f}")
                else:
                    st.metric("Regime Sharpe*", "N/A")
                
                st.metric("Market Share", f"{stats['percentage']:.1f}%")
    
    st.caption("*Regime Sharpe = Average Return / Volatility (simplified calculation)")

def small_cap_screener():
    """Small Cap Stock Screener Tab"""
    st.header("🔍 Small Cap Stock Screener")
    
    st.info("Advanced fundamental analysis to find high-quality small cap opportunities with consistent growth, strong financials, and reasonable valuations.")
    
    screener = st.session_state.small_cap_screener
    
    # Sidebar for screening criteria
    with st.sidebar:
        st.subheader("🎯 Screening Criteria")
        
        # Market cap range
        st.markdown("**Market Cap Range**")
        market_cap_min = st.number_input(
            "Minimum Market Cap ($M):",
            min_value=50,
            max_value=5000,
            value=300,
            step=50,
            help="Minimum market capitalization in millions"
        ) * 1_000_000
        
        market_cap_max = st.number_input(
            "Maximum Market Cap ($B):",
            min_value=1.0,
            max_value=10.0,
            value=2.0,
            step=0.5,
            help="Maximum market capitalization in billions"
        ) * 1_000_000_000
        
        # Growth criteria
        st.markdown("**Growth Requirements**")
        revenue_growth_min = st.slider(
            "Minimum Revenue Growth (%):",
            min_value=5,
            max_value=30,
            value=10,
            help="Minimum annual revenue growth rate"
        ) / 100
        
        eps_growth_min = st.slider(
            "Minimum EPS Growth (%):",
            min_value=5,
            max_value=30,
            value=10,
            help="Minimum annual earnings per share growth"
        ) / 100
        
        # Financial health
        st.markdown("**Financial Health**")
        debt_equity_max = st.slider(
            "Maximum Debt/Equity (%):",
            min_value=10,
            max_value=100,
            value=50,
            help="Maximum debt to equity ratio"
        ) / 100
        
        profit_margin_min = st.slider(
            "Minimum Profit Margin (%):",
            min_value=0,
            max_value=20,
            value=5,
            help="Minimum net profit margin"
        ) / 100
        
        # Valuation
        st.markdown("**Valuation Metrics**")
        peg_ratio_max = st.slider(
            "Maximum PEG Ratio:",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.1,
            help="Maximum price/earnings to growth ratio"
        )
        
        # Liquidity
        st.markdown("**Liquidity Requirements**")
        min_volume_usd = st.number_input(
            "Minimum Daily Volume ($M):",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Minimum average daily trading volume in millions"
        ) * 1_000_000
    
    # Create criteria dictionary
    criteria = {
        'market_cap_min': market_cap_min,
        'market_cap_max': market_cap_max,
        'revenue_growth_min': revenue_growth_min,
        'eps_growth_min': eps_growth_min,
        'debt_equity_max': debt_equity_max,
        'profit_margin_min': profit_margin_min,
        'peg_ratio_max': peg_ratio_max,
        'min_volume_usd': min_volume_usd,
    }
    
    # Display current criteria
    st.subheader("📋 Current Screening Criteria")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Market Cap Range", f"${market_cap_min/1e6:.0f}M - ${market_cap_max/1e9:.1f}B")
        st.metric("Revenue Growth", f"≥{revenue_growth_min*100:.0f}%")
    
    with col2:
        st.metric("EPS Growth", f"≥{eps_growth_min*100:.0f}%")
        st.metric("Profit Margin", f"≥{profit_margin_min*100:.0f}%")
    
    with col3:
        st.metric("Debt/Equity", f"≤{debt_equity_max*100:.0f}%")
        st.metric("PEG Ratio", f"≤{peg_ratio_max:.1f}")
    
    with col4:
        st.metric("Daily Volume", f"≥${min_volume_usd/1e6:.1f}M")
        st.metric("Stocks to Screen", len(screener.small_cap_universe))
    
    # Run screening button
    if st.button("🚀 Run Small Cap Screen", type="primary", key="run_screener"):
        try:
            with st.spinner("Screening small cap stocks... This may take a few minutes."):
                results = screener.screen_stocks(criteria)
                
                if results:
                    st.session_state.screening_results = results
                    
                    st.success(f"Found {len(results)} stocks that meet your criteria!")
                    
                    # Format and display results
                    results_df = screener.format_screening_results(results)
                    
                    st.subheader("📊 Screening Results")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Top picks
                    if len(results) >= 3:
                        st.subheader("🏆 Top 3 Picks")
                        
                        for i, stock in enumerate(results[:3]):
                            with st.expander(f"#{i+1}: {stock['symbol']} - Score: {stock['screening_score']}/10"):
                                display_stock_details(stock)
                    
                    # Export option
                    st.subheader("💾 Export Results")
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name=f"small_cap_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                else:
                    st.warning("No stocks met your screening criteria. Try adjusting the parameters.")
                    
        except Exception as e:
            st.error(f"Error during screening: {str(e)}")
    
    # Display previous results if available
    if 'screening_results' in st.session_state and st.session_state.screening_results:
        if st.button("🔄 Show Last Results"):
            results = st.session_state.screening_results
            results_df = screener.format_screening_results(results)
            
            st.subheader("📊 Previous Screening Results")
            st.dataframe(results_df, use_container_width=True)

def display_stock_details(stock):
    """Display detailed information for a screened stock"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Valuation Metrics**")
        st.write(f"• Market Cap: ${stock['market_cap']/1e9:.2f}B" if stock['market_cap'] > 0 else "• Market Cap: N/A")
        st.write(f"• P/E Ratio: {stock['trailing_pe']:.1f}" if stock['trailing_pe'] else "• P/E Ratio: N/A")
        st.write(f"• PEG Ratio: {stock['peg_ratio']:.2f}" if stock['peg_ratio'] else "• PEG Ratio: N/A")
        st.write(f"• Price/Book: {stock['price_to_book']:.2f}" if stock['price_to_book'] else "• Price/Book: N/A")
    
    with col2:
        st.markdown("**Growth Metrics**")
        st.write(f"• Revenue Growth: {stock['revenue_growth']*100:.1f}%" if stock['revenue_growth'] else "• Revenue Growth: N/A")
        st.write(f"• EPS Growth: {stock['earnings_growth']*100:.1f}%" if stock['earnings_growth'] else "• EPS Growth: N/A")
        st.write(f"• ROE: {stock['return_on_equity']*100:.1f}%" if stock['return_on_equity'] else "• ROE: N/A")
        st.write(f"• ROA: {stock['return_on_assets']*100:.1f}%" if stock['return_on_assets'] else "• ROA: N/A")
    
    with col3:
        st.markdown("**Financial Health**")
        st.write(f"• Profit Margin: {stock['profit_margin']*100:.1f}%" if stock['profit_margin'] else "• Profit Margin: N/A")
        st.write(f"• Operating Margin: {stock['operating_margin']*100:.1f}%" if stock['operating_margin'] else "• Operating Margin: N/A")
        st.write(f"• Debt/Equity: {stock['debt_to_equity']:.1f}%" if stock['debt_to_equity'] else "• Debt/Equity: N/A")
        st.write(f"• Current Ratio: {stock['current_ratio']:.2f}" if stock['current_ratio'] else "• Current Ratio: N/A")
    
    # Additional insights
    st.markdown("**Key Insights**")
    insights = []
    
    if stock['peg_ratio'] and 0 < stock['peg_ratio'] <= 1:
        insights.append("🎯 Excellent PEG ratio suggests undervalued growth")
    
    if stock['revenue_growth'] and stock['revenue_growth'] >= 0.15:
        insights.append("📈 Strong revenue growth momentum")
    
    if stock['debt_to_equity'] and stock['debt_to_equity'] <= 0.3:
        insights.append("💪 Conservative debt levels")
    
    if stock['profit_margin'] and stock['profit_margin'] >= 0.1:
        insights.append("💰 Strong profitability margins")
    
    if stock['free_cash_flow'] and stock['free_cash_flow'] > 0:
        insights.append("💵 Positive free cash flow generation")
    
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.write("🔍 Review detailed metrics for investment considerations")

if __name__ == "__main__":
    main()
