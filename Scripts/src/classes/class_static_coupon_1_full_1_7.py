from abaqus import *
from abaqusConstants import *
from caeModules import *

class static_coupon_1_full_1_7(coupon_generic):
    def __init__(self, couponData):
        super(static_coupon_1_full_1_7, self).__init__()
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
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (-self.lc/2.0, self.d/2.0)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.lc/2.0, self.yA)
        (self.xc, self.yc) = (self.xC, self.yC) = ((self.lt/2.0-self.C), self.D/2)
        (self.xd, self.yd) = (self.xD, self.yD) = (self.lt/2.0, self.yC)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.xD, 0)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.xB, self.yB+self.R) # center 1
        (self.xf, self.yf) = (self.xF, self.yF) = (-self.xE, self.yE)
        (self.xg, self.yg) = (self.xG, self.yG) = (-self.xD, self.yD)
        (self.xh, self.yh) = (self.xH, self.yH) = (-self.xC, self.yC)
        (self.xc2, self.yc2) = (self.xC2, self.yC2) = (-self.xC1, self.yC1) # center 2
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
        ## line AB
        self.profileSketch[0].Line(point1=(self.xA, self.yA), point2=(self.xB, self.yB))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[3], textPoint=(13, 13), value=self.lc/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], textPoint=(-13, 13), value=self.lc/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[2], textPoint=(4, 4), value=self.d/2)
        ## arc BC
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[1].coords, point2=(self.xC, self.yC), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[5], textPoint=(14, 10), radius=self.R)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[2], textPoint=(13, 4), value=self.D/2)
        ## line CD
        self.profileSketch[0].Line(point1=self.profileVertices1[2].coords, point2=(self.xD, self.yD))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[6], addUndoState=False)
        ## line DE
        self.profileSketch[0].Line(point1=self.profileVertices1[4].coords, point2=(self.xE, self.yE))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[5], entity2=self.profileGeometry1[2], addUndoState=False)
        ## line EF
        self.profileSketch[0].Line(point1=self.profileVertices1[5].coords, point2=(self.xF, self.yF))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[5], entity2=self.profileGeometry1[3], textPoint=(13, -10), value=self.lt/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[3], textPoint=(-13, -10), value=self.lt/2)
        ## line FG
        self.profileSketch[0].Line(point1=self.profileVertices1[6].coords, point2=(self.xG, self.yG))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        ## arc AH
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC2, self.yC2), point1=self.profileVertices1[0].coords, point2=(self.xH, self.yH), direction=CLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[10], textPoint=(-14, 10), radius=self.R)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[10], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[8], entity2=self.profileGeometry1[2], textPoint=(-13, 4), value=self.D/2)
        ## line GH
        self.profileSketch[0].Line(point1=self.profileVertices1[7].coords, point2=self.profileVertices1[8].coords)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[11], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xA, self.yA) = self.profileVertices1[0].coords
        (self.xB, self.yB) = self.profileVertices1[1].coords
        (self.xC, self.yC) = self.profileVertices1[2].coords
        (self.xC1, self.yC1) = self.profileVertices1[3].coords
        (self.xD, self.yD) = self.profileVertices1[4].coords
        (self.xE, self.yE) = self.profileVertices1[5].coords
        (self.xF, self.yF) = self.profileVertices1[6].coords
        (self.xG, self.yG) = self.profileVertices1[7].coords
        (self.xH, self.yH) = self.profileVertices1[8].coords
        (self.xC2, self.yC2) = self.profileVertices1[9].coords
        #######################################################################################################################################################
        self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
                         ['A', self.xa, self.ya, self.xA, self.yA],
                         ['B', self.xb, self.yb, self.xB, self.yB],
                         ['C', self.xc, self.yc, self.xC, self.yC],
                         ['D', self.xd, self.yd, self.xD, self.yD],
                         ['E', self.xe, self.ye, self.xE, self.yE],
                         ['F', self.xf, self.yf, self.xF, self.yF],
                         ['G', self.xg, self.yg, self.xG, self.yG],
                         ['H', self.xh, self.yh, self.xH, self.yH],
                         ['Center1', self.xc1, self.yc1, self.xC1, self.yC1],
                         ['Center2', self.xc2, self.yc2, self.xC2, self.yC2],
                         ['lt', '', self.lt, '', (self.xE-self.xF)],
                         ['d', '', self.d, '', 2*self.yA],
                         ['D1', '', self.D, '', 2*(self.yD-self.yE)],
                         ['D2', '', self.D, '', 2*(self.yG-self.yF)],
                         ['R1', '', self.R, '', ((self.xC1-self.xC)**2+(self.yC1-self.yC)**2)**0.5],
                         ['R2', '', self.R, '', ((self.xC2-self.xH)**2+(self.yC2-self.yH)**2)**0.5],
                         ['C1', '', self.C, '', (self.xD-self.xC)],
                         ['C2', '', self.C, '', (self.xH-self.xG)],
                         ['lc', '', self.lc, '', (self.xB-self.xA)]]
    def createPart(self):
        ## create solid
        self.part = len(self.profileSketch)*[None]
        for i in range(len(self.part)):
            self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.part[i].BaseSolidRevolve(sketch=self.profileSketch[0], angle=360, flipRevolveDirection=ON)
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
            self.sketchFace = self.part[0].faces.findAt(((self.xE, 0, 0), ))
            self.sketchEdge = self.part[0].edges.getByBoundingCylinder((self.xE-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.yD+self.lenTol))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(self.xE, 0, 0))
            self.partitionSketch = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch', sheetSize=4, transform=self.transform)
            self.partitionSketch.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch, filter=COPLANAR_EDGES)
            self.partitionSketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0, self.partitionRadius))
            self.partitionSketch.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge[0], faces=self.sketchFace[0], sketch=self.partitionSketch)
            edgesPartition = self.part[0].edges.getByBoundingCylinder((self.xE-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            self.part[0].PartitionCellByExtrudeEdge(line=self.part[0].datums[1], cells=self.part[0].cells, edges=edgesPartition, sense=REVERSE)
        def createPartitionLong(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        createPartitionCyl()
        createPartitionLong(self.xO)
        createPartitionLong(self.xA)
        createPartitionLong(self.xB)
        createPartitionLong(self.xC)
        createPartitionLong(self.xH)
        ## partition by XY plane
        self.datumPlaneXY_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=0).id
        self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlaneXY_ID], cells=self.part[0].cells)
        ## partition by XZ plane
        self.datumPlaneXZ_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=0).id
        self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlaneXZ_ID], cells=self.part[0].cells)
    def createMesh(self):
        def seedLong(part, xLeft, xRight, xPoint, yMax, **kwargs):
            pickedEdges = part.edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (yMax+self.lenTol))
            edgesLong = self.getEdgeByLength(pickedEdges, abs(xRight-xLeft))
            self.seedEdge(part, 0, xPoint, edgesLong, **kwargs)
        def seedInnerCyl(part, xLeft, xRight):
            cellsInnerCyl = part.cells.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            part.setMeshControls(regions=cellsInnerCyl, elemShape=HEX, technique=SWEEP, algorithm=ADVANCING_FRONT)
            edgesSweepPath = part.edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), self.lenTol)
            part.setSweepPath(region=cellsInnerCyl[0], edge=edgesSweepPath[0], sense=FORWARD)
        ## seed ==>> outer arc edge AA'
        edgesOuterCyl = self.getByCylinderDifference(self.part[0].edges, (self.xE-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.yD+self.lenTol), (self.partitionRadius+self.lenTol))
        edgesOuterArc = self.getArcEdge(edgesOuterCyl)
        self.part[0].seedEdgeBySize(edges=edgesOuterArc, size=self.seedSizeArcOuter, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer radial edges
        edgesRadial1 = self.part[0].edges.findAt(coordinates=((self.xE, (self.partitionRadius+self.lenTol), 0), (self.xE, -(self.partitionRadius+self.lenTol), 0), 
                                                              (self.xE, 0, (self.partitionRadius+self.lenTol)), (self.xE, 0, -(self.partitionRadius+self.lenTol))))
        self.seedEdge(self.part[0], 1, 0, edgesRadial1, minSize=self.seedSizeRadialOuter, maxSize=self.seedSizeRadialOuter)
        self.seedEdge(self.part[0], 2, 0, edgesRadial1, minSize=self.seedSizeRadialOuter, maxSize=self.seedSizeRadialOuter)
        ## seed ==>> inner radial edges
        edgesRadial2 = self.part[0].edges.findAt(coordinates=((self.xE, (self.partitionRadius-self.lenTol), 0), (self.xE, -(self.partitionRadius-self.lenTol), 0), 
                                                              (self.xE, 0, (self.partitionRadius-self.lenTol)), (self.xE, 0, -(self.partitionRadius-self.lenTol))))
        self.seedEdge(self.part[0], 1, 0, edgesRadial2, minSize=self.seedSizeRadialInner, maxSize=self.seedSizeRadialInner)
        self.seedEdge(self.part[0], 2, 0, edgesRadial2, minSize=self.seedSizeRadialInner, maxSize=self.seedSizeRadialInner)
        ## sweep path ==>> inner cylinder
        seedInnerCyl(self.part[0], self.xA, self.xB)
        seedInnerCyl(self.part[0], self.xB, self.xC)
        seedInnerCyl(self.part[0], self.xC, self.xD)
        seedInnerCyl(self.part[0], self.xG, self.xH)
        seedInnerCyl(self.part[0], self.xH, self.xA)
        ## seed ==>> longitudinal edges (posX)
        seedLong(self.part[0], self.xO, self.xB, self.xO, self.yD, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        seedLong(self.part[0], self.xB, self.xC, self.xB, self.yD, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong2)
        seedLong(self.part[0], self.xC, self.xD, self.xC, self.yD, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> longitudinal edges (negX)
        seedLong(self.part[0], self.xA, self.xO, self.xO, self.yD, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        seedLong(self.part[0], self.xH, self.xA, self.xA, self.yD, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong2)
        seedLong(self.part[0], self.xG, self.xH, self.xH, self.yD, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> arc BC
        edgesTemp1 = self.part[0].edges.findAt(coordinates=((self.xB+self.lenTol, 0, 0), ))
        ratioBias1 = self.part[0].getEdgeSeeds(edgesTemp1[0], attribute=BIAS_RATIO)
        elemNum1 = self.part[0].getEdgeSeeds(edgesTemp1[0], attribute=NUMBER)
        edgesTemp2 = self.part[0].edges.getByBoundingCylinder((self.xB-self.lenTol, 0, 0), (self.xC+self.lenTol, 0, 0), (self.yC+self.lenTol))
        edgesArc2 = self.getArcEdge(edgesTemp2)
        self.seedEdge(self.part[0], 0, self.xB, edgesArc2, ratio=ratioBias1, number=elemNum1)
        ## seed ==>> arc AH
        edgesTemp3 = self.part[0].edges.findAt(coordinates=((self.xA-self.lenTol, 0, 0), ))
        ratioBias2 = self.part[0].getEdgeSeeds(edgesTemp3[0], attribute=BIAS_RATIO)
        elemNum2 = self.part[0].getEdgeSeeds(edgesTemp3[0], attribute=NUMBER)
        edgesTemp4 = self.part[0].edges.getByBoundingCylinder((self.xH-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yH+self.lenTol))
        edgesArc4 = self.getArcEdge(edgesTemp4)
        self.seedEdge(self.part[0], 0, self.xA, edgesArc4, ratio=ratioBias2, number=elemNum2)
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
        endCellFaceArr = self.part[0].faces.getByBoundingCylinder((self.xD-self.lenTol, 0, 0), (self.xD+self.lenTol, 0, 0), (self.yD+self.lenTol))
        surfNamePosX = 'Surf_PosX_Part_'+str(0+1)
        self.getElemSurfFromCellFace(self.part[0], endCellFaceArr, surfNamePosX)
        region = self.instance[0].surfaces[surfNamePosX]
        self.model.Pressure(name='Load_PosX_Instance_'+str(0+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
        ## create pressure load on negX face
        endCellFaceArr = self.part[0].faces.getByBoundingCylinder((self.xG-self.lenTol, 0, 0), (self.xG+self.lenTol, 0, 0), (self.yG+self.lenTol))
        surfNamePosX = 'Surf_NegX_Part_'+str(0+1)
        self.getElemSurfFromCellFace(self.part[0], endCellFaceArr, surfNamePosX)
        region = self.instance[0].surfaces[surfNamePosX]
        self.model.Pressure(name='Load_NegX_Instance_'+str(0+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)

