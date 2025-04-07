import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from matplotlib.ticker import PercentFormatter

from variables import trades, current_year, df

def client_pareto_analysis(df, year, week, trades):
    """
    Creates Pareto charts showing the importance of top 5 and top 10 clients in TEU distribution.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the trade data
    year : int
        Year to analyze
    week : int
        Week number to analyze
    trades : list
        List of trade names to analyze
    
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure with 6 subplots (5 trades + total) arranged in 2 rows and 3 columns
    """
    # Filter data for the specified year and week
    filtered_df = df[(df['YEAR'] == year) & (df['WEEK'] == week)]
    
    # Add 'TOTAL' to the list of trades for plotting
    all_categories = trades + ['TOTAL']
    
    # Create figure with adjustments for better handling of long client names
    # Changed to 2 rows and 3 columns layout
    fig = plt.figure(figsize=(24, 16))  # Adjusted width and height for new layout
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.3)  # Changed to 2 rows, 3 columns
    
    # Loop through each trade and create a subplot
    for i, trade in enumerate(all_categories):
        ax = fig.add_subplot(gs[i//3, i%3])  # Position based on grid - adjusted for new layout
        
        if trade == 'TOTAL':
            # For TOTAL, use all trades data
            trade_df = filtered_df[filtered_df['TRADE'] != "OUT OF SCOPE"]
        else:
            # For specific trade
            trade_df = filtered_df[filtered_df['TRADE'] == trade]
        
        if trade_df.empty:
            ax.text(0.5, 0.5, f"No data available for {trade} in Week {week}, {year}",
                   ha='center', va='center', fontsize=12)
            ax.set_title(f'{trade} - Client Distribution', fontsize=12, fontweight='bold')
            continue
        
        # Group by client and calculate TEU sum
        client_teu = trade_df.groupby('CLEAN BUSINESS PARTNER')['TOTAL TEU'].sum().reset_index()
        
        # Sort by TEU in descending order
        client_teu = client_teu.sort_values('TOTAL TEU', ascending=False)
        
        # Calculate total TEU
        total_teu = client_teu['TOTAL TEU'].sum()
        
        # Calculate percentage and cumulative percentage
        client_teu['Percentage'] = client_teu['TOTAL TEU'] / total_teu * 100
        client_teu['Cumulative Percentage'] = client_teu['Percentage'].cumsum()
        
        # Number of clients to show in the bar chart (rest will be grouped as "Others")
        top_n = 15
        
        # Create "Others" category if there are more than top_n clients
        if len(client_teu) > top_n:
            top_clients = client_teu.iloc[:top_n].copy()
            others_teu = client_teu.iloc[top_n:]['TOTAL TEU'].sum()
            others_pct = client_teu.iloc[top_n:]['Percentage'].sum()
            
            others_row = pd.DataFrame({
                'CLEAN BUSINESS PARTNER': ['Others'],
                'TOTAL TEU': [others_teu],
                'Percentage': [others_pct],
                'Cumulative Percentage': [100.0]  # Always 100%
            })
            
            # Concatenate top clients with Others
            client_teu = pd.concat([top_clients, others_row], ignore_index=True)
        
        # Format client names for better display (if too long)
        client_teu['Short Name'] = client_teu['CLEAN BUSINESS PARTNER'].apply(
            lambda x: x[:15] + '...' if len(str(x)) > 15 else x)  # Reduced from 20 to 15 characters
        
        # Create bar plot
        bars = ax.bar(client_teu['Short Name'], client_teu['Percentage'], 
                     color='#0D173F', edgecolor='black')  # Updated color for other clients
        
        # Add cumulative line
        ax2 = ax.twinx()
        ax2.plot(client_teu['Short Name'], client_teu['Cumulative Percentage'], 
                color='red', marker='o', ms=4, linestyle='-', linewidth=2)
        
        # Mark top 5 and top 10 clients
        if len(client_teu) > 5:
            top5_pct = client_teu.iloc[:5]['Percentage'].sum()
            top5_cumul = client_teu.iloc[4]['Cumulative Percentage']
            ax2.axhline(y=top5_cumul, color='#16C47F', linestyle='--', alpha=0.7)  # Updated color
            # Position the top 5 text in a fixed location in the upper left
            ax.text(0.05, 0.90, f'Top 5: {top5_pct:.1f}%', 
                   transform=ax.transAxes, color='#16C47F', fontweight='bold')  # Updated color
        
        if len(client_teu) > 10:
            top10_pct = client_teu.iloc[:10]['Percentage'].sum()
            top10_cumul = client_teu.iloc[9]['Cumulative Percentage']
            ax2.axhline(y=top10_cumul, color='#FFD65A', linestyle='--', alpha=0.7)  # Updated color
            # Position the top 10 text in a fixed location in the upper right
            ax.text(0.65, 0.90, f'Top 10: {top10_pct:.1f}%', 
                   transform=ax.transAxes, color='#FFD65A', fontweight='bold')  # Updated color
        
        # Highlight the bars for top 5 clients
        for j, bar in enumerate(bars[:5]):
            bar.set_color('#4A06FF')  # Updated color for top 5 clients
        
        # Format y-axis as percentage
        ax.set_ylim(0, max(client_teu['Percentage']) * 1.15)  # Add some padding at the top
        ax2.set_ylim(0, 101)  # Percentage axis
        
        ax.yaxis.set_major_formatter(PercentFormatter())
        ax2.yaxis.set_major_formatter(PercentFormatter())
        
        # Rotate x-axis labels for better readability and adjust vertical position
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', va='top', fontsize=6)  # Reduced font size
        
        # Adjust bottom margin to make room for rotated labels
        plt.subplots_adjust(bottom=0.15)
        
        # Set labels and title
        ax.set_ylabel('Percentage of Total TEU', fontsize=10)
        ax2.set_ylabel('Cumulative Percentage', fontsize=10)
        
        # Add title and legend only for charts in the second row (i//3 == 1)
        if i//3 == 1:  # Second row
            ax.set_title(f'{trade} - Client Distribution (Week {week}, {year})', 
                        fontsize=12, fontweight='bold', pad=15)
            
            # Add legend
            from matplotlib.lines import Line2D
            custom_lines = [
                Line2D([0], [0], color='red', lw=2, marker='o', markersize=4),
                Line2D([0], [0], color='#16C47F', linestyle='--', lw=2),  # Updated color
                Line2D([0], [0], color='#FFD65A', linestyle='--', lw=2),  # Updated color
                Line2D([0], [0], color='#4A06FF', lw=4),  # Updated color
                Line2D([0], [0], color='#0D173F', lw=4)   # Updated color
            ]
            ax.legend(custom_lines, ['Cumulative %', 'Top 5 Clients', 'Top 10 Clients', 
                                    'Top 5 Clients', 'Other Clients'], 
                     loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8)
        else:  # First row - no title or legend
            ax.set_title(f'{trade}', fontsize=12, fontweight='bold')  # Simple trade name only
        
        # Add count of total clients (keep this for all charts)
        client_count = len(trade_df['CLEAN BUSINESS PARTNER'].unique())
        ax.text(0.02, 0.98, f'Total Clients: {client_count}', transform=ax.transAxes,
               fontsize=9, va='top')
        
        # Add grid for readability
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.suptitle(f'Client Importance Analysis - Week {week}, {year}', fontsize=16, y=0.98)
    
    return fig
