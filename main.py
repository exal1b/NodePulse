import os
import tkinter as tk
from gui import App
import sys
from ServerConnector import ServerConnector


if __name__ == "__main__":
    root = tk.Tk()
    root.title("NodePulse")

    # Resolve the path to azure.tcl
    if hasattr(sys, "_MEIPASS"):
        theme_path = os.path.join(sys._MEIPASS, "azure.tcl")
    else:
        theme_path = os.path.join(os.getcwd(), "azure.tcl")

    root.tk.call("source", theme_path)
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    ServerConnector_instance = ServerConnector(root=root, master=app, gui=app)
    root.resizable(False, False)

    root.mainloop()