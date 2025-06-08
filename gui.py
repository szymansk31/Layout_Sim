
class indices:
    def __init__(self):
        self.mainIDX = 0

class frmsWind:
    def __init__(self):
        self.listFrameMaster = any
        self.dispCardFrame = any
        self.destSelFrame = any
        self.storeCardFileFrame = any
        self.outputCtrlFrame = any
        
    def setFrms(self, editWindow, tk):
        listFrameMasterRow = 2
        listFrameMasterCol = 0
        self.listFrameMaster = tk.Frame(master=editWindow, bg="lightblue", borderwidth=4)
        self.listFrameMaster.grid(row=listFrameMasterRow, column=listFrameMasterCol)

        dispFrameRow = 4
        dispFrameCol = 0
        self.dispCardFrame = tk.Frame(editWindow, bg="darkblue")
        self.dispCardFrame.grid(row=dispFrameRow, column=dispFrameCol, columnspan=3, sticky="nw")

        destSelFrameRow = 4
        destSelFrameCol = 3
        self.destSelFrame = tk.Frame(editWindow, bg="yellow")
        self.destSelFrame.grid(row=destSelFrameRow, column=destSelFrameCol, sticky="nw")

        storeCardFileFrameRow = 5
        storeCardFileFrameCol = 0
        self.storeCardFileFrame = tk.Frame(editWindow, bg="orange")
        self.storeCardFileFrame.grid(row=storeCardFileFrameRow, 
            column=storeCardFileFrameCol, columnspan=2, sticky="nw")

        outputCtrlFrameRow = 0
        outputCtrlFrameCol = 1
        self.outputCtrlFrame = tk.Frame(editWindow, bg="orange")
        self.outputCtrlFrame.grid(row=outputCtrlFrameRow, column=outputCtrlFrameCol, sticky="nw")

