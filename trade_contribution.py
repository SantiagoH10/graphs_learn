import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from variables import trades, current_year, current_week, csv_path

#Show the evolution of the AVG contribution in the current year by week and trade.

def contrib_evol_ytd(csv_path, year, week):
    df = pd.read_csv(csv_path, encoding = "latin1")
    df = df[(df['YEAR']==year)&(df['WEEK']<=week)&(df['TRADE']!="OUT OF SCOPE")&(df['AVG CONTRIBUTION'].notna())]

    plot_data = df.pivot_table(index = 'WEEK', values = 'AVG CONTRIBUTION', columns = 'TRADE', aggfunc='mean')

    plot_data.plot(figsize=(10,6))
    plt.title(f'Average Contribution Evolution by Trade in {year}')
    plt.xlabel('Week')
    plt.ylabel('Average Contribution')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Trade')

    return plt.show()

#Show the evolution of the AVG contribution on YTD compared to the prior year by trade

def contrib_comparison(csv_path, current_year, previous_year, current_week, trades):
    """
    Creates 6 charts comparing weekly contribution evolution between current and previous year.
    
    Parameters:
    -----------
    csv_path : str
        Path to the CSV file with contribution data
    current_year : int
        Current year to analyze
    previous_year : int
        Previous year to compare against
    current_week : int
        Maximum week number to include in analysis
    trades : list
        List of trade names to analyze
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with 6 subplots (5 trades + total)
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.gridspec as gridspec
    
    # Read the data
    df = pd.read_csv(csv_path, encoding="latin1")
    
    # Filter data for current and previous year
    df_current = df[(df['YEAR'] == current_year) & 
                   (df['WEEK'] <= current_week) & 
                   (df['TRADE'] != "OUT OF SCOPE") & 
                   (df['AVG CONTRIBUTION'].notna())]
    
    df_previous = df[(df['YEAR'] == previous_year) & 
                    (df['WEEK'] <= current_week) & 
                    (df['TRADE'] != "OUT OF SCOPE") & 
                    (df['AVG CONTRIBUTION'].notna())]
    
    # Create pivot tables
    current_data = df_current.pivot_table(index='WEEK', 
                                         values='AVG CONTRIBUTION', 
                                         columns='TRADE', 
                                         aggfunc='mean')
    
    previous_data = df_previous.pivot_table(index='WEEK', 
                                           values='AVG CONTRIBUTION', 
                                           columns='TRADE', 
                                           aggfunc='mean')
    
    # Create a total column for both years
    if not current_data.empty:
        current_data['TOTAL'] = current_data.mean(axis=1)
    if not previous_data.empty:
        previous_data['TOTAL'] = previous_data.mean(axis=1)
    
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
        ax.set_title(f'{trade}', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Set x-axis tick marks to whole weeks
        ax.set_xticks(range(1, current_week+1, 2))  # Every 2 weeks for readability
    
    plt.tight_layout()
    return fig

"""
fig = contrib_comparison(csv_path, current_year, current_year-1, current_week, trades)
plt.show()
"""

#Weighted average
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.gridspec as gridspec

# Show the evolution of the WEIGHTED AVG contribution in the current year by week and trade.
def weighted_contrib_evol_ytd(df, year, week):
    """
    Creates a chart showing the evolution of TEU-weighted average contribution by trade for a single year.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the contribution data
    year : int
        Year to analyze
    week : int
        Maximum week number to include in analysis
    
    Returns:
    --------
    matplotlib.figure.Figure
        The generated figure
    """
    # Filter the dataframe
    filtered_df = df[(df['YEAR']==year) & 
                     (df['WEEK']<=week) & 
                     (df['TRADE']!="OUT OF SCOPE") & 
                     (df['AVG CONTRIBUTION'].notna()) & 
                     (df['TOTAL TEU'].notna())]
    
    # Group by WEEK and TRADE, calculate weighted average
    grouped = filtered_df.groupby(['WEEK', 'TRADE'])
    weighted_avg = grouped.apply(lambda x: np.average(x['AVG CONTRIBUTION'], weights=x['TOTAL TEU']))
    weighted_avg = weighted_avg.reset_index(name='WEIGHTED_AVG_CONTRIBUTION')
    
    # Pivot the data for plotting
    plot_data = weighted_avg.pivot_table(index='WEEK', values='WEIGHTED_AVG_CONTRIBUTION', columns='TRADE')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_data.plot(ax=ax)
    plt.title(f'TEU-Weighted Average Contribution Evolution by Trade in {year}')
    plt.xlabel('Week')
    plt.ylabel('Weighted Average Contribution')
    plt.grid(True, alpha=0.3)
    plt.legend(title='Trade')

    return fig

# Show the evolution of the WEIGHTED AVG contribution on YTD compared to the prior year by trade
def weighted_contrib_comparison(df, current_year, previous_year, current_week, trades):
    """
    Creates 6 charts comparing weekly TEU-weighted contribution evolution between current and previous year.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the contribution data
    current_year : int
        Current year to analyze
    previous_year : int
        Previous year to compare against
    current_week : int
        Maximum week number to include in analysis
    trades : list
        List of trade names to analyze
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with 6 subplots (5 trades + total)
    """
    # Filter data for current and previous year, ensuring TOTAL TEU is not null
    df_current = df[(df['YEAR'] == current_year) & 
                   (df['WEEK'] <= current_week) & 
                   (df['TRADE'] != "OUT OF SCOPE") & 
                   (df['AVG CONTRIBUTION'].notna()) &
                   (df['TOTAL TEU'].notna())]
    
    df_previous = df[(df['YEAR'] == previous_year) & 
                    (df['WEEK'] <= current_week) & 
                    (df['TRADE'] != "OUT OF SCOPE") & 
                    (df['AVG CONTRIBUTION'].notna()) &
                    (df['TOTAL TEU'].notna())]
    
    # Calculate weighted averages for each week/trade combination
    def calculate_weighted_avg(df):
        # Group by WEEK and TRADE
        result = {}
        for trade in trades + ['ALL']:
            if trade == 'ALL':
                # For 'ALL', we consider all trades
                trade_data = df
            else:
                # For specific trades, filter the data
                trade_data = df[df['TRADE'] == trade]
            
            # Group by week and calculate weighted average
            weekly_avg = {}
            for week in range(1, current_week+1):
                week_data = trade_data[trade_data['WEEK'] == week]
                if not week_data.empty:
                    weighted_avg = np.average(week_data['AVG CONTRIBUTION'], weights=week_data['TOTAL TEU'])
                    weekly_avg[week] = weighted_avg
            
            # Convert to Series
            result[trade] = pd.Series(weekly_avg)
        
        return pd.DataFrame(result)
    
    # Calculate weighted averages
    current_data = calculate_weighted_avg(df_current)
    previous_data = calculate_weighted_avg(df_previous)
    
    # Add TOTAL to the list of trades for plotting (renamed from 'ALL' for consistency)
    current_data['TOTAL'] = current_data['ALL']
    previous_data['TOTAL'] = previous_data['ALL']
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
        ax.set_title(f'{trade} (TEU-Weighted)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Set x-axis tick marks to whole weeks
        ax.set_xticks(range(1, current_week+1, 2))  # Every 2 weeks for readability
        ax.set_ylabel('Weighted Avg Contribution ($)')
    
    plt.suptitle(f'TEU-Weighted Average Contribution Evolution: {current_year} vs {previous_year}', 
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make room for suptitle
    return fig

# Example usage:
# df = pd.read_csv(csv_path, encoding="latin1")
# fig = weighted_contrib_comparison(df, current_year, current_year-1, current_week, trades)
# plt.show()

# For single year chart:
# fig = weighted_contrib_evol_ytd(df, current_year, current_week)
# plt.show()
