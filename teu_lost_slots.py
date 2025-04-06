import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from variables import trades, current_year, current_week, csv_path


# Area chart comparing YTD totals by trade
def create_teu_area_chart(csv_path, current_week, current_year):
    df = pd.read_csv(csv_path, encoding="latin1")

    filtered_df = df[(df['TRADE']!="OUT OF SCOPE")]
    
    # Create YTD dataframes for current and previous year
    current_ytd_df = filtered_df[(filtered_df['YEAR'] == current_year) & (filtered_df['WEEK'] <= current_week)]
    prior_ytd_df = filtered_df[(filtered_df['YEAR'] == current_year-1) & (filtered_df['WEEK'] <= current_week)]
    
    plt.figure(figsize=(12, 8))
    
    # Set up a figure with subplots - one for current year, one for previous year
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)
    
    
    #Group by trade
    current_grouped = current_ytd_df.groupby('TRADE').agg({
        'TEU (WITHOUT LS)': 'sum',
        'TOTAL TEU': 'sum'
    }).reset_index()
    
    prior_grouped = prior_ytd_df.groupby('TRADE').agg({
        'TEU (WITHOUT LS)': 'sum',
        'TOTAL TEU': 'sum'
    }).reset_index()
    
    # Sort by TOTAL TEU for better visualization
    current_grouped = current_grouped.sort_values('TOTAL TEU', ascending=False)
    prior_grouped = prior_grouped.sort_values('TOTAL TEU', ascending=False)
    
    # Plot for current year
    ax1.bar(current_grouped['TRADE'], current_grouped['TEU (WITHOUT LS)'], 
            color='steelblue', label='TEU (WITHOUT LS)')
    ax1.bar(current_grouped['TRADE'], 
            current_grouped['TOTAL TEU'] - current_grouped['TEU (WITHOUT LS)'], 
            bottom=current_grouped['TEU (WITHOUT LS)'], color='lightcoral', 
            label='Lost Slots Contribution')
    
    # Plot for previous year
    ax2.bar(prior_grouped['TRADE'], prior_grouped['TEU (WITHOUT LS)'], 
            color='steelblue', label='TEU (WITHOUT LS)')
    ax2.bar(prior_grouped['TRADE'], 
            prior_grouped['TOTAL TEU'] - prior_grouped['TEU (WITHOUT LS)'], 
            bottom=prior_grouped['TEU (WITHOUT LS)'], color='lightcoral', 
            label='Lost Slots Contribution')
    
    # Titles and labels
    ax1.set_title(f'{current_year} YTD TEU Contribution by Trade (Weeks 1-{current_week})', fontsize=14)
    ax2.set_title(f'{current_year-1} YTD TEU Contribution by Trade (Weeks 1-{current_week})', fontsize=14)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Common labels and formatting
    ax1.set_ylabel('TEU', fontsize=12)
    ax2.set_ylabel('TEU', fontsize=12)
    ax2.set_xlabel('Trade', fontsize=12)
    
    # Add legends
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper right')
    
    # Add grid lines for better readability
    ax1.grid(True, alpha=0.3)
    ax2.grid(True, alpha=0.3)
    
    # Add a figure title
    fig.suptitle(f'YTD Comparison: TEU with and without Lost Slots by Trade', fontsize=16, y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    
    return fig

# Visualization with detailed YTD comparison by trade
def create_ytd_comparison_chart(csv_path, current_week, current_year):

    df = pd.read_csv(csv_path, encoding="latin1")
    
    filtered_df = df[(df['TRADE']!="OUT OF SCOPE")]
    
    # Create YTD dataframes for current and previous year
    current_ytd_df = filtered_df[(filtered_df['YEAR'] == current_year) & (filtered_df['WEEK'] <= current_week)]
    prior_ytd_df = filtered_df[(filtered_df['YEAR'] == current_year-1) & (filtered_df['WEEK'] <= current_week)]
    
    # For all trades, compare YTD totals by trade between years
    current_trade_ytd = current_ytd_df.groupby('TRADE').agg({
        'TEU (WITHOUT LS)': 'sum',
        'TOTAL TEU': 'sum'
    }).reset_index()
    
    prior_trade_ytd = prior_ytd_df.groupby('TRADE').agg({
        'TEU (WITHOUT LS)': 'sum',
        'TOTAL TEU': 'sum'
    }).reset_index()
    
    # Merge the data
    merged_data = current_trade_ytd.merge(
        prior_trade_ytd, 
        on='TRADE', 
        suffixes=(f'_{current_year}', f'_{current_year-1}')
    )
    
    # Calculate growth
    merged_data[f'GROWTH_TOTAL'] = ((merged_data[f'TOTAL TEU_{current_year}'] / 
                                        merged_data[f'TOTAL TEU_{current_year-1}']) - 1) * 100
    
    # Sort by current year total TEU
    merged_data = merged_data.sort_values(f'TOTAL TEU_{current_year}', ascending=False)
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Set width of bars
    bar_width = 0.35
    index = np.arange(len(merged_data['TRADE']))
    
    # Create bars
    bars1 = ax.bar(index - bar_width/2, merged_data[f'TEU (WITHOUT LS)_{current_year}'], 
                    bar_width, color='navy', label=f'{current_year} TEU WITHOUT LS')
    
    bars2 = ax.bar(index - bar_width/2, 
                    merged_data[f'TOTAL TEU_{current_year}'] - merged_data[f'TEU (WITHOUT LS)_{current_year}'], 
                    bar_width, bottom=merged_data[f'TEU (WITHOUT LS)_{current_year}'], 
                    color='darkred', label=f'{current_year} Lost Slots')
    
    bars3 = ax.bar(index + bar_width/2, merged_data[f'TEU (WITHOUT LS)_{current_year-1}'], 
                    bar_width, color='royalblue', label=f'{current_year-1} TEU WITHOUT LS')
    
    bars4 = ax.bar(index + bar_width/2, 
                    merged_data[f'TOTAL TEU_{current_year-1}'] - merged_data[f'TEU (WITHOUT LS)_{current_year-1}'], 
                    bar_width, bottom=merged_data[f'TEU (WITHOUT LS)_{current_year-1}'], 
                    color='salmon', label=f'{current_year-1} Lost Slots')
    
    # Add labels and title
    ax.set_xlabel('Trade', fontsize=14)
    ax.set_ylabel('TEU', fontsize=14)
    ax.set_title(f'YTD TEU Comparison by Trade (Weeks 1-{current_week})', fontsize=16)
    ax.set_xticks(index)
    ax.set_xticklabels(merged_data['TRADE'], rotation=45, ha='right')
    
    # Add legend
    ax.legend()
    
    # Add data labels for growth
    for i, v in enumerate(merged_data['GROWTH_TOTAL']):
        ax.text(i, 
                merged_data[f'TOTAL TEU_{current_year}'][i] + 100, 
                f"{v:.1f}%", 
                color='black', 
                fontweight='bold', 
                ha='center')
    
    # Add grid
    ax.grid(True, axis='y', alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    return fig

#YTD cumsum by week of TEU and Lost Slots
def create_ytd_comparison_chart(csv_path, current_week, current_year):

    df = pd.read_csv(csv_path, encoding="latin1")
    
    filtered_df = df[(df['TRADE']!="OUT OF SCOPE")]
    
    # Create YTD dataframes for current and previous year
    current_ytd_df = filtered_df[(filtered_df['YEAR'] == current_year) & (filtered_df['WEEK'] <= current_week)]
    prior_ytd_df = filtered_df[(filtered_df['YEAR'] == current_year-1) & (filtered_df['WEEK'] <= current_week)]
    
    current_weekly = current_ytd_df.groupby('WEEK').agg({
        'TEU (WITHOUT LS)': 'sum',
        'TOTAL TEU': 'sum'
        }).reset_index()

    prior_weekly = prior_ytd_df.groupby('WEEK').agg({
        'TEU (WITHOUT LS)': 'sum',
        'TOTAL TEU': 'sum'
    }).reset_index()

    # Calculate cumulative sums
    current_weekly['CUM_TEU_NO_LS'] = current_weekly['TEU (WITHOUT LS)'].cumsum()
    current_weekly['CUM_TOTAL_TEU'] = current_weekly['TOTAL TEU'].cumsum()

    prior_weekly['CUM_TEU_NO_LS'] = prior_weekly['TEU (WITHOUT LS)'].cumsum()
    prior_weekly['CUM_TOTAL_TEU'] = prior_weekly['TOTAL TEU'].cumsum()

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot current year data
    ax.plot(current_weekly['WEEK'], current_weekly['CUM_TOTAL_TEU'], 
        marker='o', linestyle='-', color='darkred', linewidth=2, 
        label=f'{current_year} TOTAL TEU (Cumulative)')
    ax.plot(current_weekly['WEEK'], current_weekly['CUM_TEU_NO_LS'], 
        marker='s', linestyle='-', color='navy', linewidth=2, 
        label=f'{current_year} TEU WITHOUT LS (Cumulative)')

    # Plot previous year data
    ax.plot(prior_weekly['WEEK'], prior_weekly['CUM_TOTAL_TEU'], 
        marker='o', linestyle='--', color='salmon', linewidth=2, 
        label=f'{current_year-1} TOTAL TEU (Cumulative)')
    ax.plot(prior_weekly['WEEK'], prior_weekly['CUM_TEU_NO_LS'], 
        marker='s', linestyle='--', color='royalblue', linewidth=2, 
        label=f'{current_year-1} TEU WITHOUT LS (Cumulative)')

    # Fill the gap areas
    ax.fill_between(current_weekly['WEEK'], 
                current_weekly['CUM_TEU_NO_LS'], 
                current_weekly['CUM_TOTAL_TEU'], 
                alpha=0.3, color='red', label=f'{current_year} Lost Slots Impact')

    ax.fill_between(prior_weekly['WEEK'], 
                prior_weekly['CUM_TEU_NO_LS'], 
                prior_weekly['CUM_TOTAL_TEU'], 
                alpha=0.3, color='blue', label=f'{current_year-1} Lost Slots Impact')

    # Title and labels
    ax.set_title(f'YTD Cumulative TEU Comparison (Weeks 1-{current_week})', fontsize=16)
    ax.set_xlabel('Week', fontsize=14)
    ax.set_ylabel('Cumulative TEU', fontsize=14)

    # Add legend
    ax.legend(loc='upper left')

    # Add grid
    ax.grid(True, alpha=0.3)

    # Ensure x-axis shows all weeks
    ax.set_xticks(range(1, current_week + 1))
