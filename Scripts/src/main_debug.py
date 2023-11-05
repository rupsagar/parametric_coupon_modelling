#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
#####################################    DRIVER SCRIPT : FOR DEBUGGING    #######################################
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
## MODIFY THE TEMPLATE AND COUPON LINES FOR DEBUGGING PURPOSE AND COPY+PASTE OR RUN THE SCRIPT IN ABAQUS CLI
## USER MAY NEED TO UPDATE srcPath LIST TO INCLUDE THE SRC FOLDER WHERE THE SCRIPT IS LOCATED
#################################################################################################################

import sys

## set current src path
srcPath = [r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\02_WIP\01_Scripts\src',
           r'\\fr0-svm20\St_RnT_METAL2\05_A350_FREIGHTER\Parametric_Coupon_Modelling\Scripts\2023_08_25\src',
           r'\\fr0-svm21\St_RnT_METAL3\01-SIMU_STnS_USE_CASES\13_A350F\09_Coupon_Parametric_Modelling\Scripts\src'
           r'D:\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src']

srcPathID = 0

## set template and coupon
# template = 'Coupon_01_Fatigue_66_69_A'
# coupon = 'Coupon_01_Fatigue_69A'

# template = 'Coupon_02_Fatigue_66_69_BJ'
# coupon = 'Coupon_02_Fatigue_66E'

# template = 'Coupon_03_Fatigue_70_73_A'
# coupon = 'Coupon_03_Fatigue_72A'

# template = 'Coupon_04_Fatigue_70_73_BE'
# coupon = 'Coupon_04_Fatigue_70C'

# template = 'Coupon_05_Fatigue_74_75'
# coupon = 'Coupon_05_Fatigue_74'

# template = 'Coupon_06A_Static_1_Symm_1_7'
# coupon = 'Coupon_06A_Static_1_Symm_5'

# template = 'Coupon_06B_Static_1_Full_1_7'
# coupon = 'Coupon_06B_Static_1_Full_6'

# template = 'Coupon_07A_Static_2_Symm_1_6'
# coupon = 'Coupon_07A_Static_2_Symm_4'

# template = 'Coupon_07B_Static_2_Full_1_6'
# coupon = 'Coupon_07B_Static_2_Full_6'

# template = 'Coupon_08_Static_18_21'
# coupon = 'Coupon_08_Static_18'

# template = 'Coupon_09_Fracture_22_36'
# coupon = 'Coupon_09_Fracture_30'

# template = 'Coupon_10_Crack_44_50'
# coupon = 'Coupon_10_Crack_44'

template = 'Coupon_11_HLT_1'
coupon = 'Coupon_11_HLT_1'

## call util script
execfile(srcPath[srcPathID]+'/util/debug.py')
debugFunc = getattr(sys.modules[__name__], 'debug')
self = debugFunc(srcPath[srcPathID], template, coupon)

