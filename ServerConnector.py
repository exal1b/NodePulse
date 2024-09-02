from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
from ecash_api import BlockchairAPI
from rewards import My_rewards_function

class ServerConnector:
    def __init__(self, master, gui, root):
        self.master = master
        self.root = root
        self.gui = gui
        self.api = BlockchairAPI(root=master, gui=self.gui)
        self.saved_credentials = {}
        self.ssh_client = None
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
                    'Staking': 'N/A'
                }

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
        try:
            print("executing cmd")
            # Create SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the server
            ssh_client.connect(
                hostname=self.saved_credentials['hostname'],
                port=self.saved_credentials['port'],
                username=self.saved_credentials['username'],
                password=self.saved_credentials['password']
            )

            output = {}
            for command in commands:
                stdin, stdout, stderr = ssh_client.exec_command(command)

                # Read command output
                stdout_output = stdout.read().decode().strip()
                stderr_output = stderr.read().decode().strip()

                # Store the output
                output[command] = {
                    'stdout': stdout_output,
                    'stderr': stderr_output
                }

            if output:
                self.node_output['Server'] = "Connected"
            else:
                self.node_output['Server'] = 'Not Connected'
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


            # Close the connection
            ssh_client.close()

            return output

        except paramiko.AuthenticationException:
            messagebox.showerror("Error", "Authentication failed, please check your credentials.")
        except paramiko.SSHException as ssh_ex:
            messagebox.showerror("Error", f"Unable to establish SSH connection: {ssh_ex}")
        except Exception as ex:
            messagebox.showerror("Error", f"An error occurred: {ex}")

    def connect_to_node(self):
        print(f"connect_to_node called with selected_node={self.node_output['Selected Node']}")

        command1 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin-cli getblockchaininfo"
        command2 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin-cli getavalancheinfo"

        output = self.connect_and_execute_commands([command1, command2]
        )

        print(output)

        for command_output in output.values():
            if "Make sure the bitcoind server is running" in command_output['stderr']:
                print("Node is off")
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


            # Chain info
            self.node_output["Chain"] = filtered_lines_command1[1][11:].replace(",", "").replace('"', '').replace(':', '').capitalize()

            # Blockchain info
            self.node_output["Headers"] = int(filtered_lines_command1[3][13:].replace(",", "").replace('"', '').replace(':', ''))
            self.node_output["Blocks"] = int(filtered_lines_command1[2][12:].replace(",", "").replace('"', '').replace(':', ''))

            self.api.current_block = self.node_output["Blocks"]
            print("last block " + str(self.api.current_block))

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

            print(self.node_output)

            # Update GUI with node output
            self.gui.update_info(self.node_output)

            # Fetch my recent rewards info and update GUI
            self.initial_rewards_fetcher(self.node_output["Payout Address"], self.node_output["Blocks"])

            #{'ea5104e3be4658f1853fc1f29daf26c8912eca96cf8da94bd4b921d25ae73d66': {'local_date_time': '2024-07-01 01:10:43', 'block_height': 851298, 'amount': 31250470}, '154390e86637b78b85f5ea36cddda1f1a0373bc2dcac937b409dedb5ebd875b8': {'local_date_time': '2024-06-30 07:18:01', 'block_height': 851185, 'amount': 31262015}, '67615ff7ee2ddf432a5413b10324cc7aac5bc4596fb6bde1c38bb4446c747098': {'local_date_time': '2024-06-13 07:35:54', 'block_height': 848775, 'amount': 31251402}, 'fc1042ebad5234106e6137058e7bbeba170377b81a7c2d544de9576f9a702676': {'local_date_time': '2024-06-11 04:34:46', 'block_height': 848467, 'amount': 31250000}, '644cdbd1ddfe4edc34d7f473c1d7b3f416575db4ccb0d4ed50ed2441b82a962d': {'local_date_time': '2024-06-10 05:31:03', 'block_height': 848337, 'amount': 31250000}, 'f3fa06731625383eb2ee86b1881d443d66f7da4b16f3ed9e02c752ae8006cb56': {'local_date_time': '2024-06-04 05:14:05', 'block_height': 847528, 'amount': 31258776}, '6a1a4c1579e9b853e55a8520e58e29a16e36ba621e20d447b5a48d5d39889c1b': {'local_date_time': '2024-05-29 06:56:58', 'block_height': 846715, 'amount': 31250886}, '05cced3f89caa4952929e8fe3b5b33072ef520fa83f3da7f5ec57832139aa1a2': {'local_date_time': '2024-05-21 18:03:08', 'block_height': 845639, 'amount': 31250000}, '9cff507f84e819e191a988b76ba727d6ae821b178334e46128e0e4eaf3c24925': {'local_date_time': '2024-03-18 15:19:49', 'block_height': 836438, 'amount': 62500855}, '1c3189c99d1e50de972695faa6188467a8cd2661a4bdf907ef5df3efcdbcba7b': {'local_date_time': '2024-03-12 23:59:46', 'block_height': 835640, 'amount': 62502777}, 'd0346537876cdfccb155e241fc9f79588cebeb3c5c3790c5fe9de01a51ccf1f1': {'local_date_time': '2024-03-11 17:25:14', 'block_height': 835487, 'amount': 62500254}, 'c72c5df660027c9d8d629fedbe8b256d33243c8539fdbb255b7a164d46b7719c': {'local_date_time': '2024-03-07 23:59:29', 'block_height': 834951, 'amount': 62500022}, 'dd6388d9d4f4c122bee132bbe38a4aabadd22a1420a56e7184dce94e412a8fd8': {'local_date_time': '2024-03-04 09:23:05', 'block_height': 834310, 'amount': 62500155}, '4970f213a043c0606fbf197ae006226ea7e3ef9e749e1a9323a73f08a46d8016': {'local_date_time': '2024-02-26 21:36:26', 'block_height': 833358, 'amount': 62501152}, '3be2f4ae8b4b9df4b00b76c5067548f42735758b9469760309299e3779eb4f9e': {'local_date_time': '2024-02-26 19:07:52', 'block_height': 833344, 'amount': 62500096}, '5bfc24aa31d99b474f4da65305cfdd494e25904530416be26e36bf4d5ee6eaa7': {'local_date_time': '2024-02-20 00:26:58', 'block_height': 832381, 'amount': 62500179}, 'fb70ea5313a627fd0cbab5e2260ee8ae58a0b6744a7cfd12370ebcca3548e8a2': {'local_date_time': '2024-02-06 06:41:13', 'block_height': 830374, 'amount': 62500000}, 'cca6cdbc5174dddc83c65653d00fe0681ce962147510e6795e8584f8df3e4d3e': {'local_date_time': '2024-01-31 08:34:51', 'block_height': 829507, 'amount': 62504988}}

            self.root.after(10000, self.connect_to_node)

    def start_the_node(self):
        print("starting node: " + self.node_output['Selected Node'])
        print("Starting the node with credentials:", self.saved_credentials)
        command1 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoind -daemon"

        output = self.connect_and_execute_commands([command1]        )

        if "Bitcoin ABC starting" in str(output):
            messagebox.showinfo("Success", f"Your {self.node_output['Selected Node']} node is starting")
            self.root.after(15000, self.connect_to_node)
        else:
            messagebox.showerror("Error", "Could not start the node")

    def stop_the_node(self):
        if not self.saved_credentials:
            print("Credentials are not set. Cannot stop the node.")
            messagebox.showerror("Error", "Credentials are not set.")
            return
        print(f"stopping node")
        print("Stopping the node with credentials:", self.saved_credentials)
        command1 = f"/home/{self.saved_credentials['username']}/{self.node_output['Selected Node']}/bin/bitcoin-cli stop"

        output = self.connect_and_execute_commands([command1])

        if "Bitcoin ABC stopping" in str(output):
            messagebox.showinfo("Success", f"Your {self.node_output['Selected Node']} node is stopping")
            #button_start_the_node.config(text="Please wait", state=tk.DISABLED)
            #self.root.after(10000, connect_to_node, self.selected_node)
            #self.root.after(10000, enable_start_the_node)
        else:
            messagebox.showerror("Error", "Could not stop the node")

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