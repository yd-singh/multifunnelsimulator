import yaml
from modules import Module
import pandas as pd
from collections import deque
import os

class Funnel:
    def __init__(self, config_path):
        self.config_path = config_path  # Store config path for reference
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        self.modules = {}
        self.start_module = None
        for mod_conf in config['modules']:
            module = Module(
                name=mod_conf['name'],
                success_rate=mod_conf['success_rate'],
                cost_per_transaction=mod_conf['cost_per_transaction'],
                time_to_complete=mod_conf['time_to_complete'],
                next_module_on_success=mod_conf.get('next_module_on_success'),
                next_module_on_failure=mod_conf.get('next_module_on_failure'),
                is_parallel=mod_conf.get('is_parallel', False)
            )
            self.modules[module.name] = module
            if mod_conf.get('is_start', False):
                self.start_module = module

    def run_funnel(self, customers_count):
        total_tofu_customers = customers_count
        columns = [
            "Module", "Enter Funnel", "Success Rate", "Pass", "Fail",
            "Final Success", "Terminally Rejected", "Total Cost", "Total Time",
            "Average Cost per Customer", "Average Time per Customer"
        ]
        results = pd.DataFrame(columns=columns)
        data = []

        total_success = 0

        # Initialize processing queue
        processing_queue = deque()
        processing_queue.append((self.start_module, customers_count))

        while processing_queue:
            current_module, count = processing_queue.popleft()

            # Process the module
            result = current_module.process(count)
            last_row = result.iloc[-1]
            successful_count = int(last_row["Pass"])
            failed_count = int(last_row["Fail"])

            # Add terminally rejected or final successful customers
            if current_module.next_module_on_success == "Success":
                total_success += successful_count
            elif current_module.next_module_on_success and successful_count > 0:
                # Enqueue next module on success
                next_module = self.modules.get(current_module.next_module_on_success)
                if next_module:
                    processing_queue.append((next_module, successful_count))

            if current_module.next_module_on_failure == "Failed":
                pass  # Failures are terminally rejected
            elif current_module.next_module_on_failure and failed_count > 0:
                # Enqueue next module on failure
                next_module = self.modules.get(current_module.next_module_on_failure)
                if next_module:
                    processing_queue.append((next_module, failed_count))

            data.append(result)

        # Combine all module results into a single DataFrame
        results = pd.concat(data, ignore_index=True)

        # Calculate total cost and time
        total_cost = results["Total Cost"].sum()
        total_time = results["Total Time"].sum()

        # Calculate average cost and time per customer for the entire funnel
        average_cost_per_customer = total_cost / total_tofu_customers
        average_time_per_customer = total_time / total_tofu_customers

        # Convert total time and average time to minutes for readability
        total_time_minutes = total_time / 60
        average_time_per_customer_minutes = average_time_per_customer / 60

        # Prepare summary statistics
        total_failures = total_tofu_customers - total_success
        success_rate = (total_success / total_tofu_customers) * 100

        summary_stats = {
            'text': (
                f"- **Total Success:** {total_success}\n"
                f"- **Total Failures:** {total_failures}\n"
                f"- **Success Rate:** {success_rate:.2f}%\n"
                f"- **Total Cost:** ₹{total_cost:.2f}\n"
                f"- **Total Time:** {total_time_minutes:.2f} minutes\n"
                f"- **Average Cost per Customer:** ₹{average_cost_per_customer:.2f}\n"
                f"- **Average Time per Customer:** {average_time_per_customer_minutes:.2f} minutes"
            ),
            'metrics': {
                'Total Success': total_success,
                'Total Failures': total_failures,
                'Success Rate': success_rate,
                'Total Cost': total_cost,
                'Total Time': total_time_minutes,
                'Average Cost per Customer': average_cost_per_customer,
                'Average Time per Customer': average_time_per_customer_minutes
            }
        }

        # Print summary statistics to terminal
        print(f"Total Success: {total_success}")
        print(f"Total Failures: {total_failures}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Total Cost: ₹{total_cost:.2f}")
        print(f"Total Time: {total_time_minutes:.2f} minutes")
        print(f"Average Cost per Customer: ₹{average_cost_per_customer:.2f}")
        print(f"Average Time per Customer: {average_time_per_customer_minutes:.2f} minutes")

        return results, summary_stats