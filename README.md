
# NodePulse

NodePulse is an open-source, client-based software designed to simplify staking on the XEC blockchain. It provides users with quick access to essential information about their staking node's status, rewards, and basic controls (such as turning the node on or off).

## Features
- **Easy node management**: Start and stop your staking node directly from the app.
- **Real-time updates**: Monitor your node's status and rewards.
- **User-friendly interface**: Built using the Azure-ttk theme for a sleek and modern design.
- **Standalone executable**: Available for quick installation and use.

## GUI Theme
The graphical user interface (GUI) of NodePulse is built using the [Azure-ttk-theme](https://github.com/rdbende/Azure-ttk-theme), a modern and customizable theme for `tkinter`. You can explore the theme and its features on the repository page.

## Installation
### Prerequisites
- Python 3.x installed
- Required dependencies:
  ```sh
  pip install -r requirements.txt
  ```

### Dependencies
Here are the key dependencies used in NodePulse:

- **datetime** (standard Python library)
- **tkinter** (for GUI components)
- **paramiko** (for SSH connectivity)
- **rewards** (custom module for rewards calculation)
- **platform** (for platform-specific features)
- **subprocess** (for running system processes)
- **ping3** (for pinging nodes)
- **requests** (for HTTP requests)
- **json** (for parsing JSON data)
- **os** (for interacting with the operating system)
- **pytz** (for timezone handling)
- **tzlocal** (to get the local timezone)
- **PIL** (for image processing)
- **qrcode** (for generating QR codes)
- **getpass** (for secure password input)

### Installing Dependencies Manually
If you do not have a `requirements.txt` file, you can install the dependencies manually using pip:
```sh
pip install paramiko ping3 requests pytz tzlocal pillow qrcode
```

## Compiling the Program
Once you've cloned the repository, navigate to the root directory of the project. To compile NodePulse into a standalone executable using PyInstaller, use the following command:

```sh
pyinstaller --onefile --windowed ^
  --add-data "azure.tcl;." ^
  --add-data "theme;theme" ^
  --add-data "nodepulse_icon.ico;." ^
  --add-data "grey_icon.png;." ^
  --add-data "red_icon.png;." ^
  --add-data "green_icon.png;." ^
  --add-data "blue_icon.png;." ^
  --add-data "nodepulse_logo.png;." ^
  main.py --name NodePulse --clean
```

Note:
- The paths are now **relative**, meaning they are based on where the files are in the cloned repository. 
- The `--add-data` paths refer to the files in the folder.

### Alternative for PowerShell
For PowerShell users, use this equivalent command:

```powershell
pyinstaller --onefile --windowed `
  --add-data 'azure.tcl;.' `
  --add-data 'theme;theme' `
  --add-data 'nodepulse_icon.ico;.' `
  --add-data 'grey_icon.png;.' `
  --add-data 'red_icon.png;.' `
  --add-data 'green_icon.png;.' `
  --add-data 'blue_icon.png;.' `
  --add-data 'nodepulse_logo.png;.' `
  main.py --name NodePulse --clean
```

## Running the Executable
After compilation, the standalone executable can be found in the `dist/` directory:
```sh
cd dist
./NodePulse.exe
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## License
This project is licensed under the [MIT License](LICENSE).

## Contact
For any questions or feedback, reach out via GitHub or email.
