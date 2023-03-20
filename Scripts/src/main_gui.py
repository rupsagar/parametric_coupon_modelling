## user may need to modify this path depending on local machine or OS
abqPath = [r'C:/SIMULIA/Commands']

import os, sys

srcPath = os.getcwd()

## create gui window
exec(open(srcPath+'/classes/class_coupon_gui.py').read())
guiClass = getattr(sys.modules[__name__], 'coupon_gui')
newGUI = guiClass(abqPath, srcPath)
