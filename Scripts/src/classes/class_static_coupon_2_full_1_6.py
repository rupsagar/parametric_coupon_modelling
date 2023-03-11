from abaqus import *
from abaqusConstants import *
from caeModules import *

class static_coupon_2_full_1_6(coupon_generic):
    def __init__(self, couponData):
        super(static_coupon_2_full_1_6, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.lt = couponData['geometry']['lt']
        self.b = couponData['geometry']['b']
        self.B = couponData['geometry']['B']
        self.R = couponData['geometry']['R']
        self.C = couponData['geometry']['C']
        self.lc = couponData['geometry']['lc']
        self.thickness = couponData['thickness']
        self.lenTol = couponData['lenTol']
        self.seedSizeThickness = couponData['elemSize']['thickness']
        self.seedSizeVertical = couponData['elemSize']['vertical']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeLong3 = couponData['elemSize']['long3']
        self.seedSizeLong4 = couponData['elemSize']['long4']
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
        self.endStress = -self.nominalStress*(self.b/self.B)
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        # self.createPartition()
        # self.createMesh()
        # self.createMaterial()
        # self.createSection()
        # self.createStep()
        # self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (-self.lc/2.0, self.b/2.0)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.lc/2.0, self.yA)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.xB, self.yB+self.R) # center 1
        (self.xc, self.yc) = (self.xC, self.yC) = ((self.lt/2.0-self.C), self.B/2)
        (self.xd, self.yd) = (self.xD, self.yD) = (self.lt/2.0, self.yC)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.xD, -self.yD)
        (self.xf, self.yf) = (self.xF, self.yF) = (self.xC, -self.yC)
        (self.xc2, self.yc2) = (self.xC2, self.yC2) = (self.xC1, -self.yC1) # center 2
        (self.xg, self.yg) = (self.xG, self.yG) = (self.xB, -self.yB)
        (self.xh, self.yh) = (self.xH, self.yH) = (self.xA, -self.yA)
        (self.xc3, self.yc3) = (self.xC3, self.yC3) = (-self.xC1, -self.yC1) # center 3
        (self.xi, self.yi) = (self.xI, self.yI) = (-self.xF, self.yF)
        (self.xj, self.yj) = (self.xJ, self.yJ) = (-self.xE, self.yE)
        (self.xk, self.yk) = (self.xK, self.yK) = (-self.xD, self.yD)
        (self.xl, self.yl) = (self.xL, self.yL) = (-self.xC, self.yC)
        (self.xc4, self.yc4) = (self.xC4, self.yC4) = (-self.xC1, self.yC1) # center 4
        #################################################################################################################################################
        self.profileSketch = 1*[None]
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
        ## line AB
        self.profileSketch[0].Line(point1=(self.xA, self.yA), point2=(self.xB, self.yB))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[3], textPoint=(13, 13), value=self.lc/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], textPoint=(-13, 13), value=self.lc/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[2], textPoint=(4, 4), value=self.b/2)
        ## arc BC
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[1].coords, point2=(self.xC, self.yC), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[5], textPoint=(14, 10), radius=self.R)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[2], textPoint=(13, 4), value=self.B/2)
        ## line CD
        self.profileSketch[0].Line(point1=self.profileVertices1[2].coords, point2=(self.xD, self.yD))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[6], addUndoState=False)
        ## line DE
        self.profileSketch[0].Line(point1=self.profileVertices1[4].coords, point2=(self.xE, self.yE))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        ## line EF
        self.profileSketch[0].Line(point1=self.profileVertices1[5].coords, point2=(self.xF, self.yF))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], textPoint=(13, -4), value=self.B/2)
        ## arc FG
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC2, self.yC2), point1=self.profileVertices1[6].coords, point2=(self.xG, self.yG), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[9], textPoint=(14, -10), radius=self.R)
        ## line GH
        self.profileSketch[0].Line(point1=self.profileVertices1[7].coords, point2=(self.xH, self.yH))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[10], addUndoState=False)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[9], entity2=self.profileGeometry1[10], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[7], entity2=self.profileGeometry1[3], textPoint=(13, -13), value=self.lc/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[9], entity2=self.profileGeometry1[3], textPoint=(-13, -13), value=self.lc/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[10], entity2=self.profileGeometry1[2], textPoint=(4, -4), value=self.b/2)
        ## arc HI
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC3, self.yC3), point1=self.profileVertices1[9].coords, point2=(self.xI, self.yI), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[11], textPoint=(-14, -10), radius=self.R)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[10], entity2=self.profileGeometry1[11], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[10], entity2=self.profileGeometry1[2], textPoint=(-13, -4), value=self.B/2)
        ## line IJ
        self.profileSketch[0].Line(point1=self.profileVertices1[10].coords, point2=(self.xJ, self.yJ))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[12], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[5], entity2=self.profileGeometry1[3], textPoint=(-13, -10), value=self.lt/2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[12], entity2=self.profileGeometry1[3], textPoint=(-13, -10), value=self.lt/2)
        ## line JK
        self.profileSketch[0].Line(point1=self.profileVertices1[12].coords, point2=(self.xK, self.yK))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[13], addUndoState=False)
        ## arc LA
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC4, self.yC4), point1=self.profileVertices1[0].coords, point2=(self.xL, self.yL), direction=CLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[14], textPoint=(-14, 10), radius=self.R)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[14], entity2=self.profileGeometry1[4], addUndoState=False)
        ## line KL
        self.profileSketch[0].Line(point1=self.profileVertices1[13].coords, point2=self.profileVertices1[14].coords)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[15], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[14], entity2=self.profileGeometry1[2], textPoint=(-13, 4), value=self.B/2)
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
                         ['b', '', self.b, '', 2*self.yA],
                         ['B1', '', self.B, '', 2*(self.yD-self.yE)],
                         ['B2', '', self.B, '', 2*(self.yG-self.yF)],
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
            self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])        
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.instance = len(self.part)*[None]
        for i in range(len(self.part)):
            self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
    def createPartition(self):
        def createPartitionLong(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        createPartitionLong(self.xB)
        createPartitionLong(self.xC)
    def createMesh(self):
        ## seed ==>> thickness direction
        edgesThickness = self.part[0].edges.findAt(coordinates=((0, 0, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> vertical direction
        edgesVertical = self.part[0].edges.findAt(coordinates=((0, self.lenTol, 0), ))
        self.part[0].seedEdgeBySize(edges=edgesVertical, size=self.seedSizeVertical, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along AB
        pickedEdges3 = self.part[0].edges.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.yB+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong3 = self.getEdgeByLength(pickedEdges3, abs(self.xB-self.xA))
        self.seedEdge(self.part[0], 0, self.xA, edgesLong3, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> long edges along BC
        pickedEdges1 = self.part[0].edges.getByBoundingBox(xMin=self.xB-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong1 = self.getEdgeByLength(pickedEdges1, abs(self.xC-self.xB))
        self.seedEdge(self.part[0], 0, self.xB, edgesLong1, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> arc BC
        edgesTemp = self.part[0].edges.findAt(coordinates=((self.xB+self.lenTol, 0, 0), ))
        ratioBias = self.part[0].getEdgeSeeds(edgesTemp[0], attribute=BIAS_RATIO)
        elemNum = self.part[0].getEdgeSeeds(edgesTemp[0], attribute=NUMBER)
        edgesTemp2 = self.part[0].edges.getByBoundingBox(xMin=self.xB-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesArc = self.getArcEdge(edgesTemp2)
        self.seedEdge(self.part[0], 0, self.xB, edgesArc, ratio=ratioBias, number=elemNum)
        ## seed ==>> long edges along CD
        pickedEdges3 = self.part[0].edges.getByBoundingBox(xMin=self.xC-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong3 = self.getEdgeByLength(pickedEdges3, abs(self.xD-self.xC))
        self.seedEdge(self.part[0], 0, self.xC, edgesLong3, minSize=self.seedSizeLong3, maxSize=self.seedSizeLong4)
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
        for i in range(len(self.part)):
            ## create BC at negY face
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
            nsetNameNegY = 'Nset_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at negZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.lenTol)
            nsetNamePosZ = 'Nset_NegZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesPosZ, name=nsetNamePosZ)
            region = self.instance[i].sets[nsetNamePosZ]
            self.model.DisplacementBC(name='BC_NegZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==0:
                ## create BC at negX face
                nodesNegX = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xA+self.lenTol, yMax=self.yA+self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
                nsetNameNegX = 'Nset_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==(len(self.part)-1):
                ## create pressure load on posX face
                endCellFaceArr = self.part[i].faces.getByBoundingBox(xMin=self.xD-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.thickness+self.lenTol)
                surfNamePosX = 'Surf_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
                
