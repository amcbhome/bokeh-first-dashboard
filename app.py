import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, 
    DateRangeSlider, 
    HoverTool, 
    NumeralTickFormatter, 
    Div
)

# -------------------------------------------------------------------------
# 1. DATA GENERATION & PREPARATION LAYER
# -------------------------------------------------------------------------
def generate_business_data():
    """Generates a realistic business dataset spanning the last 6 months."""
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", end="2026-06-25", freq="D")
    n = len(dates)
    
    # Simulating standard financial accumulation and daily operational volatility
    revenue = np.random.normal(15000, 2200, n).cumsum() + 100000
    operating_costs = np.random.normal(11000, 1800, n).cumsum() + 60000
    efficiency_score = np.random.uniform(78, 96, n)
    
    df = pd.DataFrame({
        'date': dates,
        'revenue': revenue,
        'operating_costs': operating_costs,
        'efficiency_score': efficiency_score
    })
    return df

# Load core dataset
master_df = generate_business_data()

# Initialize the Bokeh ColumnDataSource (The live link between Python and the UI)
source = ColumnDataSource(data=dict(
    date=master_df['date'],
    revenue=master_df['revenue'],
    operating_costs=master_df['operating_costs'],
    efficiency_score=master_df['efficiency_score']
))

# -------------------------------------------------------------------------
# 2. INTERACTIVE WIDGETS
# -------------------------------------------------------------------------
# Title banner using HTML/CSS
title_banner = Div(
    text="""
    <div style='font-family: sans-serif; padding: 10px 0px;'>
        <h1 style='margin: 0; color: #1e293b;'>Operations & Financial Analytics Dashboard</h1>
        <p style='margin: 5px 0 0 0; color: #64748b;'>Interactive time-series and resource allocation model tracking</p>
    </div>
    """,
    sizing_mode="scale_width"
)

# Date Range Slider for global filtering
date_slider = DateRangeSlider(
    title="Select Analysis Window",
    start=master_df['date'].min(),
    end=master_df['date'].max(),
    value=(master_df['date'].min(), master_df['date'].max()),
    step=1,
    sizing_mode="scale_width",
    bar_color="#3b82f6"
)

# -------------------------------------------------------------------------
# 3. VISUALIZATION LAYER
# -------------------------------------------------------------------------
def build_performance_chart(cds_source):
    """Constructs the core dual-line interactive visualization."""
    p = figure(
        x_axis_type='datetime', 
        title="Revenue Trajectory vs. Operational Overhead",
        sizing_mode="scale_width",
        height=450,
        tools="pan,box_zoom,wheel_zoom,reset,save",
        toolbar_location="above"
    )
    
    # Render Revenue Line and Circle glyphs
    p.line('date', 'revenue', source=cds_source, color="#2563eb", line_width=3, legend_label="Gross Revenue")
    p.scatter('date', 'revenue', source=cds_source, color="#2563eb", size=5, alpha=0.4)
    
    # Render Operating Costs Line
    p.line('date', 'operating_costs', source=cds_source, color="#ea580c", line_width=2.5, legend_label="Operating Costs")
    
    # Technical Styling & Formatting
    p.yaxis.formatter = NumeralTickFormatter(format="£0,0")
    p.xaxis.axis_label = "Timeline"
    p.yaxis.axis_label = "Value (GBP)"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"  # Enables interactive toggling of metrics
    
    # Configure Custom Crosshair Hover Tools
    hover = HoverTool(
        tooltips=[
            ("Date", "@date{%F}"),
            ("Revenue", "@revenue{£0,0}"),
            ("Operating Costs", "@operating_costs{£0,0}"),
            ("Efficiency Score", "@efficiency_score{0.0}%")
        ],
        formatters={'@date': 'datetime'},
        mode='vline'
    )
    p.add_tools(hover)
    
    return p

performance_plot = build_performance_chart(source)

# -------------------------------------------------------------------------
# 4. REACTIVE SERVER-SIDE CALLBACKS
# -------------------------------------------------------------------------
def handle_date_filter_update(attr, old, new):
    """Triggered dynamically whenever the user manipulates the DateRangeSlider."""
    # Convert timestamps from millisecond integers to Pandas Datetime objects
    start_dt = pd.to_datetime(date_slider.value[0], unit='ms')
    end_dt = pd.to_datetime(date_slider.value[1], unit='ms')
    
    # Isolate sub-selection
    filtered_mask = (master_df['date'] >= start_dt) & (master_df['date'] <= end_dt)
    subset_df = master_df[filtered_mask]
    
    # Push updated dictionary arrays downstream to cleanly re-render graphics
    source.data = dict(
        date=subset_df['date'],
        revenue=subset_df['revenue'],
        operating_costs=subset_df['operating_costs'],
        efficiency_score=subset_df['efficiency_score']
    )

# Attach callback listener to the slider's value property
date_slider.on_change('value', handle_date_filter_update)

# -------------------------------------------------------------------------
# 5. DASHBOARD LAYOUT COMPOSITION
# -------------------------------------------------------------------------
# Organizes items into a clean structural column grid
dashboard_layout = column(
    title_banner,
    row(date_slider, sizing_mode="scale_width"),
    row(performance_plot, sizing_mode="scale_width"),
    sizing_mode="stretch_both",
    spacing=15
)

# Serve the layout structure directly to the active Bokeh document application
curdoc().add_root(dashboard_layout)
curdoc().title = "Analytics Application"
