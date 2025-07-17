import tkinter as tk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Window")

        self.canvas = tk.Canvas(root, width=400, height=300, bg="white")
        self.canvas.pack()

        # Create a shape (e.g., a rectangle) on the canvas
        self.rectangle = self.canvas.create_rectangle(50, 50, 150, 100, fill="blue", tags="clickable_rect")
        self.canvas.create_text(100, 75, text="Click me!", fill="white", tags="clickable_rect")

        # Bind the click event to the shape using its tag
        self.canvas.tag_bind("clickable_rect", "<Button-1>", self.open_popup)

    def open_popup(self, event):
        # Create a Toplevel window for the popup
        popup = tk.Toplevel(self.root)
        popup.title("Popup Window")
        popup.geometry("200x150")

        # Add a label to the popup
        tk.Label(popup, text="You clicked the rectangle!").pack(pady=20)

        # Add a button to close the popup
        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
