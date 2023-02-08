abqPath = 'C:/SIMULIA/Commands'

import os
import sys
import importlib
import json
import ast

srcPath = os.getcwd()
srcPath.replace('\\','/')

## read coupon json database
couponJson = open(srcPath+'/database/database_coupon.json')
couponDictUnicode = json.load(couponJson)
couponJson.close()
couponDict = ast.literal_eval(json.dumps(couponDictUnicode))

## create gui window
sys.path.append(srcPath+'/class')
couponGUI = getattr(importlib.import_module('class_coupon_gui'), 'coupon_gui')
newGUI = couponGUI(abqPath, srcPath, couponDict)
