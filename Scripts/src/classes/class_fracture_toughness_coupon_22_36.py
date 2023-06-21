#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
#####################    CLASS DEFINITION : FRACTURE TOUGHNESS COUPON : SPECIMEN 22 TO 36  ######################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Jun-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import math
from abaqus import *
from abaqusConstants import *
from caeModules import *

class fracture_toughness_coupon_22_36(coupon_generic):
    def __init__(self, couponData):
        super(fracture_toughness_coupon_22_36, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.width = couponData['geometry']['width']
        self.base = couponData['geometry']['base']
        self.diameter = couponData['geometry']['diameter']
        self.centerOffset1 = couponData['geometry']['centerOffset1']
        self.centerOffset2 = couponData['geometry']['centerOffset2']
        self.notchOffset = couponData['geometry']['notchOffset']
        self.notchOpening1Angle = couponData['geometry']['notchOpening1Angle']
        self.notchOpening2Angle = couponData['geometry']['notchOpening2Angle']
        self.notchTipAngle = couponData['geometry']['notchTipAngle']
        self.notchOpeningTop = couponData['geometry']['notchOpeningTop']
        self.notchOpeningBottom = couponData['geometry']['notchOpeningBottom']
        self.notchOpeningDepth = couponData['geometry']['notchOpeningDepth']
        self.thickness = couponData['thickness']
        self.lenTol = couponData['lenTol']
        # self.seedSizeThickness = couponData['elemSize']['thickness']
        # self.seedSizeVertical = couponData['elemSize']['vertical']
        # self.seedSizeLong1 = couponData['elemSize']['long1']
        # self.seedSizeLong2 = couponData['elemSize']['long2']
        # self.seedSizeLong3 = couponData['elemSize']['long3']
        # self.seedSizeLong4 = couponData['elemSize']['long4']
        # self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        # self.materialName = couponData['material']['name']
        # self.density = couponData['material']['density']
        # self.youngsModulus = couponData['material']['youngsModulus']
        # self.poissonsRatio = couponData['material']['poissonsRatio']
        # self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        # self.initIncr = couponData['step']['initIncr']
        # self.nominalStress = couponData['step']['nominalStress']
        # self.version = couponData['version']
        ## derived quantities
        self.notchOpening1AngleRad = math.pi/180*self.notchOpening1Angle
        self.notchOpening2AngleRad = math.pi/180*self.notchOpening2Angle
        self.notchTipAngleRad = math.pi/180*self.notchTipAngle
        # self.endStress = -self.nominalStress*(self.b/self.B)
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        # self.createAssembly()
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
        (self.xa, self.ya) = (self.xA, self.yA) = (self.notchOpeningTop/2.0, 0)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.notchOpeningTop/2.0+self.notchOpeningDepth/math.tan(self.notchOpening1AngleRad), -self.notchOpeningDepth)
        (self.xc, self.yc) = (self.xC, self.yC) = (self.notchOpeningBottom, self.yB-(self.xB-self.notchOpeningBottom)*math.tan(math.pi-(self.notchOpening1AngleRad+self.notchOpening2AngleRad)))
        (self.xd, self.yd) = (self.xD, self.yD) = (self.xC, -(self.width-self.centerOffset1+self.notchOffset)+self.xC/math.tan(self.notchTipAngleRad/2))
        (self.xe, self.ye) = (self.xE, self.yE) = (0, -(self.width-self.centerOffset1+self.notchOffset))
        (self.xf, self.yf) = (self.xF, self.yF) = (self.base/2, 0)
        (self.xg, self.yg) = (self.xG, self.yG) = (self.base/2, -self.width)
        (self.xh, self.yh) = (self.xH, self.yH) = (0, -self.width)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.centerOffset2/2.0, -(self.width-self.centerOffset1))
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
        ## notch angles construction lines
        self.profileSketch[0].ConstructionLine(point1=(self.xA, self.yA), angle=(180.0-self.notchOpening1Angle))
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[4])
        self.profileSketch[0].ConstructionLine(point1=(self.xB, self.yB), angle=(180.0-(self.notchOpening1Angle+self.notchOpening2Angle)))
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[5])
        ## line AB
        self.profileSketch[0].Line(point1=(self.xA, self.yA), point2=(self.xB, self.yB))
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[3], textPoint=(self.xA/2.0, -self.yB/2.0), value=self.notchOpeningTop/2.0)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[2], textPoint=(self.xB, self.yB/2.0), value=self.notchOpeningDepth)
        ## line BC
        self.profileSketch[0].Line(point1=(self.xB, self.yB), point2=(self.xC, self.yC))
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[3], textPoint=(self.notchOpeningBottom/2, self.yC), value=self.notchOpeningBottom)
        ## line CD
        self.profileSketch[0].Line(point1=(self.xC, self.yC), point2=(self.xD, self.yD))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        ## line DE
        self.profileSketch[0].Line(point1=(self.xD, self.yD), point2=(self.xE, self.yE))
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[4], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].AngularDimension(line1=self.profileGeometry1[3], line2=self.profileGeometry1[9], textPoint=(self.xC/2.0, (self.yD+self.yE)/2.0), value=self.notchTipAngle/2.0)
        ## line AF
        self.profileSketch[0].Line(point1=(self.xA, self.yA), point2=(self.xF, self.yF))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[10], addUndoState=False)
        ## line FG
        self.profileSketch[0].Line(point1=(self.xF, self.yF), point2=(self.xG, self.yG))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[11], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[11], entity2=self.profileGeometry1[3], textPoint=(self.xF, self.yG/2.0), value=self.base/2.0)
        ## line GH
        self.profileSketch[0].Line(point1=(self.xG, self.yG), point2=(self.xH, self.yH))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[12], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileGeometry1[2], textPoint=(self.xG/2.0, self.yG), value=self.width)
        ## circle
        self.profileSketch[0].CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(self.xC1, self.yC1-self.diameter/2.0))
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileVertices1[8], textPoint=(self.xC1, self.yC1/2.0), value=self.centerOffset1)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[3], entity2=self.profileVertices1[8], textPoint=(self.xC1/2.0, self.yC1), value=self.centerOffset2/2.0)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[13], textPoint=(self.xC1+self.diameter, self.yC1), radius=self.diameter/2.0)
        # s1.VerticalDimension(vertex1=v.findAt((0.0, -12.0)), vertex2=v.findAt((-5.5, -5.0)), textPoint=(-18.7339630126953, -5.15250873565674), value=7.0)
        ## copy and mirror
        self.profileSketch[0].copyMirror(mirrorLine=self.profileGeometry1[3], objectList=(self.profileGeometry1[6], self.profileGeometry1[7], self.profileGeometry1[8], self.profileGeometry1[9], 
                                                                    self.profileGeometry1[10], self.profileGeometry1[11], self.profileGeometry1[12], self.profileGeometry1[13]))
        
        # self.profileSketch[0].Line(point1=(self.xO, self.yO), point2=(self.xA, self.yA))
        # self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        # self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[4], addUndoState=False)
        # self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        # self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        # self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[1], textPoint=(-3, 4), value=self.b/2)
        # ## line AB
        # self.profileSketch[0].Line(point1=self.profileVertices1[1].coords, point2=(self.xB, self.yB))
        # self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        # self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[5], entity2=self.profileGeometry1[4], addUndoState=False)
        # self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[2], textPoint=(13, 13), value=self.lc/2)
        # ## arc BC
        # self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[2].coords, point2=(self.xC, self.yC), direction=COUNTERCLOCKWISE)
        # self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=(14, 10), radius=self.R)
        # self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[5], entity2=self.profileGeometry1[6], addUndoState=False)
        # self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[2], textPoint=(13, 4), value=self.B/2)
        # ## line CD
        # self.profileSketch[0].Line(point1=self.profileVertices1[3].coords, point2=(self.xD, self.yD))
        # self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        # self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[5], textPoint=(13, 10), value=self.lt/2)
        # # self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[3], vertex2=self.profileVertices1[5], textPoint=(13, -9), value=self.C)
        # ## line DE
        # self.profileSketch[0].Line(point1=self.profileVertices1[5].coords, point2=(self.xE, self.yE))
        # self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        # self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], addUndoState=False)
        # ## line EO
        # self.profileSketch[0].Line(point1=self.profileVertices1[6].coords, point2=self.profileVertices1[0].coords)
        # self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        # #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        # #######################################################################################################################################################
        # (self.xO, self.yO) = self.profileVertices1[0].coords
        # (self.xA, self.yA) = self.profileVertices1[1].coords
        # (self.xB, self.yB) = self.profileVertices1[2].coords
        # (self.xC, self.yC) = self.profileVertices1[3].coords
        # (self.xC1, self.yC1) = self.profileVertices1[4].coords
        # (self.xD, self.yD) = self.profileVertices1[5].coords
        # (self.xE, self.yE) = self.profileVertices1[6].coords
        #######################################################################################################################################################
        # self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
        #              ['A', self.xa, self.ya, self.xA, self.yA],
        #              ['B', self.xb, self.yb, self.xB, self.yB],
        #              ['C', self.xc, self.yc, self.xC, self.yC],
        #              ['D', self.xd, self.yd, self.xD, self.yD],
        #              ['E', self.xe, self.ye, self.xE, self.yE],
        #              ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
        #              ['lt', '', self.lt, '', 2*(self.xE-self.xO)],
        #              ['b', '', self.b, '', 2*(self.yA-self.yO)],
        #              ['B', '', self.B, '', 2*(self.yD-self.yE)],
        #              ['R', '', self.R, '', ((self.xC1-self.xC)**2+(self.yC1-self.yC)**2)**0.5],
        #              ['C', '', self.C, '', (self.xD-self.xC)],
        #              ['lc', '', self.lc, '', 2*(self.xB-self.xO)]]
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
        pickedEdges3 = self.part[0].edges.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.yB+self.lenTol, zMax=self.thickness/2.0+self.lenTol)
        edgesLong3 = self.getEdgeByLength(pickedEdges3, abs(self.xB-self.xA))
        self.seedEdge(self.part[0], 0, self.xA, edgesLong3, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> long edges along BC
        pickedEdges1 = self.part[0].edges.getByBoundingBox(xMin=self.xB-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.lenTol, zMax=self.thickness/2.0+self.lenTol)
        edgesLong1 = self.getEdgeByLength(pickedEdges1, abs(self.xC-self.xB))
        self.seedEdge(self.part[0], 0, self.xB, edgesLong1, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> arc BC
        edgesTemp = self.part[0].edges.findAt(coordinates=((self.xB+self.lenTol, 0, 0), ))
        ratioBias = self.part[0].getEdgeSeeds(edgesTemp[0], attribute=BIAS_RATIO)
        elemNum = self.part[0].getEdgeSeeds(edgesTemp[0], attribute=NUMBER)
        edgesTemp2 = self.part[0].edges.getByBoundingBox(xMin=self.xB-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xC+self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness/2.0+self.lenTol)
        edgesArc = self.getArcEdge(edgesTemp2)
        self.seedEdge(self.part[0], 0, self.xB, edgesArc, ratio=ratioBias, number=elemNum)
        ## seed ==>> long edges along CD
        pickedEdges3 = self.part[0].edges.getByBoundingBox(xMin=self.xC-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.thickness/2.0+self.lenTol)
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
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.lenTol, zMax=self.thickness/2.0+self.lenTol)
            nsetNameNegY = 'Nset_BC_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at negZ face
            nodesNegZ = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.lenTol)
            nsetNameNegZ = 'Nset_BC_NegZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegZ, name=nsetNameNegZ)
            region = self.instance[i].sets[nsetNameNegZ]
            self.model.DisplacementBC(name='BC_NegZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==0:
                ## create BC at negX face
                nodesNegX = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xA+self.lenTol, yMax=self.yA+self.yC+self.lenTol, zMax=self.thickness/2.0+self.lenTol)
                nsetNameNegX = 'Nset_BC_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==(len(self.part)-1):
                ## create pressure load on posX face
                endCellFaceArr = self.part[i].faces.getByBoundingBox(xMin=self.xD-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.thickness/2.0+self.lenTol)
                surfNamePosX = 'Surf_Load_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
                
