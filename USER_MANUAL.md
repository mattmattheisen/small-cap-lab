# Trading Platform User Manual

## Welcome to Your Advanced Trading Analysis Platform

This platform combines powerful market analysis tools to help you make better trading decisions. It uses advanced mathematical models and technical analysis to identify market trends and evaluate investment performance.

---

## Getting Started

When you open the platform, you'll see three main tabs at the top:
1. **HMM Trading Signals** - Get AI-powered buy/sell recommendations
2. **Sharpe Ratio Analysis** - Measure your portfolio's risk-adjusted returns
3. **Small Cap Stock Screener** - Find promising small-cap investment opportunities

---

## Tab 1: HMM Trading Signals

### What It Does
This tool uses a Hidden Markov Model (a type of AI) to detect which "market regime" a stock is currently in, then combines that with candlestick pattern recognition to give you enhanced trading signals.

### How to Use It

1. **Enter a Stock Symbol**
   - Type the ticker symbol (e.g., AAPL, TSLA, MSFT) in the text box
   - The system will fetch real-time data from Yahoo Finance

2. **Select Your Analysis Period**
   - Use the date pickers to choose your start and end dates
   - Recommended: At least 3-6 months of data for reliable results
   - More data = better pattern recognition

3. **Click "Analyze"**

### Understanding Your Results

#### Trading Signal Box
You'll see one of these signals at the top:

- **🟢 STRONG_BUY** - Both the AI model and candlestick patterns agree it's a good time to buy
  - Strength rating shows confidence (1-10 scale)
  - Higher numbers = stronger signal

- **🔴 STRONG_SELL** - Both indicators agree it's time to sell
  - Pay attention to the strength rating

- **⚪ HOLD (Conflict)** - The AI and patterns disagree
  - This means wait for clearer signals
  - It's safer to hold than to trade on conflicting signals

- **🟡 BUY (Cautious)** - Only the AI suggests buying
  - Lower confidence, no pattern confirmation

- **🟠 SELL (Cautious)** - Only the AI suggests selling
  - Lower confidence, no pattern confirmation

#### What the Reasoning Tells You
Below the signal, you'll see explanations like:
- "HMM Bull regime confirmed by bullish candlestick pattern" = Strong agreement
- "Sideways market detected" = Market is flat, unclear direction
- "Pattern conflict with regime" = Mixed signals, be cautious

#### Market Regime Analysis
The platform identifies three market conditions:

1. **Bull Market** 🐂
   - Prices are generally rising
   - Good time to look for buying opportunities
   - Average returns shown in green

2. **Sideways Market** ↔️
   - Market is flat or choppy
   - No clear trend
   - Be cautious with new positions

3. **Bear Market** 🐻
   - Prices are generally falling
   - Consider selling or waiting
   - Average returns shown in red

#### Candlestick Pattern Analysis
This section shows you:

- **Current Pattern**: What pattern the stock just formed
  - 🟢 Green = Bullish (upward) pattern
  - 🔴 Red = Bearish (downward) pattern
  
- **Direction**: Whether the pattern suggests up (+1) or down (-1)

- **30-Day Pattern History**: How often each pattern appeared recently
  - Bullish Engulfing: Strong reversal pattern indicating upward move
  - Morning Star: Bullish reversal after downtrend
  - Hammer: Potential bottom/reversal signal
  - Bearish Engulfing: Strong reversal pattern indicating downward move
  - Evening Star: Bearish reversal after uptrend

#### Signal Strength Breakdown
Shows you how confident the system is:
- **HMM Confidence**: How certain the AI is about the market regime (0-100%)
- **Pattern Signal**: What the candlestick analysis says
- **Combined Strength**: Overall confidence rating (1-10)

Higher confidence + higher strength = more reliable signal

#### Charts You'll See

1. **Price Chart with Regime Colors**
   - Green zones = Bull market periods
   - Yellow zones = Sideways market
   - Red zones = Bear market periods
   - Shows you visually when market conditions change

2. **Regime State Timeline**
   - Color-coded bars showing market regime over time
   - Helps you see regime stability

3. **Feature Importance**
   - Shows which indicators matter most for predictions
   - Technical detail for advanced users

### Pro Tips for HMM Signals

✅ **Best Practices:**
- Look for STRONG_BUY or STRONG_SELL with strength 7+ for highest confidence
- Combine with your own research and risk tolerance
- Use HOLD signals as warnings to stay out of the market
- Check the pattern history - frequently appearing patterns are more reliable

⚠️ **Cautions:**
- No system is perfect - always manage your risk
- Low confidence signals (below 60%) should be treated carefully
- Sideways markets are unpredictable - smaller positions recommended
- Always use stop losses to protect your capital

---

## Tab 2: Sharpe Ratio Analysis

### What It Does
Measures how much return you're getting for the risk you're taking. A higher Sharpe Ratio means better risk-adjusted performance.

### How to Use It

1. **Choose Analysis Type:**
   - **Single Stock**: Analyze one stock's risk/reward
   - **Portfolio**: Analyze multiple stocks together

2. **For Single Stock:**
   - Enter ticker symbol (e.g., AAPL)
   - Select date range (recommend 1+ year for meaningful results)
   - Click "Calculate Sharpe Ratio"

3. **For Portfolio:**
   - Add multiple stocks with their weights
   - Weights should add up to 100% (e.g., 50% AAPL, 30% MSFT, 20% TSLA)
   - Select date range
   - Click "Calculate Portfolio Sharpe Ratio"

### Understanding Your Results

#### Sharpe Ratio Number
- **Above 1.0** = Good risk-adjusted returns
- **Above 2.0** = Very good performance
- **Above 3.0** = Excellent performance
- **Below 1.0** = Poor risk-adjusted returns (might not be worth the risk)
- **Negative** = Losing money (returns below risk-free rate)

#### What the Metrics Mean

- **Annual Return**: How much the investment gained/lost per year (as %)
- **Annual Volatility**: How much the price bounces around (risk level)
  - Higher volatility = more risk
  - Lower volatility = more stable

- **Risk-Free Rate**: The "safe" return you could get (currently 4.5%, based on 10-year Treasury)
  - Your investment should beat this to be worthwhile

#### The Chart
Shows daily returns over time - helps you see:
- How volatile the investment is
- When major gains/losses occurred
- Pattern of returns

### Pro Tips for Sharpe Ratio

✅ **Best Practices:**
- Compare Sharpe Ratios between different investments
- Higher Sharpe = better risk-adjusted choice
- Use 1+ year of data for reliable ratios
- Rebalance portfolio if Sharpe Ratio drops significantly

⚠️ **Cautions:**
- Past performance doesn't guarantee future results
- Sharpe Ratio assumes normal distribution of returns (not always true)
- Consider other factors beyond just Sharpe Ratio
- Very high Sharpe Ratios (>5) may not be sustainable

---

## Tab 3: Small Cap Stock Screener

### What It Does
Helps you discover promising small-cap stocks (smaller companies) based on fundamental analysis criteria like growth, profitability, and valuation.

### How to Use It

1. **Set Your Screening Criteria:**

   **Growth Filters:**
   - **Revenue Growth Rate**: Minimum yearly revenue increase
     - Recommended: 15-20% for growth stocks
   - **EPS Growth Rate**: Minimum earnings growth
     - Recommended: 10-15% minimum

   **Financial Health:**
   - **Max Debt-to-Equity**: Maximum debt level you're comfortable with
     - Lower = safer, but may limit growth
     - Recommended: Below 1.0 for conservative, below 2.0 for aggressive
   
   - **Max PEG Ratio**: Price/Earnings to Growth ratio
     - Below 1.0 = potentially undervalued
     - Below 2.0 = fairly valued
     - Above 2.0 = potentially overvalued

   **Liquidity:**
   - **Min Average Volume**: Daily trading volume
     - Higher volume = easier to buy/sell
     - Recommended: At least 100,000 for liquidity

2. **Market Cap Range:**
   - Small-cap range: $300M to $2B
   - Default settings work well for most users

3. **Click "Run Screener"**

### Understanding Your Results

#### Results Table
Shows stocks that pass your filters with key data:

- **Symbol**: Stock ticker
- **Name**: Company name
- **Price**: Current stock price
- **Market Cap**: Total company value
- **P/E Ratio**: Price-to-Earnings (valuation metric)
  - Lower = potentially cheaper
  - Compare within same industry

- **Revenue Growth**: How fast sales are growing
- **EPS Growth**: How fast earnings are growing
- **Debt/Equity**: Debt level relative to shareholder equity
- **PEG Ratio**: Valuation considering growth
- **Avg Volume**: Daily trading volume

#### Quick Analysis Section
For each stock found, you can click "Quick Analysis" to see:
- Recent performance stats
- Mini price chart
- Quick assessment of the opportunity

### Pro Tips for Stock Screener

✅ **Best Practices:**
- Start with conservative filters, then adjust
- Look for stocks with both revenue AND earnings growth
- Lower PEG ratios (<1.0) often indicate value opportunities
- Check debt levels - high debt = higher risk
- Verify volume is sufficient for your position size

⚠️ **Cautions:**
- Small caps are riskier than large caps
- Do additional research before investing
- Some stocks may have data limitations
- Growth rates can be volatile - verify the trend is real
- Never invest based solely on screener results

---

## General Tips for Using the Platform

### Best Workflow

1. **Start with the Screener** to find interesting stocks
2. **Use HMM Signals** to time your entry/exit points
3. **Check Sharpe Ratio** to confirm risk/reward is acceptable
4. **Combine all three** for comprehensive analysis

### Risk Management Reminders

- Never invest more than you can afford to lose
- Diversify across multiple stocks
- Use stop-loss orders to limit downside
- Pay attention to HOLD signals - sometimes doing nothing is best
- Strong signals (8-10 strength) are more reliable than weak ones (1-5)

### When Signals Conflict

If you see:
- HMM says BUY, but patterns say SELL → System shows HOLD (wait for clarity)
- Good Sharpe Ratio but SELL signal → Consider reducing position, not adding
- Bad Sharpe Ratio but BUY signal → Might be turning around, but risky
- Screener finds stock but HMM shows SELL → Maybe wait for better entry

### Data Freshness

- Stock data updates when you run analysis
- Market data comes from Yahoo Finance (real-time during market hours)
- Run analysis daily for active trading
- Run weekly for longer-term positions

---

## Troubleshooting

### "No data available"
- Check if ticker symbol is correct
- Verify stock trades on major exchanges
- Try extending date range
- Stock may be too new or delisted

### "Insufficient data for analysis"
- Need at least 30-60 days of data
- Extend your date range
- Some stocks have limited historical data

### Strange results or errors
- Check if market is open (data may be delayed when closed)
- Refresh the page and try again
- Verify date range is logical (start before end)

---

## Glossary

**Bull Market**: Period when prices are rising  
**Bear Market**: Period when prices are falling  
**Candlestick Pattern**: Visual price pattern that may predict future movement  
**HMM (Hidden Markov Model)**: AI model that identifies market regimes  
**Market Regime**: The current market condition (bull, bear, or sideways)  
**PEG Ratio**: Price/Earnings divided by Growth rate (valuation metric)  
**Sharpe Ratio**: Risk-adjusted return measure (return per unit of risk)  
**Volatility**: How much prices move up and down (measure of risk)  
**Volume**: Number of shares traded (measure of liquidity)

---

## Need Help?

This platform combines multiple advanced techniques:
- AI-powered regime detection
- Technical pattern recognition
- Fundamental analysis screening
- Risk-adjusted performance measurement

Start simple, experiment with different settings, and always combine platform insights with your own research and risk management practices.

**Remember**: This is a tool to assist your decision-making, not a guarantee of profits. Always do your own research and invest responsibly.
