from abaqus import *
from abaqusConstants import *
from caeModules import *
import math

class static_coupon_bearing_18_21(coupon_generic):
    def __init__(self, couponData):
        super(static_coupon_bearing_18_21, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.len1 = couponData['geometry']['len1']
        self.len2 = couponData['geometry']['len2']
        self.width = couponData['geometry']['width']
        self.phi1 = couponData['geometry']['phi1']
        self.E = couponData['geometry']['E']
        self.phi2 = couponData['geometry']['phi2']
        self.thickness = couponData['thickness']
        self.lenTol = couponData['lenTol']
        self.seedSizeArc = couponData['elemSize']['arc']
        self.seedSizeInnerRadial = couponData['elemSize']['radialInner']
        self.seedSizeOuterRadial = couponData['elemSize']['radialOuter']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeThickness = couponData['elemSize']['thickness']
        self.seedSizeVertical1 = couponData['elemSize']['vertical1']
        self.seedSizeVertical2 = couponData['elemSize']['vertical2']
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
        # self.endStress = -self.nominalStress*(self.b/self.B)
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        self.createPartition()
        self.createMesh()
        self.createMaterial()
        self.createSection()
        # self.createStep()
        # self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (0, self.width/2.0)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.len1/2.0, self.yA)
        (self.xc, self.yc) = (self.xC, self.yC) = (self.xB, -self.yA)
        (self.xd, self.yd) = (self.xD, self.yD) = (0, -self.yA)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.E, 0) # center 1
        #################################################################################################################################################
        self.profileSketch = 2*[None]
        ## define sketch
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_1', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)
        ## horizontal fixed construction line ==>> self.profileGeometry1[2]
        self.profileSketch[0].ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[2])
        ## vertical fixed construction line ==>> self.profileGeometry1[3]
        self.profileSketch[0].ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[3])
        ## rectangle ABCD
        self.profileSketch[0].rectangle(point1=(self.xA, self.yA), point2=(self.xC, self.yC))
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xA, self.yA) = self.profileVertices1[0].coords
        (self.xD, self.yD) = self.profileVertices1[1].coords
        (self.xC, self.yC) = self.profileVertices1[2].coords
        (self.xB, self.yB) = self.profileVertices1[3].coords
        #######################################################################################################################################################
        ## define sketch ==>> part 2 ==>> away from area of interest  #########################################################################################
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileGeometry2, self.profileVertices2 = self.profileSketch[1].geometry, self.profileSketch[1].vertices
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)        
        self.profileSketch[1].CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(self.xC1-self.phi1/2.0, 0))
        self.profileSketch[1].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xC1, self.yC1) = self.profileVertices2[0].coords
        #######################################################################################################################################################
        # self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
        #                  ['A', self.xa, self.ya, self.xA, self.yA],
        #                  ['B', self.xb, self.yb, self.xB, self.yB],
        #                  ['C', self.xc, self.yc, self.xC, self.yC],
        #                  ['D', self.xd, self.yd, self.xD, self.yD],
        #                  ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
        #                  ['lt', '', self.lt, '', (self.xE-self.xF)],
        #                  ['b1', '', self.b, '', (self.yA-self.yH)],
        #                  ['b2', '', self.b, '', (self.yB-self.yG)],
        #                  ['B1', '', self.B, '', (self.yD-self.yE)],
        #                  ['B2', '', self.B, '', (self.yK-self.yJ)],
        #                  ['R1', '', self.R, '', ((self.xC1-self.xC)**2+(self.yC1-self.yC)**2)**0.5],
        #                  ['R2', '', self.R, '', ((self.xC2-self.xF)**2+(self.yC2-self.yF)**2)**0.5],
        #                  ['R3', '', self.R, '', ((self.xC3-self.xI)**2+(self.yC3-self.yI)**2)**0.5],
        #                  ['R4', '', self.R, '', ((self.xC4-self.xL)**2+(self.yC4-self.yL)**2)**0.5],
        #                  ['C1', '', self.C, '', (self.xD-self.xC)],
        #                  ['C2', '', self.C, '', (self.xL-self.xK)],
        #                  ['lc1', '', self.lc, '', (self.xB-self.xA)],
        #                  ['lc2', '', self.lc, '', (self.xG-self.xH)]]
    def createPart(self):
        ## create solid
        self.part = (len(self.profileSketch)-1)*[None]
        self.tempPart = len(self.profileSketch)*[None]
        for i in range(len(self.tempPart)):
            self.tempPart[i] = self.model.Part(name=self.couponName+'_Temp_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.tempPart[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.tempPart[0])        
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.tempInstance = len(self.tempPart)*[None]
        for i in range(len(self.tempPart)):
            self.tempInstance[i] = self.assembly.Instance(name=self.couponName+'_Temp_Instance_'+str(i+1), part=self.tempPart[i], dependent=ON)
        newPartName = self.couponName+'_Part_1'
        self.assembly.InstanceFromBooleanCut(name=newPartName, instanceToBeCut=self.tempInstance[0], cuttingInstances=(self.tempInstance[1], ), originalInstances=DELETE)
        del self.assembly.features[newPartName+'-1']
        self.part[0] = self.model.parts[newPartName]
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])
        ## create actual assembly instances
        self.instance = len(self.part)*[None]
        for i in range(len(self.part)):
            self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
    def createPartition(self):
        def createFacePartition():
            sketchPlane = self.part[0].faces.findAt(coordinates=(self.lenTol, self.lenTol, 0))
            sketchUpEdge = self.part[0].edges.findAt(coordinates=(0, 0, 0))
            t = self.part[0].MakeSketchTransform(sketchPlane=sketchPlane, sketchUpEdge=sketchUpEdge, sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            s1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=50.0, gridSpacing=1.0, transform=t)
            g, v = s1.geometry, s1.vertices
            s1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
            xMid = ((self.xC1-self.phi1/2.0)+self.xO)/2.0
            s1.CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(xMid, 0))
            self.partitionRadius = self.xC1-xMid
            ## line 1
            s1.Line(point1=(2*self.xC1, self.xC1), point2=(self.xC1+self.phi1/2.0*math.sin(math.pi/4.0), self.phi1/2.0*math.cos(math.pi/4.0)))
            s1.PerpendicularConstraint(entity1=g.findAt((2*self.xC1-self.lenTol, (self.xC1-self.lenTol))), entity2=g.findAt(((self.xC1-self.phi1/2.0), 0.0)))
            ## line 2
            s1.Line(point1=(2*self.xC1, -self.xC1), point2=(self.xC1+self.phi1/2.0*math.sin(math.pi/4.0), -self.phi1/2.0*math.cos(math.pi/4.0)))
            s1.PerpendicularConstraint(entity1=g.findAt((2*self.xC1-self.lenTol, -(self.xC1-self.lenTol))), entity2=g.findAt(((self.xC1-self.phi1/2.0), 0.0)))
            ## line 3
            s1.Line(point1=(0, self.xC1), point2=(self.xC1-self.phi1/2.0*math.sin(math.pi/4.0), self.phi1/2.0*math.cos(math.pi/4.0)))
            s1.PerpendicularConstraint(entity1=g.findAt((self.lenTol, (self.xC1-self.lenTol))), entity2=g.findAt(((self.xC1-self.phi1/2.0), 0.0)))
            ## line 4
            s1.Line(point1=(0, -self.xC1), point2=(self.xC1-self.phi1/2.0*math.sin(math.pi/4.0), -self.phi1/2.0*math.cos(math.pi/4.0)))
            s1.PerpendicularConstraint(entity1=g.findAt((self.lenTol, -(self.xC1-self.lenTol))), entity2=g.findAt(((self.xC1-self.phi1/2.0), 0.0)))
            ## create sketch
            self.part[0].PartitionFaceBySketch(sketchUpEdge=sketchUpEdge, faces=sketchPlane, sketch=s1)
            s1.unsetPrimaryObject()
            ## circular partition
            edgesTemp1= self.getByCylinderDifference(self.part[0].edges, (self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.lenTol), (self.partitionRadius+self.lenTol), (self.phi1/2.0+self.lenTol))
            edgesForPartition1 = self.getArcEdge(edgesTemp1)
            sweepPath1 = self.part[0].edges.findAt(coordinates=(self.xA, self.xC1, self.lenTol))
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath1, cells=self.part[0].cells, edges=edgesForPartition1)
            ## diagonal partition 1
            edgesTemp2 = self.part[0].edges.getByBoundingCylinder((self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.lenTol), (self.partitionRadius+self.lenTol))
            edgesTempArc = self.getArcEdge(edgesTemp2)
            edgesForPartition2 = self.getByDifference(edgesTemp2, edgesTempArc)
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath1, cells=self.part[0].cells, edges=edgesForPartition2)
            ## diagonal partition 2
            edgesForPartition3 = self.part[0].edges.findAt(coordinates=((2*self.xC1-self.lenTol, (self.xC1-self.lenTol), 0), (2*self.xC1-self.lenTol, -(self.xC1-self.lenTol), 0), (self.lenTol, (self.xC1-self.lenTol), 0), (self.lenTol, -(self.xC1-self.lenTol), 0)))
            edgesForPartition4 = (edgesForPartition3[0], edgesForPartition3[1], edgesForPartition3[2], edgesForPartition3[3])
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.part[0].edges.findAt(coordinates=(self.xA, self.xC1, self.lenTol)), cells=self.part[0].cells, edges=edgesForPartition4)
        def createPartitionLongYZ(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        def createPartitionLongXZ(offsetDistance):
            ## partition by XZ plane
            self.datumPlaneXZ_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlaneXZ_ID], cells=self.part[0].cells)
        createPartitionLongYZ(2*self.xC1)
        createPartitionLongXZ(self.xC1)
        createPartitionLongXZ(-self.xC1)
        createFacePartition()
        createPartitionLongYZ(self.xC1)
        createPartitionLongXZ(self.yO)
    def createMesh(self):
        ## seed ==>> thickness direction
        edgesThickness = self.part[0].edges.findAt(coordinates=((0, 0, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> inner arc
        edgesInnerArc = self.part[0].edges.getByBoundingCylinder((self.xC1, self.yC1, self.thickness-self.lenTol), (self.xC1, self.yC1, self.thickness+self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesInnerArc, size=self.seedSizeArc, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer arc
        elemNum = self.part[0].getEdgeSeeds(edgesInnerArc[0], attribute=NUMBER)
        edgesTemp1 = self.getByCylinderDifference(self.part[0].edges, (self.xC1, self.yC1, self.thickness-self.lenTol), (self.xC1, self.yC1, self.thickness+self.lenTol), (self.partitionRadius+self.lenTol), (self.phi1/2.0+self.lenTol))
        edgesOuterArc1 = self.getArcEdge(edgesTemp1)
        self.part[0].seedEdgeByNumber(edges=edgesOuterArc1, number=elemNum, constraint=FIXED)
        edgesTemp2 = self.getByCylinderDifference(self.part[0].edges, (self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.lenTol), (self.partitionRadius+self.lenTol), (self.phi1/2.0+self.lenTol))
        edgesOuterArc2 = self.getArcEdge(edgesTemp2)
        self.part[0].seedEdgeByNumber(edges=edgesOuterArc2, number=elemNum, constraint=FIXED)
        ## seed ==>> inner radial
        edgesInnerRadial1 = self.getByDifference(edgesTemp1, edgesOuterArc1)
        self.part[0].seedEdgeBySize(edges=edgesInnerRadial1, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        edgesInnerRadial2 = self.getByDifference(edgesTemp2, edgesOuterArc2)
        self.part[0].seedEdgeBySize(edges=edgesInnerRadial2, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer radial
        edgesOuterRadial = self.part[0].edges.findAt(coordinates=((self.xC1, (self.partitionRadius+self.lenTol), 0), (self.xC1, (self.partitionRadius+self.lenTol), self.thickness), 
                                                                  (self.xC1, -(self.partitionRadius+self.lenTol), 0), (self.xC1, -(self.partitionRadius+self.lenTol), self.thickness), 
                                                                  (self.xC1-(self.partitionRadius+self.lenTol), 0, 0), (self.xC1-(self.partitionRadius+self.lenTol), 0, self.thickness), 
                                                                  (self.xC1+(self.partitionRadius+self.lenTol), 0, 0), (self.xC1+(self.partitionRadius+self.lenTol), 0, self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesOuterRadial, size=self.seedSizeOuterRadial, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> vertical 1 direction
        edgesVertical1 = self.part[0].edges.findAt(coordinates=((0, self.xC1+self.lenTol, 0), (0, self.xC1+self.lenTol, self.thickness), 
                                                                (self.xC1, self.xC1+self.lenTol, 0), (self.xC1, self.xC1+self.lenTol, self.thickness), 
                                                                (2*self.xC1, self.xC1+self.lenTol, 0), (2*self.xC1, self.xC1+self.lenTol, self.thickness), 
                                                                (self.xB, self.xC1+self.lenTol, 0), (self.xB, self.xC1+self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, self.xC1, edgesVertical1, minSize=self.seedSizeVertical1, maxSize=self.seedSizeVertical2)
        ## seed ==>> vertical 2 direction
        edgesVertical2 = self.part[0].edges.findAt(coordinates=((0, -self.xC1-self.lenTol, 0), (0, -self.xC1-self.lenTol, self.thickness), 
                                                                (self.xC1, -self.xC1-self.lenTol, 0), (self.xC1, -self.xC1-self.lenTol, self.thickness), 
                                                                (2*self.xC1, -self.xC1-self.lenTol, 0), (2*self.xC1, -self.xC1-self.lenTol, self.thickness), 
                                                                (self.xB, -self.xC1-self.lenTol, 0), (self.xB, -self.xC1-self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, -self.xC1, edgesVertical2, minSize=self.seedSizeVertical1, maxSize=self.seedSizeVertical2)
        ## seed ==>> long edges along B'B
        pickedEdges1 = self.part[0].edges.getByBoundingBox(xMin=2*self.xC1-self.lenTol, yMin=self.yD-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.yB+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong1 = self.getEdgeByLength(pickedEdges1, abs(self.xB-2*self.xC1))
        self.seedEdge(self.part[0], 0, 2*self.xC1, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHexPart1, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1, ))
        ## generate mesh
        self.couponData.update({'elemNum':dict()})
        for i in range(len(self.part)):
            self.part[i].generateMesh()
            self.couponData['elemNum'].update({'part'+str(i+1):len(self.part[i].elements)})
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF'))
        self.couponData['step'].update({'endPressure':self.endStress})
        ## create pressure load on posX face
        endCellFaceArr1 = self.part[0].faces.getByBoundingBox(xMin=self.xE-self.lenTol, yMin=self.yE-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.thickness+self.lenTol)
        surfNamePosX = 'Surf_PosX_Part_'+str(0+1)
        self.getElemSurfFromCellFace(self.part[0], endCellFaceArr1, surfNamePosX)
        region1 = self.instance[0].surfaces[surfNamePosX]
        self.model.Pressure(name='Load_PosX_Instance_'+str(0+1), createStepName='Load', region=region1, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
        ## create pressure load on negX face
        endCellFaceArr2 = self.part[0].faces.getByBoundingBox(xMin=self.xJ-self.lenTol, yMin=self.yJ-self.lenTol, zMin=-self.lenTol, xMax=self.xK+self.lenTol, yMax=self.yK+self.lenTol, zMax=self.thickness+self.lenTol)
        surfNameNegX = 'Surf_NegX_Part_'+str(0+1)
        self.getElemSurfFromCellFace(self.part[0], endCellFaceArr2, surfNameNegX)
        region2 = self.instance[0].surfaces[surfNameNegX]
        self.model.Pressure(name='Load_NegX_Instance_'+str(0+1), createStepName='Load', region=region2, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)

