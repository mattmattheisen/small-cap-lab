"""
Excel-style CSS for Trading Platform
Removes emojis, applies gray color scheme, adds conditional formatting
"""

def get_excel_styles():
    """Return Excel-style CSS"""
    return """
    <style>
    /* Excel Color Scheme */
    :root {
        --excel-white: #FFFFFF;
        --excel-light-gray: #F2F2F2;
        --excel-medium-gray: #E7E6E6;
        --excel-dark-gray: #D0CECE;
        --excel-border: #A6A6A6;
        
        /* Conditional Formatting Colors */
        --positive-bg: #C6EFCE;
        --positive-text: #006100;
        --negative-bg: #FFC7CE;
        --negative-text: #9C0006;
        --neutral-bg: #FFEB9C;
        --neutral-text: #9C5700;
        
        /* Fonts */
        --excel-font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --number-font: Consolas, Monaco, "Courier New", monospace;
    }
    
    /* Remove Streamlit default styling */
    .stMetric {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Excel Table Styles */
    .excel-table {
        width: 100%;
        border-collapse: collapse;
        background: var(--excel-white);
        font-family: var(--excel-font);
        font-size: 14px;
        margin: 10px 0;
        border: 1px solid var(--excel-border);
        border-radius: 0 !important;
    }
    
    .excel-table th {
        background: var(--excel-medium-gray);
        color: #000000;
        font-weight: 600;
        text-align: left;
        padding: 8px 12px;
        border: 1px solid var(--excel-border);
        border-radius: 0 !important;
    }
    
    .excel-table td {
        padding: 6px 12px;
        border: 1px solid var(--excel-border);
        border-radius: 0 !important;
    }
    
    .excel-table tr:nth-child(even) {
        background: var(--excel-light-gray);
    }
    
    .excel-table tr:nth-child(odd) {
        background: var(--excel-white);
    }
    
    /* Two-column metric table */
    .excel-metric-table {
        width: 100%;
        border-collapse: collapse;
        margin: 5px 0;
        border: 1px solid var(--excel-border);
    }
    
    .excel-metric-table td:first-child {
        background: var(--excel-light-gray);
        font-weight: 600;
        width: 50%;
        padding: 6px 12px;
        border: 1px solid var(--excel-border);
    }
    
    .excel-metric-table td:last-child {
        background: var(--excel-white);
        font-family: var(--number-font);
        text-align: right;
        padding: 6px 12px;
        border: 1px solid var(--excel-border);
    }
    
    /* Conditional Formatting */
    .positive-cell {
        background: var(--positive-bg) !important;
        color: var(--positive-text) !important;
        font-weight: 600;
    }
    
    .negative-cell {
        background: var(--negative-bg) !important;
        color: var(--negative-text) !important;
        font-weight: 600;
    }
    
    .neutral-cell {
        background: var(--neutral-bg) !important;
        color: var(--neutral-text) !important;
        font-weight: 600;
    }
    
    /* Number formatting */
    .excel-number {
        font-family: var(--number-font);
        text-align: right;
    }
    
    /* Info box - Excel style */
    .excel-info-box {
        background: var(--excel-light-gray);
        border: 1px solid var(--excel-border);
        border-radius: 0;
        padding: 12px;
        margin: 10px 0;
        font-family: var(--excel-font);
        font-size: 14px;
    }
    
    /* Alert boxes */
    .excel-alert {
        border: 1px solid var(--excel-border);
        border-radius: 0;
        padding: 10px 15px;
        margin: 10px 0;
        font-family: var(--excel-font);
    }
    
    .excel-alert-success {
        background: var(--positive-bg);
        color: var(--positive-text);
        border-left: 4px solid var(--positive-text);
    }
    
    .excel-alert-warning {
        background: var(--neutral-bg);
        color: var(--neutral-text);
        border-left: 4px solid var(--neutral-text);
    }
    
    .excel-alert-error {
        background: var(--negative-bg);
        color: var(--negative-text);
        border-left: 4px solid var(--negative-text);
    }
    
    /* Section headers */
    .excel-section-header {
        background: var(--excel-medium-gray);
        border: 1px solid var(--excel-border);
        border-radius: 0;
        padding: 10px 15px;
        margin: 15px 0 5px 0;
        font-family: var(--excel-font);
        font-size: 16px;
        font-weight: 600;
        color: #000000;
    }
    
    /* Dense compact layout */
    .excel-compact {
        line-height: 1.3;
        margin: 0;
        padding: 0;
    }
    
    /* Remove all border radius from Streamlit elements */
    div[data-testid="stMetric"],
    div[data-testid="stAlert"],
    div.element-container {
        border-radius: 0 !important;
    }
    </style>
    """

def create_excel_metric_table(label: str, value: str, is_positive: bool = None) -> str:
    """Create a 2-column Excel-style metric table"""
    cell_class = ""
    if is_positive is True:
        cell_class = "positive-cell"
    elif is_positive is False:
        cell_class = "negative-cell"
    elif is_positive is None:
        cell_class = ""
    
    return f"""
    <table class="excel-metric-table">
        <tr>
            <td>{label}</td>
            <td class="{cell_class} excel-number">{value}</td>
        </tr>
    </table>
    """

def create_excel_table(headers: list, rows: list) -> str:
    """Create an Excel-style table with headers and rows"""
    header_html = "".join([f"<th>{h}</th>" for h in headers])
    
    rows_html = ""
    for row in rows:
        cells = "".join([f"<td>{cell}</td>" for cell in row])
        rows_html += f"<tr>{cells}</tr>"
    
    return f"""
    <table class="excel-table">
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """

def create_excel_alert(message: str, alert_type: str = "info") -> str:
    """Create an Excel-style alert box"""
    type_map = {
        "success": "excel-alert-success",
        "warning": "excel-alert-warning",
        "error": "excel-alert-error",
        "info": "excel-info-box"
    }
    
    class_name = type_map.get(alert_type, "excel-info-box")
    
    return f"""
    <div class="excel-alert {class_name}">
        {message}
    </div>
    """

def create_excel_section_header(title: str) -> str:
    """Create an Excel-style section header"""
    return f"""
    <div class="excel-section-header">
        {title}
    </div>
    """

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage for Excel display"""
    return f"{value:.{decimals}f}%"

def format_currency(value: float) -> str:
    """Format currency for Excel display"""
    return f"${value:,.2f}"

def get_conditional_class(value: float, threshold: float = 0) -> str:
    """Get conditional formatting class based on value"""
    if value > threshold:
        return "positive-cell"
    elif value < threshold:
        return "negative-cell"
    else:
        return "neutral-cell"
