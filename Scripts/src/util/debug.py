#################################################################################################################
######################                 ABAQUS PARAMETRIC COUPON MODEL                     #######################
#################################################################################################################
####################################    UTILITY SCRIPT : FOR DEBUGGING   ########################################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Mar-2023 |                                                 |
## |        Rupsagar Chatterjee     |   v2.0    | 08-Aug-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import json, ast, sys

def debug(srcPath, template, coupon):
    statusFile = open(coupon+'_Status.txt', 'w')
    try:
        masterDatabaseJson = open(srcPath+'/db/coupon_master.json', 'r')
        masterDatabaseUnicode = json.load(masterDatabaseJson)
        masterDatabaseJson.close()
        masterDatabase = ast.literal_eval(json.dumps(masterDatabaseUnicode))
        
        couponDatabaseJson = open(srcPath+'/db/'+template.lower()+'.json', 'r')
        couponDatabaseUnicode = json.load(couponDatabaseJson)
        couponDatabaseJson.close()
        couponDatabase = ast.literal_eval(json.dumps(couponDatabaseUnicode))
        
        ## create input coupon data
        couponData = couponDatabase[template][coupon]
        couponData.update(masterDatabase['Coupon_Data'][template])
        couponData.update({'Coupon_Name':coupon})
        couponData.update(masterDatabase['Constant_Data'])
        tempMaterial = dict()
        for thisMaterial, i in zip(couponData['Material'], range(len(couponData['Material']))):
            tempMaterial['Material_'+str(i+1)] = masterDatabase['Material_Data'][thisMaterial].copy()
        couponData.update({'Material':tempMaterial})

        execfile(srcPath+'/lib/coupon_generic.py', globals())
        execfile(srcPath+'/lib/'+template.lower()+'.py', globals())
        couponClass = getattr(sys.modules[__name__], template.lower())
        self = couponClass(couponData)
        statusFile.write('SUCCESS! Model created successfully.')
    except Exception as err:
        print(str(err))
        statusFile.write('FAILED! Model cannot be created.\nError Message: '+str(err))
        self = None
    statusFile.close()
    return self

