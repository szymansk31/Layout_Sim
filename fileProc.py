import xlsxwriter

from vars import *
#from Car_Cards import dispSelection
from sharedVars import indices
from framesWindows import frmsWind

defMainDictFile = "mainDict.txt"
defxlsxOutputFile = "test_display.xlsx"
defExcelDBFile = '../Ops Cards 2_2025/CarCardsv4_2_2025.xls'

class fNames:
    mainDictFile = defMainDictFile
    xlsxOutputFile = defxlsxOutputFile
    excelDBFile = defExcelDBFile
    xlsxWorkbook = any
    worksheet = any
    def __init__(self):
        pass


#=================================================
class fProc:
    fileNameEntry = any
    def __init__(self):
        self.begRow = 0
        self.begCol = 0
        self.endRow = 33
        self.endCol = 8
        self.autoNumFiles = 0
        
    def storeXLOutFName(self, event):
        whichWidget = event.widget
        fNames.xlsxOutputFile = whichWidget.get()
        print("\nstoreOutputFileName: ", fNames.xlsxOutputFile)

    def storeMDInFName(self, event):
        whichWidget = event.widget
        fNames.mainDictFile = whichWidget.get()
        print("\nnew mainDict File: ", fNames.mainDictFile)

    def newXLOutFName(self, tk):
        print("\nnewOutputFile new output file with name: ", fNames.xlsxOutputFile)
        
        reset = 1
        for idx in range(indices.cardCount):
            headerRow = idx + 2
            headerCol = storeCardHeaderCol
            print("headerRow: ", headerRow, "indices.cardCount: ", indices.cardCount)

            #writeResults = dispSelection(reset, frmsWind.frames.storeCardFileFrame, headerRow, headerCol)
            #writeResults.dispHeaders()

        indices.cardCount = 0
        fileNum +=1
        self.setXLOutFname(self, tk)

    def setXLOutFname(self, tk):
        try:    
            self.xlsxWorkbook.close()
        except:
            print("\nworkbook does not exist; starting new")

        test = self.autoNumFiles
        if (test):
            idxFilExt = fNames.xlsxOutputFile.find('.xlsx')
            idxAmp = fNames.xlsxOutputFile.find('&')
            
            if idxFilExt != -1:
                if fileNum == 0:
                    fNames.xlsxOutputFile = fNames.xlsxOutputFile[:idxFilExt] + '&' + str(fileNum) + fNames.xlsxOutputFile[idxFilExt:]
                else:
                    fNames.xlsxOutputFile = fNames.xlsxOutputFile[:idxAmp] + '&' + str(fileNum) + fNames.xlsxOutputFile[idxFilExt:]
        
        print("\nin setupXlOutputFile; opening file: ", fNames.xlsxOutputFile)    
        self.xlsxWorkbook = xlsxwriter.Workbook(fNames.xlsxOutputFile)
        fNames.worksheet = self.xlsxWorkbook.add_worksheet()
        fNames.worksheet.set_column(colOffset, colOffset+nCols, 6.3)
        fNames.worksheet.set_column(colOffset+nCols-1, colOffset+nCols-1, 27)
        for row in range(self.endRow):
            fNames.worksheet.set_row(row, 18.5)
        
        fNames.worksheet.set_margins(left=1.84, right=0.31, top=1.0, bottom=0.57)
        fNames.worksheet.print_area(self.begRow, self.begCol, self.endRow, self.endCol)
        
        self.fileNameEntry.delete(0, tk.END)
        self.fileNameEntry.insert(0, fNames.xlsxOutputFile)
    