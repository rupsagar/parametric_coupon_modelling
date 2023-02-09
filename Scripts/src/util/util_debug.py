## modify these 3 lines for debugging purpose and copy/paste (or run) in Abaqus CLI
srcPath = r'D:\Academics\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src'
template = 'Coupon_70_73_BE'
coupon = 'Coupon_70C'

import json
import ast
import imp
import os
import shutil

try:
    databaseJson = open(srcPath+'/database/database_coupon.json', 'r')
    databaseUnicode = json.load(databaseJson)
    databaseJson.close()
    couponDatabase = ast.literal_eval(json.dumps(databaseUnicode))
    couponData = couponDatabase[template][coupon]

    couponModule = imp.load_source('class_'+template.lower(), srcPath+'/class/class_'+template.lower()+'.py')
    couponClass = getattr(couponModule, template.lower())
    self = couponClass(couponData)

    if os.path.exists(srcPath+'/class/class_'+template.lower()+'.pyc'):
        os.remove(srcPath+'/class/class_'+template.lower()+'.pyc')

    if os.path.isdir(srcPath+'/class/__pycache__'):
        shutil.rmtree(srcPath+'/class/__pycache__')
except Exception as err:
    print(str(err))

