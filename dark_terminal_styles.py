"""
Dark Bloomberg Terminal CSS Theme
Professional, data-dense, easy on eyes for long trading sessions
"""

from datetime import datetime

def get_dark_terminal_styles():
    """Return Dark Bloomberg Terminal CSS"""
    return """
    <script>
    // Remove keyboard shortcuts from sidebar collapse button only
    setInterval(function() {
        // Target only sidebar header buttons that show keyboard shortcuts
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            const buttons = sidebar.querySelectorAll('button[kind="header"], button[kind="headerNoPadding"]');
            buttons.forEach(btn => {
                // Hide text nodes containing brackets (keyboard shortcuts)
                Array.from(btn.childNodes).forEach(node => {
                    if (node.nodeType === 3 && node.textContent.includes('[')) { // Text node
                        node.textContent = '';
                    }
                });
                // Also check spans
                btn.querySelectorAll('span').forEach(span => {
                    if (span.textContent.includes('[') || span.textContent.toLowerCase().includes('keyboard')) {
                        span.style.display = 'none';
                    }
                });
            });
        }
        
        // Remove tooltip popups
        document.querySelectorAll('[role="tooltip"]').forEach(el => {
            if (!el.hasAttribute('data-testid') || el.getAttribute('data-testid') !== 'stToast') {
                el.remove();
            }
        });
    }, 500);
    </script>
    
    <style>
    /* Dark Bloomberg Terminal Color Scheme */
    :root {
        --bg-main: #1e1e1e;
        --bg-sidebar: #252525;
        --bg-panel: #2a2a2a;
        --bg-header: #252525;
        --border-color: #404040;
        --text-primary: #e0e0e0;
        --text-secondary: #a0a0a0;
        --text-dim: #888888;
        
        /* Conditional Formatting - Dark Shades */
        --positive-bg: #1a3a1a;
        --positive-text: #4ade80;
        --negative-bg: #3a1a1a;
        --negative-text: #f87171;
        --neutral-bg: #3a3a1a;
        --neutral-text: #fbbf24;
        
        /* UI Elements */
        --button-bg: #2a2a2a;
        --button-border: #555555;
        --button-hover: #333333;
        --slider-track: #3a3a3a;
        --slider-thumb: #555555;
        
        /* Fonts */
        --terminal-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --number-font: Consolas, Monaco, "Courier New", monospace;
    }
    
    /* Global Resets - Remove ALL Rounded Corners */
    * {
        border-radius: 0 !important;
    }
    
    /* Hide all tooltip popups but NOT toasts */
    div[role="tooltip"],
    div[data-baseweb="tooltip"],
    .stTooltipIcon,
    [data-testid="stTooltipIcon"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Ensure toast notifications are always visible */
    div[data-testid="stToast"],
    .stToast,
    div[data-baseweb="toast"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 9999 !important;
    }
    
    /* Main App Background */
    body {
        background-color: var(--bg-main) !important;
    }
    
    .stApp {
        background-color: var(--bg-main) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background-color: var(--bg-sidebar) !important;
        text-align: left !important;
    }
    
    /* All Text */
    body, .stMarkdown, p, span, div, label {
        color: var(--text-primary) !important;
        font-family: var(--terminal-font) !important;
        font-size: 11pt !important;
        font-weight: 400 !important;
        line-height: 1.4 !important;
    }
    
    /* Headers - Slightly Larger */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-size: 14pt !important;
        font-weight: 500 !important;
        margin-top: 12px !important;
        margin-bottom: 8px !important;
    }
    
    /* BUTTONS - Dark Gray Terminal Style */
    .stButton > button {
        background-color: var(--button-bg) !important;
        border: 1px solid var(--button-border) !important;
        color: var(--text-primary) !important;
        border-radius: 0 !important;
        padding: 8px 16px !important;
        font-weight: 400 !important;
    }
    
    .stButton > button:hover {
        background-color: var(--button-hover) !important;
        border-color: #666666 !important;
    }
    
    /* Primary Button - Still Gray, Just Brighter */
    .stButton > button[kind="primary"] {
        background-color: #333333 !important;
        border: 1px solid #666666 !important;
        color: var(--text-primary) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #3a3a3a !important;
    }
    
    /* SLIDERS - Subtle Gray */
    .stSlider > div > div > div {
        background-color: var(--slider-track) !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: var(--slider-thumb) !important;
    }
    
    /* INPUT BOXES - Dark */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 0 !important;
    }
    
    /* INFO/ALERT BOXES - Dark Panel Style */
    .stAlert {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
        color: var(--text-primary) !important;
        padding: 10px 15px !important;
    }
    
    /* SUCCESS/WARNING/ERROR - Subtle */
    div[data-baseweb="notification"] {
        background-color: var(--bg-panel) !important;
        border-left: 3px solid var(--positive-text) !important;
    }
    
    /* TABS - Utilitarian Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: var(--bg-main) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 0 !important;
        color: var(--text-dim) !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-bottom: 2px solid transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--text-primary) !important;
    }
    
    /* DATAFRAMES - Dark Bloomberg Style */
    .stDataFrame {
        background-color: var(--bg-main) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stDataFrame table {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }
    
    .stDataFrame thead tr th {
        background-color: var(--bg-panel) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        font-weight: 500 !important;
    }
    
    .stDataFrame tbody tr {
        background-color: var(--bg-main) !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: var(--bg-sidebar) !important;
    }
    
    .stDataFrame tbody tr td {
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* EXPANDERS - Dark */
    .streamlit-expanderHeader {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--bg-main) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
    }
    
    /* METRIC TABLES - Dark 2-Column */
    .dark-metric-table {
        width: 100%;
        border-collapse: collapse;
        margin: 5px 0;
        border: 1px solid var(--border-color);
        background-color: var(--bg-panel);
    }
    
    .dark-metric-table td:first-child {
        background-color: var(--bg-header);
        color: var(--text-secondary);
        font-weight: 400;
        width: 50%;
        padding: 6px 12px;
        border: 1px solid var(--border-color);
    }
    
    .dark-metric-table td:last-child {
        background-color: var(--bg-panel);
        color: var(--text-primary);
        font-family: var(--number-font);
        text-align: right;
        padding: 6px 12px;
        border: 1px solid var(--border-color);
    }
    
    /* Conditional Formatting - Dark Shades */
    .positive-cell {
        background-color: var(--positive-bg) !important;
        color: var(--positive-text) !important;
        font-weight: 500;
    }
    
    .negative-cell {
        background-color: var(--negative-bg) !important;
        color: var(--negative-text) !important;
        font-weight: 500;
    }
    
    .neutral-cell {
        background-color: var(--neutral-bg) !important;
        color: var(--neutral-text) !important;
        font-weight: 500;
    }
    
    /* COMPACT SPACING - Data Dense */
    .element-container {
        margin-bottom: 8px !important;
    }
    
    .stMarkdown {
        margin-bottom: 8px !important;
    }
    
    /* Remove Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer[data-testid="stDecoration"] {visibility: hidden;}
    footer.stApp {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    
    /* Fixed Status Bar */
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 32px;
        background-color: #1a1a1a;
        border-top: 1px solid var(--border-color);
        color: var(--text-dim);
        font-size: 10pt;
        font-family: var(--terminal-font);
        display: flex;
        align-items: center;
        padding: 0 20px;
        z-index: 999;
    }
    
    /* Grid Lines for Terminal Feel */
    .terminal-section {
        border: 1px solid #333333;
        padding: 12px;
        margin: 10px 0;
        background-color: var(--bg-panel);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background-color: var(--button-bg) !important;
        border: 1px solid var(--button-border) !important;
        color: var(--text-primary) !important;
        border-radius: 0 !important;
        min-height: 38px !important;
        height: auto !important;
        padding: 8px 16px !important;
        display: inline-block !important;
        line-height: normal !important;
        font-size: 11pt !important;
    }
    
    /* Force sidebar buttons to be visible */
    section[data-testid="stSidebar"] .stDownloadButton,
    section[data-testid="stSidebar"] .stButton {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        min-height: 38px !important;
    }
    
    section[data-testid="stSidebar"] .stDownloadButton > button,
    section[data-testid="stSidebar"] .stButton > button {
        display: inline-block !important;
        min-height: 38px !important;
        height: auto !important;
        line-height: normal !important;
        font-size: 11pt !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: var(--bg-panel) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 0 !important;
    }
    
    /* Code blocks */
    code {
        background-color: var(--bg-panel) !important;
        color: var(--positive-text) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        border: 1px solid var(--border-color) !important;
    }
    </style>
    """

def create_dark_metric_table(label: str, value: str, is_positive: bool | None = None) -> str:
    """Create a 2-column dark terminal metric table"""
    cell_class = ""
    if is_positive is True:
        cell_class = "positive-cell"
    elif is_positive is False:
        cell_class = "negative-cell"
    
    return f"""
    <table class="dark-metric-table">
        <tr>
            <td>{label}</td>
            <td class="{cell_class}">{value}</td>
        </tr>
    </table>
    """

def create_status_bar(ticker: str = "", last_update: str = "") -> str:
    """Create fixed status bar at bottom"""
    if not last_update:
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ticker_display = f"Analyzing: {ticker} | " if ticker else ""
    
    return f"""
    <div class="status-bar">
        Ready | {ticker_display}Last Updated: {last_update} | Data Source: Yahoo Finance
    </div>
    """

def get_dark_chart_layout():
    """Return Plotly dark theme layout settings"""
    return {
        'plot_bgcolor': '#1e1e1e',
        'paper_bgcolor': '#2a2a2a',
        'font': {'color': '#e0e0e0', 'family': 'Consolas, Monaco, monospace'},
        'xaxis': {
            'gridcolor': '#404040',
            'zerolinecolor': '#404040',
            'color': '#e0e0e0'
        },
        'yaxis': {
            'gridcolor': '#404040',
            'zerolinecolor': '#404040',
            'color': '#e0e0e0'
        },
        'margin': {'l': 50, 'r': 20, 't': 40, 'b': 40}
    }
