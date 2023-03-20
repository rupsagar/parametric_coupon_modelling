import json, ast, sys

def debug(srcPath, template, coupon):
    statusFile = open(coupon+'_Status.txt', 'w')
    try:
        databaseJson = open(srcPath+'/databases/database_coupon.json', 'r')
        databaseUnicode = json.load(databaseJson)
        databaseJson.close()
        couponDatabase = ast.literal_eval(json.dumps(databaseUnicode))
        couponData = couponDatabase[template][coupon]
        
        execfile(srcPath+'/classes/class_coupon_generic.py', globals())
        execfile(srcPath+'/classes/class_'+template.lower()+'.py', globals())
        couponClass = getattr(sys.modules[__name__], template.lower())
        self = couponClass(couponData)
        statusFile.write('SUCCESS! Model created successfully.')
    except Exception as err:
        print(str(err))
        statusFile.write('FAILED! Model cannot be created.\nError Message: '+str(err))
        self = None
    statusFile.close()
    return self

