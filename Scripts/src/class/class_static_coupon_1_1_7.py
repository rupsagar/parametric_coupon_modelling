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
        self.seedSizeRadialInner = couponData['elemSize']['radialInner']
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
        def seedLong(part, xLeft, xRight, yMax, **kwargs):
            pickedEdges = part.edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (yMax+self.lenTol))
            edgesLong = self.getEdgeByLength(pickedEdges, abs(xRight-xLeft))
            self.seedEdge(part, 0, xLeft, edgesLong, **kwargs)
        def seedInnerCyl(part, xLeft, xRight):
            cellsInnerCyl = part.cells.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            part.setMeshControls(regions=cellsInnerCyl, elemShape=HEX, technique=SWEEP, algorithm=ADVANCING_FRONT)
            edgesSweepPath = part.edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), self.lenTol)
            part.setSweepPath(region=cellsInnerCyl[0], edge=edgesSweepPath[0], sense=FORWARD)
        ## seed ==>> outer arc edge AA'
        self.edgesOuterCyl = self.getByCylinderDifference(self.part[0].edges, (-self.lenTol, 0, 0), (self.lenTol, 0, 0), (self.yA+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArc = self.getArcEdge(self.edgesOuterCyl)
        self.part[0].seedEdgeBySize(edges=self.edgesOuterArc, size=self.seedSizeArcOuter, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer radial edges
        edgesRadial1 = self.part[0].edges.findAt(coordinates=((0, (self.partitionRadius+self.lenTol), 0), (0, 0, -(self.partitionRadius+self.lenTol))))
        self.seedEdge(self.part[0], 1, self.partitionRadius, edgesRadial1, minSize=self.seedSizeRadialOuter, maxSize=self.seedSizeRadialOuter)
        self.seedEdge(self.part[0], 2, self.partitionRadius, edgesRadial1, minSize=self.seedSizeRadialOuter, maxSize=self.seedSizeRadialOuter)
        ## seed ==>> inner radial edges
        edgesRadial2 = self.part[0].edges.findAt(coordinates=((0, (self.partitionRadius-self.lenTol), 0), (0, 0, -(self.partitionRadius-self.lenTol))))
        self.seedEdge(self.part[0], 1, self.partitionRadius, edgesRadial2, minSize=self.seedSizeRadialInner, maxSize=self.seedSizeRadialInner)
        self.seedEdge(self.part[0], 2, self.partitionRadius, edgesRadial2, minSize=self.seedSizeRadialInner, maxSize=self.seedSizeRadialInner)
        ## sweep path ==>> inner cylinder
        seedInnerCyl(self.part[0], self.xA, self.xB)
        seedInnerCyl(self.part[0], self.xB, self.xC)
        seedInnerCyl(self.part[0], self.xC, self.xD)
        ## seed ==>> longitudinal edges
        seedLong(self.part[0], self.xA, self.xB, self.yD, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        seedLong(self.part[0], self.xB, self.xC, self.yD, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong2)
        seedLong(self.part[0], self.xC, self.xD, self.yD, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> arc BC
        edgesTemp = self.part[0].edges.findAt(coordinates=((self.xB+self.lenTol, 0, 0), ))
        ratioBias = self.part[0].getEdgeSeeds(edgesTemp[0], attribute=BIAS_RATIO)
        elemNum = self.part[0].getEdgeSeeds(edgesTemp[0], attribute=NUMBER)
        edgesTemp2 = self.part[0].edges.getByBoundingCylinder((self.xB-self.lenTol, 0, 0), (self.xC+self.lenTol, 0, 0), (self.yC+self.lenTol))
        edgesArc = self.getArcEdge(edgesTemp2)
        self.seedEdge(self.part[0], 0, self.xB, edgesArc, ratio=ratioBias, number=elemNum)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHexPart1, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1, ))
        ## generate mesh
        for i in range(len(self.part)):
            self.part[i].generateMesh()
        self.couponData.update({'elemNum':len(self.part[0].elements)})
    def createMaterial(self):
        ## material definition
        self.material = self.model.Material(name=self.materialName)
        self.material.Density(table=((self.density, ), ))
        self.material.Elastic(table=((self.youngsModulus, self.poissonsRatio), ))
    def createSection(self):
        ## section definition and assigning section property to elements
        self.model.HomogeneousSolidSection(name=self.couponName+'_Section', material=self.materialName, thickness=None)
        for i in range(len(self.part)):
            pickedRegion = self.part[i].Set(elements=self.part[0].elements, name='All_Elements_Part_'+str(i+1))
            self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.couponName+'_Section', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        for i in range(len(self.part)):
            ## create BC at negY face
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=-self.lenTol, yMin=-self.lenTol, zMin=-self.yD-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.lenTol, zMax=self.lenTol)
            nsetNameNegY = 'Nset_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Part_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at posZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.lenTol)
            nsetNamePosZ = 'Nset_PosZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesPosZ, name=nsetNamePosZ)
            region = self.instance[i].sets[nsetNamePosZ]
            self.model.DisplacementBC(name='BC_PosZ_Part_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==0:
                ## create BC at negX face of Part 1
                nodesNegX = self.part[i].nodes.getByBoundingCylinder((-self.lenTol, 0, 0), (self.lenTol, 0, 0), (self.yA+self.lenTol))
                nsetNameNegX = 'Nset_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Part_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==(len(self.part)-1):
                ## create pressure load on posX face
                endCellFaceArr = self.part[i].faces.getByBoundingCylinder((self.xD-self.lenTol, 0, 0), (self.xD+self.lenTol, 0, 0), (self.yD+self.lenTol))
                surfNamePosX = 'Surf_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Part_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
                self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF'))
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
