from abaqus import *
from abaqusConstants import *
from caeModules import *

class static_coupon_2_1_6(coupon_generic):
    def __init__(self, couponData):
        super(static_coupon_2_1_6, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.lt = couponData['geometry']['lt']
        self.b = couponData['geometry']['b']
        self.B = couponData['geometry']['B']
        self.R = couponData['geometry']['R']
        self.C = couponData['geometry']['C']
        self.lc = couponData['geometry']['lc']
        self.thickness = couponData['geometry']['thickness']
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
        self.partitionRadius = self.partitionRadialFraction*self.b/2
        self.endStress = -self.nominalStress*(self.b/self.B)**2
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
        self.coordO = (self.xO, self.yO) = (0, 0)
        (self.xA, self.yA) = (self.xA, self.yA) = (0, self.b/2.0)
        (self.xB, self.yB) = (self.xB, self.yB) = (self.lc/2.0, self.yA)
        (self.xC, self.yC) = (self.xC, self.yC) = ((self.lt/2.0-self.C), self.B/2)
        (self.xD, self.yD) = (self.xD, self.yD) = (self.lt/2.0, self.yC)
        (self.xE, self.yE) = (self.xE, self.yE) = (self.xD, 0)
        (self.xC1, self.yC1) = (self.xC1, self.yC1) = (self.xB, self.yB+self.R) # center 1
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
        self.profileSketch[0].Line(point1=(self.xO, self.yO), point2=(self.xA, self.yA))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[1], textPoint=(-3, 4), value=self.b/2)
        (self.xO, self.yO), (self.xA, self.yA) = self.profileVertices1[0].coords, self.profileVertices1[1].coords
        ## line AB
        self.profileSketch[0].Line(point1=(self.xA, self.yA), point2=(self.xB, self.yB))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[5], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[2], textPoint=(13, 13), value=self.lc/2)
        (self.xA, self.yA), (self.xB, self.yB) = self.profileVertices1[1].coords, self.profileVertices1[2].coords
        ## arc BC
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=(self.xB, self.yB), point2=(self.xC, self.yC), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=(14, 10), radius=self.R)
        (self.xB, self.yB), (self.xC, self.yC), (self.xC1, self.yC1) = self.profileVertices1[2].coords, self.profileVertices1[3].coords, self.profileVertices1[4].coords
        ## line CD
        self.profileSketch[0].Line(point1=(self.xC, self.yC), point2=(self.xD, self.yD))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[5], textPoint=(13, 10), value=self.lt/2)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[3], vertex2=self.profileVertices1[5], textPoint=(13, -9), value=self.C)
        (self.xC, self.yC), (self.xD, self.yD) = self.profileVertices1[3].coords, self.profileVertices1[5].coords
        ## line DE
        self.profileSketch[0].Line(point1=(self.xD, self.yD), point2=(self.xE, self.yE))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[5], vertex2=self.profileVertices1[6], textPoint=(13, 4), value=self.B/2)
        (self.xD, self.yD), (self.xE, self.yE) = self.profileVertices1[5].coords, self.profileVertices1[6].coords
        ## line EO
        self.profileSketch[0].Line(point1=(self.xE, self.yE), point2=self.coordO)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
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
    
