srcPath = r'D:\Academics\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts Space\src'
template = 'Coupon_70_73_A'
coupon = 'Coupon_70A'

import json
import ast
import sys
import importlib
import os

try:
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
    
    couponDataStr = convertJsonDataToStr(couponData)
    sys.path.append(srcPath+'/class')
    couponDef = getattr(importlib.import_module('class_'+template.lower()), template.lower())
    self = couponDef(couponDataStr)
except Exception as err:
    print(str(err))

if os.path.exists(srcPath+'/class/class_'+template.lower()+'.pyc'):
    os.remove(srcPath+'/class/class_'+template.lower()+'.pyc')

