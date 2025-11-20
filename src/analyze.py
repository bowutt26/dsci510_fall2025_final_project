import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import pearsonr

def calculate_correlation(df_merged):
    """
    Calculates the Pearson correlation coefficient (r) and p-value between PM2.5 and chronic disease in the merged U.S. dataset.
    :param df_merged: dataframe with 'avg_pm25' and 'avg_disease_value' columns.
    :return: tuple(r, p_value)
    """
    # Find all unique topics to help the user choose:
    unique_diseases = df_merged["disease"].unique()
    print(f"Unique diseases available for correlation: {unique_diseases}")

    target_disease = ["Asthma", "Cardiovascular Disease", "Cancer"]
    results = {}

    print("--- Performing Correlation Analysis ---")

    for disease in target_disease:
        # Filter the merged data for only the target disease rate
        df_target = df_merged.query(f"disease == '{disease}'")
        if df_target.empty:
            print(f"Skipping {disease}: No standardized rate data found.")
            results[disease] = {"rho": None, "p_value": None, "status": "No Data"}
            continue

        # Use scipy.stats.pearsonr for both correlation coefficient and p-value
        r, p_value = pearsonr(df_target["avg_pm25"], df_target["avg_prevalence_rate"])
        results[disease] = {
            "rho": r,
            "p_value": p_value,
            "status": "Success"
        }
        print(f"Results for {disease} Rate vs. PM2.5: rho = {r:.4f}, P-Value = {p_value:.4f}")
    return results

def plot_us_trends(df_merged, result_dir="results"):
    """
    Generates time series plots showing PM2.5 and chronic disease trends for all 5 U.S. states.
    :param df_merged: Merged U.S. dataframe.
    :param result_dir: directory to save plots.
    """
    print("--- Generating U.S. Trend Plots ---")
    os.makedirs(result_dir, exist_ok=True)

    # Plot 1: Chronic disease trend by state
    plt.figure(figsize=(12, 6))
    for state in df_merged["state"].unique():
        df_state = df_merged[df_merged["state"] == state]
        plt.plot(df_state["year"], df_state["avg_prevalence_rate"], marker='o', label=state)

    plt.title("U.S. Chronic Disease Prevalence Rate Trend (2015-2019)")
    plt.xlabel("Year")
    plt.ylabel("Average Disease Prevalence Rate")
    plt.legend(title="State")
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_merged["year"].unique())
    plt.tight_layout()
    plt.savefig(f'{result_dir}/us_disease_trends.png')
    plt.close()
    print(f"Saved U.S. Chronic Disease Trend plot to {result_dir}/us_disease_trends.png")

    # Plot 2: PM2.5 trend by state
    plt.figure(figsize=(12, 6))
    for state in df_merged["state"].unique():
        df_state = df_merged[df_merged["state"] == state]
        plt.plot(df_state["year"], df_state["avg_pm25"], marker='o', label=state)

    plt.title("U.S. PM2.5 Concentration Trend (2015-2019)")
    plt.xlabel("Year")
    plt.ylabel(r"Average PM2.5 Concentration ($\mu g/m^3$)")
    plt.legend(title="State")
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_merged["year"].unique())
    plt.tight_layout()
    plt.savefig(f'{result_dir}/us_pm25_trends.png')
    plt.close()
    print(f"Saved U.S. PM2.5 Trend plot to {result_dir}/us_pm25_trends.png")

def plot_global_comparison(df_merged, df_who, result_dir="results"):
    """
    Compares the U.S. PM2.5 average trend against the global PM2.5 average trend using the WHO data.
    :param df_merged: Merged U.S. dataframe.
    :param df_who: Cleaned global PM2.5 dataframe (from process_pm25_who).
    :param result_dir: directory to save plots.
    """
    print("--- Generating Global Comparison Plot ---")
    os.makedirs(result_dir, exist_ok=True)

    # Calculate U.S. National Mean PM2.5 (from the 5-state average)
    df_us_national = df_merged.groupby("year")["avg_pm25"].mean().reset_index().rename(columns={"avg_pm25": "US_PM25"})

    # Calculate Global Mean PM2.5
    # The df_who has columns: 'year', 'country', 'value'
    df_global = df_who.groupby("year")["value"].mean().reset_index().rename(columns={"value": "Global_PM25"})

    # Merge for consistent plotting over years
    df_compare = pd.merge(df_us_national, df_global, on="year", how="inner")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(df_compare["year"], df_compare["US_PM25"], marker='o', label="U.S. (5-State Average)", linewidth=2)
    plt.plot(df_compare["year"], df_compare["Global_PM25"], marker='s', label="Worldwide Average", linestyle='--',
             linewidth=2)

    plt.title("U.S. vs. Global PM2.5 Concentration Trends (2015-2019)")
    plt.xlabel("Year")
    plt.ylabel(r"Average PM2.5 Concentration ($\mu g/m^3$)")
    plt.legend()
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_compare["year"].unique())
    plt.tight_layout()
    plt.savefig(f'{result_dir}/global_pm25_comparison.png')
    plt.close()
    print(f"Saved Global PM2.5 Comparison plot to {result_dir}/global_pm25_comparison.png")

def plot_disease_heatmap(df_merged, result_dir="results"):
    """
    Generates a heatmap of chronic disease prevalence by state and year.
    :param df_merged: Merged U.S. dataframe with 'state', 'year', and 'avg_disease_value' columns.
    :param result_dir: Directory to save plots.
    """
    print("--- Generating Chronic Disease Heatmap ---")
    os.makedirs(result_dir, exist_ok=True)

    # Pivot the DataFrame to get states as rows, years as columns, and avg_disease_value as values
    heatmap_data = df_merged.pivot_table(
        index="state",
        columns="year",
        values="avg_prevalence_rate"
    )

    cbar_kws = {'label': 'Average Disease Prevalence Rate'}
    plt.figure(figsize=(10, 7))
    sns.heatmap(
        heatmap_data,
        annot=True,  # Show the numerical values on the heatmap
        fmt=".1f",  # Format annotations to one decimal place
        cmap="YlGnBu",  # Choose a color map (e.g., Yellow-Green-Blue)
        linewidths=.5,  # Add lines between cells for better separation
        cbar_kws={'label': 'Average  Chronic Disease Indicator Value'}  # Color bar label
    )

    plt.title("Chronic Disease Prevalence by State and Year (2015-2019)")
    plt.xlabel("Year")
    plt.ylabel("State")
    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    plt.savefig(f'{result_dir}/disease_heatmap.png')
    plt.close()
    print(f"Saved Chronic Disease Heatmap to {result_dir}/disease_heatmap.png")

def descriptive_stats(df_merged):
    """
    Prints descriptive statistics for the merged U.S. dataset.
    :param df_merged: Merged U.S. dataframe.
    """
    print("\n--- Descriptive Statistics for Merged U.S. Data ---")
    print("Average PM2.5 Concentration:")
    print(df_merged["avg_pm25"].describe().to_string())
    print("\nAverage Chronic Disease Indicator Value:")
    print(df_merged["avg_prevalence_rate"].describe().to_string())
    print("\n")