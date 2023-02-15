## modify these 3 lines for debugging purpose and copy/paste (or run) in Abaqus CLI; the list contains possible paths for src folder
template = 'Static_Coupon_1_1_7'
coupon = 'Static_Coupon_1_1'
srcPath = [r'Z:\Rupsagar\04_Coupon_Parametric_Modelling\01_WIP\Scripts\src', 
r'D:\Programming\python\abaqus_scripts\Coupon_Parametric_Modelling\Scripts\src']

import json
import ast
import imp
import os
import shutil

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
    
    ## load current coupon module
    couponModule = imp.load_source('class_'+template.lower(), srcPath[srcPathID]+'/classes/class_'+template.lower()+'.py')
    couponClass = getattr(couponModule, template.lower())
    self = couponClass(couponData)

    if os.path.exists(srcPath[srcPathID]+'/classes/class_'+template.lower()+'.pyc'):
        os.remove(srcPath[srcPathID]+'/classes/class_'+template.lower()+'.pyc')

    if os.path.isdir(srcPath[srcPathID]+'/classes/__pycache__'):
        shutil.rmtree(srcPath[srcPathID]+'/classes/__pycache__')
except Exception as err:
    print(str(err))

