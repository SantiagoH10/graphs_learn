import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from variables import trades, current_year, current_week, csv_path, equipment_colors

# Doughnut showing the distribution of equipment types
def equipment_doughnut_single_plot(ax, csv_path, year, week, title=None):
    df = pd.read_csv(csv_path, encoding="latin1")
    df = df[(df['YEAR']==year)&(df['WEEK']<=week)&(df['TRADE']!="OUT OF SCOPE")&(df['TOTAL TEU'].notna())]

    grouped = df.groupby('EQUIPMENT')['TOTAL TEU'].sum().reset_index()
    top_categories = grouped.sort_values('TOTAL TEU', ascending=False).head(5)['EQUIPMENT'].tolist()

    # Function that maps categories to either themselves or 'Other'
    def map_category(cat):
        return cat if cat in top_categories else 'Other'
    
    df['MAPPED EQUIPMENT'] = df['EQUIPMENT'].apply(map_category)
    
    plot_data = df.groupby('MAPPED EQUIPMENT')['TOTAL TEU'].sum().reset_index().sort_values('TOTAL TEU', ascending=False)
    wedges, texts, autotexts = ax.pie(x=plot_data['TOTAL TEU'], labels=plot_data['MAPPED EQUIPMENT'], 
                                     autopct='%1.1f%%', colors=equipment_colors)
    
    # Create a donut by adding a white circle at the center
    centre_circle = plt.Circle((0, 0), 0.65, fc='white')
    ax.add_patch(centre_circle)
    
    # Set aspect ratio to be equal so it's a circle
    ax.set_aspect('equal')
    
    if title:
        ax.set_title(title)

def equipment_comparison_yoy(csv_path, year_first, year_second, week):
    # Create a single figure with two subplots arranged vertically
    fig, axs = plt.subplots(2, 1, figsize=(10, 12))
    
    # Create donuts in each subplot
    equipment_doughnut_single_plot(axs[0], csv_path, year_first, week, f"Equipment YTD W{week} {year_first}")
    equipment_doughnut_single_plot(axs[1], csv_path, year_second, week, f"Equipment YTD W{week} {year_second}")
    
    # Add an overall title
    fig.suptitle(f"Equipment - YTD W{week} {year_first} vs {year_second}", fontsize=16)
    
    plt.tight_layout()
    plt.show()

#Create 12 charts for comparison between trades and between years

def equipment_doughnut_multiple_trades(csv_path, year_first, year_second, week):
    # Read data
    df = pd.read_csv(csv_path, encoding="latin1")
    df = df[(df['YEAR'].isin([year_first, year_second]))&(df['WEEK']<=week)&(df['TRADE']!="OUT OF SCOPE")&(df['TOTAL TEU'].notna())]
    
    # Get unique trades (assuming there are 5 trades as mentioned)
    unique_trades = df['TRADE'].unique()
    
    # Create a figure with 2 rows (years) and 6 columns (5 trades + total)
    fig, axs = plt.subplots(2, 6, figsize=(24, 10))
    
    # Process each year (current and previous)
    for year_idx, year in enumerate([year_first, year_second]):
        year_df = df[df['YEAR'] == year]
        
        # Process each trade
        for trade_idx, trade in enumerate(unique_trades[:5]):  # First 5 trades
            trade_df = year_df[year_df['TRADE'] == trade]
            ax = axs[year_idx, trade_idx]
            
            # Find top categories for this trade
            grouped = trade_df.groupby('EQUIPMENT')['TOTAL TEU'].sum().reset_index()
            top_categories = grouped.sort_values('TOTAL TEU', ascending=False).head(5)['EQUIPMENT'].tolist()
            
            # Map categories
            def map_category(cat):
                return cat if cat in top_categories else 'Other'
            
            trade_df['MAPPED EQUIPMENT'] = trade_df['EQUIPMENT'].apply(map_category)
            
            # Create the donut chart
            plot_data = trade_df.groupby('MAPPED EQUIPMENT')['TOTAL TEU'].sum().reset_index()
            plot_data = plot_data.sort_values('TOTAL TEU', ascending=False)
            
            if not plot_data.empty:
                wedges, texts, autotexts = ax.pie(x=plot_data['TOTAL TEU'], labels=plot_data['MAPPED EQUIPMENT'], 
                                               autopct='%1.1f%%', colors=equipment_colors[:len(plot_data)])
                # Make some labels smaller if needed
                for text in texts:
                    text.set_fontsize(8)
                for autotext in autotexts:
                    autotext.set_fontsize(8)
            
            # Create the donut hole
            centre_circle = plt.Circle((0, 0), 0.65, fc='white')
            ax.add_patch(centre_circle)
            ax.set_aspect('equal')
            
            # Set title for this subplot
            ax.set_title(f"{trade} {year}")
        
        # Create the "Total" chart for this year (last column)
        ax = axs[year_idx, 5]
        
        # Find top categories for the total
        grouped = year_df.groupby('EQUIPMENT')['TOTAL TEU'].sum().reset_index()
        top_categories = grouped.sort_values('TOTAL TEU', ascending=False).head(5)['EQUIPMENT'].tolist()
        
        # Map categories
        def map_category(cat):
            return cat if cat in top_categories else 'Other'
        
        year_df['MAPPED EQUIPMENT'] = year_df['EQUIPMENT'].apply(map_category)
        
        # Create the donut chart for total
        plot_data = year_df.groupby('MAPPED EQUIPMENT')['TOTAL TEU'].sum().reset_index()
        plot_data = plot_data.sort_values('TOTAL TEU', ascending=False)
        
        wedges, texts, autotexts = ax.pie(x=plot_data['TOTAL TEU'], labels=plot_data['MAPPED EQUIPMENT'], 
                                       autopct='%1.1f%%', colors=equipment_colors[:len(plot_data)])
        # Make some labels smaller if needed
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)
        
        # Create the donut hole
        centre_circle = plt.Circle((0, 0), 0.65, fc='white')
        ax.add_patch(centre_circle)
        ax.set_aspect('equal')
        
        # Set title for this total subplot
        ax.set_title(f"TOTAL {year}")
    
    # Set main title
    fig.suptitle(f"Equipment Distribution by Trade - YTD W{week} Comparison", fontsize=16)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)  # Make room for the suptitle
    plt.show()

# Call the function
equipment_doughnut_multiple_trades(csv_path, current_year, current_year-1, current_week)