#################################################################################################################
######################                 ABAQUS PARAMETRIC COUPON MODEL                     #######################
#################################################################################################################
##################################    UTILITY SCRIPT : FOR CALLING ABAQUS   #####################################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Mar-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import sys, os, json, ast

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

    execfile(srcPath+'/classes/class_coupon_generic.py')
    execfile(srcPath+'/classes/class_'+template.lower()+'.py')
    couponClass = getattr(sys.modules[__name__], template.lower())
    os.chdir(savePath)
    couponClass(couponData)

    statusFile.write('SUCCESS! Model created successfully.')
except Exception as err:
    statusFile.write('FAILED! Model cannot be created.\nError Message: '+str(err))

statusFile.close()
sys.exit()

