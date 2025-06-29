
import time
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas

editWindow = tk.Tk() 
#editWindow = tk.Toplevel(root)
editWindow.title("Layout Simulation")
# Adjust size 
editWindow.geometry( "1200x800" ) 

C = Canvas(editWindow, height=800, width=1200, bg="yellow")
C.pack()
yard2Image = C.create_rectangle(100, 100, 200, 160)
yard2Text = C.create_text(150, 110, text="Yard2")

yard1Image = C.create_rectangle(500, 100, 600, 160)
yard1Text = C.create_text(550, 130, text="Yard1")

swArea1Image = C.create_rectangle(900, 100, 1000, 160)
swArea1Text = C.create_text(950, 130, text="Sw Area1")

route2_4 = C.create_line(200, 130, 500, 130)
route2_4Text = C.create_text(350, 140, text="Routes 2 and 4")

route1_3 = C.create_line(600, 130, 900, 130)
route1_3Text = C.create_text(750, 140, text="Routes 1 and 3")

train1Dict = {"x0": 210, "y0": 115, "width": 20, "height": 10}
train1 = C.create_rectangle(train1Dict["x0"], train1Dict["y0"], 
        train1Dict["x0"]+train1Dict["width"],
        train1Dict["y0"]+train1Dict["height"],
        )
train1Text = C.create_text(250, 80, text="train1", anchor="nw")
train1_consist = C.create_text(250, 95, text="3, 1, 2, 2, 0, 0", anchor="nw")

C.update()
C.after(1000, lambda: C.move(train1, 50, 0))
editWindow.mainloop()

