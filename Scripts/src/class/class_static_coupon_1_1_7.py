import json

from abaqus import *
from abaqusConstants import *
from caeModules import *

class static_coupon_1_1_7():
    def __init__(self, couponData):
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.lt = couponData['geometry']['lt']
        self.d = couponData['geometry']['d']
        self.D = couponData['geometry']['D']
        self.R = couponData['geometry']['R']
        self.C = couponData['geometry']['C']
        self.lc = couponData['geometry']['lc']
        self.lenTol = couponData['lenTol']
        self.partitionRadialFraction = couponData['partitionRadialFraction']
        self.seedSizeArcOuter = couponData['elemSize']['arcOuter']
        self.seedSizeRadialOuter = couponData['elemSize']['radialOuter']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeLong3 = couponData['elemSize']['long3']
        self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        self.materialName = couponData['material']['name']
        self.density = couponData['material']['density']
        self.youngsModulus = couponData['material']['youngsModulus']
        self.poissonsRatio = couponData['material']['poissonsRatio']
        self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        self.initIncr = couponData['step']['initIncr']
        self.nominalStress = couponData['step']['nominalStress']
        self.version = couponData['version']
        ## derived quantities
        self.partitionRadius = self.partitionRadialFraction*self.d/2
        self.endStress = -self.nominalStress*(self.d/self.D)**2
        # self.seedSizeOuterRadialMin = self.seedSizeOuterArc*self.partitionRadialFraction
        # self.seedSizeInnerRadial = self.seedSizeOuterArc*self.partitionRadialFraction
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        self.createPartition()
        self.createMesh()
        self.createMaterial()
        # self.createSection()
        # self.createStep()
        # self.createJob()
    def createModel(self):
        ## define model
        session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
        self.model = mdb.Model(name=self.couponName+'_Model')
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        self.coordO = (self.xO, self.yO) = (0, 0)
        self.coordA = (self.xA, self.yA) = (0, self.d/2.0)
        self.coordB = (self.xB, self.yB) = (self.lc/2.0, self.yA)
        self.coordC = (self.xC, self.yC) = ((self.lt/2.0-self.C), self.D/2)
        self.coordD = (self.xD, self.yD) = (self.lt/2.0, self.yC)
        self.coordE = (self.xE, self.yE) = (self.xD, 0)
        self.coordC1 = (self.xC1, self.yC1) = (self.xB, self.yB+self.R) # center 1
        #################################################################################################################################################
        self.profileSketch = 1*[None]
        ## define sketch
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_1', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)
        ## horizontal fixed construction line ==>> self.profileGeometry1[2]
        self.profileSketch[0].ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[2])
        self.profileSketch[0].assignCenterline(line=self.profileGeometry1[2])
        ## vertical fixed construction line ==>> self.profileGeometry1[3]
        self.profileSketch[0].ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[3])
        ## line OA
        self.profileSketch[0].Line(point1=self.coordO, point2=self.coordA)
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[1], textPoint=(-3, 4), value=self.d/2)
        ## line AB
        self.profileSketch[0].Line(point1=self.coordA, point2=self.coordB)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[5], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[2], textPoint=(13, 13), value=self.lc/2)
        ## arc BC
        self.profileSketch[0].ArcByCenterEnds(center=self.coordC1, point1=self.coordB, point2=self.coordC, direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=(14, 10), radius=self.R)
        ## line CD
        self.profileSketch[0].Line(point1=self.coordC, point2=self.coordD)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[5], textPoint=(13, 10), value=self.lt/2)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[3], vertex2=self.profileVertices1[5], textPoint=(13, -9), value=self.C)
        ## line DE
        self.profileSketch[0].Line(point1=self.coordD, point2=self.coordE)
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[5], vertex2=self.profileVertices1[6], textPoint=(13, 4), value=self.D/2)
        ## line EO
        self.profileSketch[0].Line(point1=self.coordE, point2=self.coordO)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
    def createPart(self):
        ## create solid
        self.part = len(self.profileSketch)*[None]
        for i in range(len(self.part)):
            self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.part[i].BaseSolidRevolve(sketch=self.profileSketch[0], angle=90, flipRevolveDirection=ON)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])        
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.instance = len(self.part)*[None]
        for i in range(len(self.part)):
            self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
    def createPartition(self):
        def createPartitionCyl():
            ## partition ==>> inner cylinder
            self.sketchFace = self.part[0].faces.getByBoundingCylinder((-self.lenTol, 0, 0), (self.lenTol, 0, 0), (self.yA+self.lenTol))
            self.sketchEdge = self.part[0].edges.findAt(((0, self.partitionRadius, 0),))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch', sheetSize=4, transform=self.transform)
            self.partitionSketchGeometry, self.partitionSketchVertices = self.partitionSketch.geometry, self.partitionSketch.vertices
            self.partitionSketch.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch, filter=COPLANAR_EDGES)
            self.partitionSketch.ArcByCenterEnds(center=(0, 0), point1=(0, self.partitionRadius), point2=(-self.partitionRadius, 0), direction=COUNTERCLOCKWISE)
            self.projectionLine1 = self.partitionSketchGeometry.findAt((0, self.partitionRadius/2), 1)
            self.projectionLine2 = self.partitionSketchGeometry.findAt((-self.partitionRadius/2, 0), 1)
            self.vertexPoint1 = self.partitionSketchVertices.findAt((0, self.partitionRadius), 1)
            self.vertexPoint2 = self.partitionSketchVertices.findAt((-self.partitionRadius, 0), 1)
            self.partitionSketch.CoincidentConstraint(entity1=self.vertexPoint1, entity2=self.projectionLine1, addUndoState=False)
            self.partitionSketch.CoincidentConstraint(entity1=self.vertexPoint2, entity2=self.projectionLine2, addUndoState=False)
            self.partitionSketch.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge[0], faces=self.sketchFace[0], sketch=self.partitionSketch)
            edgesTemp = self.part[0].edges.getByBoundingCylinder((-self.lenTol, 0, 0), (self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            self.edgesArcForPartition = self.getArcEdge(edgesTemp)
            self.sweepEdges = self.part[0].edges.getByBoundingCylinder((-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.partitionRadius-self.lenTol))
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.sweepEdges[0], cells=self.part[0].cells, edges=self.edgesArcForPartition)
        def createPartitionLong(offsetDistance):
            ## partition by YZ plane
            self.datumPlane1_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane1_ID], cells=self.part[0].cells)
        createPartitionCyl()
        createPartitionLong(self.xB)
        createPartitionLong(self.xC)
    def createMesh(self):
        def seedOuterRadial(pointOnRadius, **kwargs):
            ## method to seed the outer radial edge at sections through A and B
            edgesOuterRadial = self.part[0].edges.findAt((pointOnRadius, ))  
            edgesRadialVertexIDPair = edgesOuterRadial[0].getVertices()
            for thisVertexID in edgesRadialVertexIDPair:
                vertexCoord = self.part[0].vertices[thisVertexID].pointOn
                if abs(abs(vertexCoord[0][1])-self.partitionRadius) < self.lenTol or abs(abs(vertexCoord[0][2])-self.partitionRadius) < self.lenTol or abs(abs(vertexCoord[0][2])-self.partitionRadius) < self.lenTol:
                    if edgesRadialVertexIDPair.index(thisVertexID) == 0:
                        if 'minSize' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end1Edges=edgesOuterRadial, minSize=kwargs['minSize'], maxSize=kwargs['maxSize'], constraint=FIXED)
                        elif 'ratio' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end1Edges=edgesOuterRadial, ratio=kwargs['ratio'], number=kwargs['number'], constraint=FIXED)
                    elif edgesRadialVertexIDPair.index(thisVertexID) == 1:
                        if 'minSize' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end2Edges=edgesOuterRadial, minSize=kwargs['minSize'], maxSize=kwargs['maxSize'], constraint=FIXED)
                        elif 'ratio' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end2Edges=edgesOuterRadial, ratio=kwargs['ratio'], number=kwargs['number'], constraint=FIXED)
        def seedLongEdges(xLeft, xRight, seedSize):
            ## method to seed the longitudinal edges
            edgesInnerArcLong = self.part[0].edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.yD+self.lenTol))
            edgesInnerArc = self.getArcEdge(edgesInnerArcLong)
            edgesStraight = self.getByDifference(edgesInnerArcLong, edgesInnerArc)
            edgesLong = self.getEdgeByLength(edgesStraight, abs(xRight-xLeft))
            self.part[0].seedEdgeBySize(edges=edgesLong, size=seedSize, deviationFactor=0.1, constraint=FINER)
        def setInnerCylSweepPath(xLeft, xRight):
            ## method to set the sweep path for the inner cylindrical mesh
            cellsInnerCyl = self.part[0].cells.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            edgesSweepPath = self.part[0].edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), self.lenTol)
            self.part[0].setMeshControls(regions=cellsInnerCyl, technique=SWEEP, algorithm=ADVANCING_FRONT)
            self.part[0].setSweepPath(region=cellsInnerCyl[0], edge=edgesSweepPath[0], sense=FORWARD)
        ## seed ==>> outer arc edge AA'
        self.edgesOuterCyl = self.getByCylinderDifference(self.part[0].edges, (self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArc = self.getArcEdge(self.edgesOuterCyl)
        self.part[0].seedEdgeBySize(edges=self.edgesOuterArc, size=self.seedSizeArcOuter, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer radial edges
        edgesRadial1 = self.part[0].edges.findAt(coordinates=((0, (self.partitionRadius+self.lenTol), 0), ))
        self.seedEdge(self.part[0], 1, self.partitionRadius, edgesRadial1, minSize=self.seedSizeRadialOuter, maxSize=self.seedSizeRadialOuter)
        edgesRadial2 = self.part[0].edges.findAt(coordinates=((0, 0, -(self.partitionRadius+self.lenTol)), ))
        self.seedEdge(self.part[0], 2, self.partitionRadius, edgesRadial2, minSize=self.seedSizeRadialOuter, maxSize=self.seedSizeRadialOuter)
        ## seed ==>> edge Bb ==>> not applied; seeding with increase the element size at the surface by small amount
        self.edgesOuterCylAtB = self.getByCylinderDifference(self.part[0].edges, (self.xB-self.lenTol, 0, 0), (self.xB+self.lenTol, 0, 0), (self.yB+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArcAtB = self.getArcEdge(self.edgesOuterCylAtB)
        self.edgesOuterRadialAtB = self.getByDifference(self.edgesOuterCylAtB, self.edgesOuterArcAtB)
        ratioBias = self.part[0].getEdgeSeeds(self.edgesOuterRadial[0], attribute=BIAS_RATIO)
        elemNum = self.part[0].getEdgeSeeds(self.edgesOuterRadial[0], attribute=NUMBER)
        #seedOuterRadial((self.xB, self.partitionRadius+self.lenTol, 0.0), ratio=ratioBias, number=elemNum)
        #seedOuterRadial((self.xB, 0.0, -(self.partitionRadius+self.lenTol)), ratio=ratioBias, number=elemNum)
        ## seed ==>> longitudinal edges
        seedLongEdges(self.xA, self.xB, self.seedSizeLong1)
        seedLongEdges(self.xB, self.xC, self.seedSizeLong2)
        seedLongEdges(self.xC, self.xD, self.seedSizeLong3)
        ## seed ==>> inner radial edges
        self.edgesInnerCyl = self.part[0].edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xB-self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        self.edgesInnerArc = self.getArcEdge(self.edgesInnerCyl)
        self.edgesInnerRadial = self.getByDifference(self.edgesInnerCyl, self.edgesInnerArc)
        self.part[0].seedEdgeBySize(edges=self.edgesInnerRadial, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        ## sweep path ==>> inner cylinder
        setInnerCylSweepPath(self.xA, self.xB)
        setInnerCylSweepPath(self.xB, self.xC)
        setInnerCylSweepPath(self.xC, self.xD)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHex, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1, ))
        ## generate mesh
        self.part[0].generateMesh()
        self.couponData.update({'elemNum':len(self.part[0].elements)})
    def createMaterial(self):
        ## material definition
        self.material = self.model.Material(name=self.materialName)
        self.material.Density(table=((self.density, ), ))
        self.material.Elastic(table=((self.youngsModulus, self.poissonsRatio), ))
    def createSection(self):
        ## section definition and assigning section property to elements
        self.model.HomogeneousSolidSection(name=self.couponName+'_Section', material=self.materialName, thickness=None)
        pickedRegion = self.part[0].Set(elements=self.part[0].elements, name='All_Elements')
        self.part[0].SectionAssignment(region=pickedRegion, sectionName=self.couponName+'_Section', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        ## create BC at negY face
        nodesNegY = self.part.nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin=-self.lenTol, zMin=-self.yD-self.lenTol, xMax=self.xE+self.lenTol, yMax=self.lenTol, zMax=self.lenTol)
        nsetNameNegY = 'Nset_NegY'
        self.part.Set(nodes=nodesNegY, name=nsetNameNegY)
        region = self.instance.sets[nsetNameNegY]
        self.model.DisplacementBC(name='BC_NegY', createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at posZ face
        nodesPosZ = self.part.nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xE+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.lenTol)
        nsetNamePosZ = 'Nset_PosZ'
        self.part.Set(nodes=nodesPosZ, name=nsetNamePosZ)
        region = self.instance.sets[nsetNamePosZ]
        self.model.DisplacementBC(name='BC_PosZ', createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at negX face
        nodesNegX = self.part.nodes.getByBoundingCylinder((self.xO-self.lenTol, 0, 0), (self.xO+self.lenTol, 0, 0), (self.yA+self.lenTol))
        nsetNameNegX = 'Nset_NegX'
        self.part.Set(nodes=nodesNegX , name=nsetNameNegX)
        region = self.instance.sets[nsetNameNegX]
        self.model.DisplacementBC(name='BC_NegX', createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create pressure load on posX face
        endCellFaceArr = self.part.faces.getByBoundingCylinder((self.xE-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.yD+self.lenTol))
        surfNamePosX = 'Surf_PosX'
        self.getElemSurfFromCellFace(self.part, endCellFaceArr, surfNamePosX)
        region = self.instance.surfaces[surfNamePosX]
        self.model.Pressure(name='Load_PosX', createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
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
