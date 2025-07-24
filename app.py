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
    st.title("🚀 Advanced Trading Platform")
    st.markdown("**Hidden Markov Model Regime Detection + Professional Sharpe Ratio Analysis**")
    
    # Initialize session state
    if 'hmm_generator' not in st.session_state:
        st.session_state.hmm_generator = HMMSignalGenerator()
    if 'sharpe_calculator' not in st.session_state:
        st.session_state.sharpe_calculator = SharpeCalculator()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔮 HMM Trading Signals", "📊 Sharpe Ratio Analysis", "🔬 Combined Analytics"])
    
    with tab1:
        hmm_trading_signals()
    
    with tab2:
        sharpe_ratio_analysis()
    
    with tab3:
        combined_analytics()

def hmm_trading_signals():
    """HMM Trading Signals Tab"""
    st.header("🔮 Markov Chain Trading Signals")
    
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
                
                # Generate signal
                signal_info = hmm.generate_signal(current_regime, current_confidence, regime_stats)
                
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
    """Display HMM analysis results"""
    
    # Current Signal Display
    signal = signal_info['signal']
    strength = signal_info['strength']
    regime = signal_info['regime']
    confidence = signal_info['confidence']
    
    # Signal box
    if signal == 'BUY':
        st.success(f"🟢 **{signal}** Signal - Strength: {strength}/10")
    elif signal == 'SELL':
        st.error(f"🔴 **{signal}** Signal - Strength: {strength}/10")
    else:
        st.warning(f"🟡 **{signal}** Signal - Strength: {strength}/10")
    
    # Current regime info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Regime", f"{regime} {st.session_state.hmm_generator.regime_icons.get(list(st.session_state.hmm_generator.regime_names.keys())[list(st.session_state.hmm_generator.regime_names.values()).index(regime)], '')}")
    
    with col2:
        st.metric("Confidence", f"{confidence:.1f}%")
    
    with col3:
        st.metric("Signal Strength", f"{strength}/10")
    
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

if __name__ == "__main__":
    main()
