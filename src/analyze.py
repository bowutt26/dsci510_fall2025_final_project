import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import spearmanr

def calculate_correlation(df_merged):
    """
    Calculates the Spearman correlation coefficient (r) and p-value between PM2.5 and
    the targeted chronic diseases over the overlapping 2019-2022 period.
    :param df_merged: dataframe with 'avg_pm25' and 'avg_prevalence_rate' columns.
    :return: dict where keys are disease names and values are {'rho', 'p_value', 'status'}
    """
    # Define the 6 diseases found to have 2019-2022 data
    TARGET_DISEASE = ['Alcohol', 'Arthritis', 'Asthma', 'Cardiovascular Disease',
         'Chronic Obstructive Pulmonary Disease', 'Cognitive Health and Caregiving',
         'Diabetes', 'Disability', 'Health Status', 'Immunization', 'Mental Health',
         'Nutrition, Physical Activity, and Weight Status',
         'Social Determinants of Health', 'Tobacco', 'Cancer', 'Oral Health', 'Sleep']

    print(f"Targeted disease:\n{TARGET_DISEASE}\n")

    print("--- Performing Correlation Analysis ---")

    results = {}
    for disease in TARGET_DISEASE:
        # Filter for only the target diseases
        df_target = df_merged.query(f"disease == '{disease}'").copy()
        df_target_clean = df_target.dropna(subset=["avg_pm25", "avg_prevalence_rate"])

        if len(df_target_clean) < 4:  # Small sample check (5 states * 4 years = 20 total points possible)
            print(
                f"Skipping {disease}: Insufficient data for meaningful correlation after cleaning ({len(df_target_clean)} points).")
            results[disease] = {"rho": None, "p_value": None, "status": "Insufficient Data"}
            continue

        # Use scipy.stats.spearmanr for both correlation coefficient and p-value
        r, p_value = spearmanr(df_target_clean["avg_pm25"], df_target_clean["avg_prevalence_rate"])
        results[disease] = {
            "rho": r,
            "p_value": p_value,
            "status": "Success"
        }
        print(f"Results for {disease} Rate vs. PM2.5: rho = {r:.4f}, P-Value = {p_value:.4f}")
    return results

def plot_us_trends(df_merged, result_dir="results", notebook_plot=False):
    """
    Generates time series plots showing PM2.5 and chronic disease trends for all 5 U.S. states.
    :param df_merged: Merged U.S. dataframe.
    :param result_dir: directory to save plots.
    """
    print("\n--- Generating U.S. Trend Plots ---")
    os.makedirs(result_dir, exist_ok=True)

    # Plot 1: Chronic disease trend by state
    plt.figure(figsize=(12, 6))
    for state in df_merged["state"].unique():
        df_state = df_merged[df_merged["state"] == state]
        plt.plot(df_state["year"], df_state["avg_prevalence_rate"], marker='o', label=state)

    plt.title("U.S. Chronic Disease Prevalence Rate Trend (2015-2022)")
    plt.xlabel("Year")
    plt.ylabel("Average Disease Prevalence Rate")
    plt.legend(title="State")
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_merged["year"].unique())
    plt.tight_layout()
    if not notebook_plot:
        plt.savefig(f'{result_dir}/us_disease_trends.png')
        print(f"Saved U.S. Chronic Disease Trend plot to {result_dir}/us_disease_trends.png")
        plt.close()
    else:
        plt.plot()

    # Plot 2: PM2.5 trend by state
    plt.figure(figsize=(12, 6))
    for state in df_merged["state"].unique():
        df_state = df_merged[df_merged["state"] == state]
        plt.plot(df_state["year"], df_state["avg_pm25"], marker='o', label=state)

    plt.title("U.S. PM2.5 Concentration Trend (2015-2022)")
    plt.xlabel("Year")
    plt.ylabel(r"Average PM2.5 Concentration ($\mu g/m^3$)")
    plt.legend(title="State")
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_merged["year"].unique())
    plt.tight_layout()
    if not notebook_plot:
        plt.savefig(f'{result_dir}/us_pm25_trends.png')
        print(f"Saved U.S. PM2.5 Trend plot to {result_dir}/us_pm25_trends.png")
        plt.close()
    else:
        plt.plot()

def plot_all_chronic_trends(df_merged, result_dir='results', notebook_plot=False):
    """
    Generates a line plot for the time trend of each unique (disease, unit)
    combination in the merged U.S. dataset, showing a separate line for each state.

    :param df_merged: DataFrame containing the merged PM2.5 and chronic data,
                      must have columns: 'state', 'year', 'disease', 'unit', and the
                      aggregated value column (e.g., 'avg_prevalence_rate').
    :param result_dir: Directory to save the output plots. Defaults to 'results'.
    """
    print("\n--- Generating All Chronic Diseases Trend Plots ---")
    os.makedirs(result_dir, exist_ok=True)

    # Identify all unique trends (combinations of disease and unit)
    unique_trends = df_merged[['disease', 'unit']].drop_duplicates().to_records(index=False)

    # Loop through each unique trend and generate a plot
    for disease, unit in unique_trends:
        # Filter the merged data for this specific trend combination
        df_plot = df_merged.query(f"disease == '{disease}' and unit == '{unit}'").copy()

        if df_plot.empty:
            print(f"Skipping plot for {disease} ({unit}): No data found.")
            continue

        # Plot Generation
        plt.figure(figsize=(12, 6))

        for state in df_plot["state"].unique():
            df_state = df_plot[df_plot["state"] == state]
            plt.plot(df_state["year"], df_state["avg_prevalence_rate"], marker='o', label=state)

        # Create a safe file name
        file_name_safe = f"us_trend_{disease.replace(' ', '_').replace('/', '_')}_{unit.replace(' ', '_').replace('%', 'pct')}.png"
        plot_title = f"Trend of {disease} - {unit} (2019-2022)"

        plt.title(plot_title)
        plt.xlabel("Year")
        plt.ylabel(f"Average Prevalence Rate ({unit})")
        plt.legend(title="State")
        plt.grid(axis='y', linestyle='--')

        # Ensure all year ticks are visible
        plt.xticks(np.sort(df_plot["year"].unique()).astype(int))

        plt.tight_layout()
        if not notebook_plot:
            plt.savefig(f'{result_dir}/{file_name_safe}')
            print(f"Saved plot: {file_name_safe}")
            plt.close()
        else:
            plt.plot()

    print("All individual disease trend plots have been generated.")

def plot_global_comparison(df_merged, df_who, result_dir="results", notebook_plot=False):
    """
    Compares the U.S. PM2.5 average trend against the global PM2.5 average trend using the WHO data.
    :param df_merged: Merged U.S. dataframe.
    :param df_who: Cleaned global PM2.5 dataframe (from process_pm25_who).
    :param result_dir: directory to save plots.
    """
    print("\n--- Generating Global Comparison Plot ---")
    os.makedirs(result_dir, exist_ok=True)

    # Calculate U.S. National Mean PM2.5 (from the 5-state average)
    df_us_national = df_merged.groupby("year")["avg_pm25"].mean().reset_index().rename(columns={"avg_pm25": "US_PM25"})

    # Calculate Global Mean PM2.5
    # The df_who has columns: 'year', 'country', 'value'
    df_global = df_who.groupby("year")["value"].mean().reset_index().rename(columns={"value": "Global_PM25"})

    # Merge for consistent plotting over years
    df_compare = pd.merge(df_global, df_us_national, on="year", how="outer")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(df_compare["year"], df_compare["US_PM25"], marker='o', label="U.S. (5-State Average)", linewidth=2)
    plt.plot(df_compare["year"], df_compare["Global_PM25"], marker='s', label="Worldwide Average", linestyle='--',
             linewidth=2)

    plt.title("U.S. vs. Global PM2.5 Concentration Trends (2015-2022)")
    plt.xlabel("Year")
    plt.ylabel(r"Average PM2.5 Concentration ($\mu g/m^3$)")
    plt.legend()
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_compare["year"].unique())
    plt.tight_layout()
    if not notebook_plot:
        plt.savefig(f'{result_dir}/global_pm25_comparison.png')
        print(f"Saved Global PM2.5 Comparison plot to {result_dir}/global_pm25_comparison.png")
        plt.close()
    else:
        plt.plot()

def plot_disease_heatmap(df_merged, result_dir="results", notebook_plot=False):
    """
    Generates a heatmap of chronic disease prevalence by state and year.
    :param df_merged: Merged U.S. dataframe with 'state', 'year', and 'avg_disease_value' columns.
    :param result_dir: Directory to save plots.
    """
    print("\n--- Generating Chronic Disease Heatmap ---")
    os.makedirs(result_dir, exist_ok=True)

    # Pivot the DataFrame to get states as rows, years as columns, and avg_disease_value as values
    heatmap_data = df_merged.pivot_table(
        index="state",
        columns="year",
        values="avg_prevalence_rate"
    )

    plt.figure(figsize=(10, 7))
    sns.heatmap(
        heatmap_data,
        annot=True,  # Show the numerical values on the heatmap
        fmt=".1f",  # Format annotations to one decimal place
        cmap="YlGnBu",  # Choose a color map (e.g., Yellow-Green-Blue)
        linewidths=.5,  # Add lines between cells for better separation
        cbar_kws={'label': 'Average Disease Prevalence Rate'}  # Color bar label
    )

    plt.title("Chronic Disease Prevalence Rate by State and Year (2019-2022)")
    plt.xlabel("Year")
    plt.ylabel("State")
    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    if not notebook_plot:
        plt.savefig(f'{result_dir}/disease_heatmap.png')
        print(f"Saved Chronic Disease Heatmap to {result_dir}/disease_heatmap.png")
        plt.close()
    else:
        plt.plot()

def plot_correlation_bar_chart(correlation_results, result_dir='results', notebook_plot=False):
    """
    Creates a horizontal bar chart comparing Spearman correlation coefficients
    for different diseases, colored by statistical significance.
    """
    print("\n--- Generating Correlation Bar Chart ---")
    os.makedirs(result_dir, exist_ok=True)

    # Extract data from the results dictionary
    diseases = []
    rhos = []
    p_values = []

    for disease, stats in correlation_results.items():
        if stats['status'] == 'Success':
            diseases.append(disease)
            rhos.append(stats['rho'])
            p_values.append(stats['p_value'])

    # Setup colors based on significance (p < 0.05) and direction
    colors = []
    for r, p in zip(rhos, p_values):
        if p >= 0.05:
            colors.append('lightgray')  # Not significant
        else:
            colors.append('#d62728' if r > 0 else '#1f77b4')  # Red for positive, Blue for negative

    # Create the Plot
    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(diseases))
    bars = plt.barh(y_pos, rhos, color=colors, edgecolor='black')

    # Add vertical line at 0
    plt.axvline(0, color='black', linewidth=0.8)

    # Labels and Title
    plt.yticks(y_pos, diseases)
    plt.xlabel("Spearman Correlation Coefficient ($\\rho$)")
    plt.title("Correlation between PM2.5 and Chronic Disease Prevalence (2019-2022)")
    plt.xlim(-1, 1)  # Correlation is always between -1 and 1
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Add text labels to bars
    for i, bar in enumerate(bars):
        rho_text = f"{rhos[i]:.2f}"
        p_text = f"(p={p_values[i]:.3f})"

        # Position text slightly to the right/left of the bar
        x_pos = bar.get_width()
        plt.text(x_pos + (0.05 if x_pos >= 0 else -0.05), bar.get_y() + bar.get_height() / 2,
                 f"{rho_text} {p_text}", va='center', ha='left' if x_pos >= 0 else 'right', fontsize=9)

    # Add a custom legend
    legend_elements = [
        Patch(facecolor='#d62728', edgecolor='black', label='Significant Positive Correlation'),
        Patch(facecolor='#1f77b4', edgecolor='black', label='Significant Negative Correlation'),
        Patch(facecolor='lightgray', edgecolor='black', label='Not Significant (p >= 0.05)')
    ]
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 0.9), loc='upper right')

    plt.tight_layout()
    if not notebook_plot:
        plt.savefig(f'{result_dir}/correlation_summary_bar.png')
        print(f"Saved correlation bar chart to {result_dir}/correlation_summary_bar.png")
        plt.close()
    else:
        plt.plot()

def plot_correlation_scatters(df_merged, correlation_results, result_dir='results', notebook_plot=False):
    """
    Creates individual scatter plots for each disease vs PM2.5,
    annotated with the correlation stats.
    """
    print("\n--- Generating Individual Scatter Plot ---")
    os.makedirs(result_dir, exist_ok=True)

    # Filter for the analysis period
    df_analysis = df_merged[df_merged["year"] >= 2019].copy()

    for disease, stats in correlation_results.items():
        if stats['status'] != 'Success':
            continue

        rho = stats['rho']
        p_value = stats['p_value']

        # Filter data for this disease
        df_plot = df_analysis[df_analysis['disease'] == disease]

        plt.figure(figsize=(8, 6))

        # Create Scatter Plot with Regression Line
        # Use seaborn because it draws the confidence interval automatically
        sns.regplot(
            data=df_plot,
            x="avg_pm25",
            y="avg_prevalence_rate",
            scatter_kws={'s': 50, 'alpha': 0.7},
            line_kws={'color': 'red'}
        )

        # Title with Stats
        significance = "Significant" if p_value < 0.05 else "Not Significant"
        plt.title(f"{disease} vs. PM2.5 (2019-2022)\nSpearman $\\rho = {rho:.3f}$, p = {p_value:.3f} ({significance})")
        plt.xlabel("Average PM2.5 Concentration ($\\mu g/m^3$)")
        plt.ylabel("Age-adjusted Prevalence Rate (%)")
        plt.grid(True, linestyle='--', alpha=0.5)

        # Create a safe file name
        filename = f"scatter_pm25_vs_{disease.replace(' ', '_').replace(',', '')}.png"
        plt.tight_layout()
        if not notebook_plot:
            plt.savefig(f'{result_dir}/{filename}')
            print(f"Saved scatter plot: {filename}")
            plt.close()
        else:
            plt.plot()