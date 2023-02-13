## user may need to modify this path depending on local machine or OS
abqPath = [r'C:/SIMULIA/Commands']

import os
import imp

srcPath = os.getcwd()

## create gui window
guiModule = imp.load_source('class_coupon_gui', srcPath+'/class/class_coupon_gui.py')
guiClass = getattr(guiModule, 'coupon_gui')
newGUI = guiClass(abqPath, srcPath)
