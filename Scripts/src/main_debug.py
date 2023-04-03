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


srcPath = [r'\\fr0-svm20\St_RnT_METAL2\05_A350_FREIGHTER\Parametric_Coupon_Modelling\Scripts\src']

# template = 'Fatigue_Coupon_66_69_A'
# coupon = 'Fatigue_Coupon_69A'

# template = 'Fatigue_Coupon_66_69_BJ'
# coupon = 'Fatigue_Coupon_69E'

# template = 'Fatigue_Coupon_70_73_A'
# coupon = 'Fatigue_Coupon_72A'

# template = 'Fatigue_Coupon_70_73_BE'
# coupon = 'Fatigue_Coupon_70C'

# template = 'Fatigue_Coupon_74_75'
# coupon = 'Fatigue_Coupon_74'

# template = 'Static_Coupon_1_Full_1_7'
# coupon = 'Static_Coupon_1_Full_6'

# template = 'Static_Coupon_1_Symmetric_1_7'
# coupon = 'Static_Coupon_1_Symmetric_5'

# template = 'Static_Coupon_2_Full_1_6'
# coupon = 'Static_Coupon_2_Full_6'

# template = 'Static_Coupon_2_Symmetric_1_6'
# coupon = 'Static_Coupon_2_Symmetric_4'

import os, sys

for i in range(len(srcPath)):
    if os.path.isdir(srcPath[i]):
        srcPathID = i
        break

execfile(srcPath[srcPathID]+'/utils/util_debug.py')
debugFunc = getattr(sys.modules[__name__], 'debug')
self = debugFunc(srcPath[srcPathID], template, coupon)

