## Modify the template and coupon lines for debugging purpose and copy+paste or run the script in Abaqus CLI
## The srcPath list contains possible paths for src folder which may need to be updated based on where the script is located
srcPath = [r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\01_WIP\Scripts\src', 
        r'D:\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src']

# template = 'Fatigue_Coupon_66_69_A'
# coupon = 'Fatigue_Coupon_67A'

# template = 'Fatigue_Coupon_66_69_BJ'
# coupon = 'Fatigue_Coupon_66E'

# template = 'Fatigue_Coupon_70_73_A'
# coupon = 'Fatigue_Coupon_70A'

template = 'Fatigue_Coupon_70_73_BE'
coupon = 'Fatigue_Coupon_73E'

# template = 'Fatigue_Coupon_74_75'
# coupon = 'Fatigue_Coupon_74'

# template = 'Static_Coupon_1_1_7'
# coupon = 'Static_Coupon_1_7'

# template = 'Static_Coupon_2_1_6'
# coupon = 'Static_Coupon_2_6'

import os, sys

for i in range(len(srcPath)):
    if os.path.isdir(srcPath[i]):
        srcPathID = i
        break

execfile(srcPath[srcPathID]+'/utils/util_debug.py')
debugFunc = getattr(sys.modules[__name__], 'debug')
self = debugFunc(srcPath[srcPathID], template, coupon)
