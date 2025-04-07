import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.gridspec as gridspec

from variables import trades, current_year, current_week, df

# Show the evolution of the TEU/TONS on YTD compared to the prior year by trade

def contrib_comparison(df, current_year, previous_year, current_week, trades, teus_or_tons):
    """
    Creates 6 charts comparing weekly TEUs or Tons evolution between current and previous year.
    
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
    teus_or_tons : str
        Column name for the metric to analyze (e.g., 'TEU' or 'TONS')
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with 6 subplots (5 trades + total)
    """
    # Filter data for current and previous year
    df_current = df[(df['YEAR'] == current_year) & 
                   (df['WEEK'] <= current_week) & 
                   (df['TRADE'] != "OUT OF SCOPE") & 
                   (df[teus_or_tons].notna())]
    
    df_previous = df[(df['YEAR'] == previous_year) & 
                    (df['WEEK'] <= current_week) & 
                    (df['TRADE'] != "OUT OF SCOPE") & 
                    (df[teus_or_tons].notna())]
    
    # Create pivot tables using sum instead of average
    current_data = df_current.pivot_table(index='WEEK', 
                                         values=teus_or_tons, 
                                         columns='TRADE', 
                                         aggfunc='sum')
    
    previous_data = df_previous.pivot_table(index='WEEK', 
                                           values=teus_or_tons, 
                                           columns='TRADE', 
                                           aggfunc='sum')
    
    # Create a total column for both years
    if not current_data.empty:
        current_data['TOTAL'] = current_data.sum(axis=1)  # Changed to sum for total column
    if not previous_data.empty:
        previous_data['TOTAL'] = previous_data.sum(axis=1)  # Changed to sum for total column
    
    # Add TOTAL to the list of trades for plotting
    all_categories = trades + ['TOTAL']
    
    # Create figure with 6 subplots (5 trades + total)
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(3, 2, figure=fig)  # 3 rows, 2 columns grid
    
    # Loop through each trade and create a subplot
    for i, trade in enumerate(all_categories):
        ax = fig.add_subplot(gs[i//2, i%2])  # Position based on grid
        
        # Extract data for this trade, handle missing data
        current_series = current_data.get(trade, pd.Series()).reindex(range(1, current_week+1))
        previous_series = previous_data.get(trade, pd.Series()).reindex(range(1, current_week+1))
        
        # Interpolate missing values
        current_series = current_series.interpolate(method='linear')
        previous_series = previous_series.interpolate(method='linear')
        
        # Plot the lines
        weeks = range(1, current_week+1)
        ax.plot(weeks, current_series, marker='o', markersize=4, 
                linewidth=2, label=f'{current_year}', color='#0D173F')
        ax.plot(weeks, previous_series, marker='o', markersize=4, 
                linewidth=2, label=f'{previous_year}', color='#FF0000')
        
        # Fill the difference
        for w in weeks:
            if w in current_series.index and w in previous_series.index:
                curr = current_series.get(w, np.nan)
                prev = previous_series.get(w, np.nan)
                
                if not (np.isnan(curr) or np.isnan(prev)):
                    # Determine fill color based on which year is higher
                    if curr > prev:
                        ax.fill_between([w-0.5, w+0.5], [prev, prev], [curr, curr], 
                                       color='green', alpha=0.3)
                    elif prev > curr:
                        ax.fill_between([w-0.5, w+0.5], [curr, curr], [prev, prev], 
                                       color='red', alpha=0.3)
        
        # Set labels and title
        ax.set_title(f'{trade} - {teus_or_tons}', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Set x-axis tick marks to whole weeks
        ax.set_xticks(range(1, current_week+1, 2))  # Every 2 weeks for readability
        ax.set_xlabel('Week')
        ax.set_ylabel(teus_or_tons)
    
    plt.tight_layout()
    plt.suptitle(f'Weekly {teus_or_tons} by Trade: {current_year} vs {previous_year}', 
                fontsize=16, y=1.02)
    return fig

# Example usage:
"""
fig = contrib_comparison(df, current_year, current_year-1, current_week, trades, 'TEU')
plt.show()

# For tons analysis
fig = contrib_comparison(df, current_year, current_year-1, current_week, trades, 'TONS')
plt.show()
"""
