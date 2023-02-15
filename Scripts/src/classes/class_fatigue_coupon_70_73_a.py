import json

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
        pickedRegion = self.part.Set(elements=self.part.elements, name='Elset_All')  
        self.part.SectionAssignment(region=pickedRegion, sectionName=self.section.name, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def createJob(self):
        ## create job
        self.job = mdb.Job(name=self.couponName+'_Job'+self.version, model=self.model, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
        memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=2, numDomains=2, numGPUs=1)
        self.job.writeInput(consistencyChecking=OFF)
        ## save cae file
        mdb.saveAs(pathName=self.model.name+self.version)
        ## write json data of the model
        couponString = json.dumps(self.couponData, indent=4, sort_keys=True)
        couponJson = open(self.couponName+'_Data'+self.version+'.json', 'w')
        couponJson.write(couponString)
        couponJson.close()
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
                    if abs(abs(vertexCoord[0][index])-distance) < self.lenTol:
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


from abaqus import *
from abaqusConstants import *
from caeModules import *

class fatigue_coupon_70_73_a(coupon_generic):
    def __init__(self, couponData):
        super(fatigue_coupon_70_73_a, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.h1 = couponData['geometry']['h1']
        self.h2 = couponData['geometry']['h2']
        self.rad1 = couponData['geometry']['rad1']
        self.len1 = couponData['geometry']['len1']
        self.thickness = couponData['geometry']['thickness']
        self.givenKt = couponData['givenKt']
        self.lenTol = couponData['lenTol']
        self.seedSizeThickness = couponData['elemSize']['thickness']
        self.seedSizeVertical = couponData['elemSize']['vertical']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeLong3 = couponData['elemSize']['long3']
        self.elemTypeHex = SymbolicConstant(couponData['elemType']['hex'])
        self.materialName = couponData['material']['name']
        self.density = couponData['material']['density']
        self.youngsModulus = couponData['material']['youngsModulus']
        self.poissonsRatio = couponData['material']['poissonsRatio']
        self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        self.initIncr = couponData['step']['initIncr']
        self.nominalStress = couponData['step']['nominalStress']
        self.version = couponData['version']
        ## derived quantities
        self.endStress = -self.nominalStress*self.h1/self.h2
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        self.createPartition()
        self.createMesh()
        self.createMaterial()
        self.createSection()
        self.createStep()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates ###############################################################################################################
        self.coordO = (self.xO, self.yO) = (0, 0)
        self.coordA = (self.xA, self.yA) = (0, self.h1/2)
        self.coordB = (self.xB, self.yB) = (self.rad1*(1-((self.rad1+self.h1/2-self.h2/2)/self.rad1)**2)**0.5, self.h2/2)
        self.coordC = (self.xC, self.yC) = (self.len1/2, self.h2/2)
        self.coordD = (self.xE, self.yE) = (self.len1/2, 0)
        self.coordC1 = (self.xC1, self.yC1) = (0, self.yA+self.rad1) # center 1
        ###############################################################################################################################################
        ## define sketch    ###########################################################################################################################
        self.profileSketch = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch', sheetSize=200.0)
        self.profileGeometry, self.profileVertices = self.profileSketch.geometry, self.profileSketch.vertices
        self.profileSketch.setPrimaryObject(option=STANDALONE)
        ## horizontal fixed construction line ==>> self.profileGeometry[2]
        self.profileSketch.ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch.FixedConstraint(entity=self.profileGeometry[2])
        self.profileSketch.assignCenterline(line=self.profileGeometry[2])
        ## vertical fixed construction line ==>> self.profileGeometry[3]
        self.profileSketch.ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch.FixedConstraint(entity=self.profileGeometry[3])
        ## line OA: self.profileGeometry[4]; vertices ==>> self.profileVertices[0], self.profileVertices[1]; dimension: d[0]
        self.profileSketch.Line(point1=self.coordO, point2=self.coordA)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[4], addUndoState=False)
        self.profileSketch.PerpendicularConstraint(entity1=self.profileGeometry[2], entity2=self.profileGeometry[4], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[0], entity2=self.profileGeometry[2], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[1], entity2=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.ObliqueDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[1], textPoint=(-3, 4), value=self.h1/2)
        (self.xO, self.yO), (self.xA, self.yA) = self.profileVertices[0].coords, self.profileVertices[1].coords
        ## arc AB: self.profileGeometry[5]; vertices ==>> self.profileVertices[1], self.profileVertices[2]; center: self.profileVertices[3]; dimension: d[1], d[2]
        self.profileSketch.ArcByCenterEnds(center=self.coordC1, point1=self.coordA, point2=self.coordB, direction=COUNTERCLOCKWISE)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[3], entity2=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.RadialDimension(curve=self.profileGeometry[5], textPoint=(0, 25), radius=self.rad1)
        self.profileSketch.DistanceDimension(entity1=self.profileVertices[2], entity2=self.profileGeometry[2], textPoint=(10, 1), value=self.h2/2)
        (self.xB, self.yB), (self.xC1, self.yC1) = self.profileVertices[2].coords, self.profileVertices[3].coords
        ## line BC: self.profileGeometry[6]; vertices ==>> self.profileVertices[3], self.profileVertices[4]; dimension: d[3]
        self.profileSketch.Line(point1=self.coordB, point2=self.coordC)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[6], addUndoState=False)
        self.profileSketch.HorizontalDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[4], textPoint=(13, -9), value=self.len1/2)
        (self.xC, self.yC) = self.profileVertices[4].coords
        ## line CD: self.profileGeometry[7]; vertices ==>> self.profileVertices[4], self.profileVertices[5]
        self.profileSketch.Line(point1=self.coordC, point2=self.coordD)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[7], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[5], entity2=self.profileGeometry[2], addUndoState=False)
        (self.xD, self.yD) = self.profileVertices[5].coords
        ## line DO: self.profileGeometry[8]; vertices ==>> self.profileVertices[5], self.profileVertices[0]
        self.profileSketch.Line(point1=self.coordD, point2=self.coordO)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[8], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch.unsetPrimaryObject()
    def createPart(self):
        ## create solid
        self.part = self.model.Part(name=self.couponName+'_Part', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        self.part.BaseSolidExtrude(sketch=self.profileSketch, depth=self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part)
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.instance = self.assembly.Instance(name=self.couponName+'_Instance', part=self.part, dependent=ON)
    def createPartition(self):
        def createPartitionLong(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part.PartitionCellByDatumPlane(datumPlane=self.part.datums[self.datumPlane_ID], cells=self.part.cells)
        createPartitionLong(self.xB)
    def createMesh(self):
        ## seed ==>> thickness direction
        edgesThickness = self.part.edges.findAt(((0, 0, self.thickness/2),))
        self.part.seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along AB
        pickedEdges1 = self.part.edges.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong1 = self.getEdgeByLength(pickedEdges1, abs(self.xB-self.xA))
        self.seedEdge(self.part, 0, self.xA, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> arc along AB
        pickedEdges2 = self.part.edges
        edgesLong2 = self.getArcEdge(pickedEdges2)
        biasRatio = self.part.getEdgeSeeds(edgesLong1[0], attribute=BIAS_RATIO)
        elemNum = self.part.getEdgeSeeds(edgesLong1[0], attribute=NUMBER)
        self.seedEdge(self.part, 0, self.xA, edgesLong2, ratio=biasRatio, number=elemNum)
        ## seed ==>> long edges along BC
        pickedEdges3 = self.part.edges.getByBoundingBox(xMin=self.xB-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong3 = self.getEdgeByLength(pickedEdges3, abs(self.xC-self.xB))
        self.seedEdge(self.part, 0, self.xB, edgesLong3, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> vertical edge
        edgesVertical1 = self.part.edges.findAt(((self.xO, self.yA/2, 0),))
        self.part.seedEdgeBySize(edges=edgesVertical1, size=self.seedSizeVertical, deviationFactor=0.1, constraint=FINER)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHex, elemLibrary=STANDARD)
        self.part.setElementType(regions=(self.part.cells,), elemTypes=(elemType1,))
        ## generate mesh
        self.part.generateMesh()
        self.couponData.update({'elemNum':len(self.part.elements)})
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        ## create BC at negY face
        nodesNegY = self.part.nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        nsetNameNegY = 'Nset_NegY'
        self.part.Set(nodes=nodesNegY, name=nsetNameNegY)
        region = self.instance.sets[nsetNameNegY]
        self.model.DisplacementBC(name='BC_NegY', createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at negZ face
        nodesPosZ = self.part.nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.lenTol)
        nsetNamePosZ = 'Nset_NegZ'
        self.part.Set(nodes=nodesPosZ, name=nsetNamePosZ)
        region = self.instance.sets[nsetNamePosZ]
        self.model.DisplacementBC(name='BC_NegZ', createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at negX face
        nodesNegX = self.part.nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xA+self.lenTol, yMax=self.yA+self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
        nsetNameNegX = 'Nset_NegX'
        self.part.Set(nodes=nodesNegX , name=nsetNameNegX)
        region = self.instance.sets[nsetNameNegX]
        self.model.DisplacementBC(name='BC_NegX', createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create pressure load on posX face
        endCellFaceArr = self.part.faces.getByBoundingBox(xMin=self.xC-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
        surfNamePosX = 'Surf_PosX'
        self.getElemSurfFromCellFace(self.part, endCellFaceArr, surfNamePosX)
        region = self.instance.surfaces[surfNamePosX]
        self.model.Pressure(name='Load_PosX', createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF'))
    
