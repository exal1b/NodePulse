import tkinter as tk
from gui import App
from ServerConnector import ServerConnector

if __name__ == "__main__":
    root = tk.Tk()
    root.title("NodePulse")

    # Simply set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    ServerConnector_instance = ServerConnector(root=root, master=app, gui=app)
    root.resizable(False, False)

    root.mainloop()