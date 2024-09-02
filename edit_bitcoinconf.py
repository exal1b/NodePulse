import paramiko
import tempfile
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox

def ssh_connect(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password)
    return client

def check_and_create_file(client, remote_path):
    stdin, stdout, stderr = client.exec_command(f'test -f {remote_path} || touch {remote_path}')
    stderr_output = stderr.read().decode()
    if stderr_output:
        raise Exception(f"Error while checking/creating the file: {stderr_output}")

def fetch_file(client, remote_path):
    sftp = client.open_sftp()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            sftp.get(remote_path, temp_file.name)
        except FileNotFoundError:
            open(temp_file.name, 'w').close()  # Create an empty local file if the remote file does not exist
        temp_file_path = temp_file.name
    sftp.close()
    return temp_file_path

def push_file(client, local_path, remote_path):
    sftp = client.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()

def load_file():
    host = '62.169.31.103'
    port = 22
    username = 'kikoo'
    password = 'brunet'
    remote_path = '/home/kikoo/bitcoin-abc-0.29.8/bin/bitcoin.conf'

    client = ssh_connect(host, port, username, password)

    try:
        check_and_create_file(client, remote_path)
        temp_file_path = fetch_file(client, remote_path)
        with open(temp_file_path, 'r') as file:
            content = file.read()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.INSERT, content)
        os.remove(temp_file_path)
        global ssh_client, remote_file_path
        ssh_client = client
        remote_file_path = remote_path
    except Exception as e:
        messagebox.showerror("Error", str(e))
        client.close()

def save_file():
    if not ssh_client:
        messagebox.showerror("Error", "No SSH connection established.")
        return

    try:
        temp_file_path = tempfile.mktemp()
        with open(temp_file_path, 'w') as file:
            file.write(text_area.get(1.0, tk.END))
        push_file(ssh_client, temp_file_path, remote_file_path)
        os.remove(temp_file_path)
        messagebox.showinfo("Success", "File saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

    ssh_client.close()

ssh_client = None
remote_file_path = ''

root = tk.Tk()
root.title("Bitcoin Configuration Editor")

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
text_area.pack(padx=10, pady=10)

load_button = tk.Button(root, text="Load File", command=load_file)
load_button.pack(side=tk.LEFT, padx=10, pady=10)

save_button = tk.Button(root, text="Save File", command=save_file)
save_button.pack(side=tk.RIGHT, padx=10, pady=10)

root.mainloop()