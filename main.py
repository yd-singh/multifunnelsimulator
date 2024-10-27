import os
import glob
from simulator import simulate_onboarding
import pandas as pd
from tabulate import tabulate

def main():
    customers_count = 100
    config_files = glob.glob('configs/*.yaml')
    all_results = []
    comparative_stats = []

    for config_file in config_files:
        print(f"\nRunning simulation for configuration: {config_file}")
        results_df, summary_stats = simulate_onboarding(customers_count, config_file)
        all_results.append((config_file, results_df, summary_stats))

        # Extract key statistics for comparison
        stats = summary_stats['metrics']
        stats['Configuration'] = os.path.basename(config_file)
        comparative_stats.append(stats)

        # Optionally, save individual results
        config_name = os.path.splitext(os.path.basename(config_file))[0]
        results_df.to_csv(f'results_{config_name}.csv', index=False)

    # Create a DataFrame for comparative statistics
    comparison_df = pd.DataFrame(comparative_stats)

    # Identify the best funnels based on criteria
    cheapest_funnel = comparison_df.loc[comparison_df['Total Cost'].idxmin()]
    fastest_funnel = comparison_df.loc[comparison_df['Total Time'].idxmin()]
    highest_success_funnel = comparison_df.loc[comparison_df['Success Rate'].idxmax()]

    # Generate a summary report in Markdown
    generate_summary_report(all_results, comparison_df, cheapest_funnel, fastest_funnel, highest_success_funnel)

    print("\nComparative summary report has been saved to 'comparative_summary.md'.")

def generate_summary_report(all_results, comparison_df, cheapest_funnel, fastest_funnel, highest_success_funnel):
    from tabulate import tabulate

    md_content = "# Comparative Onboarding Simulation Results\n\n"

    # Add comparative statistics table
    md_content += "## Comparative Statistics\n\n"
    comparison_table = comparison_df[[
        'Configuration', 'Success Rate', 'Total Cost', 'Total Time', 'Average Cost per Customer', 'Average Time per Customer'
    ]]
    md_content += tabulate(comparison_table, headers='keys', tablefmt='github', showindex=False)
    md_content += "\n\n"

    # Highlight the best funnels
    md_content += "## Best Performing Funnels\n\n"
    md_content += "### Cheapest Funnel\n\n"
    md_content += f"**Configuration:** {cheapest_funnel['Configuration']}\n\n"
    md_content += tabulate(cheapest_funnel.to_frame().T, headers='keys', tablefmt='github', showindex=False)
    md_content += "\n\n"

    md_content += "### Fastest Funnel\n\n"
    md_content += f"**Configuration:** {fastest_funnel['Configuration']}\n\n"
    md_content += tabulate(fastest_funnel.to_frame().T, headers='keys', tablefmt='github', showindex=False)
    md_content += "\n\n"

    md_content += "### Highest Success Rate Funnel\n\n"
    md_content += f"**Configuration:** {highest_success_funnel['Configuration']}\n\n"
    md_content += tabulate(highest_success_funnel.to_frame().T, headers='keys', tablefmt='github', showindex=False)
    md_content += "\n\n"

    # Append individual results
    for config_file, results_df, summary_stats in all_results:
        config_name = os.path.basename(config_file)
        md_content += f"## Results for {config_name}\n\n"
        md_content += "### Summary Statistics\n\n"
        md_content += f"{summary_stats['text']}\n\n"
        md_table = tabulate(results_df, headers='keys', tablefmt='github', showindex=False)
        md_content += "### Detailed Module Results\n\n"
        md_content += f"{md_table}\n\n"

    # Write the Markdown content to a file
    with open('comparative_summary.md', 'w') as f:
        f.write(md_content)

if __name__ == "__main__":
    main()
