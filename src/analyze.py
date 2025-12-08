import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import spearmanr
import statsmodels.formula.api as smf

def mixed_effects_model(df_merged_us):
    print("\n--- Performing Mixed-Effects Models ---")

    df = df_merged_us.copy()
    df = df.dropna(subset=["avg_pm25", "avg_prevalence", "state", "year", "disease"])
    df = df.rename(columns={"avg_prevalence": "prevalence", "avg_pm25": "pm25"})
    df["year"] = df["year"].astype(int)

    results_per_disease = {}

    # ============================================================
    # 1. GLOBAL MODEL — all diseases combined
    # ============================================================
    print("\n================ GLOBAL MIXED MODEL ================")
    try:
        global_model = smf.mixedlm(
            formula="prevalence ~ pm25 + C(disease) + year",
            data=df,
            groups=df["state"],  # random intercept per state
            re_formula="~1"
        )
        global_fit = global_model.fit(reml=False, method="lbfgs")
        print(global_fit.summary())

    except Exception as e:
        print("\nGlobal model failed:", e)

    # ============================================================
    # 2. PER-DISEASE MODELS
    # ============================================================
    print("\n================ PER-DISEASE MODELS ================")

    for disease in sorted(df["disease"].unique()):
        sub = df[df["disease"] == disease]

        print(f"\n--- {disease} ---")

        if len(sub) < 8:
            print(f"Skipped: Too few rows ({len(sub)})")
            continue

        try:
            model = smf.mixedlm(
                formula="prevalence ~ pm25 + year",
                data=sub,
                groups=sub["state"],
                re_formula="~1"
            )
            fit = model.fit(reml=False, method="lbfgs")

            results_per_disease[disease] = fit
            print(fit.summary())

        except Exception as e:
            print(f"Model failed for {disease}: {e}")

    # ============================================================
    # 3. Extract PM2.5 coefficients for forest plot
    # ============================================================
    rows = []
    for disease, model in results_per_disease.items():
        if "pm25" not in model.params:
            continue

        coef = model.params["pm25"]
        se = model.bse["pm25"]
        rows.append({
            "disease": disease,
            "coef_pm25": coef,
            "se_pm25": se,
            "lower": coef - 1.96 * se,
            "upper": coef + 1.96 * se,
        })

    return pd.DataFrame(rows)

def calculate_correlation(df_merged_us):
    """
    Calculates the Spearman correlation coefficient (r) and p-value between PM2.5 and
    the targeted chronic diseases over the overlapping 2019-2022 period.
    :param df_merged_us: dataframe with 'avg_pm25' and 'avg_prevalence' columns.
    :return: dict where keys are disease names and values are {'rho', 'p_value', 'status'}
    """
    from config import TARGET_DISEASE, MIN_SAMPLE_SIZE

    print("--- Performing Correlation Analysis ---")

    results = {}
    for disease in TARGET_DISEASE:
        # Filter for only the target diseases and create a copy
        df_target = df_merged_us.query(f"disease == '{disease}'").copy()

        # Drop any rows where either PM2.5 or prevalence rate is missing
        df_target_clean = df_target.dropna(subset=["avg_pm25", "avg_prevalence"])

        if len(df_target_clean) < MIN_SAMPLE_SIZE:
            print(
                f"Skipping {disease}: Insufficient data for meaningful correlation after cleaning ({len(df_target_clean)} points).")
            results[disease] = {"rho": None, "p_value": None, "status": "Insufficient Data"}
            continue

        # Use scipy.stats.spearmanr for both correlation coefficient and p-value
        r, p_value = spearmanr(df_target_clean["avg_pm25"], df_target_clean["avg_prevalence"])
        results[disease] = {
            "rho": r,
            "p_value": p_value,
            "status": "Success"
        }
        print(f"Results for {disease} Rate vs. PM2.5: rho = {r:.4f}, P-Value = {p_value:.4f}")
    return results

def set_font_style():
    # Set the font family to 'sans-serif'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Times New Roman', 'DejaVu Sans', 'Arial']
    plt.rcParams['font.weight'] = 'medium'

class PlottingTool:
    """
    Manage common plotting setup, saving, and cleanup logic.
    """
    def __init__(self, result_dir="results", notebook_plot=False):
        self.result_dir = result_dir
        self.notebook_plot = notebook_plot
        os.makedirs(self.result_dir, exist_ok=True)
        set_font_style()

    def _save_plot(self, file_name_safe, plot_context_message="Plot"):
        # Handles saving or showing the plot based on the run environment.
        plt.tight_layout()
        if not self.notebook_plot:
            save_path = f'{self.result_dir}/{file_name_safe}'
            plt.savefig(save_path)
            print(f"Saved {plot_context_message} plot to {save_path}")
            plt.close()
        else:
            plt.show()

    @staticmethod
    def _sanitize_filename(name, suffix):
        # Creates a safe filename from a string.
        return f"{name.replace(' ', '_').replace('/', '_').replace(',', '')}{suffix}"

def plot_us_trends(df_merged, result_dir="results", notebook_plot=False):
    """
    Generates time series plots showing PM2.5 and chronic disease trends for all 5 U.S. states.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating U.S. Trend Plots ---")

    # Plot 1: Chronic disease trend by state
    plt.figure(figsize=(12, 6))
    for state in df_merged["state"].unique():
        df_state = df_merged[df_merged["state"] == state]
        plt.plot(df_state["year"], df_state["avg_prevalence"], marker='o', label=state)

    plt.title("U.S. Chronic Disease Prevalence Rate Trend (2015-2022)", fontsize=20)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Average Disease Prevalence Rate", fontsize=14)
    plt.legend(title="State", fontsize=16)
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_merged["year"].unique().astype(int))
    plt.tick_params(axis='both', which='major', labelsize=16)
    tool._save_plot('us_disease_trends.png', "U.S. Chronic Disease Trend")

    # Plot 2: PM2.5 trend by state
    plt.figure(figsize=(12, 6))
    for state in df_merged["state"].unique():
        df_state = df_merged[df_merged["state"] == state]
        df_state_unique_pm25 = df_state.groupby('year').agg({'avg_pm25': 'mean'}).reset_index() # Remove redundant year entries if PM2.5 data was duplicated during merge
        plt.plot(df_state_unique_pm25["year"], df_state_unique_pm25["avg_pm25"], marker='o', label=state)

    plt.title("U.S. PM2.5 Concentration Trend", fontsize=20)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel(r"Avg. PM2.5 Concentration ($\mu g/m^3$)", fontsize=14)
    plt.legend(title="State", fontsize=16)
    plt.grid(axis='y', linestyle='--')
    plt.xticks(df_merged["year"].unique().astype(int))
    plt.tick_params(axis='both', which='major', labelsize=16)
    tool._save_plot('us_pm25_trends.png', "U.S. PM2.5 Trend")

def plot_all_chronic_trends(df_merged, result_dir='results', notebook_plot=False):
    """
    Generates a line plot for the time trend of each unique (disease, unit)
    combination in the merged U.S. dataset, showing a separate line for each state.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating All Chronic Diseases Trend Plots ---")

    # Identify all unique trends (combinations of disease and unit)
    unique_trends = df_merged[['disease', 'unit']].drop_duplicates().to_records(index=False)

    # Loop through each unique trend and generate a plot
    for disease, unit in unique_trends:
        # Filter the merged data for this specific trend combination
        df_plot = df_merged.query(f"disease == '{disease}' and unit == '{unit}'").copy()

        if df_plot.empty:
            print(f"Skipping plot for {disease} ({unit}): No data found.")
            continue

        plt.figure(figsize=(8, 6))
        for state in df_plot["state"].unique():
            df_state = df_plot[df_plot["state"] == state]
            plt.plot(df_state["year"], df_state["avg_prevalence"], marker='o', label=state)

        # Create a safe file name
        file_name_safe = tool._sanitize_filename(f"us_trend_{disease}_{unit}", ".png")
        plt.title(f"Trend of {disease} - {unit}", fontsize=20)
        plt.xlabel("Year", fontsize=14)
        plt.ylabel(f"Average Prevalence Rate ({unit})", fontsize=14)
        plt.legend(
            title="State",
            fontsize=16,
            loc='center left',  # Anchor the legend's left edge
            bbox_to_anchor=(1.0, 0.5)  # Position it just right of the plot boundary (1.0) and center vertically (0.5)
        )
        plt.grid(axis='y', linestyle='--')
        plt.xticks(np.sort(df_plot["year"].unique()).astype(int))
        plt.tick_params(axis='both', which='major', labelsize=16)

        tool._save_plot(file_name_safe, f"Trend plot for {disease}")

def plot_grouped_bar_charts(df_merged, result_dir='results', notebook_plot=False):
    """
    Generates a grouped bar chart for each disease, showing Avg. Prevalence Rate by State, grouped by Year.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating Grouped Bar Charts ---")

    # Ensure 'year' is treated as a category for grouping
    df_merged['year'] = df_merged['year'].astype(str)

    diseases = df_merged['disease'].unique()
    for disease in diseases:
        df_plot = df_merged[df_merged['disease'] == disease].copy()

        # Check for empty data before plotting
        if df_plot.empty or df_plot['avg_prevalence'].dropna().empty:
            print(f"Skipping grouped bar chart for {disease}: No valid data.")
            continue

        fig, ax = plt.subplots(figsize=(10, 6))

        # Use seaborn.barplot for clustered bars
        sns.barplot(
            data=df_plot,
            x='state',
            y='avg_prevalence',
            hue='year',
            palette='viridis',
            ax=ax
        )

        ax.set_title(f'Avg. Prevalence Rate by State and Year: {disease}', fontsize=20)
        ax.set_xlabel('State', fontsize=12)
        ax.set_ylabel('Avg. Prevalence Rate (%)', fontsize=14)

        ax = plt.gca()
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.legend(
            title='Year',
            loc='center left',  # Align the legend box's left edge to the anchor
            bbox_to_anchor=(1.0, 0.5),  # Move the legend box slightly right (1.0) and center it vertically (0.5)
            fancybox=True,
            shadow=True,
            fontsize=14,
            ncol=1  # Ensure legend items stack vertically
        )
        plt.xticks(rotation=45, ha='right')

        safe_disease_name = tool._sanitize_filename(disease, "")
        tool._save_plot(f'grouped_bar_{safe_disease_name}.png', f"Grouped Bar Chart for {disease}")

def plot_global_comparison(df_pm25_us_agg, df_global_agg, result_dir="results", notebook_plot=False):
    """
    Compares the U.S. PM2.5 average trend against the global PM2.5 average trend using the WHO data.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating Global Comparison Plot ---")

    # Calculate U.S. National Mean PM2.5 (from the 5-state average)
    df_us = df_pm25_us_agg.groupby("year")["avg_pm25"].mean().reset_index().rename(columns={"avg_pm25": "US_PM25"})
    df_us['year'] = pd.to_numeric(df_us['year'], errors='coerce').astype('Int64')

    # Global Mean PM2.5
    df_global = df_global_agg.copy()
    df_global['year'] = pd.to_numeric(df_global['year'], errors='coerce').astype('Int64')

    # Merge for consistent plotting over years
    df_compare = pd.merge(df_global, df_us, on="year", how="outer")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(df_compare["year"], df_compare["US_PM25"], marker='o', label="U.S. (5-State Average)", linewidth=2)
    plt.plot(df_compare["year"], df_compare["Global_PM25"], marker='s', label="Worldwide Average", linestyle='--', linewidth=2)

    plt.title("U.S. vs. Global PM2.5 Concentration Trends", fontsize=20)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel(r"Avg. PM2.5 Concentration ($\mu g/m^3$)", fontsize=14)
    plt.legend(fontsize=16)
    plt.grid(axis='y', linestyle='--')

    plt.xticks(df_compare["year"].unique())
    plt.tick_params(axis='both', which='major', labelsize=16)

    tool._save_plot('global_pm25_comparison.png', "Global PM2.5 Comparison")

def plot_disease_heatmap(df_merged, result_dir="results", notebook_plot=False):
    """
    Generates a heatmap of chronic disease prevalence by state and year.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating Chronic Disease Heatmap ---")

    # Pivot the DataFrame to get states as rows, years as columns, and avg_disease_value as values
    heatmap_data = df_merged.pivot_table(
        index="state",
        columns="year",
        values="avg_prevalence"
    )

    plt.figure(figsize=(10, 7))
    ax = sns.heatmap(
        heatmap_data,
        annot=True,  # Show the numerical values on the heatmap
        fmt=".1f",  # Format annotations to one decimal place
        cmap="YlGnBu",  # Choose a color map (e.g., Yellow-Green-Blue)
        linewidths=.5,  # Add lines between cells for better separation
        cbar_kws={'label': 'Average Chronic Disease Prevalence'},  # Color bar label
        annot_kws = {"fontsize": 14}
    )
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_size(16)
    cbar.ax.tick_params(labelsize=14)

    plt.title("Chronic Disease Prevalence Rate by State and Year", fontsize=20)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("State", fontsize=12)
    ax = plt.gca()
    ax.tick_params(axis='both', which='major', labelsize=16)

    tool._save_plot('disease_heatmap.png', "U.S. Chronic Disease Heatmap")

def plot_correlation_bar_chart(correlation_results, result_dir='results', notebook_plot=False):
    """
    Creates a horizontal bar chart comparing Spearman correlation coefficients
    for different diseases, colored by statistical significance.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating Correlation Bar Chart ---")

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
    plt.yticks(y_pos, diseases, fontsize=14)
    plt.xlabel("Spearman Correlation Coefficient ($\\rho$)", fontsize=14)
    plt.title("Correlation between PM2.5 and Chronic Disease Prevalence", fontsize=20)
    plt.xlim(-1, 1)  # Correlation is always between -1 and 1
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Add text labels to bars
    for i, bar in enumerate(bars):
        rho_text = f"{rhos[i]:.2f}"
        p_text = f"(p={p_values[i]:.3f})"

        # Position text slightly to the right/left of the bar
        x_pos = bar.get_width()
        plt.text(x_pos + (0.05 if x_pos >= 0 else -0.05), bar.get_y() + bar.get_height() / 2,
                 f"{rho_text} {p_text}", va='center', ha='left' if x_pos >= 0 else 'right', fontsize=12)

    # Add a custom legend
    legend_elements = [
        Patch(facecolor='#d62728', edgecolor='black', label='Significant Positive Correlation'),
        Patch(facecolor='#1f77b4', edgecolor='black', label='Significant Negative Correlation'),
        Patch(facecolor='lightgray', edgecolor='black', label='Not Significant (p >= 0.05)')
    ]
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.1, 0.9), loc='upper right')

    tool._save_plot('correlation_summary_bar.png', "Correlation Bar Chart")

def plot_correlation_scatters(df_merged, correlation_results, result_dir='results', notebook_plot=False):
    """
    Creates individual scatter plots for each disease vs PM2.5,
    annotated with the correlation stats.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating Individual Scatter Plot ---")

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
        sns.regplot(
            data=df_plot,
            x="avg_pm25",
            y="avg_prevalence",
            scatter_kws={'s': 50, 'alpha': 0.7},
            line_kws={'color': 'red'}
        )

        # Title with Stats
        significance = "Significant" if p_value < 0.05 else "Not Significant"
        plt.title(f"{disease} vs. PM2.5\nSpearman $\\rho = {rho:.3f}$, p = {p_value:.3f} ({significance})", fontsize=20 )
        plt.xlabel("Average PM2.5 Concentration ($\\mu g/m^3$)", fontsize=16)
        plt.ylabel("Age-adjusted Prevalence Rate (%)", fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.5)

        filename = tool._sanitize_filename(f"scatter_pm25_vs_{disease}", ".png")
        tool._save_plot(filename, f"Scatter plot for {disease}")

def plot_mixed_effects_forest(df_me, result_dir='results', notebook_plot=False):
    """
    Generates a forest plot visualizing the estimated PM2.5 effect
    (coefficient and 95% confidence interval) for each disease from a
    mixed-effects model.
    """
    tool = PlottingTool(result_dir, notebook_plot)
    print("\n--- Generating Mixed-Effects Forest Plot ---")

    # Sort data by the coefficient magnitude for better visualization
    df_plot = df_me.sort_values("coef_pm25")

    # Determine significance: Confidence Interval does not cross zero OR p_value < alpha
    df_plot['is_significant'] = (df_plot['lower'] > 0) | (df_plot['upper'] < 0)

    # Define colors
    point_colors = np.where(df_plot['is_significant'], 'red', 'gray')
    line_colors = np.where(df_plot['is_significant'], 'red', 'lightgray')

    # Points (the coefficient estimate)
    plt.figure(figsize=(11, 8))

    # Error bars
    plt.hlines(
        y=df_plot["disease"],
        xmin=df_plot["lower"],
        xmax=df_plot["upper"],
        linewidth=3,
        color=line_colors,
        alpha=0.7
    )
    plt.scatter(df_plot["coef_pm25"], df_plot["disease"], s=100, color=point_colors, zorder=5)

    # Add Text Annotations (Coefficient Value)
    for i, row in df_plot.iterrows():
        x_pos = row['upper'] + 0.02
        label = f"{row['coef_pm25']:.3f}"
        if row['is_significant']:
            label += ' *'  # Add asterisk to highlight significance

        plt.text(
            x_pos,
            row['disease'],
            label,
            verticalalignment='center',
            fontsize=11,
            color=point_colors[df_plot.index.get_loc(i)],
            fontweight='bold' if row['is_significant'] else 'normal'
        )

    # Vertical reference line
    plt.axvline(0, linestyle="--", color='black', alpha=0.7, linewidth=1.5)

    plt.xlabel("Effect of PM2.5 on Age-Adjusted Prevalence", fontsize=14)
    plt.ylabel("Disease", fontsize=14)
    plt.title("Mixed-Effects Model: PM2.5 Effect Across Diseases (95% CI)", fontsize=18)

    # Add ticks and style (using the global settings applied by PlottingTool)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(axis='x', linestyle=':', alpha=0.6)

    tool._save_plot('mixed_effects_forest_plot.png', "Mixed-Effects Forest")