## Modify the template and coupon lines for debugging purpose and copy+paste or run the script in Abaqus CLI
## The srcPath list contains possible paths for src folder which may need to be updated based on where the script is located
srcPath = [r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\01_WIP\Scripts\src', 
        r'D:\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src']

template = 'Fatigue_Coupon_66_69_A'
coupon = 'Fatigue_Coupon_66A'

# template = 'Static_Coupon_1_1_7'
# coupon = 'Static_Coupon_1_5'

# template = 'Static_Coupon_2_1_6'
# coupon = 'Static_Coupon_2_4'


import os
import imp

for i in range(len(srcPath)):
    if os.path.isdir(srcPath[i]):
        srcPathID = i
        break

debugModule = imp.load_source('util_debug', srcPath[srcPathID]+'/utils/util_debug.py')
debugFunc = getattr(debugModule, 'debug')

self = debugFunc(srcPath[srcPathID], template, coupon)

