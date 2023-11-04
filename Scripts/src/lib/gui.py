#################################################################################################################
######################                 ABAQUS PARAMETRIC COUPON MODEL                     #######################
#################################################################################################################
############################    CLASS DEFINITION : GRAPHICAL USER INTERFACE   ###################################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Mar-2023 |                                                 |
## |        Rupsagar Chatterjee     |   v2.0    | 08-Aug-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import os, sys, shutil, json, ast, math
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
from PIL import ImageTk, Image

class gui():
    def __init__(self, abqPath, srcPath):
        self.abqPath = abqPath
        self.srcPath = srcPath
        ## set window sizes
        self.windowSize = 'custom'
        self.initialYSpacing = 0.01
        self.ySpacing = 0.035
        ## read coupon json database
        couponMasterJson = open(self.srcPath+'/database/coupon_master.json', 'r')
        couponMasterDictUnicode = json.load(couponMasterJson)
        couponMasterJson.close()
        self.masterDatabase = ast.literal_eval(json.dumps(couponMasterDictUnicode))
        ## read coupon gui database
        couponGUIJson = open(self.srcPath+'/database/coupon_gui.json', 'r')
        couponGUIDictUnicode = json.load(couponGUIJson)
        couponGUIJson.close()
        self.GUIDatabase = ast.literal_eval(json.dumps(couponGUIDictUnicode))
        ## clear old cache files
        if os.path.isdir(self.srcPath+'/class/__pycache__'):
            shutil.rmtree(self.srcPath+'/class/__pycache__')
        self.createGUI()
    def createGUI(self):
        ## create GUI
        self.windowGUI = tk.Tk()
        self.windowGUI.title('Parametric Coupon Modelling')
        self.dispWidth, self.dispHeight = int(self.windowGUI.winfo_screenwidth()), int(self.windowGUI.winfo_screenheight())
        if self.windowSize=='custom':
            self.windowSizeArr = [0.9, 0.9]
            self.windowGUIWidth, self.windowGUIHeight = self.windowSizeArr[0]*self.dispWidth, self.windowSizeArr[1]*self.dispHeight
            self.windowGUI.geometry('%dx%d' %(self.windowGUIWidth, self.windowGUIHeight))
        elif self.windowSize=='zoomed':
            self.windowGUI.state('zoomed')
            self.windowGUIWidth, self.windowGUIHeight = self.dispWidth, self.dispHeight
        ## create menu bar
        self.createMenu()
        ## get selected template
        self.template()
        self.windowGUI.mainloop()
    def createMenu(self):
        menuBar = tk.Menu(self.windowGUI)
        self.windowGUI.config(menu=menuBar)
        ## file menu
        fileMenu = tk.Menu(menuBar, tearoff="off")
        fileMenu.add_command(label='Exit', compound='left', command=self.windowGUI.destroy)
        menuBar.add_cascade(label="File", menu=fileMenu, underline=0)
        ## help menu
        # helpMenu = tk.Menu(menuBar, tearoff="off")
        # helpMenu.add_command(label='About', compound='left', command=self.windowGUI.destroy)
        # menuBar.add_cascade(label="Help", menu=helpMenu, underline=0)
    def template(self):
        templateLabel = ttk.Label(self.windowGUI, text='Select coupon template')
        templateLabel.place(x=0.02*self.windowGUIWidth, y=0.02*self.windowGUIHeight)
        templateOptions = list(self.masterDatabase['Coupon_Data'].keys())
        self.templateDropDown = ttk.Combobox(self.windowGUI, values=templateOptions, state='readonly')
        self.templateDropDown.place(x=0.25*self.windowGUIWidth, y=0.02*self.windowGUIHeight, width=0.3*self.windowGUIWidth)
        self.templateDropDown.bind('<<ComboboxSelected>>', self.templateSelection)
    def templateSelection(self, event):
        ## dropdown event for template selection
        self.typeFrameWidth, self.typeFrameHeight = 0.96*self.windowGUIWidth, 0.9*self.windowGUIHeight
        self.typeFrame = ttk.LabelFrame(self.windowGUI, text='Coupon type', width=self.typeFrameWidth, height=self.typeFrameHeight)
        self.typeFrame.place(x=0.02*self.windowGUIWidth, y=0.06*self.windowGUIHeight)
        self.radioVar = tk.IntVar()
        self.radioBuiltIn = ttk.Radiobutton(self.typeFrame, text='Built-in model', variable=self.radioVar, value=1, command=self.radioSelection)
        self.radioBuiltIn.place(x=0.01*self.typeFrameWidth, y=0.01*self.typeFrameHeight)
        self.radioCustom = ttk.Radiobutton(self.typeFrame, text='Custom model', variable=self.radioVar, value=2, command=self.radioSelection)
        self.radioCustom.place(x=0.5*self.typeFrameWidth, y=0.01*self.typeFrameHeight)
        self.radioVar.set(1)
        self.currentCouponID = 0
        self.radioSelection()
        ## create label for save location
        pathLabel = ttk.Label(self.typeFrame, text='Model save location')
        pathLabel.place(x=0.02*self.typeFrameWidth, y=0.85*self.typeFrameHeight)
        ## create path entry field
        self.pathEntry = tk.Entry(self.typeFrame, state='readonly')
        self.pathEntry.place(x=0.2*self.typeFrameWidth, y=0.85*self.typeFrameHeight, width = 0.6*self.typeFrameWidth)
        ## create button for entering file path
        selectFolderButton = ttk.Button(self.typeFrame, text='Select Folder', command=self.selectFolder)
        selectFolderButton.place(x=0.85*self.typeFrameWidth, y=0.845*self.typeFrameHeight)
        ## create button for running model creation script
        self.createModelButton = ttk.Button(self.typeFrame, text='Create Model', command=self.createModel)
        self.createModelButton.place(x=0.4*self.typeFrameWidth, y=0.9*self.typeFrameHeight)
    def radioSelection(self):
        ## radio button for built-in and custom model
        self.couponDatabaseJson = open(self.srcPath+'/database/'+self.templateDropDown.get().lower()+'.json', 'r')
        couponDatabaseUnicode = json.load(self.couponDatabaseJson)
        self.couponDatabaseJson.close()
        self.couponDatabase = ast.literal_eval(json.dumps(couponDatabaseUnicode))
        self.couponOptions = list(self.couponDatabase[self.templateDropDown.get()].keys())
        self.labelBuiltIn = ttk.Label(self.typeFrame, text='Select built-in coupon')
        self.labelBuiltIn.place(x=0.02*self.typeFrameWidth, y=0.05*self.typeFrameHeight)
        self.couponDropDown = ttk.Combobox(self.typeFrame, values=self.couponOptions, state='readonly')
        self.couponDropDown.place(x=0.2*self.typeFrameWidth, y=0.05*self.typeFrameHeight, width=0.25*self.typeFrameWidth)
        self.couponDropDown.bind('<<ComboboxSelected>>', self.selectCoupon)
        self.couponDropDown.set(self.couponOptions[self.currentCouponID])
        self.selectCoupon(self.couponOptions[self.currentCouponID])
        self.labelCustom = ttk.Label(self.typeFrame, text='Enter coupon name')
        self.labelCustom.place(x=0.5*self.typeFrameWidth, y=0.05*self.typeFrameHeight)
        self.couponNameEntry = ttk.Entry(self.typeFrame)
        self.couponNameEntry.place(x=0.7*self.typeFrameWidth, y=0.05*self.typeFrameHeight, width=0.25*self.typeFrameWidth)     
        if self.radioVar.get()==1:
            self.couponNameEntry.config(state='readonly')
    def selectCoupon(self, event):
        ## label frame for selecting coupon
        self.paramFrameWidth, self.paramFrameHeight = 0.96*self.typeFrameWidth, 0.75*self.typeFrameHeight
        self.paramFrame = ttk.LabelFrame(self.typeFrame, text='Coupon parameters', width=self.paramFrameWidth, height=self.paramFrameHeight)
        self.paramFrame.place(x=0.02*self.typeFrameWidth, y=0.09*self.typeFrameHeight)
        self.dataFrame = self.paramFrame
        self.canvasFrameWidth, self.canvasFrameHeight = 0.5*self.paramFrameWidth, 1*self.paramFrameHeight
        ## create input coupon data
        self.couponParams = self.couponDatabase[self.templateDropDown.get()][self.couponDropDown.get()].copy()
        self.couponParams.update(self.masterDatabase['Coupon_Data'][self.templateDropDown.get()])
        self.couponParams.update({'Coupon_Name':self.couponDropDown.get()})
        self.couponParams.update(self.masterDatabase['Constant_Data'])
        tempMaterial = dict()
        for thisMaterial, i in zip(self.couponParams['Material'], range(len(self.couponParams['Material']))):
            tempMaterial['Material_'+str(i+1)] = self.masterDatabase['Material_Data'][thisMaterial].copy()
        self.couponParams.update({'Material':tempMaterial})
        ## create GUI info
        self.couponGUIParams = self.GUIDatabase['Coupon_Data'][self.templateDropDown.get()].copy()
        self.couponGUIParams.update({'Coupon_Name':["display-no", "editable-no"]})
        self.couponGUIParams.update(self.GUIDatabase['Constant_Data'])
        self.couponGUIParams['Material'] = self.couponParams['Material'].copy()
        for key in self.couponGUIParams['Material'].keys():
            self.couponGUIParams['Material'][key] = self.GUIDatabase['Material_Data']['Material_ID'].copy()
        ## populate data frame
        self.currentCouponID = self.couponDropDown.current()
        self.totalNumParam = self.totalNumKeys(self.couponGUIParams)
        self.modelData = []
        self.populateParams(self.couponParams, self.couponGUIParams)
        ## populate coupon figure
        self.imageSlider()
    def totalNumKeys(self, dictData):
        numKeys = 0
        for val in dictData.values():
            if isinstance(val, dict):
                tempNumKeys = numKeys
                numKeys = numKeys+self.totalNumKeys(val)
                if numKeys>tempNumKeys:
                    numKeys = numKeys+1
            elif val[0]=='display-yes':
                numKeys = numKeys+1
        return numKeys
    def populateParams(self, dictData, guiData, keyStr='', xCount=0, yCount=0, heading=False, dataBlock=False):
        ## populate GUI with built-in data
        self.xCount, self.yCount, self.heading, self.dataBlock = xCount, yCount, heading, dataBlock
        for key, val in dictData.items():                
            if self.yCount>=math.ceil((self.totalNumParam-1)/2.0) and self.dataBlock==False:
                self.xCount = self.xCount+1
                self.yCount = 0
            if isinstance(val, dict):  
                self.populateParams(val, guiData[key], keyStr+key+': ', self.xCount, self.yCount, True, True)
                self.dataBlock = False
                continue
            else:
                if keyStr!='' and self.heading:
                    paramLabel = ttk.Label(self.dataFrame, text=keyStr, font=('bold', '11'))
                    paramLabel.place(x=(0.02+0.5*self.xCount)*self.canvasFrameWidth, y=(self.initialYSpacing+self.ySpacing*self.yCount)*self.canvasFrameHeight)
                    self.heading = False
                    self.yCount = self.yCount+1
                if guiData[key][0]=='display-no':
                    continue
                paramLabel = ttk.Label(self.dataFrame, text=key+': ')
                paramLabel.place(x=(0.02+0.5*self.xCount)*self.canvasFrameWidth, y=(self.initialYSpacing+self.ySpacing*self.yCount)*self.canvasFrameHeight)
                if self.dataBlock == False:
                    paramLabel.config(font=('bold','11'))
                paramEntry = tk.Entry(self.dataFrame)
                paramEntry.place(x=(0.25+0.5*self.xCount)*self.canvasFrameWidth, y=(self.initialYSpacing+self.ySpacing*self.yCount)*self.canvasFrameHeight)
                paramEntry.insert(0, val)
                if (self.radioVar.get()==1 and guiData[key][1]=='editable-no'):
                    paramEntry.config(state='readonly')
                self.modelData.append(paramEntry)
                self.yCount = self.yCount+1
    def selectFolder(self):
        ## select file save path
        self.path = askdirectory()
        self.pathEntry.config(state='normal')
        self.pathEntry.delete(0, tk.END)
        self.pathEntry.insert(0, self.path)
        self.pathEntry.config(state='readonly')
    def createModel(self):
        ## model create button event
        if self.pathEntry.get()=='' or (self.radioVar.get()==2 and self.couponNameEntry.get()==''):
            messagebox.showinfo('Input Check', 'Enter save location and/or coupon name')
            return
        ## read the input data
        self.couponOutput = self.readParam(self.couponParams.copy(), self.couponGUIParams)
        self.couponName = self.couponOutput['Coupon_Name']
        self.version = self.couponOutput['Version'] if self.couponOutput['Version']=='' else '_'+self.couponOutput['Version']
        ## final coupon json
        couponType = 'Built-In' if self.radioVar.get()==1 else 'Custom'
        self.couponOutput.update({'Coupon_Template':self.templateDropDown.get(), 'Coupon_Type':couponType, 'Save_Path':self.pathEntry.get()})
        couponString = json.dumps(self.couponOutput, indent=4, sort_keys=True)
        self.jsonFileName = self.couponName+'_Data'+self.version+'.json'
        couponMasterJson = open(self.pathEntry.get()+'/'+self.jsonFileName, 'w')
        couponMasterJson.write(couponString)
        couponMasterJson.close()
        try:
            self.callAbaqus()
        except Exception as errMsg:
            messagebox.showinfo('Status Info', str(errMsg))
    def readParam(self, dictData, guiData, idRetrieve=0):
        ## read data from GUI
        self.idRetrieve = idRetrieve
        for key, val in dictData.items():
            if isinstance(val, dict):
                dictData[key] = self.readParam(val.copy(), guiData[key], self.idRetrieve)
                continue
            else:
                if guiData[key][0]=='display-yes':
                    try:
                        dictData[key] = float(eval(self.modelData[self.idRetrieve].get()))
                    except:
                        dictData[key] = self.modelData[self.idRetrieve].get()
                    self.idRetrieve = self.idRetrieve+1
                elif guiData[key][0]=='display-no' and key=='Coupon_Name':
                    dictData[key] = self.couponDropDown.get() if self.radioVar.get()==1 else self.couponNameEntry.get()
                    continue
        return dictData
    def callAbaqus(self):
        ## call Abaqus
        statusFileName = self.couponName+'_Status'+self.version+'.txt'
        abqCall = 'abaqus cae noGUI="'+self.srcPath+'/util/call_abaqus.py" -- '+statusFileName+' '+self.jsonFileName+' '+self.templateDropDown.get()+' "'+self.pathEntry.get()+'" "'+self.srcPath+'"'
        for j in range(len(self.abqPath)):
            try:
                sys.path.append(self.abqPath[j])
            except:
                pass
        os.system(abqCall)
        statusFile = open(self.pathEntry.get()+'/'+statusFileName, 'r')
        msgText = statusFile.read()
        statusFile.close()
        if os.path.exists(self.srcPath+'/abaqus.rpy'):
            os.remove(self.srcPath+'/abaqus.rpy')
        if os.path.exists(self.srcPath+'/abaqus_acis.log'):
            os.remove(self.srcPath+'/abaqus_acis.log')
        messagebox.showinfo('Status Info', msgText)
    def imageSlider(self):
        self.imgFrameWidth, self.imgFrameHeight = 0.49*self.paramFrameWidth, .75*self.paramFrameHeight
        self.imgFrame = ttk.LabelFrame(self.paramFrame, text='Coupon figure', width=self.imgFrameWidth, height=self.imgFrameHeight)
        self.imgFrame.place(x=0.5*self.paramFrameWidth, y=0.05*self.paramFrameHeight)
        imgLabelRelWidth, imgLabelRelHeight = 0.8, 0.8
        ## parse images
        frameAspectRatio = (imgLabelRelWidth*self.imgFrameWidth)/(imgLabelRelHeight*self.imgFrameHeight)
        self.couponImg = []
        while True:
            try:
                openImgFile = Image.open(self.srcPath+'/res/img/'+self.templateDropDown.get().lower()+'/img_'+str(len(self.couponImg)+1)+'.jpg')
            except:
                break
            imgAspectRatio = ImageTk.PhotoImage(openImgFile).width()/ImageTk.PhotoImage(openImgFile).height()
            if imgAspectRatio>=frameAspectRatio:
                openImgFile = openImgFile.resize((int(imgLabelRelWidth*self.imgFrameWidth), int(int(imgLabelRelWidth*self.imgFrameWidth)/imgAspectRatio)), Image.ANTIALIAS)
            elif imgAspectRatio<frameAspectRatio:
                openImgFile = openImgFile.resize((int(int(imgLabelRelHeight*self.imgFrameHeight)*imgAspectRatio), int(imgLabelRelHeight*self.imgFrameHeight)), Image.ANTIALIAS)
            self.couponImg.append(ImageTk.PhotoImage(openImgFile))
        ## display image
        self.curImg = 0
        self.dispImg=tk.Label(self.imgFrame, image=self.couponImg[self.curImg])
        self.dispImg.image = self.couponImg
        self.dispImg.place(relx=0.1, rely=0.1, relwidth=imgLabelRelWidth, relheight=imgLabelRelHeight)
        ## left button
        self.leftButton = tk.Button(self.imgFrame, text="<", fg='red', font=('', 11, 'bold'), command=self.left)
        self.leftButton.place(relx=0.05, rely=0.45, relwidth=0.05, relheight=0.05)
        ## right button
        self.rightButton = tk.Button(self.imgFrame, text=">", fg='red', font=('', 11, 'bold'), command=self.right)
        self.rightButton.place(relx=0.9, rely=0.45, relwidth=0.05, relheight=0.05)
    def left(self):
        self.curImg = (self.curImg - 1) % len(self.couponImg)
        self.update_image()
    def right(self):
        self.curImg = (self.curImg + 1) % len(self.couponImg)
        self.update_image()
    def update_image(self):
        self.dispImg.config(image=self.couponImg[self.curImg])

