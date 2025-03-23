from datetime import datetime, timedelta
import tkinter as tk
import time
from tkinter import ttk, messagebox
import paramiko
from rewards import rewards
import platform
import subprocess
import re
import threading
from ping3 import ping
#from rewards import My_rewards_function

class ServerConnector:
    def __init__(self, master, gui, root):
        self.master = master
        self.last_block_checked = 0
        self.root = root
        self.gui = gui
        self.saved_credentials = {}
        self.ssh_client = None
        self.loop_thread = None
        self.kill_switch = threading.Event()
        self.refresh_active = True
        self.node_output = {
                    'Selected Node': 'N/A',
                    'Server': 'N/A',
                    'Node': 'N/A',
                    'Chain': 'N/A',
                    'Headers': 'N/A',
                    'Blocks': 'N/A',
                    'Blockchain': 'N/A',
                    'Payout Address': 'N/A',
                    'Stake Amount': 'N/A',
                    'Proof': 'N/A',
                    'Staking': 'N/A',
                    'Last Refresh': 'N/A',
                    'Ping': 'N/A'
                }

        self.rewards = rewards(
            address=self.node_output['Payout Address'],
            gui=self.gui,            # Pass the GUI instance
            root=self.root           # Pass the root instance
        )
        self.current_rewards_thread = None
        self.retry_count = 0

    def update_selected_node(self, selected_node):
        self.node_output['Selected Node'] = selected_node
        self.gui.update_info(self.node_output)

    def initial_rewards_fetcher(self, address, block_height):
        self.api.threading_my_rewards(address, block_height)

    def connect_to_server(self, hostname, port, username, password):
        self.saved_credentials['hostname'] = hostname
        self.saved_credentials['port'] = port
        self.saved_credentials['username'] = username
        self.saved_credentials['password'] = password
        print("connecting to server")
        list_command = "ls -d bitcoin-abc*/"
        output = self.connect_and_execute_commands([list_command])

        if output:
            self.retry_count = 0
            self.node_output['Server'] = "Connected"
            self.gui.update_info(self.node_output)
            result = output[list_command]
            directories = [line.rstrip('/') for line in result['stdout'].split('\n') if not line.endswith('.tar.gz') and line]

            if len(directories) > 1:
                self.gui.create_select_node_window(directories)

            else:
                self.node_output['Selected Node'] = directories[-1]
                self.node_output['Node'] = 'Connected'
                self.gui.update_info(self.node_output)
                print(self.node_output['Selected Node'])
                self.connect_to_node()

    def connect_and_execute_commands(self, commands):
        ssh_client = None
        try:
            # Test ping
            self.node_output['Ping'] = self.measure_latency(self.saved_credentials['hostname'])
            print(f"Ping result: {self.node_output['Ping']}")

            print("Executing commands via SSH...")

            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the server with a timeout
            ssh_client.connect(
                hostname=self.saved_credentials['hostname'],
                port=self.saved_credentials['port'],
                username=self.saved_credentials['username'],
                password=self.saved_credentials['password'],
                timeout=10
            )

            output = {}
            for command in commands:
                stdin, stdout, stderr = ssh_client.exec_command(command)
                output[command] = {
                    'stdout': stdout.read().decode().strip(),
                    'stderr': stderr.read().decode().strip()
                }

            # Reset retry count on successful connection
            self.retry_count = 0

            return output

        except paramiko.AuthenticationException:
            messagebox.showerror("Error", "Authentication failed, please check your credentials.")
        except (EOFError, paramiko.SSHException) as ssh_ex:
            print(f"SSH error: {ssh_ex}")
            self.retry_logic()
        except Exception as ex:
            print(f"Unexpected error: {ex}")
            self.retry_logic()
        finally:
            if ssh_client:
                ssh_client.close()

    def retry_logic(self):
        """Handle retry logic for connection attempts."""
        if self.retry_count < 30:
            self.node_output['Server'] = 'Disconnected'
            self.node_output['Node'] = 'N/A'
            self.node_output['Chain'] = 'N/A'
            self.node_output['Headers'] = 'N/A'
            self.node_output['Blocks'] = 'N/A'
            self.node_output['Blockchain'] = 'N/A'
            self.node_output['Proof'] = 'N/A'
            self.node_output['Staking'] = 'N/A'
            self.node_output['Payout Address'] = 'N/A'
            self.node_output['Stake Amount'] = 'N/A'
            self.gui.update_info(self.node_output)
            self.retry_count += 1
            if self.retry_count == 1:
                threading.Thread(
                    target=lambda: messagebox.showinfo(
                        "Information", f"Connection error, NodePulse will attempt to connect again repeatedly for 5 minutes"
                    )
                ).start()
            print(f"Retry attempt {self.retry_count} after 10 seconds.")
            self.gui.start_count_down()
        else:
            print("Maximum retry attempts reached. Stopping further retries.")
            threading.Thread(
                target=lambda: messagebox.showinfo(
                    "Information", f"Connection error, Maximum retry attempts reached. Stopping further retries."
                )
            ).start()

    def connect_to_node(self):
        if not self.refresh_active:
            print("Refresh loop stopped.")
            return  # Exit the loop if the kill switch is triggered

        command1 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin-cli getblockchaininfo"
        command2 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin-cli getavalancheinfo"

        output = self.connect_and_execute_commands([command1, command2]
        )

        #print(output)

        for command_output in output.values():
            if "Make sure the bitcoind server is running" in command_output['stderr']:
                #print("Node is off")
                self.node_output['Server'] = 'Connected'
                self.node_output['Node'] = 'Off'
                self.node_output['Chain'] = 'N/A'
                self.node_output['Headers'] = 'N/A'
                self.node_output['Blocks'] = 'N/A'
                self.node_output['Blockchain'] = 'N/A'
                self.node_output['Proof'] = 'N/A'
                self.node_output['Staking'] = 'N/A'
                self.node_output['Payout Address'] = 'N/A'
                self.node_output['Stake Amount'] = 'N/A'

                self.gui.update_info(self.node_output)

                self.root.after(
                    10000,
                    self.connect_to_server,
                    self.saved_credentials['hostname'],
                    self.saved_credentials['port'],
                    self.saved_credentials['username'],
                    self.saved_credentials['password']
                )

                return
            else:
                print("Node is on")
                self.node_output['Server'] = 'Connected'
                self.node_output['Node'] = "Connected"

        filtered_lines_command1 = []
        filtered_lines_command2 = []

        if output:

            for command, result in output.items():
                stdout_lines = result['stdout'].split('\n')
                if command == command1:
                    filtered_lines_command1 = stdout_lines  # Capture all lines for command1
                else:
                    filtered_lines_command2 = stdout_lines  # Capture all lines for command2


            # Check to be deleted

            print(f"Command1 output:")
            for line in filtered_lines_command1:
                print(line)

            print(f"\nCommand2 output:")
            for line in filtered_lines_command2:
                print(line)

            # Server info
            self.node_output['Server'] = "Connected"

            # Chain info
            self.node_output["Chain"] = filtered_lines_command1[1][11:].replace(",", "").replace('"', '').replace(':', '').capitalize()

            # Blockchain info
            self.node_output["Headers"] = int(filtered_lines_command1[3][13:].replace(",", "").replace('"', '').replace(':', ''))
            self.node_output["Blocks"] = int(filtered_lines_command1[2][12:].replace(",", "").replace('"', '').replace(':', ''))

            #self.api.current_block = self.node_output["Blocks"]
            #print("last block " + str(self.api.current_block))

            if self.node_output["Blocks"] == self.node_output["Headers"]:
                self.node_output["Blockchain"] = "Synced"
            else:
                self.node_output["Blockchain"] = "Syncing"

            # Payout address info
            self.node_output["Payout Address"] = "ecash:" + filtered_lines_command2[7][28:].replace(",", "").replace('"', '').replace(':', '')

            # Stake amount info
            self.node_output["Stake Amount"] = "{:,.2f}".format(float(filtered_lines_command2[8][17:].replace(",", "").replace('"', '').replace(':', '')))

            # Proof info
            if filtered_lines_command2[3][16:].replace(",", "").replace('"', '').replace(':', '') == "true":
                self.node_output["Proof"] = "Verified"
            else:
                self.node_output["Proof"] = "Unverified"

            # Staking info
            if filtered_lines_command2[1][19:].replace(",", "").replace('"', '').replace(':', '') == "true":
                self.node_output["Staking"] = "Activated"
            elif self.node_output["Proof"] == "Verified":
                self.node_output["Staking"] = "Awaiting block"
            else:
                self.node_output["Proof"] = "Not activated"

            # Last refresh time
            self.node_output['Last Refresh'] = self.last_refresh_time()

            print(self.node_output)

            # Update GUI with node output
            self.gui.update_info(self.node_output)

            if self.last_block_checked != self.node_output['Blocks']:
                self.start_rewards_processing(self.node_output["Payout Address"])
                self.last_block_checked = self.node_output['Blocks']
            else:
                print("Waiting for new block before updating rewards")

            self.gui.start_count_down()

    def start_the_node(self):
        print("starting node: " + self.node_output['Selected Node'])
        print("Starting the node with credentials:", self.saved_credentials)
        command1 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoind -daemon"

        output = self.connect_and_execute_commands([command1])

        if "Bitcoin ABC starting" in str(output):
            messagebox.showinfo("Success", f"Your {self.node_output['Selected Node']} node is starting")
            self.refresh_active = True  # Reactivate the refresh loop
            self.gui.start_count_down()
        else:
            messagebox.showerror("Error", "Could not start the node")

    def stop_the_node(self):
        # Trigger the kill switch
        print("Stopping the refresh loop to stop the node.")
        self.refresh_active = False

        # Execute stop logic
        if not self.saved_credentials:
            messagebox.showerror("Error", "Credentials are not set.")
            return

        print("Stopping the node...")
        command = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin-cli stop"
        output = self.connect_and_execute_commands([command])

        if "Bitcoin ABC stopping" in str(output):
            messagebox.showinfo("Success", f"{self.node_output['Selected Node']} node is stopping.")
            self.node_output['Server'] = 'Connected'
            self.node_output['Node'] = 'Off'
            self.node_output['Chain'] = 'N/A'
            self.node_output['Headers'] = 'N/A'
            self.node_output['Blocks'] = 'N/A'
            self.node_output['Blockchain'] = 'N/A'
            self.node_output['Proof'] = 'N/A'
            self.node_output['Staking'] = 'N/A'
            self.node_output['Payout Address'] = 'N/A'
            self.node_output['Stake Amount'] = 'N/A'
            self.gui.update_info(self.node_output)
        else:
            messagebox.showerror("Error", "Could not stop the node.")

    def check_and_create_file(self):
        print("stage 2")
        self.remote_path = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin.conf"
        output = self.connect_and_execute_commands(commands)
        if output[commands[0]]['stderr']:
            raise Exception(f"Error while checking/creating the file: {output[commands[0]]['stderr']}")

    def fetch_file(self):
        print("stage 3")
        self.ssh_connect()
        sftp = self.ssh_client.open_sftp()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                sftp.get(self.remote_path, temp_file.name)
            except FileNotFoundError:
                open(temp_file.name, 'w').close()  # Create an empty local file if the remote file does not exist
            temp_file_path = temp_file.name
        sftp.close()
        return temp_file_path

    def push_file(self, local_path):
        sftp = self.ssh_client.open_sftp()
        sftp.put(local_path, self.remote_path)
        sftp.close()

    def load_file(self):
        try:
            print("stage 1")
            self.check_and_create_file()
            temp_file_path = self.fetch_file()
            with open(temp_file_path, 'r') as file:
                content = file.read()
            return content
            #self.text_area.delete(1.0, tk.END)
            #self.text_area.insert(tk.INSERT, content)
            os.remove(temp_file_path)
        except Exception as e:
            messagebox.showerror("Error 1", str(e))
            if self.ssh_client:
                self.ssh_client.close()

    def save_file(self, content):
        try:
            temp_file_path = tempfile.mktemp()
            with open(temp_file_path, 'w') as file:
                file.write(content)
            self.push_file(temp_file_path)
            os.remove(temp_file_path)
            messagebox.showinfo("Success", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.ssh_client.close()
        self.ssh_client = None

    def ssh_connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(
            hostname=self.saved_credentials['hostname'],
            port=self.saved_credentials['port'],
            username=self.saved_credentials['username'],
            password=self.saved_credentials['password']
        )

    def start_rewards_processing(self, address):
        if self.current_rewards_thread and self.current_rewards_thread.is_alive():
            print("Rewards processing is still running. Please wait.")
            return

        # Initialize and start the Rewards thread
        self.current_rewards_thread = rewards(
            address=address,
            gui=self.gui,  # Pass the GUI instance
            root=self.root  # Pass the root instance
        )
        self.current_rewards_thread.start()
        print(f"Started rewards processing for address: {address}")

    def stop_rewards_processing(self):
        if self.current_rewards_thread:
            self.current_rewards_thread.stop()
            self.current_rewards_thread.join()  # Wait for the thread to finish
            print("Rewards processing has been stopped.")

    def check_rewards_status(self):
        if self.current_rewards_thread and self.current_rewards_thread.is_alive():
            print("Rewards processing is still running.")
        else:
            print("Rewards processing has finished or has not started.")

    def last_refresh_time(self):
        # Get the local time adjusted for DST
        local_time = time.localtime()

        # Format the time and date
        formatted_time = time.strftime("%H:%M:%S  %d-%m-%Y", local_time)

        print(f"Local Date and Time: {formatted_time}")
        return formatted_time

    def measure_latency(self, ip):
        try:
            response_time = ping(ip, timeout=2)  # Timeout in seconds
            if response_time is None:
                return "Host unreachable"
            else:
                return f"{response_time * 1000:.0f}ms"  # Convert to milliseconds
        except Exception as e:
            return "N/A"

    def start_loop(self):
        if self.loop_thread and self.loop_thread.is_alive():
            print("Loop is already running.")
            return

        print("Starting the node refresh loop.")
        self.kill_switch.clear()
        self.loop_thread = threading.Thread(target=self.refresh_loop, daemon=True)
        self.loop_thread.start()

    def refresh_loop(self):
        while not self.kill_switch.is_set():
            self.connect_to_node()
            print("Node data refreshed.")
            for _ in range(100):  # Countdown in 100 steps (10 seconds)
                if self.kill_switch.is_set():
                    print("Loop interrupted.")
                    return
                time.sleep(0.1)  # Adjust based on your countdown intervals

    def stop_loop(self):
        if not self.loop_thread or not self.loop_thread.is_alive():
            print("Loop is not running.")
            return

        print("Stopping the node refresh loop.")
        self.kill_switch.set()
        self.loop_thread.join()  # Wait for the loop thread to finish

    def restart_loop(self):
        print("Restarting the node refresh loop.")
        self.stop_loop()
        self.start_loop()