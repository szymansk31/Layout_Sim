    def testPop(self, loc):
        # Create a shape (e.g., a rectangle) on the canvas
        gui.C.create_rectangle(300, 300, 400, 400, fill="blue", tags="testPopID")
        gui.C.create_text(350, 350, text=loc, fill="white", tags="testPopID")
        gui.C.tag_bind("testPopID", "<Button-1>", 
        #    lambda: self.openTestPop( "from testPop Rectangle"))
            lambda event, loc=loc: self.openTestPop(event, loc))
        #gui.C.tag_bind("testPopID", "<Button-1>", 
        #    self.openTestPop)

    def openTestPop(self, event, loc):
        # Create a Toplevel window for the popup
        popup = tk.Toplevel(gui.root)
        popup.title("Popup Window")
        popup.geometry("200x150")
        tk.Label(popup, text=loc).pack()
