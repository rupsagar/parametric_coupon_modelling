srcPath = r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\01_WIP\Scripts\src'
template = 'Coupon_70_73_BE'
coupon = 'Coupon_70C'

import json
import ast
import sys
import importlib
import os
import shutil

# try:
databaseJson = open(srcPath+'/database/database_coupon.json', 'r')
databaseUnicode = json.load(databaseJson)
databaseJson.close()
couponDatabase = ast.literal_eval(json.dumps(databaseUnicode))
couponData = couponDatabase[template][coupon]

def convertJsonDataToStr(dictData):
    for key, val in dictData.items():
        if isinstance(val, dict):
            convertJsonDataToStr(val)
            continue
        if not isinstance(val, str):
            dictData[key] = str(val)
    return dictData

import imp

def createCoupon():
    couponDataStr = convertJsonDataToStr(couponData)
    sys.path.append(srcPath+'/class')
    foo = imp.load_source('class_'+template.lower()+'.py', srcPath+'/class/class_'+template.lower()+'.py')
    couponDef = getattr(importlib.import_module('class_'+template.lower()), template.lower())
    foo_class = getattr(foo, template.lower())
    coupon = couponDef(couponDataStr)
    foo_class(couponDataStr)
    return coupon

self = createCoupon()

# except Exception as err:
#     print(str(err))

if os.path.exists(srcPath+'/class/class_'+template.lower()+'.pyc'):
    os.remove(srcPath+'/class/class_'+template.lower()+'.pyc')

if os.path.isdir(srcPath+'/class/__pycache__'):
    shutil.rmtree(srcPath+'/class/__pycache__')

