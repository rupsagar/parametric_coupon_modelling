## Modify the template and coupon lines for debugging purpose and copy+paste or run the script in Abaqus CLI
## The srcPath list contains possible paths for src folder which may need to be updated based on where the script is located
srcPath = [r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\01_WIP\Scripts\src', 
        r'D:\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src']

# template = 'Fatigue_Coupon_66_69_A'
# coupon = 'Fatigue_Coupon_67A'

# template = 'Fatigue_Coupon_66_69_BJ'
# coupon = 'Fatigue_Coupon_66C'

# template = 'Fatigue_Coupon_70_73_A'
# coupon = 'Fatigue_Coupon_70A'

# template = 'Fatigue_Coupon_70_73_BE'
# coupon = 'Fatigue_Coupon_70C'

# template = 'Fatigue_Coupon_74_75'
# coupon = 'Fatigue_Coupon_74'

# template = 'Static_Coupon_1_1_7'
# coupon = 'Static_Coupon_1_5'

# template = 'Static_Coupon_2_1_6'
# coupon = 'Static_Coupon_2_4'

import json
import ast
import os
import sys

try:
    for i in range(len(srcPath)):
        if os.path.isdir(srcPath[i]):
            srcPathID = i
            break

    databaseJson = open(srcPath[srcPathID]+'/databases/database_coupon.json', 'r')
    databaseUnicode = json.load(databaseJson)
    databaseJson.close()
    couponDatabase = ast.literal_eval(json.dumps(databaseUnicode))
    couponData = couponDatabase[template][coupon]
    
    currentPath = os.getcwd()
    os.chdir(srcPath[srcPathID]+'/classes')
    try:
        execfile('class_coupon_generic.py')
        execfile('class_'+template.lower()+'.py')
        couponClass = getattr(sys.modules[__name__], template.lower())
    except:
        pass
    os.chdir(currentPath)

    self = couponClass(couponData)
except Exception as err:
    print(str(err))
    self = None

