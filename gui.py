import tkinter as tk
from tkinter import ttk, Toplevel, Label, Text, END, messagebox, scrolledtext
from PIL import Image, ImageTk
import qrcode
from ServerConnector import ServerConnector
from ecash_api import BlockchairAPI
from LoginManager import LoginManager

class App(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        ttk.Frame.__init__(self, root)
        self.root = root
        self.ServerConnector = ServerConnector(master=self.root, gui=self, root=self.root)
        self.setup_widgets()
        self.LoginManager = LoginManager()
        self.login_window = None
        self.edit_bitcoin_conf_window = None

    def setup_widgets(self):
        # Create a Commands frame for the buttons
        self.commands_frame = ttk.LabelFrame(self, text="Commands", padding=(20, 10))
        self.commands_frame.grid(row=0, column=0, padx=(20, 15), pady=(20, 20), rowspan=3, sticky="nsew")

        # Commands frame - Button - Connect to server
        self.connect_to_server_button = ttk.Button(self.commands_frame, text="Connect to server", command=self.show_login_window)
        self.connect_to_server_button.grid(row=0, column=0, padx=5, pady=12, sticky="nsew")

        # Commands frame - Button - Start the node
        self.select_node_button = ttk.Button(self.commands_frame, text="Select a node", command=self.handle_login)
        self.select_node_button.grid(row=1, column=0, padx=5, pady=12, sticky="nsew")

        # Commands frame - Button - Stop the node
        self.start_or_stop_the_node_button = ttk.Button(self.commands_frame, text="Start the node", command=self.node_error_msg4)
        self.start_or_stop_the_node_button.grid(row=2, column=0, padx=5, pady=12, sticky="nsew")

        # Commands frame - Button - Install a node
        self.install_a_node_button = ttk.Button(self.commands_frame, text="Install a node", command=self.server_error_msg)
        self.install_a_node_button.grid(row=3, column=0, padx=5, pady=12, sticky="nsew")

        # Commands frame - Button - Update the node
        self.update_the_node_button = ttk.Button(self.commands_frame, text="Update the node")
        self.update_the_node_button.grid(row=4, column=0, padx=5, pady=12, sticky="nsew")

        # Commands frame - Button - Edit Bitcoin.conf
        self.edit_bitcoinconf_button = ttk.Button(self.commands_frame, text="Edit Bitcoin.conf", command=self.create_edit_bitcoin_conf_window)
        self.edit_bitcoinconf_button.grid(row=5, column=0, padx=5, pady=11, sticky="nsew")

        # Commands frame - Button - Support us
        self.support_us_button = ttk.Button(self.commands_frame, text="Support us", command=self.show_qr_code)
        self.support_us_button.grid(row=6, column=0, padx=5, pady=11, sticky="nsew")

        # Create a Frame to display main info
        self.main_info_frame = ttk.LabelFrame(self, text="Main Information", padding=(20, 10))
        self.main_info_frame.grid( row=0, column=1, padx=(10, 20), pady=(20, 9), sticky="new")

        # Load the icon image
        self.grey_icon_file = Image.open(r"C:\Users\Mises\PycharmProjects\NodePulse\Azure-ttk-theme-main\grey_icon.png")
        self.green_icon_file = Image.open(r"C:\Users\Mises\PycharmProjects\NodePulse\Azure-ttk-theme-main\green_icon.png")
        self.red_icon_file = Image.open(r"C:\Users\Mises\PycharmProjects\NodePulse\Azure-ttk-theme-main\red_icon.png")
        self.blue_icon_file = Image.open(r"C:\Users\Mises\PycharmProjects\NodePulse\Azure-ttk-theme-main\blue_icon.png")

        # Resize the icon to 15x15 pixels
        self.grey_icon_file = self.grey_icon_file.resize((15, 15), Image.Resampling.LANCZOS)
        self.green_icon_file = self.green_icon_file.resize((15, 15), Image.Resampling.LANCZOS)
        self.red_icon_file = self.red_icon_file.resize((15, 15), Image.Resampling.LANCZOS)
        self.blue_icon_file = self.blue_icon_file.resize((15, 15), Image.Resampling.LANCZOS)

        # Convert the icon
        self.grey_icon = ImageTk.PhotoImage(self.grey_icon_file)
        self.green_icon = ImageTk.PhotoImage(self.green_icon_file)
        self.red_icon = ImageTk.PhotoImage(self.red_icon_file)
        self.blue_icon = ImageTk.PhotoImage(self.blue_icon_file)

        # Main info frame - Server status info
        self.server_info_label = tk.Label(self.main_info_frame, text="Server")
        self.server_info_label.grid(row=1, column=0, padx=3, pady=1, sticky="e")
        self.server_status_output = tk.Label(self.main_info_frame, text="N/A")
        self.server_status_output.grid(row=1, column=1, padx=3, pady=1, sticky="w")
        self.server_status_icon_label = tk.Label(self.main_info_frame, image=self.grey_icon)
        self.server_status_icon_label.image = self.grey_icon
        self.server_status_icon_label.grid(row=1, column=2)

        # Main info frame - Node status info
        self.node_info_label = tk.Label(self.main_info_frame, text="Node")
        self.node_info_label.grid(row=2, column=0, padx=3, pady=1, sticky="e")
        self.node_status_output = tk.Label(self.main_info_frame, text="N/A")
        self.node_status_output.grid(row=2, column=1, padx=3, pady=1, sticky="w")
        self.node_status_icon_label = tk.Label(self.main_info_frame, image=self.grey_icon)
        self.node_status_icon_label.image = self.grey_icon
        self.node_status_icon_label.grid(row=2, column=2)

        # Main info frame - Chain status info
        self.chain_info_label = tk.Label(self.main_info_frame, text="Chain")
        self.chain_info_label.grid(row=3, column=0, padx=3, pady=1, sticky="e")
        self.chain_status_output = tk.Label(self.main_info_frame, text="N/A")
        self.chain_status_output.grid(row=3, column=1, padx=3, pady=1, sticky="w")
        self.chain_status_icon_label = tk.Label(self.main_info_frame, image=self.grey_icon)
        self.chain_status_icon_label.image = self.grey_icon
        self.chain_status_icon_label.grid(row=3, column=2)

        # Main info frame - Blockchain status info
        self.blockchain_info_label = tk.Label(self.main_info_frame, text="Blockchain")
        self.blockchain_info_label.grid(row=1, column=4, padx=(10, 3), pady=1, sticky="e")
        self.blockchain_status_output = tk.Label(self.main_info_frame, text="N/A")
        self.blockchain_status_output.grid(row=1, column=5, padx=3, pady=1, sticky="w")
        self.blockchain_info_icon_label = tk.Label(self.main_info_frame, image=self.grey_icon)
        self.blockchain_info_icon_label.image = self.grey_icon
        self.blockchain_info_icon_label.grid(row=1, column=6)

        # Main info frame - Proof status info
        self.proof_info_label = tk.Label(self.main_info_frame, text="Proof")
        self.proof_info_label.grid(row=2, column=4, padx=3, pady=1, sticky="e")
        self.proof_status_output = tk.Label(self.main_info_frame, text="N/A")
        self.proof_status_output.grid(row=2, column=5, padx=3, pady=1, sticky="w")
        self.proof_info_icon_label = tk.Label(self.main_info_frame, image=self.grey_icon)
        self.proof_info_icon_label.image = self.grey_icon
        self.proof_info_icon_label.grid(row=2, column=6)

        # Main info frame - Staking status info
        self.stake_info_label = tk.Label(self.main_info_frame, text="Staking")
        self.stake_info_label.grid(row=3, column=4, padx=3, pady=1, sticky="e")
        self.stake_status_output = tk.Label(self.main_info_frame, text="N/A")
        self.stake_status_output.grid(row=3, column=5, padx=3, pady=1, sticky="w")
        self.stake_info_icon_label = tk.Label(self.main_info_frame, image=self.grey_icon)
        self.stake_info_icon_label.image = self.grey_icon
        self.stake_info_icon_label.grid(row=3, column=6)

        # Create a Frame to display other info
        self.other_info_frame = ttk.LabelFrame(self, text="Other Information", padding=(10, 10))
        self.other_info_frame.grid(row=1, column=1, padx=(10, 20), pady=(9, 9), sticky="new")

        # Other info frame - Client version info
        self.client_version_label = tk.Label(self.other_info_frame, text="Client version")
        self.client_version_label.grid(row=0, column=0, padx=3, pady=1, sticky="e")
        self.client_version_output = tk.Label(self.other_info_frame, text="N/A")
        self.client_version_output.grid(row=0, column=1, padx=3, pady=1, sticky="w")

        # Other info frame - Stake amount info
        self.stake_amount_label = tk.Label(self.other_info_frame, text="Stake amount")
        self.stake_amount_label.grid(row=2, column=0, padx=3, pady=1, sticky="e")
        self.stake_amount_output = tk.Label(self.other_info_frame, text="N/A")
        self.stake_amount_output.grid(row=2, column=1, padx=3, pady=1, sticky="w")

        # Other info frame - Payout address info
        self.payout_address_label = tk.Label(self.other_info_frame, text="Payout address")
        self.payout_address_label.grid(row=3, column=0, padx=3, pady=1, sticky="e")
        self.payout_address_output = tk.Label(self.other_info_frame, text="N/A")
        self.payout_address_output.grid(row=3, column=1, padx=3, pady=1, sticky="w")

        # Set the column width within the main info frame
        self.main_info_frame.grid_columnconfigure(0, minsize=40)
        self.main_info_frame.grid_columnconfigure(1, minsize=95)
        self.main_info_frame.grid_columnconfigure(2, minsize=10)
        self.main_info_frame.grid_columnconfigure(3, minsize=40)
        self.main_info_frame.grid_columnconfigure(4, minsize=50)
        self.main_info_frame.grid_columnconfigure(5, minsize=95)
        self.main_info_frame.grid_columnconfigure(6, minsize=10)

        # Create a Frame to display my rewards
        self.panned_window_frame = ttk.LabelFrame(self, text="My recent rewards", padding=(10, 10))
        self.panned_window_frame.grid(row=2, column=1, padx=(10, 20), pady=(9, 20), sticky="new")

        # Panedwindow
        self.paned = ttk.PanedWindow(self.panned_window_frame)
        self.paned.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew", rowspan=3)

        # Pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=0)
        self.paned.add(self.pane_1, weight=1)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self.treeview = ttk.Treeview(
            self.pane_1,
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
            columns=("1", "2"),
            height=3
        )
        self.treeview.pack(expand=True, fill="both")
        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview.column("#0", anchor="w", width=140)
        self.treeview.column(1, anchor="center", width=110)
        self.treeview.column(2, anchor="center", width=110)

        # Treeview headings
        self.treeview.heading("#0", text="Local time", anchor="center")
        self.treeview.heading(1, text="Blockheight", anchor="center")
        self.treeview.heading(2, text="Amount in XEC", anchor="center")

    def create_select_node_window(self, nodes):
        self.select_node_window = tk.Toplevel(self.master)
        self.select_node_window.title("Select a node")
        self.select_node_window_label = tk.Label(self.select_node_window, text="NodePulse has detected several nodes on the server. \nPlease select one")
        self.select_node_window_label.grid(row=0, column=0, pady=15, padx=15)

        self.selected_option = tk.StringVar()
        self.dropdown = ttk.Combobox(self.select_node_window, textvariable=self.selected_option, values=nodes)
        self.dropdown.grid(row=1, column=0, pady=(0, 15), padx=15)

        self.select_button = tk.Button(self.select_node_window, text="Connect", command=self.connect_to_node)
        self.select_button.grid(row=2, column=0, pady=(0, 15))

    def connect_to_node(self):
        selected_node = self.selected_option.get()

        if selected_node == "":
            self.select_node_error_msg()
        else:
            #node_output["Selected Node"] = selected_node
            #self.update_info(node_output)
            self.ServerConnector.update_selected_node(selected_node)
            self.ServerConnector.connect_to_node()

            if self.select_node_window and self.select_node_window.winfo_exists():
                self.select_node_window.withdraw()

    def show_login_window(self):
        if not self.login_window or not self.login_window.winfo_exists():
            self.create_login_window()
        else:
            self.login_window.deiconify()

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Login")
        self.login_title_label = tk.Label(self.login_window, text="Connect to Server")
        self.login_title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        # Load saved credentials if available
        credentials = self.LoginManager.load_credentials()
        default_hostname = credentials['server_ip'] if credentials else ""
        default_port = credentials['server_port'] if credentials else ""
        default_username = credentials['username'] if credentials else ""

        self.label_hostname = tk.Label(self.login_window, padx=5, pady=5, text="Hostname:")
        self.label_hostname.grid(row=1, column=0)
        self.entry_hostname = tk.Entry(self.login_window)
        self.entry_hostname.grid(row=1, column=1)
        self.entry_hostname.insert(0, default_hostname)

        self.label_port = tk.Label(self.login_window, padx=5, pady=5, text="Port:")
        self.label_port.grid(row=2, column=0)
        self.entry_port = tk.Entry(self.login_window)
        self.entry_port.grid(row=2, column=1)
        self.entry_port.insert(0, default_port)

        self.label_username = tk.Label(self.login_window, padx=5, pady=5, text="Username:")
        self.label_username.grid(row=3, column=0)
        self.entry_username = tk.Entry(self.login_window)
        self.entry_username.grid(row=3, column=1)
        self.entry_username.insert(0, default_username)

        self.label_password = tk.Label(self.login_window, padx=5, pady=5, text="Password:")
        self.label_password.grid(row=4, column=0)
        self.entry_password = tk.Entry(self.login_window, show="*")
        self.entry_password.grid(row=4, column=1)
        self.entry_password.insert(0, "")

        # Checkbuttons
        self.remember_me_var = tk.IntVar()
        self.remember_me_check = ttk.Checkbutton(self.login_window, text="Remember me", variable=self.remember_me_var)
        self.remember_me_check.grid(row=5, columnspan=2, padx=5, pady=5)


        self.button_login = ttk.Button(self.login_window, text="Login", command=self.handle_login)
        self.button_login.grid(row=6, columnspan=2, padx=5, pady=5)

        self.login_window.bind('<Return>', lambda event: self.handle_login())

    def handle_login(self):
        hostname = self.entry_hostname.get()
        port = int(self.entry_port.get())
        username = self.entry_username.get()
        password = self.entry_password.get()

        if self.remember_me_var.get() == 1:
            self.LoginManager.save_credentials(username, hostname, port)

        self.ServerConnector.connect_to_server(hostname, port, username, password)

        if self.login_window and self.login_window.winfo_exists():
            self.login_window.withdraw()

    def handle_start_node(self):
        # Example method to handle stopping the node
        self.ServerConnector.start_the_node()

    def handle_stop_node(self):
        # Example method to handle stopping the node
        self.ServerConnector.stop_the_node()

    def server_error_msg(self):
        messagebox.showinfo("Information", f"You first need to connect to the server to install a node")

    def handle_install_node(self):
        if self.server_status_output != 'Connected':
            messagebox.showinfo("Information", f"You first need to connect to the server to install a node")
        elif self.server_node_output == 'Connected':
            messagebox.showinfo("Information", f"You first turn off the node to install a node")
        else:
            create_install_node_window()

    def create_edit_bitcoin_conf_window(self):
        self.edit_bitcoin_conf_window = tk.Toplevel(self.master)
        self.edit_bitcoin_conf_window.title("Bitcoin.conf file editor")

        bitcoin_conf_text = self.ServerConnector.load_file()
        print(bitcoin_conf_text)

        self.text_area = scrolledtext.ScrolledText(self.edit_bitcoin_conf_window, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(padx=10, pady=10)
        self.text_area.insert(tk.INSERT, bitcoin_conf_text)

        #self.save_button = tk.Button(self.edit_bitcoin_conf_window, text="Save File", command=self.save_file)
        #self.save_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def save_file(self):
        content = self.text_area.get(1.0, tk.END)
        self.ServerConnector.save_file(content)

    def create_install_node_window(self):
        return

    def show_qr_code(self):

        # Bitcoin address to display for donation
        bitcoin_address = "ecash:qpdl7hgkv9gypv6evjupxaqrmgma3jkqaqpqlhxg7a"

        # Generate QR code for donation
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(bitcoin_address)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Create a top-level window (popup)
        popup = Toplevel(self)
        popup.title("eCash Address for donation")
        popup.geometry("410x410")

        # Display the QR code
        img = img.resize((340, 340), Image.Resampling.NEAREST)
        img = ImageTk.PhotoImage(img)
        label_qr = Label(popup, image=img)
        label_qr.image = img
        label_qr.pack(pady=5)

        # Display the Bitcoin address in a Text widget for selectable text
        text_widget_qr = Text(popup, height=1, wrap='none')
        text_widget_qr.insert(END, bitcoin_address)
        text_widget_qr.tag_configure("center", justify='center')
        text_widget_qr.tag_add("center", "1.0", "end")
        text_widget_qr.config(state='disabled')  # Make the text widget read-only
        text_widget_qr.pack(pady=10)

    def update_icon(self, label, icon_color):
        if icon_color == 'green':
            label.config(image=self.green_icon)
            label.image = self.green_icon
        elif icon_color == 'red':
            label.config(image=self.red_icon)
            label.image = self.red_icon
        elif icon_color == 'blue':
            label.config(image=self.blue_icon)
            label.image = self.red_icon
        else:
            label.config(image=self.blue_icon)
            label.image = self.grey_icon

    def update_label_text(self, label, new_text):
        label.config(text=new_text)

    def update_button(self, button, new_text, new_command=None):
        button.config(text=new_text)
        if new_command is not None:
            button.config(command=new_command)

    def update_treeview(self, api_output):
        self.root.after(0, self.update_treeview_main_thread, api_output)

    def update_treeview_main_thread(self, api_output):
        print("updating treeview via Gui function")
        if self.treeview:
            for item in self.treeview.get_children():
                self.treeview.delete(item)

            # Insert rewards into the Treeview
            if api_output:
                for tx_hash, details in api_output.items():
                    self.treeview.insert(
                        "",
                        "end",
                        text=(details['local_date_time'][:16]),
                        values=(
                        "{:,}".format(details['block_height']), "{:,.2f}".format(float(details['amount'] / 100))))

    def update_info(self, node_output):
        # Update install node button
        if node_output['Server'] != "Connected":
            self.install_a_node_button.config(command=self.server_error_msg)
            self.update_button(start_or_stop_the_node_button, "Start the node", self.node_error_msg4)
        elif node_output['Node'] == "Connected":
            self.install_a_node_button.config(command=self.node_error_msg1)
        elif node_output['Node'] == "N/A":
            self.install_a_node_button.config(command=self.node_error_msg3)
        else:
            self.install_a_node_button.config(command=self.create_install_node_window)

        # Update edit bitcoin.conf button
        if node_output['Server'] != "Connected":
            self.edit_bitcoinconf_button.config(command=self.server_error_msg)
        elif node_output['Node'] == "Connected":
            self.edit_bitcoinconf_button.config(command=self.node_error_msg2)
        else:
            self.edit_bitcoinconf_button.config(command=self.create_edit_bitcoin_conf_window)

        # Update start or stop the node button
        if node_output['Server'] != "Connected":
            self.start_or_stop_the_node_button.config(text="Start the node", command=self.node_error_msg4)
        elif node_output['Node'] == "Connected":
            self.start_or_stop_the_node_button.config(text="Stop the node", command=self.handle_stop_node)
        elif node_output['Selected Node'] == "N/A":
            self.start_or_stop_the_node_button.config(text="Start the node", command=self.node_error_msg5)
        else:
            self.start_or_stop_the_node_button.config(text="Start the node", command=self.handle_start_node)

        # Update server status
        if node_output['Server'] == "Connected":
            self.update_icon(self.server_status_icon_label, "green")
        elif node_output["Server"] == "N/A":
            self.update_icon(self.server_status_icon_label, "grey")
        else:
            self.update_icon(self.server_status_icon_label, "red")
        self.update_label_text(self.server_status_output, node_output["Server"])

        # Update node status
        if node_output["Node"] == "Connected":
            self.update_icon(self.node_status_icon_label, "green")
        elif node_output["Node"] == "N/A":
            self.update_icon(self.node_status_icon_label, "grey")
        else:
            self.update_icon(self.node_status_icon_label, "red")
        self.update_label_text(self.node_status_output, node_output["Node"])

        # Update chain status
        if node_output["Chain"] == "Main":
            self.update_icon(self.chain_status_icon_label, "green")
        elif node_output["Chain"] == "N/A":
            self.update_icon(self.chain_status_icon_label, "grey")
        else:
            self.update_icon(self.chain_status_icon_label, "red")
        self.update_label_text(self.chain_status_output, node_output["Chain"])

        # Update blockchain status
        if node_output["Blockchain"] == "Synced":
            self.update_icon(self.blockchain_info_icon_label, "green")
        elif node_output["Blockchain"] == "N/A":
            self.update_icon(self.blockchain_info_icon_label, "grey")
        else:
            self.update_icon(self.blockchain_info_icon_label, "red")
        self.update_label_text(self.blockchain_status_output, node_output["Blockchain"])

        # Update Proof status
        if node_output["Proof"] == "Verified":
            self.update_icon(self.proof_info_icon_label, "green")
        elif node_output["Proof"] == "N/A":
            self.update_icon(self.proof_info_icon_label, "grey")
        else:
            self.update_icon(self.proof_info_icon_label, "red")
        self.update_label_text(self.proof_status_output, node_output["Proof"])

        # Update Staking status
        if node_output["Staking"] == "Activated":
            self.update_icon(self.stake_info_icon_label, "green")
        elif node_output["Staking"] == "Awaiting block":
            self.update_icon(self.stake_info_icon_label, "blue")
        elif node_output["Staking"] == "N/A":
            self.update_icon(self.stake_info_icon_label, "grey")
        else:
            self.update_icon(self.stake_info_icon_label, "red")
        self.update_label_text(self.stake_status_output, node_output["Staking"])

        # Update Stake amount status
        if node_output['Stake Amount'] == "N/A":
            self.update_label_text(self.stake_amount_output, node_output["Stake Amount"])
        else:
            self.update_label_text(self.stake_amount_output, node_output["Stake Amount"] + " XEC")

        # Update payout address
        self.update_label_text(self.payout_address_output, node_output["Payout Address"])

        # Update client version
        reformatted_client_version = node_output["Selected Node"].replace('-', ' ')
        self.update_label_text(self.client_version_output, reformatted_client_version)

    def new_reward_messagebox(self, formatted_reward):
        messagebox.showinfo("Congratulations", f"You've received a reward of {formatted_reward} XEC")

    def bring_forward_select_node(self):
        # Bring the window to the front after the error message is closed
        self.select_node_window.lift()
        self.select_node_window.attributes('-topmost', True)
        self.select_node_window.attributes('-topmost', False)
        self.select_node_window.focus_force()

    def select_node_error_msg(self):
        messagebox.showerror("Error", "Please select a node before connecting")
        self.master.after(10, self.bring_forward_select_node)

    def node_error_msg1 (self):
        messagebox.showinfo("Information", f"You first turn off the node to install a node")

    def node_error_msg2(self):
        messagebox.showinfo("Information", f"You first turn off the node to edit the bitcoin.conf file")

    def node_error_msg3(self):
        messagebox.showinfo("Information", f"You first install a node on the server to edit the bitcoin.conf file")

    def node_error_msg4(self):
        messagebox.showerror("Error", f"You first need to connect to a server")

    def node_error_msg5(self):
        messagebox.showerror("Error", f"No node was found")
