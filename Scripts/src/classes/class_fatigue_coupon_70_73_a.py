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
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (0, self.h1/2)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.rad1*(1-((self.rad1+self.h1/2-self.h2/2)/self.rad1)**2)**0.5, self.h2/2)
        (self.xc, self.yc) = (self.xC, self.yC) = (self.len1/2, self.yB)
        (self.xd, self.yd) = (self.xD, self.yD) = (self.xC, 0)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (0, self.yA+self.rad1) # center 1
        ###############################################################################################################################################
        self.profileSketch = 1*[None]
        ## define sketch ##############################################################################################################################
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)
        ## horizontal fixed construction line ==>> self.profileGeometry1[2]
        self.profileSketch[0].ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[2])
        ## vertical fixed construction line ==>> self.profileGeometry1[3]
        self.profileSketch[0].ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[3])
        ## line OA: self.profileGeometry1[4]; vertices ==>> self.profileVertices1[0], self.profileVertices1[1]; dimension: d[0]
        self.profileSketch[0].Line(point1=(self.xO, self.yO), point2=(self.xA, self.yA))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].ObliqueDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[1], textPoint=(-3, 4), value=self.h1/2)
        ## arc AB: self.profileGeometry1[5]; vertices ==>> self.profileVertices1[1], self.profileVertices1[2]; center: self.profileVertices1[3]; dimension: d[1], d[2]
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[1].coords, point2=(self.xB, self.yB), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[5], textPoint=(0, 25), radius=self.rad1)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[2], textPoint=(10, 1), value=self.h2/2)
        ## line BC: self.profileGeometry1[6]; vertices ==>> self.profileVertices1[3], self.profileVertices1[4]; dimension: d[3]
        self.profileSketch[0].Line(point1=self.profileVertices1[2].coords, point2=(self.xC, self.yC))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[6], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[4], textPoint=(13, -9), value=self.len1/2)
        ## line CD: self.profileGeometry1[7]; vertices ==>> self.profileVertices1[4], self.profileVertices1[5]
        self.profileSketch[0].Line(point1=self.profileVertices1[4].coords, point2=(self.xD, self.yD))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[5], entity2=self.profileGeometry1[2], addUndoState=False)
        ## line DO: self.profileGeometry1[8]; vertices ==>> self.profileVertices1[5], self.profileVertices1[0]
        self.profileSketch[0].Line(point1=self.profileVertices1[5].coords, point2=self.profileVertices1[0].coords)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xO, self.yO) = self.profileVertices1[0].coords
        (self.xA, self.yA) = self.profileVertices1[1].coords
        (self.xB, self.yB) = self.profileVertices1[2].coords
        (self.xC1, self.yC1) = self.profileVertices1[3].coords
        (self.xC, self.yC) = self.profileVertices1[4].coords
        (self.xD, self.yD) = self.profileVertices1[5].coords
        #######################################################################################################################################################
        self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
                     ['A', self.xa, self.ya, self.xA, self.yA],
                     ['B', self.xb, self.yb, self.xB, self.yB],
                     ['C', self.xc, self.yc, self.xC, self.yC],
                     ['D', self.xd, self.yd, self.xD, self.yD],
                     ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
                     ['h1', '', self.h1, '', 2*(self.yA-self.yO)],
                     ['h2', '', self.h2, '', 2*(self.yB-self.yO)],
                     ['rad1', '', self.rad1, '', ((self.xC1-self.xB)**2+(self.yC1-self.yB)**2)**0.5],
                     ['len1', '', self.len1, '', 2*(self.xC-self.xO)]]
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
    def createMesh(self):
        ## seed ==>> thickness direction
        edgesThickness = self.part[0].edges.findAt(((0, 0, self.thickness/2),))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along AB
        pickedEdges1 = self.part[0].edges.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong1 = self.getEdgeByLength(pickedEdges1, abs(self.xB-self.xA))
        self.seedEdge(self.part[0], 0, self.xA, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> arc along AB
        pickedEdges2 = self.part[0].edges
        edgesLong2 = self.getArcEdge(pickedEdges2)
        biasRatio = self.part[0].getEdgeSeeds(edgesLong1[0], attribute=BIAS_RATIO)
        elemNum = self.part[0].getEdgeSeeds(edgesLong1[0], attribute=NUMBER)
        self.seedEdge(self.part[0], 0, self.xA, edgesLong2, ratio=biasRatio, number=elemNum)
        ## seed ==>> long edges along BC
        pickedEdges3 = self.part[0].edges.getByBoundingBox(xMin=self.xB-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong3 = self.getEdgeByLength(pickedEdges3, abs(self.xC-self.xB))
        self.seedEdge(self.part[0], 0, self.xB, edgesLong3, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> vertical edge
        edgesVertical1 = self.part[0].edges.findAt(((self.xO, self.yA/2, 0),))
        self.part[0].seedEdgeBySize(edges=edgesVertical1, size=self.seedSizeVertical, deviationFactor=0.1, constraint=FINER)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHex, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1,))
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
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
            nsetNameNegY = 'Nset_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at negZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.lenTol)
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
                endCellFaceArr = self.part[i].faces.getByBoundingBox(xMin=self.xC-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
                surfNamePosX = 'Surf_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
                
        
