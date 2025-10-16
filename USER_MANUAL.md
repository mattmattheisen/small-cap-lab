# small-cap lab User Manual

## Welcome to small-cap lab

small-cap lab is a professional trading analysis platform with a Dark Bloomberg Terminal aesthetic. It combines powerful market analysis tools to help you make better trading decisions using advanced mathematical models and technical analysis to identify market trends and optimize position sizing.

---

## Getting Started

When you open the platform, you'll see four main tabs at the top:
1. **Small Cap Stock Screener** - Find promising small-cap investment opportunities
2. **HMM Trading Signals** - Get AI-powered buy/sell recommendations with Kelly preview
3. **Kelly Position Sizing** - Calculate optimal position sizes for your trades
4. **Combined Analytics** - Integrated HMM + Kelly analysis dashboard

The interface features a professional dark theme optimized for traders and analysts.

---

## Tab 1: Small Cap Stock Screener

### What It Does
This tool helps you discover promising small-cap stocks (market cap under $2B) using advanced fundamental analysis and scoring algorithms. It applies multiple filters for growth, profitability, and financial health.

### How to Use It

1. **Adjust Screening Criteria** in the sidebar:
   - Market Cap Range (in millions)
   - Growth Requirements (Revenue & EPS growth percentages)
   - Financial Health (Debt/Equity ratio, Profit Margin)
   - Valuation Metrics (Maximum PEG ratio)
   - Liquidity Requirements (Minimum daily volume)

2. **Click "Run Screener"**
   - The system analyzes 200+ small-cap stocks
   - Applies all your filters
   - Scores each stock from 0-10

3. **Review Results**
   - Stocks are sorted by score (highest first)
   - Export to CSV for further analysis

### Understanding the Results

Each stock is displayed with:
- **Symbol & Name**: Stock ticker and company name
- **Score**: Overall quality rating (0-10, higher is better)
- **Market Cap**: Company size in millions
- **Revenue Growth**: Year-over-year revenue increase
- **EPS Growth**: Earnings per share growth
- **Profit Margin**: Operating profitability
- **Debt/Equity**: Financial leverage ratio
- **PEG Ratio**: Price/Earnings to Growth (valuation metric)

---

## Tab 2: HMM Trading Signals

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

3. **Click "Generate HMM Signal"**

### Understanding Your Results

#### Trading Signal Box
You'll see one of these signals at the top:

- **STRONG_BUY** - Both the AI model and candlestick patterns agree it's a good time to buy
  - Strength rating shows confidence (1-10 scale)
  - Higher numbers = stronger signal

- **STRONG_SELL** - Both indicators agree it's time to sell
  - Pay attention to the strength rating

- **HOLD (Conflict)** - The AI and patterns disagree
  - This means wait for clearer signals
  - It's safer to hold than to trade on conflicting signals

- **BUY (Cautious)** - Only the AI suggests buying
  - Lower confidence, no pattern confirmation

- **SELL (Cautious)** - Only the AI suggests selling
  - Lower confidence, no pattern confirmation

#### What the Reasoning Tells You
Below the signal, you'll see explanations like:
- "HMM Bull regime confirmed by bullish candlestick pattern" = Strong agreement
- "Sideways market detected" = Market is flat, unclear direction
- "Pattern conflict with regime" = Mixed signals, be cautious

#### Market Regime Analysis
The platform identifies three market conditions:

1. **Bull Market**
   - Prices are generally rising
   - Good time to look for buying opportunities
   - Average returns displayed in regime table

2. **Sideways Market**
   - Market is flat or choppy
   - No clear trend
   - Be cautious with new positions

3. **Bear Market**
   - Prices are generally falling
   - Consider selling or waiting
   - Average returns displayed in regime table

#### Candlestick Pattern Analysis
This section shows you:

- **Current Pattern**: What pattern the stock just formed
  - Bullish patterns indicate upward moves
  - Bearish patterns indicate downward moves
  
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

#### Kelly Position Sizing Summary

At the bottom of the HMM results, you'll see a **Kelly Position Sizing Summary** card with:

- **Win Probability**: Combined probability of winning based on HMM regimes
- **Full Kelly**: Optimal position size according to Kelly Criterion (%)
- **Half Kelly**: Conservative position size (50% of Full Kelly) - **RECOMMENDED**
- **Risk Level**: Visual risk indicator
  - Conservative (0-25%): Safe position sizing
  - Moderate (25-50%): Balanced approach - OPTIMAL ZONE
  - Aggressive (50-75%): Higher risk
  - Danger (75-100%): Very aggressive - AVOID

**Quick Tip**: This is a preview based on $100k portfolio and 5% stop loss. Visit the Kelly Position Sizing tab to customize for your actual portfolio.

### Pro Tips for HMM Signals

**Best Practices:**
- Look for STRONG_BUY or STRONG_SELL with strength 7+ for highest confidence
- Only trade Bull regimes with 75%+ confidence for conservative approach
- Use HOLD signals as warnings to stay out of the market
- Check the pattern history - frequently appearing patterns are more reliable
- Always reference the Kelly summary for position sizing guidance

**Cautions:**
- No system is perfect - always manage your risk
- Low confidence signals (below 60%) should be treated carefully
- Sideways markets are unpredictable - smaller positions recommended
- Always use stop losses to protect your capital
- Never risk more than the Kelly calculator recommends

---

## Tab 3: Kelly Position Sizing

### What Is Kelly Criterion?

The Kelly Criterion is a mathematical formula that tells you the **optimal size** for each trade based on your edge (advantage) in the market. Unlike fixed position sizing (e.g., always risking 2%), Kelly dynamically adjusts based on:

- **Your probability of winning** (calculated from HMM regime analysis)
- **Your win/loss ratio** (how much you make when right vs. lose when wrong)

**Why Kelly Is Better Than Fixed Position Sizing:**
- Maximizes long-term growth while managing risk
- Automatically sizes down when edge is small
- Sizes up when you have a strong advantage
- Prevents over-leveraging on bad trades
- Mathematically optimal for wealth growth

### Why Half Kelly (0.5x) Is Recommended

**Full Kelly** can be too aggressive, especially for volatile small-cap stocks. Here's why we recommend **Half Kelly**:

- **Reduces volatility**: Half the position size = smoother equity curve
- **Lower drawdowns**: Protects against estimation errors in probabilities
- **Safer for small caps**: Small-cap stocks are inherently more volatile
- **Still optimal**: Half Kelly still grows wealth faster than fixed sizing
- **Forgives mistakes**: If your win probability estimate is off, Half Kelly cushions the impact

### How to Use It

1. **Stock Symbol**
   - Auto-populated if you ran HMM analysis first
   - Or manually enter any ticker symbol
   - Data fetches automatically from Yahoo Finance

2. **Set Your Parameters:**

   - **Portfolio Value**: Your total trading capital
     - Be honest - only use actual trading capital
     - Don't include long-term holdings
   
   - **Stop Loss %**: Where you'll exit if trade goes against you
     - Recommended: 3-5% for moderate risk
     - Conservative: 5-7%
     - Aggressive: 2-3% (requires tighter monitoring)
   
   - **Fractional Kelly Multiplier**:
     - **0.25x (Quarter Kelly)**: Ultra-conservative, beginner-friendly
     - **0.50x (Half Kelly)**: **RECOMMENDED** - Best balance
     - **0.75x (Three-Quarter Kelly)**: Aggressive, experienced traders only
     - **1.0x (Full Kelly)**: **NEVER USE ON SMALL CAPS** - Too risky

3. **Click "Calculate Kelly Position"**

### Understanding Your Results

#### Win Probability Calculation
Shows you:
- **Hybrid win probability**: Combines HMM regime analysis with historical win rates
  - Bull regime probability × Bull win rate
  - Sideways regime probability × Sideways win rate
  - = Your overall chance of winning this trade

#### Win/Loss Ratio Breakdown
- **Average Win**: Mean return when trades are profitable (from Bull regime positive days)
- **Average Loss**: Mean loss when trades fail (from Bear regime negative days)
- **Win/Loss Ratio**: How many dollars you make per dollar risked

#### Kelly Fraction
- **Full Kelly %**: Mathematically optimal position size
  - Formula: f* = (p × b - q) / b
  - p = win probability, q = loss probability, b = win/loss ratio

#### Applied Kelly %
- Your **actual position size** after applying fractional multiplier
- This is the percentage of your portfolio to risk on this trade

#### The Speedometer Gauge

The gauge visually shows your position size with color-coded risk zones:

- **Green Zone (0-25%)**: Conservative
  - Safe for beginners
  - Lower returns but minimal risk
  - Good for uncertain markets

- **Yellow Zone (25-50%)**: Moderate/Optimal
  - **IDEAL ZONE FOR MOST TRADERS**
  - Balances growth and safety
  - Half Kelly typically lands here

- **Orange Zone (50-75%)**: Aggressive
  - Higher risk of significant drawdowns
  - Only for experienced traders
  - Requires excellent risk management

- **Red Zone (75-100%)**: Very Aggressive/Danger
  - **AVOID THIS ZONE**
  - Can lead to devastating losses
  - Even professionals don't use this
  - Indicates over-leveraging

#### Position Sizing Recommendations

You'll see three key numbers:

1. **Position Size ($)**: Dollar amount to invest
   - Based on your portfolio value × Applied Kelly %
   
2. **Number of Shares**: How many shares to buy
   - Position size ÷ current stock price
   
3. **Stop Loss Price**: Exact price to exit if trade fails
   - Protects your capital automatically

### Critical Risk Warnings

**Kelly Criterion Assumes Your Probabilities Are Accurate:**
- If your win rate estimate is wrong, Kelly can over-leverage
- This is why we use fractional Kelly (0.5x) - forgives estimation errors
- Always conservative with probability estimates

**Small Caps Are Volatile:**
- **NEVER use Full Kelly (1.0x) on small-cap stocks**
- Minimum recommended: Half Kelly (0.5x)
- Safer: Quarter Kelly (0.25x) for volatile small caps
- Small caps can gap down 20%+ overnight - be prepared

**Kelly Optimizes Long-Term Growth, Not Short-Term Safety:**
- Kelly maximizes wealth over many trades
- Single trade can still lose money
- You need proper bankroll to survive drawdowns
- Don't use Kelly if you can't afford volatility

**Always Use Stop-Losses:**
- Kelly calculation assumes you'll cut losses at specified %
- **MUST execute stop loss** at the percentage you entered
- No stop loss = Kelly formula breaks down
- Use guaranteed stops for overnight holdings

### Pro Tips for Different Strategies

#### Conservative Small Cap Strategy

**Best for: Beginners, risk-averse traders, volatile markets**

- Use **Quarter Kelly (0.25x)**
- Only trade in **Bull regimes with 75%+ confidence**
- Require **STRONG_BUY signals** (strength 8+)
- Set **stop-losses at 5-7%**
- Maximum 3-5 positions at once
- **Expected**: Lower returns, much lower risk

#### Moderate Strategy (RECOMMENDED)

**Best for: Most traders, balanced approach**

- Use **Half Kelly (0.5x)**
- Trade **Bull regimes with 65%+ confidence**
- Require signal **strength 7+**
- Set **3-5% stop-losses**
- Maximum 5-8 positions
- **Expected**: Good returns with manageable risk

#### Aggressive Strategy

**Best for: Experienced traders only, high risk tolerance**

- Max **Three-Quarter Kelly (0.75x)** - NEVER Full Kelly
- Bull regimes with **60%+ confidence**
- Signal **strength 6+**
- Tighter **2-3% stops** to compensate for larger positions
- Maximum 3-5 positions (concentrated)
- Requires daily monitoring
- **Expected**: Highest returns, highest volatility

### Kelly Warning System

The platform will show warnings when:

**Position Exceeds 20% of Portfolio**
- Consider reducing to avoid concentration risk
- Even if Kelly says higher, diversification matters
- Suggests splitting into multiple positions

**Full Kelly Detected (1.0x multiplier)**
- Switch to Half Kelly (0.5x) for lower volatility
- Full Kelly too aggressive for small caps
- Reduce multiplier immediately

**Low Edge Detected (Kelly < 5%)**
- Skip this trade - edge is too small
- Transaction costs may eat profits
- Wait for better opportunities
- Focus on higher-conviction setups

**High Volatility Stock**
- Use Quarter Kelly (0.25x) instead
- Volatility can cause large swings
- Smaller position = better sleep
- Consider options strategies instead

---

## Tab 4: Combined Analytics

### What It Does

This tab brings together HMM regime detection and Kelly position sizing into one integrated dashboard, giving you a complete picture of:
- Current market regime and trading signal
- Optimal position size based on regime probabilities
- Win probability calculations
- Risk level assessment
- Historical regime performance

### How to Use It

1. **Run HMM Trading Signals first** (Tab 1)
   - The Combined Analytics tab needs HMM data to work
   - Make sure you've analyzed at least one stock

2. **Navigate to Combined Analytics tab**
   - View appears automatically with integrated metrics

### Understanding Your Results

#### Top Metrics Row

You'll see four key metrics:

1. **Current Signal**: 
   - Shows the trading recommendation (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)
   - Includes signal strength rating (1-10)

2. **Kelly Fraction**:
   - The optimal position size percentage
   - Based on HMM regime probabilities

3. **Win Probability**:
   - Your calculated edge from HMM regime analysis
   - Higher probability = stronger edge

4. **Risk Level**:
   - Visual indicator with emoji
   - Shows if position sizing is conservative/moderate/aggressive

#### Regime-Specific Risk Analysis

Expandable sections for each regime (Bull, Sideways, Bear) showing:

- **Days in Regime**: How long the stock stayed in this state
- **Persistence**: Likelihood regime continues
- **Average Return**: Expected return in this regime
- **Volatility**: How risky this regime is
- **Market Share**: % of time spent in this regime

This helps you understand which regimes are most common and most profitable.

#### Integrated Visualization

- Price chart with colored regime backgrounds
- Shows transitions between Bull/Sideways/Bear states
- Helps you visualize regime stability and changes

### Pro Tips for Combined Analytics

**Best Practices:**
- Look for alignment between signal and Kelly recommendations
- High win probability + moderate Kelly = good setup
- Use this tab for final decision before trading
- Check regime persistence before entering trades

**Important Notes:**
- This tab requires HMM analysis first
- Data refreshes when you refresh HMM tab
- Always cross-reference with individual tabs for details

---



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

**Best Practices:**
- Start with conservative filters, then adjust
- Look for stocks with both revenue AND earnings growth
- Lower PEG ratios (<1.0) often indicate value opportunities
- Check debt levels - high debt = higher risk
- Verify volume is sufficient for your position size

**Cautions:**
- Small caps are riskier than large caps
- Do additional research before investing
- Some stocks may have data limitations
- Growth rates can be volatile - verify the trend is real
- Never invest based solely on screener results

---

## General Tips for Using the Platform

### Recommended Trading Workflow

Follow this systematic approach for best results:

**Step 1: Run Screener → Find Candidates**
- Use Tab 1 (Small Cap Screener) to find promising stocks
- Look for strong growth metrics and reasonable valuations
- Filter for adequate liquidity (volume)
- Create a watchlist of 5-10 candidates

**Step 2: HMM Analysis → Check Regime + See Kelly Preview**
- Run Tab 1 (HMM Trading Signals) on each candidate
- Look for Bull regimes with 65%+ confidence
- Check candlestick pattern confirmation (STRONG_BUY signals)
- Review the Kelly Position Sizing Summary at bottom
- Eliminate stocks with HOLD or weak signals

**Step 3: Kelly Tab → Fine-Tune Position Size**
- Switch to Tab 3 (Kelly Position Sizing)
- Stock symbol auto-populates from HMM
- Enter your actual portfolio value
- Set appropriate stop-loss percentage (3-7%)
- Choose fractional Kelly multiplier:
  - Beginners: 0.25x (Quarter Kelly)
  - Most traders: 0.5x (Half Kelly)
  - Experienced: 0.75x max
- Review gauge - stay in Green or Yellow zones
- Note exact position size and stop-loss price

**Step 4: Execute with Proper Stop-Loss**
- Enter trade at calculated position size
- **IMMEDIATELY set stop-loss** at specified price
- Use guaranteed/hard stops for overnight positions
- Never move stop-loss lower (only higher as price rises)
- Monitor position daily
- Exit at stop-loss if hit - NO EXCEPTIONS

### Risk Management Reminders

- **Never invest more than you can afford to lose**
- **Diversify across multiple stocks** - Don't put all capital in one position
- **Always use stop-loss orders** - Kelly assumes you'll execute stops
- **Never exceed 20% in single position** - Even if Kelly says higher
- **Pay attention to HOLD signals** - Sometimes doing nothing is best
- **Strong signals (8-10 strength) are more reliable** than weak ones (1-5)
- **Use fractional Kelly (0.5x or less)** - Full Kelly is too aggressive
- **Monitor Kelly gauge colors** - Stay in Green/Yellow zones

### When Signals Conflict

If you see:
- **HMM says BUY, but patterns say SELL** → System shows HOLD (wait for clarity)
- **High Kelly % but SELL signal** → Don't trade - signals must align
- **Low Kelly % but STRONG_BUY** → Small edge detected, consider skipping
- **Screener finds stock but HMM shows SELL** → Wait for regime change
- **Kelly in Red zone** → Reduce position size immediately
- **Multiple warnings in Kelly tab** → Skip this trade entirely

### Data Freshness & Caching

- **Data cached for 1 hour** to prevent stale information
- **Use Refresh buttons** to force update:
  - Global refresh in sidebar (refreshes all tabs)
  - Per-tab refresh buttons (updates specific analysis)
- **Market data from Yahoo Finance** (real-time during market hours)
- **Run analysis daily** for active trading
- **Run weekly** for longer-term positions
- **Always refresh before placing trades** to ensure current data

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

**Applied Kelly %**: Your actual position size after fractional Kelly multiplier (e.g., Full Kelly × 0.5 = Applied Kelly)  
**Bear Market**: Period when prices are falling  
**Bull Market**: Period when prices are rising  
**Candlestick Pattern**: Visual price pattern that may predict future movement  
**Fractional Kelly**: Multiplier applied to Full Kelly to reduce risk (0.25x, 0.5x, 0.75x)  
**Full Kelly**: Mathematically optimal position size (often too aggressive for real trading)  
**Half Kelly**: 50% of Full Kelly - recommended position size for most traders  
**HMM (Hidden Markov Model)**: AI model that identifies market regimes  
**Kelly Criterion**: Mathematical formula for optimal position sizing based on edge and win probability  
**Market Regime**: The current market condition (bull, bear, or sideways)  
**PEG Ratio**: Price/Earnings divided by Growth rate (valuation metric)  
**Position Sizing**: Determining how much capital to allocate to each trade  
**Quarter Kelly**: 25% of Full Kelly - ultra-conservative position sizing  
**Stop-Loss**: Pre-determined price where you exit to limit losses  
**Volatility**: How much prices move up and down (measure of risk)  
**Volume**: Number of shares traded (measure of liquidity)  
**Win Probability**: Your calculated chance of winning based on HMM regime analysis  
**Win/Loss Ratio**: Average win amount divided by average loss amount

---

## Need Help?

This platform combines multiple advanced techniques:
- **AI-powered regime detection** (HMM with candlestick patterns)
- **Optimal position sizing** (Kelly Criterion with fractional options)
- **Integrated risk analysis** (Combined HMM + Kelly dashboard)
- **Fundamental screening** (Small-cap stock discovery)

### Quick Start Tips

1. **New to Kelly?** Start with Quarter Kelly (0.25x) until comfortable
2. **First time using platform?** Follow the 4-step workflow above
3. **Not sure about a signal?** When in doubt, use smaller positions or wait
4. **Seeing warnings?** Pay attention - they prevent over-leveraging

### Important Reminders

**Kelly is POWERFUL but requires discipline:**
- Always execute stop-losses at specified levels
- Never override Kelly with emotions
- Smaller fractional multipliers = safer trading
- Green/Yellow gauge zones = optimal positioning

**This is NOT financial advice:**
- Platform provides analysis tools, not trading recommendations
- You are responsible for your own trading decisions
- Past performance doesn't guarantee future results
- Small-cap trading involves significant risk

**Start simple, experiment with different settings, and always combine platform insights with your own research and strict risk management practices.**

---

## Download This Manual

Click the **"Download User Manual"** button in the sidebar to save this guide as a PDF for offline reference.

---

**Remember**: This is a sophisticated tool to assist your decision-making, not a guarantee of profits. The Kelly Criterion optimizes long-term growth but individual trades can still lose money. Always do your own research, use proper position sizing, and invest responsibly.
