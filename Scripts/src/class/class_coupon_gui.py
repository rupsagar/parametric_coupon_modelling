import os
import sys
import shutil
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory

class coupon_gui():
    def __init__(self, abqPath, srcPath, couponDatabase):
        self.abqPath = abqPath
        self.srcPath = srcPath
        self.couponDatabase = couponDatabase
        self.createGUI()
    def createGUI(self):
        windowGUI = tk.Tk()
        windowGUI.title('Coupon Modelling')
        self.dispWidth, self.dispHeight = int(windowGUI.winfo_screenwidth()), int(windowGUI.winfo_screenheight())
        self.windowGUIWidth, self.windowGUIHeight = 0.5*self.dispWidth, 0.8*self.dispHeight
        windowGUI.geometry('%dx%d' % (self.windowGUIWidth, self.windowGUIHeight))
        # self.windowGUI.state('zoomed')
        def totalNumKeys(dictData):
            numKeys = 0
            for val in dictData.values():
                if isinstance(val, dict):
                    numKeys = numKeys+totalNumKeys(val)
                else:
                    numKeys = numKeys+1
            return numKeys
        def populateParams(dictData, keyStr='', xCount=0, yCount=0):
            self.xCount, self.yCount = xCount, yCount
            for key, val in dictData.items():
                if isinstance(val, dict):
                    populateParams(val, key+': ', self.xCount, self.yCount)
                    continue
                if key=='couponName':
                    continue
                paramLabel = ttk.Label(self.paramFrame, text=keyStr+key)
                paramLabel.place(x=(0.02+0.5*self.xCount)*self.paramFrameWidth, y=(0.015+0.04*self.yCount)*self.paramFrameHeight)
                paramEntry = tk.Entry(self.paramFrame)
                paramEntry.place(x=(0.25+0.5*self.xCount)*self.paramFrameWidth, y=(0.015+0.04*self.yCount)*self.paramFrameHeight)
                paramEntry.insert(0, val)
                self.modelData.append(paramEntry)
                if (self.radioVar.get()==1 and (keyStr=='geometry: ' or key=='lenTol' or key=='givenKt')): 
                    ## or (self.radioVar.get()==2 and (key=='lenTol' or key=='givenKt'))):
                    paramEntry.config(state='readonly')
                self.yCount = self.yCount+1
                if self.yCount>=math.ceil((self.totalNumParam-1)/2.0):
                    self.xCount = self.xCount+1
                    self.yCount = 0
        def readParam(dictData):
            for key, val in dictData.items():
                if isinstance(val, dict):
                    dictData[key] = readParam(val.copy())
                    continue
                if key=='couponName':
                    dictData[key] = self.couponDropDown.get() if self.radioVar.get()==1 else self.couponNameEntry.get()
                    continue
                if key=='version' and self.modelData[self.iRetrieve].get()!='':
                    dictData[key] = '_'+self.modelData[self.iRetrieve].get()
                    continue
                try:
                    dictData[key] = float(eval(self.modelData[self.iRetrieve].get()))
                except:
                    dictData[key] = self.modelData[self.iRetrieve].get()
                self.iRetrieve = self.iRetrieve+1
            return dictData
        def callAbaqus():
            statusFileName = 'statusInfo.txt'
            abqCall = 'abaqus cae noGUI="'+self.srcPath+'/util/util_call_abaqus.py" -- '+statusFileName+' '+self.jsonFileName+' '+templateDropDown.get()+' "'+self.pathEntry.get()+'" "'+self.srcPath+'"'
            sys.path.append(self.abqPath)
            os.system(abqCall)
            statusFile = open(self.pathEntry.get()+'/'+statusFileName, 'r')
            msgText = statusFile.read()
            statusFile.close()
            os.remove(self.pathEntry.get()+'/'+statusFileName)
            if os.path.exists(self.srcPath+'/abaqus.rpy'):
                os.remove(self.srcPath+'/abaqus.rpy')
                os.remove(self.srcPath+'/abaqus_acis.log')
            messagebox.showinfo('Status Info', msgText)
            # runCommand = 'cmd.exe /c'+abqCall
            # process = subprocess.Popen(runCommand)
        def createModel():
            if self.pathEntry.get()=='' or (self.radioVar.get()==2 and self.couponNameEntry.get()==''):
                    messagebox.showinfo('Input Check', 'Enter save location and/or coupon name')
                    return
            self.iRetrieve = 0
            self.couponOutput = readParam(self.couponParams.copy())
            couponType = 'Built-In' if self.radioVar.get()==1 else 'Custom'
            self.couponOutput.update({'couponTemplate':templateDropDown.get(), 'couponType':couponType,'savePath':self.pathEntry.get()})
            couponString = json.dumps(self.couponOutput, indent=4, sort_keys=True)
            self.jsonFileName = self.couponOutput['couponName']+'_Data'+self.couponOutput['version']+'.json'
            couponJson = open(self.pathEntry.get()+'/'+self.jsonFileName, 'w')
            couponJson.write(couponString)
            couponJson.close()
            try:
                callAbaqus()
            except Exception as errMsg:
                messagebox.showinfo('Status Info', str(errMsg))
        def selectFolder():
            self.path = askdirectory()
            self.pathEntry.config(state='normal')
            self.pathEntry.delete(0, tk.END)
            self.pathEntry.insert(0, self.path)
            self.pathEntry.config(state='readonly')
        def selectCoupon(event):
            self.paramFrameWidth, self.paramFrameHeight = 0.96*self.typeFrameWidth, 0.85*self.typeFrameHeight
            self.paramFrame = ttk.LabelFrame(self.typeFrame, text='Coupon parameters', width=self.paramFrameWidth, height=self.paramFrameHeight)
            self.paramFrame.place(x=0.02*self.typeFrameWidth, y=0.09*self.typeFrameHeight)
            self.couponParams = self.couponDatabase[templateDropDown.get()][self.couponDropDown.get()]
            self.currentCouponID = self.couponDropDown.current()
            self.totalNumParam = totalNumKeys(self.couponParams)
            self.modelData = []
            populateParams(self.couponParams)
            pathLabel = ttk.Label(self.paramFrame, text='Model save location')
            pathLabel.place(x=0.02*self.paramFrameWidth, y=0.8*self.paramFrameHeight)
            self.pathEntry = tk.Entry(self.paramFrame, state='readonly')
            self.pathEntry.place(x=0.2*self.paramFrameWidth, y=0.8*self.paramFrameHeight, width = 0.6*self.paramFrameWidth)
            selectFolderButton = ttk.Button(self.paramFrame, text='Select Folder', command=selectFolder)
            selectFolderButton.place(x=0.85*self.paramFrameWidth, y=0.795*self.paramFrameHeight)
            self.createModelButton = ttk.Button(self.paramFrame, text='Create Model', command=createModel)
            self.createModelButton.place(x=0.4*self.paramFrameWidth, y=0.9*self.paramFrameHeight)
        def radioSelection():
            self.couponOptions = list(self.couponDatabase[templateDropDown.get()].keys())
            self.labelBuiltIn = ttk.Label(self.typeFrame, text='Select built-in coupon')
            self.labelBuiltIn.place(x=0.02*self.typeFrameWidth, y=0.05*self.typeFrameHeight)
            self.couponDropDown = ttk.Combobox(self.typeFrame, values=self.couponOptions, state='readonly')
            self.couponDropDown.place(x=0.25*self.typeFrameWidth, y=0.05*self.typeFrameHeight)
            self.couponDropDown.bind('<<ComboboxSelected>>', selectCoupon)
            self.couponDropDown.set(self.couponOptions[self.currentCouponID])
            selectCoupon(self.couponOptions[self.currentCouponID])
            self.labelCustom = ttk.Label(self.typeFrame, text='Enter coupon name')
            self.labelCustom.place(x=0.5*self.typeFrameWidth, y=0.05*self.typeFrameHeight)
            self.couponNameEntry = ttk.Entry(self.typeFrame)
            self.couponNameEntry.place(x=0.75*self.typeFrameWidth, y=0.05*self.typeFrameHeight)     
            if self.radioVar.get()==1:
                self.couponNameEntry.config(state='readonly')
        def templateSelection(event):
            self.typeFrameWidth, self.typeFrameHeight = 0.96*self.windowGUIWidth, 0.9*self.windowGUIHeight
            self.typeFrame = ttk.LabelFrame(windowGUI, text='Coupon type', width=self.typeFrameWidth, height=self.typeFrameHeight)
            self.typeFrame.place(x=0.02*self.windowGUIWidth, y=0.06*self.windowGUIHeight)
            self.radioVar = tk.IntVar()
            self.radioBuiltIn = ttk.Radiobutton(self.typeFrame, text='Built-in model', variable=self.radioVar, value=1, command=radioSelection)
            self.radioBuiltIn.place(x=0.01*self.typeFrameWidth, y=0.01*self.typeFrameHeight)
            self.radioCustom = ttk.Radiobutton(self.typeFrame, text='Custom model', variable=self.radioVar, value=2, command=radioSelection)
            self.radioCustom.place(x=0.5*self.typeFrameWidth, y=0.01*self.typeFrameHeight)
            self.radioVar.set(1)
            self.currentCouponID = 0
            radioSelection()
        ## get template
        templateLabel = ttk.Label(windowGUI, text='Select coupon template')
        templateLabel.place(x=0.02*self.windowGUIWidth, y=0.02*self.windowGUIHeight)
        templateOptions = list(self.couponDatabase.keys())
        templateDropDown = ttk.Combobox(windowGUI, values=templateOptions, state='readonly')
        templateDropDown.place(x=0.25*self.windowGUIWidth, y=0.02*self.windowGUIHeight)
        templateDropDown.bind('<<ComboboxSelected>>', templateSelection)
        windowGUI.mainloop()

        if os.path.isdir(self.srcPath+'/class/__pycache__'):
            shutil.rmtree(self.srcPath+'/class/__pycache__')
