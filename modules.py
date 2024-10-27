import pandas as pd

class Module:
    def __init__(
        self, name, success_rate, cost_per_transaction, time_to_complete,
        next_module_on_success=None, next_module_on_failure=None, is_parallel=False
    ):
        self.name = name
        self.success_rate = success_rate
        self.cost_per_transaction = cost_per_transaction
        self.time_to_complete = time_to_complete
        self.next_module_on_success = next_module_on_success
        self.next_module_on_failure = next_module_on_failure
        self.is_parallel = is_parallel

    def process(self, count):
        module = self.name
        enter_funnel = count
        success_rate = self.success_rate

        pass_count = int(round(self.success_rate * count))
        fail_count = count - pass_count

        # Calculate total cost and time
        total_cost = self.cost_per_transaction * enter_funnel
        total_time = self.time_to_complete * enter_funnel

        # Average cost and time per customer for this module
        average_cost_per_customer = self.cost_per_transaction
        average_time_per_customer = self.time_to_complete

        new_data = pd.DataFrame({
            "Module": [module],
            "Enter Funnel": [enter_funnel],
            "Success Rate": [f"{success_rate * 100:.0f}%"],
            "Pass": [pass_count],
            "Fail": [fail_count],
            "Final Success": [pass_count if self.next_module_on_success == "Success" else 0],
            "Terminally Rejected": [fail_count if self.next_module_on_failure == "Failed" else 0],
            "Total Cost": [total_cost],
            "Total Time": [total_time],
            "Average Cost per Customer": [average_cost_per_customer],
            "Average Time per Customer": [average_time_per_customer]
        })

        return new_data