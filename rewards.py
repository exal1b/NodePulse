import requests
import json
from datetime import datetime
import time
import os
from pytz import utc
from tzlocal import get_localzone
import threading
from config import BASE_DIRECTORY


class rewards(threading.Thread):
    def __init__(self, address, gui, root, file_path=None):
        super().__init__()  # Initialize threading
        self.address = address
        #self.api_key = api_key
        self.root = root
        self.gui = gui
        self.file_path = file_path or f"{address.replace(':', '_')}_transactions.json"
        self.file_path = os.path.join(BASE_DIRECTORY, self.file_path)  # Save within BASE_DIRECTORY

        # Ensure the directory exists
        os.makedirs(BASE_DIRECTORY, exist_ok=True)

        self.offset = 0
        self.all_processed_transactions = self.load_existing_data()
        self.stop_event = threading.Event()

    def load_existing_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return json.load(file)
        return []

    def save_data(self):
        with open(self.file_path, "w") as file:
            json.dump(self.all_processed_transactions, file, indent=4)

    def fetch_transaction_history(self):
        base_url = f"https://api.blockchair.com/ecash/dashboards/address/{self.address}"
        params = {"offset": self.offset}

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an error for HTTP errors
            data = response.json()

            if "data" in data and self.address in data["data"]:
                transactions = data["data"][self.address]["transactions"]
                print(transactions)
                return transactions
            else:
                print("Unexpected response format:", data)
                return None

        except requests.exceptions.RequestException as e:
            print("Error fetching data from Blockchair API:", e)
            return None

    def fetch_transaction_details_batch(self, tx_hashes):
        base_url = f"https://api.blockchair.com/ecash/dashboards/transactions/{','.join(tx_hashes)}"

        try:
            response = requests.get(base_url)
            response.raise_for_status()  # Raise an error for HTTP errors
            data = response.json()

            if "data" in data:
                print(data)
                return data["data"]
            else:
                print("Unexpected response format for transactions:", data)
                return {}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching details for transactions {tx_hashes}:", e)
            return {}

    def process_transactions(self, transactions):
        processed_data = []

        for i in range(0, len(transactions), 10):
            batch = transactions[i:i + 10]
            batch_data = self.fetch_transaction_details_batch(batch)

            for tx_hash in batch:
                tx_details = batch_data.get(tx_hash, {}).get("transaction", {})
                outputs = batch_data.get(tx_hash, {}).get("outputs", [])

                if tx_details:
                    is_coinbase = tx_details.get("is_coinbase", False)
                    block_height = tx_details["block_id"]  # Assume block_height always exists
                    timestamp = tx_details.get("time", None)

                    utc_time = datetime.fromisoformat(timestamp).replace(tzinfo=utc) if timestamp else None
                    local_timezone = get_localzone()
                    local_time = utc_time.astimezone(local_timezone) if utc_time else None

                    tx_value = sum(output["value"] for output in outputs) / 100

                    processed_data.append({
                        "tx_hash": tx_hash,
                        "is_coinbase": is_coinbase,
                        "block_height": block_height,
                        "local_time": local_time.strftime("%Y-%m-%d %H:%M:%S") if local_time else None,
                        "tx_value": tx_value,
                    })

        # Sort by block height in descending order
        return sorted(processed_data, key=lambda x: x["block_height"], reverse=True)

    def run(self):
        while not self.stop_event.is_set():
            transactions = self.fetch_transaction_history()
            if not transactions:
                print("No more transactions to fetch or an error occurred.")
                break

            processed_tx_hashes = {tx["tx_hash"] for tx in self.all_processed_transactions}
            new_transactions = [tx for tx in transactions if tx not in processed_tx_hashes]

            if not new_transactions:
                print("No new transactions to process.")
                break

            processed_transactions = self.process_transactions(new_transactions[:10])

            # Extend with sorted transactions
            self.all_processed_transactions.extend(processed_transactions)

            # Sort the full list again before saving or updating the GUI
            self.all_processed_transactions.sort(key=lambda x: x["block_height"], reverse=True)

            self.save_data()
            self.update_gui_treeview(self.all_processed_transactions)

            print(f"Processed transactions for {self.address} (offset {self.offset}):")
            print(json.dumps(processed_transactions, indent=4))

            if len(new_transactions) < 10:
                print("All transactions processed.")
                break

            self.offset += 10
            time.sleep(114)  # Wait 10 seconds before fetching the next set of transactions

        self.save_data()
        self.update_gui_treeview(self.all_processed_transactions)

        print("All transactions have been processed and saved.")
        self.stop()

    def stop(self):
        self.stop_event.set()

    def update_gui_treeview(self, my_rewards):
        if my_rewards:
            self.gui.update_treeview(my_rewards)