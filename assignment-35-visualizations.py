"""
Business Visualisation Principles - Assignment 35
Author: Visualisation Designer
Description: Creates five distinct, professional data visualisations using matplotlib and seaborn.
Applies chart matching principles, complete labelling, consistent colour palette, and insight annotations.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Ensure output directory exists
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global seaborn / matplotlib design style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# ==========================================
# Task 3: Consistent Colour Palette Definition
# ==========================================
PALETTE = {
    'primary': '#1f77b4',      # Deep Professional Blue - Core metric baseline
    'secondary': '#ff7f0e',    # Energetic Orange - Secondary series & highlight lines
    'success': '#2ca02c',      # Forest Green - Positive targets & growth indicators
    'danger': '#d62728',       # Crimson Red - Threshold lines, dips, and outliers
    'purple': '#9467bd',       # Royal Purple - Supplementary product line
    'neutral': '#7f7f7f',      # Slate Gray - Benchmark/Average lines & neutral elements
    'light_bg': '#f8f9fa'      # Off-white background for annotation boxes
}

CHART_COLORS = [
    PALETTE['primary'],
    PALETTE['secondary'],
    PALETTE['success'],
    PALETTE['purple'],
    PALETTE['neutral']
]

# Helper function for currency formatting
def format_currency_millions(x, pos):
    """Formats values in millions of dollars."""
    return f'${x:.1f}M' if x < 10 else f'${x:.0f}M'

def format_currency_thousands(x, pos):
    """Formats values in thousands of dollars."""
    return f'${x:.0f}K'

def format_currency_direct(x, pos):
    """Formats direct dollar values."""
    return f'${x:.0f}'


# ==========================================
# Task 1 & 2 & 4: Chart Generation Functions
# ==========================================

def create_chart1_bar_chart():
    """
    Chart 1: Horizontal Bar Chart (Comparison across Categories)
    Business Question: Which product line generated the most revenue in Q4?
    """
    products = ['Enterprise Suite', 'Cloud SaaS', 'Hardware Systems', 'Professional Services', 'Data Analytics']
    revenue = [6.2, 4.8, 3.5, 2.4, 1.9]  # in Millions USD
    
    df = pd.DataFrame({'product': products, 'revenue': revenue}).sort_values('revenue', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color bars with primary palette color, top bar highlighted
    bar_colors = [PALETTE['primary'] if p != 'Enterprise Suite' else '#0f4c81' for p in df['product']]
    bars = ax.barh(df['product'], df['revenue'], color=bar_colors, height=0.6, edgecolor='white', linewidth=1)
    
    # Task 2: Complete Labelling
    ax.set_title('Q4 Revenue by Product Line (Category Comparison)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Revenue ($ Millions)', fontsize=12, labelpad=10)
    ax.set_ylabel('Product Line', fontsize=12, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_millions))
    ax.set_xlim(0, 7.5)
    
    # Add Data Labels on Bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.15, bar.get_y() + bar.get_height()/2, f'${width:.1f}M', 
                va='center', ha='left', fontsize=11, fontweight='bold', color='#333333')
        
    # Task 4: Annotations & Reference Line
    avg_revenue = np.mean(revenue)
    ax.axvline(x=avg_revenue, color=PALETTE['neutral'], linestyle='--', linewidth=1.5, 
               label=f'Average Revenue (${avg_revenue:.2f}M)')
    
    # Top performer callout
    top_revenue = df.loc[df['product'] == 'Enterprise Suite', 'revenue'].values[0]
    top_y = df['product'].tolist().index('Enterprise Suite')
    ax.annotate(
        f'Top Performer\n(${top_revenue:.1f}M, 32.9% of Total)',
        xy=(top_revenue, top_y),
        xytext=(top_revenue - 1.2, top_y - 0.7),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2),
        fontsize=10, fontweight='bold', color=PALETTE['danger'],
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['light_bg'], edgecolor=PALETTE['danger'], alpha=0.9)
    )
    
    ax.legend(loc='lower right', fontsize=11, frameon=True, facecolor='white')
    ax.grid(True, axis='x', linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'chart1_revenue_by_product.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def create_chart2_line_chart():
    """
    Chart 2: Multi-Series Line Chart (Trend over Time)
    Business Question: How has monthly revenue trended across top product lines over the last 12 months?
    """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    enterprise = [1.8, 1.9, 2.1, 2.0, 2.2, 2.3, 2.4, 1.7, 2.5, 2.6, 2.7, 2.9]
    cloud_saas = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.8, 2.0, 2.1, 2.3, 2.5]
    hardware   = [1.5, 1.4, 1.5, 1.3, 1.4, 1.5, 1.4, 1.1, 1.4, 1.3, 1.4, 1.5]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Task 3: Consistent Palette & Accessibility (markers + line styles)
    ax.plot(months, enterprise, marker='o', linewidth=2.5, color=PALETTE['primary'], 
            label='Enterprise Suite', linestyle='-')
    ax.plot(months, cloud_saas, marker='s', linewidth=2.5, color=PALETTE['secondary'], 
            label='Cloud SaaS', linestyle='--')
    ax.plot(months, hardware, marker='^', linewidth=2.5, color=PALETTE['success'], 
            label='Hardware Systems', linestyle='-.')
    
    # Task 2: Complete Labelling
    ax.set_title('Monthly Revenue Trend for Top 3 Product Lines (Last 12 Months)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Month (2024)', fontsize=12, labelpad=10)
    ax.set_ylabel('Monthly Revenue ($ Millions)', fontsize=12, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_millions))
    ax.set_ylim(0.8, 3.4)
    
    # Task 4: Reference Line & Annotations
    target = 2.0
    ax.axhline(y=target, color=PALETTE['danger'], linestyle=':', linewidth=2, label=f'Monthly Growth Target (${target:.1f}M)')
    
    # Annotate August Dip (Seasonal Anomaly)
    ax.annotate(
        'August Dip\n(Seasonal Slowdown: $1.7M)',
        xy=('Aug', 1.7),
        xytext=('Aug', 1.05),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff3cd', edgecolor=PALETTE['danger'], alpha=0.9)
    )
    
    # Annotate Cloud SaaS Steady Growth
    ax.annotate(
        'Steady 108% Growth\n($1.2M → $2.5M)',
        xy=('Dec', 2.5),
        xytext=('Oct', 3.0),
        arrowprops=dict(arrowstyle='->', color=PALETTE['secondary'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['light_bg'], edgecolor=PALETTE['secondary'], alpha=0.9)
    )
    
    ax.legend(loc='upper left', fontsize=11, frameon=True, facecolor='white', framealpha=0.95)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'chart2_revenue_trend.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def create_chart3_histogram():
    """
    Chart 3: Histogram with KDE (Distribution of Values)
    Business Question: How are individual customer order values distributed across the business?
    """
    np.random.seed(42)
    # Generate bimodal order value distribution: SMB orders ($150 mode) & Enterprise orders ($650 mode)
    smb_orders = np.random.normal(loc=150, scale=40, size=650)
    enterprise_orders = np.random.normal(loc=650, scale=80, size=350)
    order_values = np.clip(np.concatenate([smb_orders, enterprise_orders]), 20, 1000)
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Task 3: Palette application
    n, bins, patches = ax.hist(order_values, bins=30, color=PALETTE['primary'], 
                               edgecolor='white', alpha=0.85, label='Order Frequency Density')
    
    # Overlay KDE curve scaled to frequency
    sns.kdeplot(order_values, ax=ax, color=PALETTE['secondary'], linewidth=2.5, 
                label='KDE Density Trend', bw_adjust=0.7)
    
    # Task 2: Complete Labelling
    ax.set_title('Customer Order Value Distribution (Bimodal Pattern Analysis)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Order Value ($ USD)', fontsize=12, labelpad=10)
    ax.set_ylabel('Number of Orders (Frequency)', fontsize=12, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_direct))
    
    # Task 4: Reference Line & Annotations
    median_val = np.median(order_values)
    ax.axvline(x=median_val, color=PALETTE['danger'], linestyle='--', linewidth=2, 
               label=f'Median Order (${median_val:.0f})')
    
    # Annotate SMB Peak
    ax.annotate(
        'SMB Peak\n(~ $150 Mode)',
        xy=(150, 95),
        xytext=(230, 110),
        arrowprops=dict(arrowstyle='->', color=PALETTE['primary'], lw=2),
        fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['light_bg'], edgecolor=PALETTE['primary'], alpha=0.9)
    )
    
    # Annotate Enterprise Peak
    ax.annotate(
        'Enterprise Peak\n(~ $650 Mode)',
        xy=(650, 42),
        xytext=(740, 70),
        arrowprops=dict(arrowstyle='->', color=PALETTE['secondary'], lw=2),
        fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['light_bg'], edgecolor=PALETTE['secondary'], alpha=0.9)
    )
    
    ax.legend(loc='upper right', fontsize=11, frameon=True, facecolor='white')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'chart3_order_value_distribution.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def create_chart4_stacked_bar():
    """
    Chart 4: Stacked Bar Chart (Composition / Part-to-Whole)
    Business Question: How has quarterly revenue composition shifted across product lines over 2024?
    """
    quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
    product_data = {
        'Enterprise Suite':     [5.2, 5.5, 5.8, 6.2],
        'Cloud SaaS':           [3.1, 3.7, 4.2, 4.8],
        'Hardware Systems':     [3.9, 3.8, 3.6, 3.5],
        'Professional Services': [2.1, 2.2, 2.3, 2.4],
        'Data Analytics':       [1.2, 1.4, 1.6, 1.9]
    }
    
    df = pd.DataFrame(product_data, index=quarters)
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    bottom = np.zeros(len(quarters))
    bars_list = []
    
    # Task 3: Use Palette Colors consistently for products
    for idx, (col, color) in enumerate(zip(df.columns, CHART_COLORS)):
        values = df[col].values
        bars = ax.bar(quarters, values, bottom=bottom, label=col, color=color, width=0.55, edgecolor='white', linewidth=1)
        bars_list.append(bars)
        
        # Add segment labels for significant parts
        for j, val in enumerate(values):
            if val >= 2.0:
                ax.text(j, bottom[j] + val/2, f'${val:.1f}M', ha='center', va='center', 
                        color='white', fontweight='bold', fontsize=10)
        bottom += values
        
    # Task 2: Complete Labelling
    ax.set_title('Quarterly Revenue Composition by Product Line (2024)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Fiscal Quarter', fontsize=12, labelpad=10)
    ax.set_ylabel('Total Revenue ($ Millions)', fontsize=12, labelpad=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_millions))
    ax.set_ylim(0, 22)
    
    # Add Total Labels on top of stacked bars
    for j, total in enumerate(bottom):
        ax.text(j, total + 0.4, f'Total: ${total:.1f}M', ha='center', va='bottom', 
                fontweight='bold', fontsize=11, color='#222222')
        
    # Task 4: Annotation highlighting composition change
    # Cloud SaaS grew from 3.1 / 15.5 = 20% to 4.8 / 18.8 = 25.5%
    saas_q4_top = bottom[3] - df['Hardware Systems'].values[3] - df['Professional Services'].values[3] - df['Data Analytics'].values[3]
    ax.annotate(
        'Cloud SaaS Composition\nExpanded from 20% to 25.5%',
        xy=(3, 9.0),
        xytext=(1.8, 14.5),
        arrowprops=dict(arrowstyle='->', color=PALETTE['secondary'], lw=2),
        fontsize=10, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=PALETTE['light_bg'], edgecolor=PALETTE['secondary'], alpha=0.9)
    )
    
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=11, title='Product Lines', frameon=True)
    ax.grid(True, axis='y', linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'chart4_revenue_composition.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def create_chart5_scatter_plot():
    """
    Chart 5: Scatter Plot with Trend Line (Correlation between Variables)
    Business Question: Does marketing campaign spend correlate with revenue generated?
    """
    np.random.seed(101)
    campaign_spend = np.random.uniform(15, 90, 30)  # in $K
    # Strong positive linear relationship with noise
    revenue_generated = 1.2 + 0.055 * campaign_spend + np.random.normal(0, 0.45, 30)  # in $M
    
    # Introduce one specific outlier campaign (high spend, low yield)
    outlier_idx = 14
    campaign_spend[outlier_idx] = 85.0
    revenue_generated[outlier_idx] = 2.10
    
    df = pd.DataFrame({'spend': campaign_spend, 'revenue': revenue_generated})
    
    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    # Task 3: Scatter Plot points in Primary color
    ax.scatter(df['spend'], df['revenue'], color=PALETTE['primary'], s=75, alpha=0.85, 
               edgecolors='white', linewidth=1.2, label='Marketing Campaigns (N=30)')
    
    # Fit linear trend line
    z = np.polyfit(df['spend'], df['revenue'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(df['spend'].min(), df['spend'].max(), 100)
    
    # Calculate Pearson Correlation coefficient
    r_corr = np.corrcoef(df['spend'], df['revenue'])[0, 1]
    
    ax.plot(x_trend, p(x_trend), color=PALETTE['secondary'], linestyle='--', linewidth=2.5, 
            label=f'Linear Trendline (r = {r_corr:.2f})')
    
    # Task 2: Complete Labelling
    ax.set_title('Marketing Spend vs. Revenue Generated (Correlation Analysis)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Marketing Campaign Spend ($ Thousands)', fontsize=12, labelpad=10)
    ax.set_ylabel('Revenue Generated ($ Millions)', fontsize=12, labelpad=10)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_currency_thousands))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_millions))
    
    # Correlation Summary Box
    corr_text = f"Correlation: r = {r_corr:.2f}\nStrong Positive Association"
    ax.text(0.05, 0.82, corr_text, transform=ax.transAxes, fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#e8f4f8', edgecolor=PALETTE['primary'], alpha=0.9))
    
    # Task 4: Annotate Outlier Campaign
    outlier_x = campaign_spend[outlier_idx]
    outlier_y = revenue_generated[outlier_idx]
    
    # Highlight Outlier Circle
    ax.scatter([outlier_x], [outlier_y], color='none', s=250, edgecolors=PALETTE['danger'], linewidth=2.5)
    
    ax.annotate(
        'Outlier Campaign #15\n(High Spend: $85K, Low Return: $2.1M)',
        xy=(outlier_x, outlier_y),
        xytext=(outlier_x - 22, outlier_y + 1.1),
        arrowprops=dict(arrowstyle='->', color=PALETTE['danger'], lw=2),
        fontsize=10, fontweight='bold', ha='center', color=PALETTE['danger'],
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8d7da', edgecolor=PALETTE['danger'], alpha=0.95)
    )
    
    ax.legend(loc='lower right', fontsize=11, frameon=True, facecolor='white')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'chart5_marketing_vs_revenue.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filepath}")


def main():
    print("==========================================")
    print("Generating Assignment 35 Visualisations...")
    print("==========================================")
    
    create_chart1_bar_chart()
    create_chart2_line_chart()
    create_chart3_histogram()
    create_chart4_stacked_bar()
    create_chart5_scatter_plot()
    
    print("\nAll 5 charts successfully generated and saved to output/ directory!")

if __name__ == '__main__':
    main()
