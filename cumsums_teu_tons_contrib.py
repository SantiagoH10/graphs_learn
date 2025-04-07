import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

from variables import trades, current_year, current_week, df

def plot_cumulative_comparison(df, current_year, previous_year, current_week, trades, metric_type='TEU'):
    """
    Creates 6 charts comparing cumulative evolution between current and previous year.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the trade data
    current_year : int
        Current year to analyze
    previous_year : int
        Previous year to compare against
    current_week : int
        Maximum week number to include in analysis
    trades : list
        List of trade names to analyze
    metric_type : str
        Type of metric to analyze:
        - 'TEU': Cumulative sum of TEUs
        - 'TONS': Cumulative sum of tons
        - 'WEIGHTED': Weighted contribution (TEU x AVG CONTRIBUTION)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with 6 subplots (5 trades + total)
    """
    # Determine the column(s) based on metric type
    if metric_type == 'WEIGHTED':
        # For weighted contribution, we'll need both TEU and AVG CONTRIBUTION
        value_col = 'WEIGHTED_CONTRIB'
        # Create weighted contribution if it doesn't exist
        if 'WEIGHTED_CONTRIB' not in df.columns:
            df['WEIGHTED_CONTRIB'] = df['TEU'] * df['AVG CONTRIBUTION']
    else:
        # For TEU or TONS, use the column directly
        value_col = metric_type
    
    # Filter data for current and previous year
    df_current = df[(df['YEAR'] == current_year) & 
                   (df['WEEK'] <= current_week) & 
                   (df['TRADE'] != "OUT OF SCOPE")]
    
    df_previous = df[(df['YEAR'] == previous_year) & 
                    (df['WEEK'] <= current_week) & 
                    (df['TRADE'] != "OUT OF SCOPE")]
    
    # Create pivot tables with weekly sums
    current_weekly = df_current.pivot_table(index='WEEK', 
                                           values=value_col, 
                                           columns='TRADE', 
                                           aggfunc='sum')
    
    previous_weekly = df_previous.pivot_table(index='WEEK', 
                                             values=value_col, 
                                             columns='TRADE', 
                                             aggfunc='sum')
    
    # Convert to cumulative sums
    current_data = current_weekly.cumsum()
    previous_data = previous_weekly.cumsum()
    
    # Create a total column for both years if not already present
    if 'TOTAL' not in current_data.columns and not current_data.empty:
        # For total, sum across trades for each week
        current_total = current_weekly.sum(axis=1).cumsum()
        current_data['TOTAL'] = current_total
    
    if 'TOTAL' not in previous_data.columns and not previous_data.empty:
        previous_total = previous_weekly.sum(axis=1).cumsum()
        previous_data['TOTAL'] = previous_total
    
    # Add TOTAL to the list of trades for plotting
    all_categories = trades + ['TOTAL']
    
    # Create figure with 6 subplots (5 trades + total)
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(3, 2, figure=fig)  # 3 rows, 2 columns grid
    
    # Determine title based on metric type
    if metric_type == 'WEIGHTED':
        title_metric = 'Weighted Contribution (TEU × Contribution)'
    else:
        title_metric = metric_type
    
    # Loop through each trade and create a subplot
    for i, trade in enumerate(all_categories):
        ax = fig.add_subplot(gs[i//2, i%2])  # Position based on grid
        
        # Extract data for this trade, handle missing data
        current_series = current_data.get(trade, pd.Series()).reindex(range(1, current_week+1))
        previous_series = previous_data.get(trade, pd.Series()).reindex(range(1, current_week+1))
        
        # Forward fill missing values for cumulative data (more appropriate than interpolation)
        current_series = current_series.fillna(method='ffill').fillna(0)
        previous_series = previous_series.fillna(method='ffill').fillna(0)
        
        # Plot the lines
        weeks = range(1, current_week+1)
        ax.plot(weeks, current_series, marker='o', markersize=4, 
                linewidth=2, label=f'{current_year}', color='#0D173F')
        ax.plot(weeks, previous_series, marker='o', markersize=4, 
                linewidth=2, label=f'{previous_year}', color='#FF0000')
        
        # Fill the area between lines
        ax.fill_between(weeks, previous_series, current_series, 
                       where=(current_series >= previous_series),
                       interpolate=True, color='green', alpha=0.3)
        
        ax.fill_between(weeks, previous_series, current_series, 
                       where=(current_series < previous_series),
                       interpolate=True, color='red', alpha=0.3)
        
        # Set labels and title
        ax.set_title(f'{trade} - Cumulative {title_metric}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Set x-axis tick marks to whole weeks
        ax.set_xticks(range(1, current_week+1, 2))  # Every 2 weeks for readability
        ax.set_xlabel('Week')
        ax.set_ylabel(f'Cumulative {title_metric}')
        
        # Format y-axis with commas for thousands
        ax.get_yaxis().set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    plt.tight_layout()
    plt.suptitle(f'Cumulative {title_metric} by Trade: {current_year} vs {previous_year}', 
                fontsize=16, y=1.02)
    return fig

# Example usage for TEU or TONS
"""
# For TEU cumulative analysis
fig_teu = plot_cumulative_comparison(df, current_year, current_year-1, current_week, trades, 'TEU')
plt.show()

# For TONS cumulative analysis
fig_tons = plot_cumulative_comparison(df, current_year, current_year-1, current_week, trades, 'TONS')
plt.show()

# For weighted contribution analysis (TEU × AVG CONTRIBUTION)
fig_weighted = plot_cumulative_comparison(df, current_year, current_year-1, current_week, trades, 'WEIGHTED')
plt.show()
"""

# Alternative function specifically for weighted contribution if needed
def plot_weighted_contribution(df, current_year, previous_year, current_week, trades):
    """
    Creates 6 charts comparing cumulative weighted contribution (TEU × Contribution)
    between current and previous year.
    
    This is a convenience function that calls plot_cumulative_comparison with metric_type='WEIGHTED'
    """
    return plot_cumulative_comparison(df, current_year, previous_year, current_week, trades, 'WEIGHTED')

  
