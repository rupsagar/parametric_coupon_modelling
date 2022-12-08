couponClassPath = r'Z:\Rupsagar\04_COUPON_MODELLING\01_WIP\Coupon_Mark_A\Scripts'
couponDatabasePath = r'Z:\Rupsagar\04_COUPON_MODELLING\01_WIP\Coupon_Mark_A\Scripts'
couponDatabaseJsonFileName = r'Coupon_Mark_A_Database.json'

import sys
import os
import json
import ast
sys.path.append(couponClassPath)
from Coupon_Mark_A_Class_File import createCouponMarkA

fileJson = open(os.path.join(couponDatabasePath, couponDatabaseJsonFileName), 'r')
couponMarkADatabaseUnicode = json.load(fileJson)
fileJson.close
couponMarkADatabase = ast.literal_eval(json.dumps(couponMarkADatabaseUnicode))

couponModelList = []
for thisCoupon in couponMarkADatabase:
    couponModelList.append(createCouponMarkA(couponMarkADatabase[thisCoupon]))

