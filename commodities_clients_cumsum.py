import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

import df, current_week, current_year from variables

def plot_commodity_cumulative_comparison(df, current_year, previous_year, current_week, num_commodities=12):
    """
    Creates charts comparing cumulative evolution of the top commodities between current and previous year.
    
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
    num_commodities : int
        Number of top commodities to display (default: 12)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with subplots (3 rows, 4 columns for 12 commodities)
    """
    # Ensure we have the weighted contribution column
    if 'WEIGHTED_CONTRIB' not in df.columns:
        df['WEIGHTED_CONTRIB'] = df['TEU'] * df['AVG CONTRIBUTION']
    
    # Filter data for current year up to current week
    df_current_ytd = df[(df['YEAR'] == current_year) & 
                        (df['WEEK'] <= current_week)]
    
    # Identify top commodities based on weighted contribution YTD
    top_commodities = df_current_ytd.groupby('COMMODITY HS CHAPTER')['WEIGHTED_CONTRIB'].sum().nlargest(num_commodities).index.tolist()
    
    # Filter data for current and previous year
    df_current = df[(df['YEAR'] == current_year) & 
                   (df['WEEK'] <= current_week) & 
                   (df['COMMODITY HS CHAPTER'].isin(top_commodities))]
    
    df_previous = df[(df['YEAR'] == previous_year) & 
                    (df['WEEK'] <= current_week) & 
                    (df['COMMODITY HS CHAPTER'].isin(top_commodities))]
    
    # Create pivot tables with weekly sums for each commodity
    current_weekly = df_current.pivot_table(index='WEEK', 
                                           values='WEIGHTED_CONTRIB', 
                                           columns='COMMODITY HS CHAPTER', 
                                           aggfunc='sum')
    
    previous_weekly = df_previous.pivot_table(index='WEEK', 
                                             values='WEIGHTED_CONTRIB', 
                                             columns='COMMODITY HS CHAPTER', 
                                             aggfunc='sum')
    
    # Convert to cumulative sums
    current_data = current_weekly.cumsum()
    previous_data = previous_weekly.cumsum()
    
    # Create figure with 3x4 subplots for 12 commodities
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(3, 4, figure=fig)  # 3 rows, 4 columns grid
    
    # Determine the ranking of commodities for labeling
    commodity_ranks = {commodity: f"#{i+1}" for i, commodity in enumerate(top_commodities)}
    
    # Loop through each commodity and create a subplot
    for i, commodity in enumerate(top_commodities):
        ax = fig.add_subplot(gs[i//4, i%4])  # Position based on grid
        
        # Extract data for this commodity, handle missing data
        current_series = current_data.get(commodity, pd.Series()).reindex(range(1, current_week+1))
        previous_series = previous_data.get(commodity, pd.Series()).reindex(range(1, current_week+1))
        
        # Forward fill missing values for cumulative data
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
        
        # Set labels and title (include rank in title)
        ax.set_title(f"{commodity_ranks[commodity]} {commodity}\nCumulative Weighted Contribution", 
                    fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Set x-axis tick marks to whole weeks
        ax.set_xticks(range(1, current_week+1, 4))  # Every 4 weeks for readability
        ax.set_xlabel('Week')
        ax.set_ylabel('Weighted Contribution')
        
        # Format y-axis with commas for thousands
        ax.get_yaxis().set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    plt.tight_layout()
    plt.suptitle(f'Top {num_commodities} Commodities: Cumulative Weighted Contribution\n{current_year} vs {previous_year}', 
                fontsize=16, y=1.02)
    return fig

  import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec

def plot_client_cumulative_comparison(df, current_year, previous_year, current_week, num_clients=21):
    """
    Creates charts comparing cumulative evolution of the top clients between current and previous year.
    
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
    num_clients : int
        Number of top clients to display (default: 21)
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with subplots (3 rows, 7 columns for 21 clients)
    """
    # Filter data for current year up to current week
    df_current_ytd = df[(df['YEAR'] == current_year) & 
                        (df['WEEK'] <= current_week)]
    
    # Identify top clients based on weighted contribution YTD
    top_clients = df_current_ytd.groupby('CLEAN BUSINESS PARTNER')['WEIGHTED CONTRIB'].sum().nlargest(num_clients).index.tolist()
    
    # Filter data for current and previous year
    df_current = df[(df['YEAR'] == current_year) & 
                   (df['WEEK'] <= current_week) & 
                   (df['CLEAN BUSINESS PARTNER'].isin(top_clients))]
    
    df_previous = df[(df['YEAR'] == previous_year) & 
                    (df['WEEK'] <= current_week) & 
                    (df['CLEAN BUSINESS PARTNER'].isin(top_clients))]
    
    # Create pivot tables with weekly sums for each client
    current_weekly = df_current.pivot_table(index='WEEK', 
                                           values='WEIGHTED CONTRIB', 
                                           columns='CLEAN BUSINESS PARTNER', 
                                           aggfunc='sum')
    
    previous_weekly = df_previous.pivot_table(index='WEEK', 
                                             values='WEIGHTED CONTRIB', 
                                             columns='CLEAN BUSINESS PARTNER', 
                                             aggfunc='sum')
    
    # Convert to cumulative sums
    current_data = current_weekly.cumsum()
    previous_data = previous_weekly.cumsum()
    
    # Calculate the new width while maintaining the same height
    # Original was 20x15 for 15 items (3x5 grid)
    # For 21 items (3x7 grid), increase width proportionally
    original_width = 20
    original_cols = 5
    new_cols = 7
    new_width = original_width * (new_cols / original_cols)  # Proportionally wider
    
    # Create figure with 3x7 subplots for 21 clients
    fig = plt.figure(figsize=(new_width, 15))
    gs = gridspec.GridSpec(3, 7, figure=fig)  # 3 rows, 7 columns grid
    
    # Determine the ranking of clients for labeling
    client_ranks = {client: f"#{i+1}" for i, client in enumerate(top_clients)}
    
    # Loop through each client and create a subplot
    for i, client in enumerate(top_clients):
        # Use i//7 for rows and i%7 for columns to match the 3x7 grid
        ax = fig.add_subplot(gs[i//7, i%7])  # Position based on grid
        
        # Extract data for this client, handle missing data
        current_series = current_data.get(client, pd.Series()).reindex(range(1, current_week+1))
        previous_series = previous_data.get(client, pd.Series()).reindex(range(1, current_week+1))
        
        # Forward fill missing values for cumulative data
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
        
        # Set labels and title (include rank in title)
        # Truncate long client names to fit in the title
        client_display = client if len(client) < 25 else client[:22] + "..."
        ax.set_title(f"{client_ranks[client]} {client_display}", 
                    fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Set x-axis tick marks to whole weeks
        ax.set_xticks(range(1, current_week+1, 4))  # Every 4 weeks for readability
        ax.set_xlabel('Week')
        ax.set_ylabel('Weighted Contribution')
        
        # Format y-axis with commas for thousands
        ax.get_yaxis().set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    plt.tight_layout()
    plt.suptitle(f'Top {num_clients} Clients: Cumulative Weighted Contribution', 
                fontsize=16, y=1.02)
    return fig


# Example usage:
# fig = plot_client_cumulative_comparison(df, current_year, current_year-1, current_week)
