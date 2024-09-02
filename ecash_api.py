import requests
import threading
import tkinter as tk
from datetime import datetime, timedelta
from tzlocal import get_localzone
import pytz

class BlockchairAPI:
    def __init__(self, root, gui, base_url='https://api.blockchair.com/ecash/dashboards'):
        self.base_url = base_url
        self.root = root
        self.gui = gui
        self.initial_reward = True
        self.current_block = 0
        self.last_checked_block = 0
        self.rewards = None
        self.sorted_rewards = None
        self.last_check_time = 0

    def get_transaction_details(self, transaction_hash):
        url = f"{self.base_url}/transaction/{transaction_hash}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch transaction details. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching transaction details: {e}")
            return None

    def get_block_details(self, block_id):
        print("Get block details")
        url = f"{self.base_url}/block/{block_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch block details. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching block details: {e}")
            return None

    def is_coinbase_transaction(self, transaction_details):
        print("Is it a reward?")
        if transaction_details is None:
            return False
        transaction_data = transaction_details.get('data')
        if not transaction_data or len(transaction_data) == 0:
            return False
        transaction = list(transaction_data.values())[0].get('transaction')
        if not transaction:
            return False
        return transaction.get('is_coinbase', False)

    def get_utc_to_local_time(self, utc_time_str):
        print("Convert to local time")
        try:
            # Parse UTC time string
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")

            # Get the system's local timezone
            local_timezone = get_localzone()

            # Convert UTC to local time
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)

            return local_time.strftime("%Y-%m-%d %H:%M:%S")

        except ValueError as e:
            print(f"ValueError converting time: {e}")
            return None

    def create_coinbase_utxo_dict(self, utxos):
        coinbase_utxos = {}
        print("Create coinbase uxto")
        for utxo in utxos:
            transaction_hash = utxo['transaction_hash']
            block_id = utxo['block_id']
            value = utxo['value']

            transaction_details = self.get_transaction_details(transaction_hash)
            if self.is_coinbase_transaction(transaction_details):
                block_details = self.get_block_details(block_id)
                if block_details:
                    block_time_utc = block_details['data'].get(str(block_id), {}).get('block', {}).get('time')
                    block_height = block_details['data'].get(str(block_id), {}).get('block', {}).get('id')

                    if block_time_utc and block_height:
                        local_date_time = self.get_utc_to_local_time(block_time_utc)
                        if local_date_time:
                            coinbase_utxos[transaction_hash] = {
                                'local_date_time': local_date_time,
                                'block_height': block_height,
                                'amount': value
                            }

        return coinbase_utxos

    def update_treeview_main_thread(self, rewards):
        if self.gui.treeview:
            for item in self.gui.treeview.get_children():
                self.gui.treeview.delete(item)

            # Insert rewards into the Treeview
            if rewards:
                for tx_hash, details in rewards.items():
                    self.gui.treeview.insert(
                        "",
                        "end",
                        text=(details['local_date_time'][:16]),
                        values=(
                        "{:,}".format(details['block_height']), "{:,.2f}".format(float(details['amount'] / 100))))

    def update_treeview(self, rewards):
        # Ensure GUI updates are done in the main thread
        self.gui.root.after(0, self.gui.update_treeview_main_thread, rewards)

    def initial_rewards_request(self, address):
        print(address)
        print("last block " + str(self.current_block))
        url = f"{self.base_url}/address/{address}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            utxo_info = data.get('data', {}).get(address, {}).get('utxo', [])
            self.rewards = self.create_coinbase_utxo_dict(utxo_info)
            print(self.rewards)
            self.update_treeview(self.rewards)

        else:
            print(f"Failed to fetch address details. Status code: {response.status_code}")
            return None

    def threading_my_rewards(self, address, block_height):
        thread = threading.Thread(target=self.get_rewards, args=(address, block_height,))
        thread.start()

    def update_for_new_block(self, address, block_height):
        try:
            # Fetch block details
            response = requests.get(f"{self.base_url}/block/{block_height}")
            print(response.json())
            print(self.rewards)
            if response.status_code == 200:
                # Fetch the first transaction hash in the block
                first_transaction_hash = response.json()['data'][str(block_height)]['transactions'][0]

                try:
                    # Fetch transaction details
                    response = requests.get(f"{self.base_url}/transaction/{first_transaction_hash}")

                    if response.status_code == 200:
                        # Print the fetched transaction data
                        data = response.json()

                        # Iterate through each transaction in the 'data' dictionary
                        for transaction_id, transaction_data in data['data'].items():
                            # Check if the transaction has 'outputs' and iterate through them
                            if 'outputs' in transaction_data:
                                for output in transaction_data['outputs']:
                                    # Check if the recipient matches the specified recipient
                                    if output['recipient'] == address:
                                        # Check if the transaction is a coinbase transaction
                                        if transaction_data['transaction']['is_coinbase']:
                                            # Extract relevant information
                                            result = {
                                                'local_date_time': transaction_data['transaction']['time'],
                                                'block_height': transaction_data['transaction']['block_id'],
                                                'amount': output['value']
                                            }
                                            # Add the result to the rewards
                                            if transaction_id not in self.rewards:
                                                # Initialize an empty list for the new transaction_id
                                                self.rewards[transaction_id] = []
                                            # Append the result to the list associated with the transaction_id
                                            self.rewards[transaction_id].append(result)

                                            self.sorted_rewards = dict(sorted(self.rewards(), key=lambda x: x[1]['local_date_time'], reverse=True))
                                            self.update_treeview(self.rewards)

                                            # Popup message to the user
                                            formatted_reward = "{:,.2f}".format(float(result['amount'] / 100))
                                            self.new_reward_messagebox_main_thread(formatted_reward)

                                            print(self.rewards)
                                            return self.rewards

                    else:
                        print(f"Failed to fetch transaction details. Status code: {response.status_code}")

                except Exception as e:
                    print(f"Error fetching transaction details: {e}")

            else:
                print(f"Failed to fetch block details. Status code: {response.status_code}")

        except Exception as e:
            print(f"Error fetching block details: {e}")

    def get_rewards(self, address, block_height):
        if self.initial_reward is True:
            self.initial_reward = False
            self.last_checked_block = block_height
            self.last_check_time = datetime.now()
            self.initial_rewards_request(address)
            print(self.last_checked_block, self.initial_reward)
        elif block_height != self.last_checked_block and datetime.now() - self.last_check_time > timedelta(minutes=1.1):
            print(f"Updating my rewards (new block found #{self.last_checked_block + 1}")
            self.update_for_new_block(address, self.last_checked_block + 1)
            self.last_checked_block = self.last_checked_block + 1
            self.last_check_time = datetime.now()
        else:
            print("Too early to update my rewards")

    def new_reward_messagebox_main_thread(self, formatted_reward):
        # Ensure GUI updates are done in the main thread
        self.root.after(0, self.gui.new_reward_messagebox, formatted_reward)
