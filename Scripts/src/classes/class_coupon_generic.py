#################################################################################################################
######################                 ABAQUS PARAMETRIC COUPON MODEL                     #######################
#################################################################################################################
##############################    CLASS DEFINITION : COUPON GENERIC METHODS   ###################################
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


import json, os, re

class coupon_generic(object):
    def __init__(self):
        pass
    def createModel(self):
        ## define model
        session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
        self.model = mdb.Model(name=self.couponName+'_Model')
    def createMaterial(self):
        ## material definition
        self.material = self.model.Material(name=self.materialName)
        self.material.Density(table=((self.density, ), ))
        self.material.Elastic(table=((self.youngsModulus, self.poissonsRatio), ))
    def createSection(self):
        ## section definition and assigning section property to elements
        self.section = self.model.HomogeneousSolidSection(name=self.couponName+'_Section', material=self.materialName, thickness=None)
        for i in range(len(self.part)):
            pickedRegion = self.part[i].Set(elements=self.part[i].elements, name='Elset_All_Part_'+str(i+1))
            self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.section.name, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def createJob(self):
        ## create job
        self.job = mdb.Job(name=self.couponName+'_Job'+self.version, model=self.model, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, 
            getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
            scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=2, numDomains=2, numGPUs=1)
        self.job.writeInput(consistencyChecking=OFF)
        ## create cae file
        try:
            del mdb.models['Model-1']
        except:
            pass
        mdb.saveAs(pathName=self.model.name+self.version)
        ## create json data of the model
        couponString = json.dumps(self.couponData, indent=4, sort_keys=True)
        couponJson = open(self.couponName+'_Data'+self.version+'.json', 'w')
        couponJson.write(couponString)
        couponJson.close()
        ## create txt file of geometry data
        geomFileName = self.couponName+'_Geom'+self.version+'.txt'
        geomFile = open(geomFileName, 'w')
        self.geomData.insert(0, ['', 'Initial', '', 'Final', ''])
        for thisList in self.geomData:
            for i in range(len(thisList)):
                geomFile.write(str(thisList[i])+'\t')
            geomFile.write('\n')
        geomFile.close()
        ## creating separate inp files
        self.inpFileSplitter()
    def getByDifference(self, listA, listB):
        ## method to return list with elements of difference of two lists
        differenceList = []
        for thisItem in listA:
            if thisItem not in listB:
                differenceList.append(thisItem)
        return differenceList
    def getByCylinderDifference(self, feature, center1, center2, outerRadius, innerRadius):
        ## method to return list with geometric features by subtraction of two bounding cylinders
        featureOuter = feature.getByBoundingCylinder(center1, center2, outerRadius)
        featureInner = feature.getByBoundingCylinder(center1, center2, innerRadius)
        pickedFeatures = self.getByDifference(featureOuter, featureInner)
        return pickedFeatures
    def getArcEdge(self, edgeList):
        ## method to return edge list containing only arc edges from a given edge list
        arcEdge = []
        for thisEdge in edgeList:
            try:
                thisEdge.getRadius()
                arcEdge.append(thisEdge)
            except:
                pass
        return arcEdge
    def getEdgeByLength(self, edgeList, length):
        ## method to return edge list of a desired length from a given edge list
        pickedEdges = []
        for thisEdge in edgeList:
            if abs(thisEdge.getSize(0)-length) < self.lenTol:
                pickedEdges.append(thisEdge)
        return pickedEdges
    def seedEdge(self, part, index, distance, edges, **kwargs):
            for thisEdge in edges:
                edgeVertices = thisEdge.getVertices()
                for thisVertexID in edgeVertices:
                    vertexCoord = part.vertices[thisVertexID].pointOn
                    if abs(vertexCoord[0][index]-distance) < self.lenTol:
                        if edgeVertices.index(thisVertexID) == 0:
                            part.seedEdgeByBias(biasMethod=SINGLE, end1Edges=(thisEdge,), constraint=FINER, **kwargs)
                        elif edgeVertices.index(thisVertexID) == 1:
                            part.seedEdgeByBias(biasMethod=SINGLE, end2Edges=(thisEdge,), constraint=FINER, **kwargs)
    def getElemSurfFromCellFace(self, part, cellFaceArr, surfName):
        ## method to create element based surface from cell face
        elemWithFace = [[], [], [], [], [], []]
        for thisCellFace in cellFaceArr:
            elemFaceArr = thisCellFace.getElementFaces()   
            for thisElem in elemFaceArr:
                for thisfaceID in range(6):
                    if thisElem.face == SymbolicConstant('FACE'+str(thisfaceID+1)):
                        elemWithFace[thisfaceID].append(thisElem)
                        break
        surfDict = {'name':surfName}
        for thisfaceID in range(6):
            if len(elemWithFace[thisfaceID]) > 0:
                elemWithFace[thisfaceID] = mesh.MeshFaceArray(elemWithFace[thisfaceID])
                surfDict.update({'face'+str(thisfaceID+1)+'Elements':elemWithFace[thisfaceID]})
        part.Surface(**surfDict)
    def getNsetFromCellFace(self, part, cellFaceArr, nsetName):
        ## method to extract node set from cell face
        nodes = []
        for thisCellFace in cellFaceArr:
            nodeArray = thisCellFace.getNodes()
            for thisNode in nodeArray:
                nodes.append(thisNode)
        nodes = mesh.MeshNodeArray(nodes)
        part.Set(nodes=nodes, name=nsetName)
    def inpFileSplitter(self):
        dictFileID = {0:'Job', 
                      1:'Parts', 
                      2:'Materials', 
                      3:'Step'}
        eliminationList = ['** ASSEMBLY','** INTERACTION PROPERTIES', '** INTERACTIONS']
        oldJobFileName = self.job.name+'.inp'
        newJobFileName = self.couponName+'_Job_Temp'+self.version+'.inp'
        os.rename(oldJobFileName, newJobFileName)
        fileTemp = open(newJobFileName, 'r')
        InpFolderName = self.couponName+'_InpFolder'+self.version
        try:
            os.mkdir(InpFolderName)
        except:
            pass
        file = len(dictFileID)*[None] 
        for key, val in dictFileID.items():
            if key==0:
                file[key] = open(self.couponName+'_'+val+self.version+'.inp', 'w')
            else:
                file[key] = open(InpFolderName+'/'+self.couponName+'_'+val+self.version+'.inp', 'w')
        prevFile = 0
        currentFile = 0
        lineCount = len(dictFileID)*[0]
        for thisLine in fileTemp:
            lineCount[currentFile] = lineCount[currentFile]+1
            for key in range(len(file)):
                if re.search("^\*\*.*"+dictFileID[key], thisLine.title()):
                    prevFile = currentFile
                    currentFile = key
                    break
                elif thisLine.rstrip('\n') in eliminationList:
                    prevFile = currentFile
                    currentFile = 0
            if currentFile!=0 and prevFile!=currentFile and lineCount[currentFile]==0:
                file[0].write(thisLine)
                file[0].write('*Include, input = ./'+file[currentFile].name+'\n')
                lineCount[0] = lineCount[0]+1
            else:
                file[currentFile].write(thisLine)
        fileTemp.close()
        for i in range(len(file)):
            file[i].close()
        ## delete old temp job file
        if os.path.exists(newJobFileName):
                os.remove(newJobFileName)

