
from gui import gui
import tkinter as tk

class popups:
    
    def __init__(self):
        pass

    def open_popup(self, event):
        # Create a Toplevel window for the popup
        popup = tk.Toplevel(gui.root)
        popup.title("Popup Window")
        popup.geometry("200x150")
        #gui.C.pack()
