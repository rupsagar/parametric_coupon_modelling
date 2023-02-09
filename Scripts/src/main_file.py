## may need to modify this path depending on local machine or OS
abqPath = 'C:/SIMULIA/Commands'

import os
import imp
import json
import ast

srcPath = os.getcwd()

## read coupon json database
couponJson = open(srcPath+'/database/database_coupon.json', 'r')
couponDictUnicode = json.load(couponJson)
couponJson.close()
couponDict = ast.literal_eval(json.dumps(couponDictUnicode))

## create gui window
guiModule = imp.load_source('class_coupon_gui', srcPath+'/class/class_coupon_gui.py')
guiClass = getattr(guiModule, 'coupon_gui')
newGUI = guiClass(abqPath, srcPath, couponDict)
