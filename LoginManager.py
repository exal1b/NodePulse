import json
import os
from getpass import getpass

# LoginManager class definition
class LoginManager:
    def __init__(self, credentials_file='credentials.json'):
        # Define the path to the user's home directory
        home_directory = os.path.expanduser("~")
        # Create a standard directory under the user's home directory
        self.credentials_file = os.path.join(home_directory, '.config', credentials_file)
        directory = os.path.dirname(self.credentials_file)
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

    def save_credentials(self, username, server_ip, server_port):
        """Save username, server IP, and server port to a file."""
        credentials = {
            'username': username,
            'server_ip': server_ip,
            'server_port': server_port,
        }
        with open(self.credentials_file, 'w') as file:
            json.dump(credentials, file)
        os.chmod(self.credentials_file, 0o600)  # Restrict file access

    def load_credentials(self):
        """Load credentials from a file."""
        if not os.path.exists(self.credentials_file):
            return None
        with open(self.credentials_file, 'r') as file:
            credentials = json.load(file)
        return credentials