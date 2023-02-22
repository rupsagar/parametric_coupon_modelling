## user may need to modify this path depending on local machine or OS
abqPath = [r'C:/SIMULIA/Commands']

import os, imp

srcPath = os.getcwd()

## create gui window
guiModule = imp.load_source('class_coupon_gui', srcPath+'/classes/class_coupon_gui.py')
guiClass = getattr(guiModule, 'coupon_gui')
newGUI = guiClass(abqPath, srcPath)

