import os
import sys
import importlib
import json
import ast

srcPath = sys.argv[-1]
savePath = sys.argv[-2]
template = sys.argv[-3]
tempDataFileName = sys.argv[-4]
statusFileName = sys.argv[-5]

textSuccess = r'SUCCESS! Model created successfully.'
textFail = r'FAILED! Model cannot be created.'
statusFile = open(savePath+'/'+statusFileName, 'w')

try:
    fileJson = open(savePath+'/'+tempDataFileName, 'r')
    couponDataUnicode = json.load(fileJson)
    fileJson.close()
    couponData = ast.literal_eval(json.dumps(couponDataUnicode))
    
    sys.path.append(srcPath+'/class')
    couponDef = getattr(importlib.import_module('class_'+template.lower()), template.lower())
    os.chdir(savePath)
    couponDef(couponData)
    statusFile.write(textSuccess)
except Exception as err:
    statusFile.write(textFail+'\nError Message: '+str(err))

if os.path.exists(srcPath+'/class/class_'+template.lower()+'.pyc'):
    os.remove(srcPath+'/class/class_'+template.lower()+'.pyc')

statusFile.close()
sys.exit()
