from funnel import Funnel

def simulate_onboarding(customers_count, config_path):
    funnel = Funnel(config_path)
    results, summary_stats = funnel.run_funnel(customers_count)
    return results, summary_stats