import os
import sys
import json
import ast
import imp

srcPath = sys.argv[-1]
savePath = sys.argv[-2]
template = sys.argv[-3]
tempDataFileName = sys.argv[-4]
statusFileName = sys.argv[-5]

statusFile = open(savePath+'/'+statusFileName, 'w')

try:
    fileJson = open(savePath+'/'+tempDataFileName, 'r')
    couponDataUnicode = json.load(fileJson)
    fileJson.close()
    couponData = ast.literal_eval(json.dumps(couponDataUnicode))

    coupunModule = imp.load_source('class_'+template.lower(), srcPath+'/classes/class_'+template.lower()+'.py')
    couponClass = getattr(coupunModule, template.lower())
    os.chdir(savePath)
    couponClass(couponData)
    if os.path.exists(srcPath+'/classes/class_'+template.lower()+'.pyc'):
        os.remove(srcPath+'/classes/class_'+template.lower()+'.pyc')

    statusFile.write('SUCCESS! Model created successfully.')
except Exception as err:
    statusFile.write('FAILED! Model cannot be created.\nError Message: '+str(err))

statusFile.close()
sys.exit()

