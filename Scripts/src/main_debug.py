#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
#####################################    DRIVER SCRIPT : FOR DEBUGGING    #######################################
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
## MODIFY THE TEMPLATE AND COUPON LINES FOR DEBUGGING PURPOSE AND COPY+PASTE OR RUN THE SCRIPT IN ABAQUS CLI
## USER MAY NEED TO UPDATE srcPath LIST TO INCLUDE THE SRC FOLDER WHERE THE SCRIPT IS LOCATED
#################################################################################################################


srcPath = [r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\01_WIP\Scripts\src', 
        r'D:\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src',
        r'\\fr0-svm21\St_RnT_METAL3\01-SIMU_STnS_USE_CASES\13_A350F\09_Coupon_Parametric_Modelling\Scripts\src']

# template = 'Fatigue_Coupon_66_69_A'
# coupon = 'Fatigue_Coupon_66A'

# template = 'Fatigue_Coupon_66_69_BJ'
# coupon = 'Fatigue_Coupon_69E'

# template = 'Fatigue_Coupon_70_73_A'
# coupon = 'Fatigue_Coupon_73A'

# template = 'Fatigue_Coupon_70_73_BE'
# coupon = 'Fatigue_Coupon_73E'

# template = 'Fatigue_Coupon_74_75'
# coupon = 'Fatigue_Coupon_74'

# template = 'Static_Coupon_1_Full_1_7'
# coupon = 'Static_Coupon_1_Full_5'

# template = 'Static_Coupon_1_Symmetric_1_7'
# coupon = 'Static_Coupon_1_Symmetric_7'

# template = 'Static_Coupon_2_Full_1_6'
# coupon = 'Static_Coupon_2_Full_4'

# template = 'Static_Coupon_2_Symmetric_1_6'
# coupon = 'Static_Coupon_2_Symmetric_6'

template = 'Static_Coupon_18_21'
coupon = 'Static_Coupon_18'

import os, sys

for i in range(len(srcPath)):
    if os.path.isdir(srcPath[i]):
        srcPathID = i
        break

execfile(srcPath[srcPathID]+'/utils/util_debug.py')
debugFunc = getattr(sys.modules[__name__], 'debug')
self = debugFunc(srcPath[srcPathID], template, coupon)

