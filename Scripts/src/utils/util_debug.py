import json, ast, sys

def debug(srcPath, template, coupon):
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
    except Exception as err:
        print(str(err))
        self = None
    return self

