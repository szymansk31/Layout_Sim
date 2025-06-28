
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas

editWindow = tk.Tk() 
#editWindow = tk.Toplevel(root)
editWindow.title("Layout Simulation")
# Adjust size 
editWindow.geometry( "800x600" ) 

C = Canvas(editWindow, height=800, width=600, bg="yellow")
C.pack()
yard2Image = C.create_rectangle(100, 100, 150, 140)
yard2Text = C.create_text(125, 120, text="Yard2")

yard1Image = C.create_rectangle(275, 100, 325, 140)
yard1Text = C.create_text(300, 120, text="Yard1")

swArea1Image = C.create_rectangle(450, 100, 500, 140)
swArea1Text = C.create_text(475, 120, text="Sw Area1")

route2_4 = C.create_line(150, 125, 275, 125)
route2_4Text = C.create_text(200, 140, text="Routes 2 and 4")

route1_3 = C.create_line(325, 125, 450, 125)
route1_3Text = C.create_text(375, 140, text="Routes 1 and 3")

editWindow.mainloop()
