import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Urban Development Dashboard: Sri Lanka",
    page_icon="🏙️",
    layout="wide"
)

import streamlit as st

# Apply the animated border styling
st.markdown("""
<style>
@keyframes border-runner {
    0%   { top: 0; left: 0; }
    25%  { top: 0; left: 100%; transform: translateX(-100%); }
    50%  { top: 100%; left: 100%; transform: translate(-100%, -100%); }
    75%  { top: 100%; left: 0; transform: translateY(-100%); }
    100% { top: 0; left: 0; }
}

div.block-container {
    position: relative;
    margin-top: 65px;
    margin-bottom: 10px;
    border: 2px solid #39FF14;  /* Bright neon green border */
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 0 15px rgba(57, 255, 20, 0.3);
}

div.block-container::before {
    content: "";
    width: 12px;
    height: 12px;
    background-color: #39FF14;
    border-radius: 50%;
    position: absolute;
    animation: border-runner 12s linear infinite;
    box-shadow: 0 0 10px 4px rgba(57, 255, 20, 0.6);
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)



# More dashboard elements
st.subheader("Dashboard Controls")
option = st.selectbox(
    'Choose an option',
    ['Option 1', 'Option 2', 'Option 3'])

st.write('You selected:', option) 

# Load data
@st.cache_data
def load_data():
    # In a real scenario, you'd upload and read your CSV file
    # Since you've uploaded a file, we'll create a placeholder for the data structure
    df=pd.read_csv("cleaned_urban_data.csv")
    return df

# Function to categorize indicators
def categorize_indicators(indicators):
    categories = {
        'Population': [
            'Population density (people per sq. km of land area)',
            'Population in largest city',
            'Population in the largest city (% of urban population)',
            'Urban population',
            'Urban population (% of total population)',
            'Urban population growth (annual %)',
            'Urban population living in areas where elevation is below 5 meters (% of total population)'
        ],
        'Area': [
            'Urban land area (sq. km)',
            'Urban land area where elevation is below 5 meters (% of total land area)',
            'Urban land area where elevation is below 5 meters (sq. km)'
        ],
        'Infrastructure': [
            'Access to electricity, urban (% of urban population)',
            'Mortality caused by road traffic injury (per 100,000 population)',
            'PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)',
            'PM2.5 air pollution, population exposed to levels exceeding WHO guideline value (% of total)'
        ]
    }
    
    # Create a dictionary mapping indicators to categories
    indicator_to_category = {}
    for category, indicator_list in categories.items():
        for indicator in indicator_list:
            indicator_to_category[indicator] = category
    
    return categories, indicator_to_category

# Function to format values based on indicator
def format_value(value, indicator):
    if "%" in indicator:
        return f"{value:.2f}%"
    elif "sq. km" in indicator:
        return f"{value:.2f} km²"
    elif "per 100,000" in indicator:
        return f"{value:.2f} per 100k"
    elif "micrograms" in indicator:
        return f"{value:.2f} μg/m³"
    else:
        # For large numbers, format with commas
        if value >= 1000:
            return f"{value:,.0f}"
        return f"{value:.2f}"

# Custom CSS for styling
def apply_custom_css():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #424242;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f7f7f7;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #0d47a1;
            border-radius: 5px 5px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            font-size: 16px;
            font-weight: bold;
            color: white;    
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5;
            color: white;
            font-size: 16px; 
            font-weight: bold;
        }
        .info-box {
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        footer {
            margin-top: 50px;
            text-align: center;
            color: #757575;
            font-size: 0.8rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Function to upload file
def file_uploader():
    uploaded_file = st.file_uploader("Upload your dataset (CSV file)", type="csv")
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        return True
    return False

# Main app
def main():
    apply_custom_css()
    
    # Title and Introduction
    st.markdown('<div class="main-header">Urban Development Dashboard: Sri Lanka</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Explore trends in urban indicators across categories (Population, Area, Infrastructure) from 1960 to 2023</div>', unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    if data is None:
        return
    
    # Display raw data structure (just for debugging, can be removed in production)
    with st.expander("View Raw Data Structure"):
        st.dataframe(data.head())
    
    # Ensure data is properly filtered for Sri Lanka only
    data = data[data['Country Name'] == 'Sri Lanka']
    
    # Get years range
    min_year = data['Year'].min()
    max_year = data['Year'].max()
    
    # Get indicators and categorize them
    indicators = data['Indicator Name'].unique().tolist()
    categories, indicator_to_category = categorize_indicators(indicators)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category selector
    selected_category = st.sidebar.selectbox(
        "Select Category",
        list(categories.keys())
    )
    
    # Indicator selector filtered by category
    filtered_indicators = categories[selected_category]
    selected_indicator = st.sidebar.selectbox(
        "Select Indicator",
        filtered_indicators
    )
    
    # Year range slider
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year))
    )
    
    # Optional: Indicator search (you can implement this if needed)
    indicator_search = st.sidebar.text_input("Search Indicator", "")
    if indicator_search:
        search_results = [ind for ind in indicators if indicator_search.lower() in ind.lower()]
        if search_results:
            selected_indicator = st.sidebar.selectbox(
                "Search Results",
                search_results
            )
            # Update category based on the selected indicator from search
            selected_category = indicator_to_category.get(selected_indicator, selected_category)
        else:
            st.sidebar.warning("No indicators found matching your search.")
    
    # Filter data based on selections
    filtered_data = data[
        (data['Year'] >= year_range[0]) & 
        (data['Year'] <= year_range[1])
    ]
    
    # Get data for the selected indicator
    indicator_data = filtered_data[filtered_data['Indicator Name'] == selected_indicator].sort_values('Year')
    
    # Get data for all indicators in the selected category
    category_data = filtered_data[filtered_data['Indicator Name'].isin(categories[selected_category])]
    
    # Latest year data for metrics and yearly snapshot
    latest_year = int(max(filtered_data['Year']))
    latest_year_data = filtered_data[filtered_data['Year'] == latest_year]
    
    # Toggle for chart type
    chart_type = st.sidebar.radio("Chart Type", ["Line", "Bar"])
    
    # Main content area (Tabs)
    tab1, tab2, tab3, tab4 = st.tabs([
        "Indicator Trend", 
        "Category Comparison", 
        "Yearly Snapshot", 
        "Summary Stats"
    ])
    
    # Tab 1: Indicator Trend
    with tab1:
        st.header(f"Trend of {selected_indicator} ({year_range[0]}-{year_range[1]})")
        
        if not indicator_data.empty:
            # Prepare data for plotting
            plot_data = indicator_data[['Year', 'Value']].copy()
            plot_data['Year'] = plot_data['Year'].astype(int)
            
            # Create plot based on selected chart type
            if chart_type == "Line":
                fig = px.line(
                    plot_data, 
                    x='Year', 
                    y='Value',
                    title=f"{selected_indicator} ({year_range[0]}-{year_range[1]})",
                    markers=True
                )
            else:
                fig = px.bar(
                    plot_data, 
                    x='Year', 
                    y='Value',
                    title=f"{selected_indicator} ({year_range[0]}-{year_range[1]})"
                )
            
            # Customize y-axis title based on indicator
            if "%" in selected_indicator:
                fig.update_layout(yaxis_title="Percentage (%)")
            elif "sq. km" in selected_indicator:
                fig.update_layout(yaxis_title="Area (sq. km)")
            else:
                fig.update_layout(yaxis_title="Value")
            
            # Custom tooltip to show formatted values
            fig.update_traces(
                hovertemplate='<b>Year</b>: %{x}<br><b>Value</b>: %{y:,.2f}<extra></extra>'
            )
            
            # Improve layout
            fig.update_layout(
                xaxis_title="Year",
                height=500,
                template='plotly_white',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for {selected_indicator} in the selected year range.")
    
    # Tab 2: Category Comparison
    with tab2:
        st.header(f"Comparison of {selected_category} Indicators")
        
        if not category_data.empty:
            # Pivot the data to get indicators as columns
            pivot_data = category_data.pivot_table(
                index='Year',
                columns='Indicator Name',
                values='Value'
            ).reset_index()
            
            # For line chart
            if chart_type == "Line":
                fig = go.Figure()
                
                for indicator in categories[selected_category]:
                    if indicator in pivot_data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=pivot_data['Year'], 
                                y=pivot_data[indicator],
                                mode='lines+markers',
                                name=indicator
                            )
                        )
            else:  # For bar chart
                # Create a melted dataframe for grouped bar chart
                melted_data = category_data.copy()
                fig = px.bar(
                    melted_data,
                    x='Year',
                    y='Value',
                    color='Indicator Name',
                    barmode='group',
                    title=f"Comparison of {selected_category} Indicators"
                )
            
            # Improve layout
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Value",
                height=600,
                template='plotly_white',
                legend_title="Indicator",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for {selected_category} indicators in the selected year range.")
    
    # Tab 3: Yearly Snapshot
    with tab3:
        selected_snapshot_year = st.slider(
            "Select Year for Snapshot",
            min_value=int(min_year),
            max_value=int(max_year),
            value=latest_year
        )
        
        st.header(f"Snapshot of {selected_category} Indicators in {selected_snapshot_year}")
        
        # Filter data for the selected year and category
        snapshot_data = filtered_data[
            (filtered_data['Year'] == selected_snapshot_year) & 
            (filtered_data['Indicator Name'].isin(categories[selected_category]))
        ]
        
        if not snapshot_data.empty:
            # Sort by value for better visualization
            snapshot_data = snapshot_data.sort_values('Value')
            
            # Create horizontal bar chart
            fig = px.bar(
                snapshot_data,
                y='Indicator Name',
                x='Value',
                orientation='h',
                title=f"{selected_category} Indicators in {selected_snapshot_year}"
            )
            
            # Custom hover template
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Value: %{x:,.2f}<extra></extra>'
            )
            
            # Improve layout
            fig.update_layout(
                xaxis_title="Value",
                yaxis_title="",
                height=500,
                template='plotly_white',
                yaxis={'categoryorder':'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No data available for {selected_category} indicators in {selected_snapshot_year}.")
    
    # Tab 4: Summary Stats (KPI Panel)
    with tab4:
        st.header(f"Summary Statistics for {selected_category} Indicators")
        
        # Filter data for the latest year and selected category
        summary_data = latest_year_data[
            latest_year_data['Indicator Name'].isin(categories[selected_category])
        ]
        
        if not summary_data.empty:
            # Create columns based on the number of indicators
            num_indicators = len(categories[selected_category])
            cols_per_row = 3  # Number of columns per row
            
            # Create metrics in rows with multiple columns
            for i in range(0, num_indicators, cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j in range(cols_per_row):
                    if i + j < num_indicators:
                        indicator = categories[selected_category][i + j]
                        indicator_value = summary_data[summary_data['Indicator Name'] == indicator]['Value'].values
                        
                        if len(indicator_value) > 0:
                            formatted_value = format_value(indicator_value[0], indicator)
                            
                            # Get previous year data for delta calculation
                            prev_year_data = filtered_data[
                                (filtered_data['Year'] == latest_year - 1) & 
                                (filtered_data['Indicator Name'] == indicator)
                            ]
                            
                            delta = None
                            if not prev_year_data.empty:
                                prev_value = prev_year_data['Value'].values[0]
                                delta = indicator_value[0] - prev_value
                                # Format delta for percentage indicators
                                if "%" in indicator:
                                    delta_formatted = f"{delta:.2f}%"
                                else:
                                    delta_formatted = f"{delta:.2f}"
                            
                            with cols[j]:
                                st.metric(
                                    label=indicator,
                                    value=formatted_value,
                                    delta=delta_formatted if delta is not None else None,
                                    delta_color="normal"
                                )
                        else:
                            with cols[j]:
                                st.metric(
                                    label=indicator,
                                    value="No data"
                                )
            
            # Add a radar chart for category overview
            st.subheader(f"Radar Chart Overview of {selected_category} Indicators")
            
            # Prepare data for radar chart
            radar_data = summary_data.copy()
            
            # Normalize values for better radar chart visualization
            if not radar_data.empty:
                radar_data['Normalized Value'] = (radar_data['Value'] - radar_data['Value'].min()) / (radar_data['Value'].max() - radar_data['Value'].min())
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=radar_data['Normalized Value'],
                    theta=radar_data['Indicator Name'],
                    fill='toself',
                    name=f'{latest_year}'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    showlegend=True,
                    title=f"Normalized Values of {selected_category} Indicators in {latest_year}"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("Note: Values are normalized (0-1) for better comparison in the radar chart.")
        else:
            st.warning(f"No data available for {selected_category} indicators in {latest_year}.")
    
    # Data Table Section
    st.header("Data Table")
    
    # Filter data based on selections for the table
    table_data = filtered_data[
        filtered_data['Indicator Name'].isin(categories[selected_category])
    ].sort_values(['Indicator Name', 'Year'])
    
    if not table_data.empty:
        with st.expander("View and Download Data"):
            # Display the dataframe
            st.dataframe(table_data[['Year', 'Indicator Name', 'Value']])
            
            # Download button
            csv = table_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f"sri_lanka_{selected_category}_indicators_{year_range[0]}-{year_range[1]}.csv",
                mime="text/csv"
            )
    else:
        st.warning("No data available for the selected filters.")
    
    # Footer with data limitations
    st.markdown("""
    <footer>
        <p><strong>Data Limitations and Notes:</strong></p>
        <p>This dashboard presents urban development indicators for Sri Lanka from 1960 to 2023. 
        Some indicators may have missing data for certain years. 
        All data is sourced from official statistics and international development databases.</p>
        <p>© 2025 Urban Development Dashboard</p>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()









