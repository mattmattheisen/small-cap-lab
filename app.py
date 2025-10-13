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
from kelly_calculator import KellyCalculator
from small_cap_screener import SmallCapScreener
from utils import format_percentage, format_number, validate_date_range, get_stock_data_cached, clear_stock_data_cache, format_currency

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
    st.markdown("**Hidden Markov Model Regime Detection + Kelly Criterion Position Sizing**")
    
    # Sidebar - User Manual Download and Global Refresh
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
        except Exception as e:
            st.error(f"Unable to load manual: {e}")
        
        st.markdown("---")
        
        st.markdown("### 🔄 Data Refresh")
        if st.button("🔄 Refresh All Data", help="Clear all cached data and force fresh data fetch"):
            clear_stock_data_cache()
            st.success("✅ All data cache cleared!")
            st.rerun()
        
        st.markdown("---")
    
    # Initialize session state
    if 'hmm_generator' not in st.session_state:
        st.session_state.hmm_generator = HMMSignalGenerator()
    if 'kelly_calculator' not in st.session_state:
        st.session_state.kelly_calculator = KellyCalculator()
    if 'small_cap_screener' not in st.session_state:
        st.session_state.small_cap_screener = SmallCapScreener()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["HMM Trading Signals", "💰 Kelly Position Sizing", "🔬 Combined Analytics", "🔍 Small Cap Screener"])
    
    with tab1:
        hmm_trading_signals()
    
    with tab2:
        kelly_position_sizing()
    
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
    
    # Refresh and analysis buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_button = st.button("🚀 Generate HMM Signal", type="primary", key="hmm_analyze")
    with col2:
        refresh_hmm = st.button("🔄 Refresh", key="hmm_refresh", help="Clear cached data for fresh fetch")
    
    if refresh_hmm:
        clear_stock_data_cache()
        st.success("✅ HMM data cache cleared!")
        st.rerun()
    
    if analyze_button:
        try:
            with st.spinner(f"Analyzing {symbol} market regimes..."):
                # Download data using cached function
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(lookback_days * 1.8))
                
                data = get_stock_data_cached(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                
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
    
    # Kelly Criterion Summary Card
    st.subheader("💰 Kelly Position Sizing Summary")
    st.info("Quick Kelly calculation based on HMM regime analysis. Visit the Kelly Position Sizing tab for detailed analysis.")
    
    try:
        kelly = st.session_state.kelly_calculator
        probabilities = st.session_state.hmm_results['probabilities']
        current_probs = probabilities[-1]
        
        quick_kelly = kelly.calculate_from_hmm_results(
            regime_stats,
            current_probs,
            100000.0,
            0.5,
            0.05
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Win Probability", f"{quick_kelly['win_probability']*100:.1f}%")
        
        with col2:
            st.metric("Full Kelly", f"{quick_kelly['kelly_fraction']*100:.1f}%")
        
        with col3:
            st.metric("Half Kelly", f"{quick_kelly['kelly_fraction']*50:.1f}%")
        
        with col4:
            risk_emoji = quick_kelly['risk_level']['emoji']
            risk_level = quick_kelly['risk_level']['level']
            st.metric("Risk Level", f"{risk_emoji} {risk_level}")
        
        st.caption("💡 Based on $100k portfolio with 5% stop loss and Half Kelly (0.5x). Customize in Kelly Position Sizing tab →")
        
    except Exception as e:
        st.warning(f"Kelly summary unavailable: {str(e)}")

def create_kelly_gauge(applied_kelly_pct, full_kelly_pct=None):
    """Create speedometer gauge for Kelly percentage"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=applied_kelly_pct,
        title={'text': "Applied Kelly %", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': "darkblue", 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#28a745'},      # Green - Conservative
                {'range': [25, 50], 'color': '#ffc107'},     # Yellow - Moderate/Optimal
                {'range': [50, 75], 'color': '#fd7e14'},     # Orange - Aggressive
                {'range': [75, 100], 'color': '#dc3545'}     # Red - Very Aggressive/Danger
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': full_kelly_pct if full_kelly_pct else applied_kelly_pct
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        font={'size': 16}
    )
    
    return fig

def kelly_position_sizing():
    """Kelly Criterion Position Sizing Tab"""
    st.header("💰 Kelly Criterion Position Sizing")
    
    st.info("Calculate optimal position sizes using the Kelly Criterion. Integrates with HMM regime detection or use manual inputs.")
    
    # Check if HMM results are available
    has_hmm_results = 'hmm_results' in st.session_state
    
    # Mode selection
    if has_hmm_results:
        mode = st.radio(
            "Calculation Mode:",
            ["Use HMM Results", "Manual Input"],
            help="Use HMM regime data or enter parameters manually"
        )
    else:
        mode = "Manual Input"
        st.warning("💡 Run HMM analysis first to auto-populate Kelly calculations from regime data")
    
    if mode == "Use HMM Results" and has_hmm_results:
        kelly_from_hmm()
    else:
        kelly_manual_input()

def kelly_from_hmm():
    """Kelly calculation from HMM results"""
    st.subheader("📊 HMM-Based Kelly Calculation")
    
    hmm_results = st.session_state.hmm_results
    regime_stats = hmm_results['regime_stats']
    probabilities = hmm_results['probabilities']
    current_probs = probabilities[-1]
    
    # Kelly parameters
    col1, col2 = st.columns(2)
    
    with col1:
        portfolio_value = st.number_input(
            "Portfolio Value ($):",
            min_value=1000.0,
            max_value=10000000.0,
            value=100000.0,
            step=1000.0,
            format="%.0f"
        )
        
        applied_fraction = st.slider(
            "Kelly Fraction:",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Fraction of Kelly to apply (0.5 = Half Kelly, recommended)"
        )
    
    with col2:
        stop_loss_pct = st.slider(
            "Stop Loss (%):",
            min_value=1.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            format="%.1f%%"
        ) / 100
    
    if st.button("💰 Calculate Kelly Position Size", type="primary"):
        try:
            kelly = st.session_state.kelly_calculator
            
            results = kelly.calculate_from_hmm_results(
                regime_stats,
                current_probs,
                portfolio_value,
                applied_fraction,
                stop_loss_pct
            )
            
            display_kelly_results(results)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def kelly_manual_input():
    """Manual Kelly calculation"""
    st.subheader("✏️ Manual Kelly Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        win_probability = st.slider(
            "Win Probability:",
            min_value=0.0,
            max_value=1.0,
            value=0.55,
            step=0.01,
            format="%.2f",
            help="Probability of winning trade (0 to 1)"
        )
        
        avg_win_pct = st.number_input(
            "Average Win (%):",
            min_value=0.1,
            max_value=100.0,
            value=5.0,
            step=0.5,
            format="%.1f"
        )
        
        avg_loss_pct = st.number_input(
            "Average Loss (%):",
            min_value=0.1,
            max_value=100.0,
            value=3.0,
            step=0.5,
            format="%.1f"
        )
    
    with col2:
        portfolio_value = st.number_input(
            "Portfolio Value ($):",
            min_value=1000.0,
            max_value=10000000.0,
            value=100000.0,
            step=1000.0,
            format="%.0f"
        )
        
        applied_fraction = st.slider(
            "Kelly Fraction:",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="0.5 = Half Kelly (recommended)"
        )
        
        stop_loss_pct = st.slider(
            "Stop Loss (%):",
            min_value=1.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            format="%.1f%%"
        ) / 100
    
    if st.button("💰 Calculate Kelly Position Size", type="primary", key="kelly_manual"):
        try:
            kelly = st.session_state.kelly_calculator
            
            results = kelly.calculate_manual_kelly(
                win_probability,
                avg_win_pct,
                avg_loss_pct,
                portfolio_value,
                applied_fraction,
                stop_loss_pct
            )
            
            display_kelly_results(results)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def display_kelly_results(results):
    """Display Kelly calculation results"""
    st.subheader("📊 Kelly Position Sizing Results")
    
    position_info = results['position_info']
    risk_level = results['risk_level']
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Full Kelly %",
            f"{position_info['full_kelly_fraction']*100:.1f}%",
            help="Optimal Kelly percentage"
        )
    
    with col2:
        st.metric(
            "Applied Kelly %",
            f"{position_info['applied_kelly']*100:.1f}%",
            help=f"Using {position_info['applied_fraction']*100:.0f}% Kelly fraction"
        )
    
    with col3:
        st.metric(
            "Position Size",
            format_currency(position_info['position_size']),
            help="Recommended position size"
        )
    
    with col4:
        st.metric(
            "Risk Budget",
            format_currency(position_info['risk_budget']),
            help="Maximum capital at risk"
        )
    
    # Speedometer Gauge
    st.subheader("📊 Risk Level Gauge")
    
    gauge_fig = create_kelly_gauge(
        position_info['applied_kelly'] * 100,
        position_info['full_kelly_fraction'] * 100
    )
    st.plotly_chart(gauge_fig, use_container_width=True)
    
    # Risk level indicator
    st.markdown(f"### {risk_level['emoji']} {risk_level['level']}")
    st.info(f"**{risk_level['description']}**")
    
    # Color zone legend
    st.markdown("""
    **Kelly Zones:**
    - 🟢 **0-25%**: Conservative/Quarter Kelly - Safe, lower growth
    - 🟡 **25-50%**: Moderate/Half Kelly - **OPTIMAL ZONE** (recommended)
    - 🟠 **50-75%**: Aggressive/Three-Quarter Kelly - Higher risk
    - 🔴 **75-100%**: Very Aggressive/Full Kelly+ - Danger zone
    """)
    
    # Recommendation
    st.subheader("💡 Recommendation")
    st.success(results['recommendation'])
    
    # Detailed breakdown
    with st.expander("📋 Detailed Calculation Breakdown"):
        st.markdown(f"""
        **Position Sizing Details:**
        - Portfolio Value: {format_currency(position_info['portfolio_value'])}
        - Full Kelly Fraction: {position_info['full_kelly_fraction']*100:.2f}%
        - Applied Fraction: {position_info['applied_fraction']*100:.0f}% (Fractional Kelly)
        - Applied Kelly %: {position_info['applied_kelly']*100:.2f}%
        - Risk Budget: {format_currency(position_info['risk_budget'])}
        - Stop Loss: {position_info['stop_loss_pct']*100:.1f}%
        - Position Size: {format_currency(position_info['position_size'])}
        - Stop Loss Amount: {format_currency(position_info['stop_loss_amount'])}
        """)
        
        if 'win_prob_breakdown' in results:
            wpb = results['win_prob_breakdown']
            st.markdown(f"""
            **Win Probability Calculation (Hybrid):**
            - Bull Regime Probability: {wpb['bull_prob']*100:.1f}%
            - Bull Win Rate: {wpb['bull_win_rate']*100:.1f}%
            - Sideways Regime Probability: {wpb['sideways_prob']*100:.1f}%
            - Sideways Win Rate: {wpb['sideways_win_rate']*100:.1f}%
            - **Combined Win Probability: {wpb['combined_win_prob']*100:.1f}%**
            """)
        
        if 'win_loss_breakdown' in results:
            wlb = results['win_loss_breakdown']
            st.markdown(f"""
            **Win/Loss Ratio:**
            - Average Win: {wlb['avg_win']:.2f}%
            - Average Loss: {wlb['avg_loss']:.2f}%
            - Win/Loss Ratio: {wlb['win_loss_ratio']:.2f}
            """)

def combined_analytics():
    """Combined Analytics Tab"""
    st.header("🔬 Combined HMM & Kelly Analytics")
    
    if 'hmm_results' not in st.session_state:
        st.warning("Please run HMM Trading Signals first to see combined analytics.")
        return
    
    st.success("Analyzing combined HMM regime detection with Kelly position sizing...")
    
    # Get stored results
    hmm_results = st.session_state.hmm_results
    
    # Quick Kelly calculation for display
    try:
        kelly = st.session_state.kelly_calculator
        regime_stats = hmm_results['regime_stats']
        probabilities = hmm_results['probabilities']
        current_probs = probabilities[-1]
        
        kelly_results = kelly.calculate_from_hmm_results(
            regime_stats,
            current_probs,
            100000.0,
            0.5,
            0.05
        )
        
        # Combined metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            signal = hmm_results['signal_info'].get('combined_signal', hmm_results['signal_info'])
            if isinstance(signal, dict) and 'action' in signal:
                action = signal['action']
            else:
                action = hmm_results['signal_info']['signal']
            st.metric("Current Signal", action, f"Strength: {hmm_results['signal_info']['strength']}/10")
        
        with col2:
            st.metric("Kelly Fraction", f"{kelly_results['kelly_fraction']*100:.1f}%", "Optimal sizing")
        
        with col3:
            st.metric("Win Probability", f"{kelly_results['win_probability']*100:.1f}%", "From HMM regimes")
        
        with col4:
            risk_level = kelly_results['risk_level']
            st.metric("Risk Level", f"{risk_level['emoji']} {risk_level['level']}")
    
    except Exception as e:
        st.error(f"Error calculating Kelly metrics: {str(e)}")
    
    # Regime-specific performance analysis
    st.subheader("📊 Regime-Specific Risk Analysis")
    
    # Display regime stats with Kelly implications
    try:
        analyze_regime_performance(hmm_results)
    except Exception as e:
        st.warning(f"Unable to display regime metrics: {str(e)}")
    
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
    
    # Update layout
    fig.update_layout(
        title="HMM Regime Detection Over Time",
        xaxis_title="Date",
        yaxis_title="Stock Price ($)",
        hovermode='x unified',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

def analyze_regime_performance(hmm_results):
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
