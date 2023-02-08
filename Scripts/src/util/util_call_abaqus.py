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

savePath = savePath.replace(' ', '\\ ')
os.chdir(savePath)

fileJson = open(savePath+'/'+tempDataFileName)
couponDatabaseUnicode = json.load(fileJson)
fileJson.close()
couponDatabase = ast.literal_eval(json.dumps(couponDatabaseUnicode))

if os.path.exists(savePath+'/'+statusFileName):
    os.remove(savePath+'/'+statusFileName)
statusFile = open(savePath+'/'+statusFileName, 'w')

textSuccess = 'SUCCESS! Model created successfully.'
textFail = 'FAILED! Model cannot be created.'

sys.path.append(srcPath+'/class')
couponDef = getattr(importlib.import_module('class_'+template.lower()), template.lower())
try:
    couponDef(couponDatabase)
    statusFile.write(textSuccess)
except Exception as e:
    statusFile.write(textFail+'\nError Message: '+str(e))
os.remove(srcPath+'/class/class_'+template.lower()+'.pyc')

statusFile.close()
sys.exit()
