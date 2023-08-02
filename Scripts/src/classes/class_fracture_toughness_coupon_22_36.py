#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
##########################    CLASS DEFINITION : FRACTURE COUPON : SPECIMEN 22 TO 36  ###########################
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

class fracture_coupon_22_36(coupon_generic):
    def __init__(self, couponData):
        super(fracture_coupon_22_36, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.height = couponData['geometry']['height']
        self.width = couponData['geometry']['width']
        self.thickness = couponData['geometry']['thickness']
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
        self.lenTol = couponData['lenTol']
        self.seedSizeThickness = couponData['elemSize']['thickness']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeLong3 = couponData['elemSize']['long3']
        self.seedSizeNotch = couponData['elemSize']['notch']
        self.seedSizePinDia = couponData['elemSize']['pinDia']
        self.seedSizePinLength = couponData['elemSize']['pinLength']
        self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        self.elemTypeHexPart2 = SymbolicConstant(couponData['elemType']['hexPart2'])
        self.materialNamePlate = couponData['materialPlate']['name']
        self.densityPlate = couponData['materialPlate']['density']
        self.youngsModulusPlate = couponData['materialPlate']['youngsModulus']
        self.poissonsRatioPlate = couponData['materialPlate']['poissonsRatio']
        self.materialNamePin = couponData['materialPin']['name']
        self.densityPin = couponData['materialPin']['density']
        self.youngsModulusPin = couponData['materialPin']['youngsModulus']
        self.poissonsRatioPin = couponData['materialPin']['poissonsRatio']
        self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        self.initIncr = couponData['step']['initIncr']
        self.pinLoad = couponData['step']['pinLoad']
        self.version = couponData['version']
        ## derived quantities
        self.notchOpening1AngleRad = math.pi/180*self.notchOpening1Angle
        self.notchOpening2AngleRad = math.pi/180*self.notchOpening2Angle
        self.notchTipAngleRad = math.pi/180*self.notchTipAngle
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        self.createPartition()
        self.createMesh()
        self.createMaterial()
        self.createSection()
        self.createEquation()
        self.createContact()
        self.createStep()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (self.notchOpeningTop/2.0, 0)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.notchOpeningTop/2.0+self.notchOpeningDepth/math.tan(self.notchOpening1AngleRad), -self.notchOpeningDepth)
        (self.xc, self.yc) = (self.xC, self.yC) = (self.notchOpeningBottom, self.yB-(self.xB-self.notchOpeningBottom)*math.tan(math.pi-(self.notchOpening1AngleRad+self.notchOpening2AngleRad)))
        (self.xd, self.yd) = (self.xD, self.yD) = (self.xC, -(self.height-self.centerOffset1+self.notchOffset)+self.xC/math.tan(self.notchTipAngleRad/2))
        (self.xe, self.ye) = (self.xE, self.yE) = (0, -(self.height-self.centerOffset1+self.notchOffset))
        (self.xf, self.yf) = (self.xF, self.yF) = (self.width/2, 0)
        (self.xg, self.yg) = (self.xG, self.yG) = (self.width/2, -self.height)
        (self.xh, self.yh) = (self.xH, self.yH) = (0, -self.height)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.centerOffset2/2.0, -(self.height-self.centerOffset1))
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
        self.profileSketch[0].AngularDimension(line1=self.profileGeometry1[3], line2=self.profileGeometry1[9], textPoint=(self.lenTol, (self.yD+self.yE)/2.0), value=self.notchTipAngle/2.0)
        ## line AF
        self.profileSketch[0].Line(point1=(self.xA, self.yA), point2=(self.xF, self.yF))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[10], addUndoState=False)
        ## line FG
        self.profileSketch[0].Line(point1=(self.xF, self.yF), point2=(self.xG, self.yG))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[11], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[11], entity2=self.profileGeometry1[3], textPoint=(self.xF, self.yG/2.0), value=self.width/2.0)
        ## line GH
        self.profileSketch[0].Line(point1=(self.xG, self.yG), point2=(self.xH, self.yH))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[12], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[7], entity2=self.profileGeometry1[3])
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileGeometry1[2], textPoint=(-(self.xG+self.xC1)/2.0, self.yG), value=self.height)
        ## circle
        self.profileSketch[0].CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(self.xC1, self.yC1-self.diameter/2.0))
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileVertices1[8], textPoint=(self.xC1, self.yC1/2.0), value=self.centerOffset1)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[3], entity2=self.profileVertices1[8], textPoint=(self.xC1/2.0, self.yC1), value=self.centerOffset2/2.0)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[13], textPoint=(self.xC1+self.diameter, self.yC1), radius=self.diameter/2.0)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[4], vertex2=self.profileVertices1[8], textPoint=(-self.xC1, (self.yE-self.yC1)/2.0), value=self.notchOffset)
        ## copy and mirror
        self.profileSketch[0].copyMirror(mirrorLine=self.profileGeometry1[3], objectList=(self.profileGeometry1[6], self.profileGeometry1[7], self.profileGeometry1[8], self.profileGeometry1[9], 
                                                                    self.profileGeometry1[10], self.profileGeometry1[11], self.profileGeometry1[12], self.profileGeometry1[13]))
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        ## define sketch ==>> hole ############################################################################################################################
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileGeometry2, self.profileVertices2 = self.profileSketch[1].geometry, self.profileSketch[1].vertices
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)
        self.profileSketch[1].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.diameter/2.0, self.yO))
        self.profileSketch[1].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xA, self.yA) = self.profileVertices1[0].coords
        (self.xB, self.yB) = self.profileVertices1[1].coords
        (self.xC, self.yC) = self.profileVertices1[2].coords
        (self.xD, self.yD) = self.profileVertices1[3].coords
        (self.xE, self.yE) = self.profileVertices1[4].coords
        (self.xF, self.yF) = self.profileVertices1[5].coords
        (self.xG, self.yG) = self.profileVertices1[6].coords
        (self.xH, self.yH) = self.profileVertices1[7].coords
        (self.xC1, self.yC1) = self.profileVertices1[8].coords
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
                     ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
                     ['height', '', self.height, '', (self.yA-self.yH)],
                     ['width', '', self.width, '', 2*(self.xG-self.xH)],
                     ['centerOffset1', '', self.centerOffset1, '', (self.yC1-self.yH)],
                     ['notchOffset', '', self.notchOffset, '', (self.yC1-self.yE)],
                     ['centerOffset2', '', self.centerOffset2, '', 2*self.xC1],
                     ['notchOpeningTop', '', self.notchOpeningTop, '', 2*self.xA],
                     ['notchOpeningBottom', '', self.notchOpeningBottom, '', 2*self.xC],
                     ['notchOpeningDepth', '', self.notchOpeningDepth, '', (self.yA-self.yB)]]
    def createPart(self):
        self.pinLenFactor = 0.5
        ## create solid
        self.part = len(self.profileSketch)*[None]
        for i in range(len(self.part)):
            if i==0:
                self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
            if i==1:
                self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=(1+self.pinLenFactor)*self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])        
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.instance = (len(self.part)+1)*[None]
        for i in range(len(self.instance)):
            if i==0:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
            if i==1:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[1], dependent=ON)
                self.assembly.translate(instanceList=(self.instance[i].name, ), vector=(self.xC1, self.yC1, -self.pinLenFactor/2.0*self.thickness))
            if i==2:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[1], dependent=ON)
                self.assembly.translate(instanceList=(self.instance[i].name, ), vector=(-self.xC1, self.yC1, -self.pinLenFactor/2.0*self.thickness))
    def createPartition(self):
        def createPartitionCyl():
            ## partition face
            self.sketchFace = self.part[0].faces.findAt(coordinates=(self.xA+self.lenTol, self.yA-self.lenTol, self.thickness))
            self.sketchEdge = self.part[0].edges.findAt(coordinates=(self.xF, self.yF-self.lenTol, self.thickness))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace, sketchUpEdge=self.sketchEdge, sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=200, transform=self.transform)
            self.partitionSketch1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch1, filter=COPLANAR_EDGES)
            self.partitionSketch1.ArcByCenterEnds(center=(0, self.yE), point1=(-self.xD, self.yD), point2=(self.xD, self.yD), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.ArcByCenterEnds(center=(0, self.yE), point1=(-(self.xD+self.xE)/2.0, (self.yD+self.yE)/2.0), point2=((self.xD+self.xE)/2.0, (self.yD+self.yE)/2.0), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge, faces=self.sketchFace, sketch=self.partitionSketch1)
            ## partition solid
            edges1 = self.part[0].edges.getByBoundingCylinder((0, self.yE, self.thickness+self.lenTol), (0, self.yE, self.thickness-self.lenTol), (((((self.xD+self.xE)/2.0)**2+((self.yD+self.yE)/2.0)**2))**0.5+self.lenTol))
            edges1Arc = self.getArcEdge(edges1)
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.part[0].edges.findAt(coordinates=(self.xD, self.yD, self.lenTol)), cells=self.part[0].cells, edges=(edges1Arc[0],))
            edges2 = self.getByCylinderDifference(self.part[0].edges, (0, self.yE, self.thickness+self.lenTol), (0, self.yE, self.thickness-self.lenTol), (((self.xD**2+self.yD**2)**0.5+self.lenTol), (((((self.xD+self.xE)/2.0)**2+((self.yD+self.yE)/2.0)**2))**0.5+self.lenTol)))
            edges2Arc = self.getArcEdge(edges2)
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.part[0].edges.findAt(coordinates=(self.xD, self.yD, self.lenTol)), cells=self.part[0].cells, edges=(edges2Arc[0],))
        def createPartitionDatumPlane(thisPart, thisPlane, offsetDistance):
            self.datumPlane_ID = thisPart.DatumPlaneByPrincipalPlane(principalPlane=SymbolicConstant(thisPlane), offset=offsetDistance).id
            thisPart.PartitionCellByDatumPlane(datumPlane=thisPart.datums[self.datumPlane_ID], cells=thisPart.cells)
        # createPartitionCyl()
        createPartitionDatumPlane(self.part[0], 'XZPLANE', self.yC1)
        createPartitionDatumPlane(self.part[0], 'XZPLANE', self.yB)
        createPartitionDatumPlane(self.part[0], 'XZPLANE', self.yC1-abs(self.yC1-self.yB))
        createPartitionDatumPlane(self.part[0], 'XZPLANE', self.yE-self.xC1)
        createPartitionDatumPlane(self.part[0], 'XZPLANE', self.yD)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', self.xO)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', self.xC1)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', -self.xC1)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', self.xD)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', -self.xD)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', (self.xC1+(self.xC1-self.xD)))
        createPartitionDatumPlane(self.part[0], 'YZPLANE', -(self.xC1+(self.xC1-self.xD)))
        self.part[0].PartitionCellByExtendFace(extendFace=self.part[0].faces.findAt(coordinates=((self.xA+self.xB)/2.0, (self.yA+self.yB)/2.0, self.lenTol)), cells=self.part[0].cells.findAt(((self.xC, self.yC, 0), )))
        self.part[0].PartitionCellByExtendFace(extendFace=self.part[0].faces.findAt(coordinates=(-(self.xA+self.xB)/2.0, (self.yA+self.yB)/2.0, self.lenTol)), cells=self.part[0].cells.findAt(((-self.xC, self.yC, 0), )))
        # createPartitionDatumPlane(self.part[1], 'XZPLANE', self.yO)
        createPartitionDatumPlane(self.part[1], 'YZPLANE', self.xO)
        createPartitionDatumPlane(self.part[1], 'XYPLANE', self.pinLenFactor/2.0*self.thickness)
        createPartitionDatumPlane(self.part[1], 'XYPLANE', (1+self.pinLenFactor/2.0)*self.thickness)
    def createMesh(self):
        ## seed ==>> edges thickness
        numThicknessElem = self.thickness/self.seedSizeThickness
        if (numThicknessElem%2)!=0:
            numThicknessElem = math.ceil(numThicknessElem)
            if ((numThicknessElem/2)%2)!=0:
                numThicknessElem = numThicknessElem+1
        edgesThickness = self.part[0].edges.findAt(coordinates=((self.xE, self.yE, self.lenTol), ))
        # self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        self.part[0].seedEdgeByNumber(edges=edgesThickness, number=int(numThicknessElem), constraint=FINER)
        ## seed ==>> edges long 1
        edgesLong1 = self.part[0].edges.findAt(coordinates=((self.xE, self.yE-self.lenTol, 0), (self.xE, self.yE-self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, self.yE, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> edges long 2
        edgesLong2Temp1 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yE-self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp2 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yE-self.xC1-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yE-self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp3 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yG+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp4 = self.getByDifference(edgesLong2Temp1, edgesLong2Temp2)
        edgesLong2 = self.getByDifference(edgesLong2Temp4, edgesLong2Temp3)
        self.seedEdge(self.part[0], 1, (self.yE-self.xC1), edgesLong2, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> edges long 3
        # edgesLong3Temp1 = self.part[0].edges.getByBoundingBox(xMin=(self.xC1+(self.xC1-self.xD)-self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesLong3Temp2 = self.part[0].edges.getByBoundingBox(xMin=(self.xC1+(self.xC1-self.xD)-self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xC1+(self.xC1-self.xD)+self.lenTol), yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesLong3Temp3 = self.part[0].edges.getByBoundingBox(xMin=(self.xF-self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xC1+(self.xC1-self.xD)+self.lenTol), yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesLong3Temp4 = self.getByDifference(edgesLong3Temp1, edgesLong3Temp2)
        # edgesLong3 = self.getByDifference(edgesLong3Temp4, edgesLong3Temp3)
        # self.seedEdge(self.part[0], 0, self.xC1+(self.xC1-self.xD), edgesLong3, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> notch edge
        edgesNotch = self.part[0].edges.findAt(coordinates=(((self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), 0), 
                                                            (-(self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), 0), 
                                                            ((self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), self.thickness), 
                                                            (-(self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesNotch, size=self.seedSizeNotch, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin circumference portion
        self.part[1].seedEdgeBySize(edges=self.getArcEdge(self.part[1].edges), size=self.seedSizePinDia, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin length portion
        edgesPin1 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, -self.lenTol), (self.xO, self.yO, self.lenTol), (self.diameter/2.0+self.lenTol))
        edgesPin2 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol-self.lenTol), (self.xO, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol), (self.diameter/2.0+self.lenTol))
        edgesPin3 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, (1+self.pinLenFactor/2.0)*self.thickness-self.lenTol), (self.xO, self.yO, (1+self.pinLenFactor/2.0)*self.thickness+self.lenTol), (self.diameter/2.0+self.lenTol))
        edgesPin4 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol), (self.xO, self.yO, (1+self.pinLenFactor)*self.thickness+self.lenTol), (self.diameter/2.0+self.lenTol))
        edgesPinTemp1 = self.getByCylinderDifference(self.part[1].edges, (self.xO, self.yO, -self.lenTol), (self.xO, self.yO, (1+self.pinLenFactor)*self.thickness+self.lenTol), (self.diameter/2.0+self.lenTol), (self.diameter/2.0-self.lenTol))
        edgesPinTemp2 = self.getByDifference(edgesPinTemp1, edgesPin1)
        edgesPinTemp3 = self.getByDifference(edgesPinTemp2, edgesPin2)
        edgesPinTemp4 = self.getByDifference(edgesPinTemp3, edgesPin3)
        edgesPin = self.getByDifference(edgesPinTemp4, edgesPin4)
        self.part[1].seedEdgeBySize(edges=edgesPin, size=self.seedSizePinLength, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin diameter portion
        numDiaElem = self.diameter/self.seedSizePinDia
        if (numDiaElem%2)!=0:
            numDiaElem = math.ceil(numDiaElem)
            if ((numDiaElem/2)%2)!=0:
                numDiaElem = numDiaElem+1
        diaEdges = self.part[1].edges.findAt(coordinates=((self.xO, self.yO, 0), (self.xO, self.yO, self.pinLenFactor/2.0*self.thickness), (self.xO, self.yO, (1+self.pinLenFactor/2.0)*self.thickness), (self.xO, self.yO, (1+self.pinLenFactor)*self.thickness)))
        self.part[1].seedEdgeByNumber(edges=diaEdges, number=int(numDiaElem), constraint=FIXED)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHexPart1, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1, ))
        elemType2 = mesh.ElemType(elemCode=self.elemTypeHexPart2, elemLibrary=STANDARD)
        self.part[1].setElementType(regions=(self.part[1].cells,), elemTypes=(elemType2, ))
        ## generate mesh
        self.couponData.update({'elemNum':dict()})
        for i in range(len(self.part)):
            self.part[i].generateMesh()
            self.couponData['elemNum'].update({'part'+str(i+1):len(self.part[i].elements)})
    def createMaterial(self):
        ## material definition
        self.materialPlate = self.model.Material(name=self.materialNamePlate)
        self.materialPlate.Density(table=((self.densityPlate, ), ))
        self.materialPlate.Elastic(table=((self.youngsModulusPlate, self.poissonsRatioPlate), ))
        self.materialPin = self.model.Material(name=self.materialNamePin)
        self.materialPin.Density(table=((self.densityPin, ), ))
        self.materialPin.Elastic(table=((self.youngsModulusPin, self.poissonsRatioPin), ))
    def createSection(self):
        ## section definition and assigning section property to elements
        self.sectionPlate = self.model.HomogeneousSolidSection(name=self.couponName+'_Section_Plate', material=self.materialNamePlate, thickness=None)
        self.sectionPin = self.model.HomogeneousSolidSection(name=self.couponName+'_Section_Pin', material=self.materialNamePin, thickness=None)
        for i in range(len(self.part)):
            if i==0:
                pickedRegion = self.part[i].Set(elements=self.part[i].elements, name='Elset_All_Part_'+str(i+1))
                self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.sectionPlate.name, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
            if i==1:
                pickedRegion = self.part[i].Set(elements=self.part[i].elements, name='Elset_All_Part_'+str(i+1))
                self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.sectionPin.name, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def createEquation(self):
        i=1
        nodesEqnPosY = self.part[i].nodes.getByBoundingSphere((self.xO, self.diameter/2.0, 0), self.lenTol)
        nsetNameEqnPosY = 'Nset_Eqn_Part_'+str(i+1)+'_PosY'
        self.part[i].Set(nodes=nodesEqnPosY, name=nsetNameEqnPosY)
        nodesEqnNegY = self.part[i].nodes.getByBoundingSphere((self.xO, -self.diameter/2.0, 0), self.lenTol)
        nsetNameEqnNegY = 'Nset_Eqn_Part_'+str(i+1)+'_NegY'
        self.part[i].Set(nodes=nodesEqnNegY, name=nsetNameEqnNegY)
        self.model.Equation(name=self.couponName+'_Equation_1', terms=((1.0, self.instance[1].name+'.'+nsetNameEqnPosY, 1), (-1.0, self.instance[1].name+'.'+nsetNameEqnNegY, 1)))
        self.model.Equation(name=self.couponName+'_Equation_2', terms=((1.0, self.instance[2].name+'.'+nsetNameEqnPosY, 1), (-1.0, self.instance[2].name+'.'+nsetNameEqnNegY, 1)))
    def createContact(self):
        for i in range(len(self.part)):
            if i==0:
                ## contact surface ==> plate cyl1
                faceCellPlateCyl1 = self.part[0].faces.getByBoundingCylinder((self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.thickness+self.lenTol), (self.diameter/2.0+self.lenTol))
                nameSurfPlateCyl1 = 'Surf_Contact_Part_'+str(i+1)+'_Cyl_1'
                self.getElemSurfFromCellFace(self.part[i], faceCellPlateCyl1, nameSurfPlateCyl1)
                regionPlateCyl1 = self.instance[0].surfaces[nameSurfPlateCyl1]
                ## plate contact surface ==> cyl2
                faceCellPlateCyl2 = self.part[0].faces.getByBoundingCylinder((-self.xC1, self.yC1, -self.lenTol), (-self.xC1, self.yC1, self.thickness+self.lenTol), (self.diameter/2.0+self.lenTol))
                nameSurfPlateCyl2 = 'Surf_Contact_Part_'+str(i+1)+'_Cyl_2'
                self.getElemSurfFromCellFace(self.part[i], faceCellPlateCyl2, nameSurfPlateCyl2)
                regionPlateCyl2 = self.instance[0].surfaces[nameSurfPlateCyl2]
            if i==1:
                # contact surface ==> pin
                faceCellPin = self.part[i].faces.findAt(coordinates=((self.xO-self.diameter/2.0, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol), (self.xO+self.diameter/2.0, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol)))
                nameSurfPin = 'Surf_Contact_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPin, nameSurfPin)
                regionPin1 = self.instance[1].surfaces[nameSurfPin]
                regionPin2 = self.instance[2].surfaces[nameSurfPin]
        self.contactProperty = self.model.ContactProperty(self.couponName+'_Contact_Property')
        self.contactProperty.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact_1', createStepName='Initial', master=regionPin1, slave=regionPlateCyl1, sliding=SMALL, thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=0.0, datumAxis=None, clearanceRegion=None)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact_2', createStepName='Initial', master=regionPin2, slave=regionPlateCyl2, sliding=SMALL, thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=0.0, datumAxis=None, clearanceRegion=None)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF', 'CF', 'CDISP', 'CSTRESS'))
        for i in range(len(self.part)):
            if i==0:
                ## plate ==> BC
                # nodesNegZ = self.part[i].nodes.getByBoundingBox(xMin=-(self.xC1+(self.xC1-self.xD))-self.lenTol, yMin=self.yC1-abs(self.yC1-self.yB)-self.lenTol, zMin=-self.lenTol, xMax=(self.xC1+(self.xC1-self.xD))+self.lenTol, yMax=self.lenTol, zMax=self.lenTol)
                # nameNsetPlateBC = 'Nset_NegZ_Part_'+str(i+1)
                # self.part[i].Set(nodes=nodesNegZ, name=nameNsetPlateBC)
                # regionPlateBC = self.instance[0].sets[nameNsetPlateBC]
                # self.model.DisplacementBC(name='BC_NegZ_Instance_'+str(1), createStepName='Load', region=regionPlateBC, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=SET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## BC ==> Z
                nodePlateBCNegX = self.part[i].nodes.getByBoundingSphere((self.xG, self.yG, self.thickness/2.0), self.lenTol)
                nodePlateBCPosX = self.part[i].nodes.getByBoundingSphere((-self.xG, self.yG, self.thickness/2.0), self.lenTol)
                nodePlateBC_Z = [nodePlateBCNegX, nodePlateBCPosX]
                nsetNamePlateBC_Z = 'Nset_BC_Z_Part_'+str(i+1)
                self.part[i].Set(nodes=nodePlateBC_Z , name=nsetNamePlateBC_Z)
                regionPlateBC_Z = self.instance[0].sets[nsetNamePlateBC_Z]
                self.model.DisplacementBC(name='BC_Z_Instance_'+str(1), createStepName='Load', region=regionPlateBC_Z, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## BC ==> X
                nodePlateBCNegZ = self.part[i].nodes.getByBoundingSphere((self.xH, self.yH, 0), self.lenTol)
                nodePlateBCPosZ = self.part[i].nodes.getByBoundingSphere((self.xH, self.yH, self.thickness), self.lenTol)
                nodePlateBC_X = [nodePlateBCNegZ, nodePlateBCPosZ]
                nsetNamePlateBC_X = 'Nset_BC_X_Part_'+str(i+1)
                self.part[i].Set(nodes=nodePlateBC_X , name=nsetNamePlateBC_X)
                regionPlateBC_X = self.instance[0].sets[nsetNamePlateBC_X]
                self.model.DisplacementBC(name='BC_X_Instance_'+str(1), createStepName='Load', region=regionPlateBC_X, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==1:
                ## pin ==> BC_Z
                nodesNegZ = self.part[i].nodes.getByBoundingSphere((self.xO, self.yO, 0), self.lenTol)
                nodesPosZ = self.part[i].nodes.getByBoundingSphere((self.xO, self.yO, (1+self.pinLenFactor)*self.thickness), self.lenTol)
                nodesPinBC_Z = [nodesNegZ, nodesPosZ]
                nsetNamePinBC_Z = 'Nset_BC_Z_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesPinBC_Z , name=nsetNamePinBC_Z)
                regionPin1BC_Z = self.instance[1].sets[nsetNamePinBC_Z]
                self.model.DisplacementBC(name='BC_Z_Instance_'+str(2), createStepName='Load', region=regionPin1BC_Z, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                # self.model.DisplacementBC(name='BC_Z_Instance_'+str(2), createStepName='Load', region=regionPin1BC_Z, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                regionPin2BC_Z = self.instance[2].sets[nsetNamePinBC_Z]
                # self.model.DisplacementBC(name='BC_Z_Instance_'+str(3), createStepName='Load', region=regionPin2BC_Z, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                self.model.DisplacementBC(name='BC_Z_Instance_'+str(3), createStepName='Load', region=regionPin2BC_Z, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                # self.model.DisplacementBC(name='BC_Z_Instance_'+str(3), createStepName='Load', region=regionPin2BC_Z, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## pin ==> BC_X
                # faceCellPinBC_X = self.part[i].faces.findAt(coordinates=((self.xO+self.diameter/2.0, self.yO, self.lenTol), (self.xO+self.diameter/2.0, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol)))
                # nameNsetPinBC_X = 'Nset_BC_X_Part_'+str(i+1)
                # self.getNsetFromCellFace(self.part[i], faceCellPinBC_X, nameNsetPinBC_X)
                # regionPin2BC_X = self.instance[2].sets[nameNsetPinBC_X]
                # self.model.DisplacementBC(name='BC_NegX_Instance_'+str(3), createStepName='Load', region=regionPin2BC_X, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=SET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## pin ==> presssure/concentrated load
                # self.model.ConcentratedForce(name='Point_Load_1', createStepName='Load', region=regionPin1BC_Z, cf1=self.pinLoad, distributionType=UNIFORM, field='', localCsys=None)
                faceCellPinLoadNegX = self.part[i].faces.findAt(coordinates=((self.xO-self.diameter/2.0, self.yO, self.lenTol), (self.xO-self.diameter/2.0, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol)))
                nameSurfPinLoadNegX = 'Surf_NegX_Load_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPinLoadNegX, nameSurfPinLoadNegX)
                regionPin1BC = self.instance[1].surfaces[nameSurfPinLoadNegX]
                faceCellPinLoadPosX = self.part[i].faces.findAt(coordinates=((self.xO+self.diameter/2.0, self.yO, self.lenTol), (self.xO+self.diameter/2.0, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol)))
                nameSurfPinLoadPosX = 'Surf_PosX_Load_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPinLoadPosX, nameSurfPinLoadPosX)
                regionPin2BC = self.instance[2].surfaces[nameSurfPinLoadPosX]
                self.model.Pressure(name='Load_NegX_Pressure_Instance_'+str(2), createStepName='Load', region=regionPin1BC, distributionType=UNIFORM, field='', magnitude=self.pinLoad, amplitude=UNSET)
                self.model.Pressure(name='Load_PosX_Pressure_Instance_'+str(3), createStepName='Load', region=regionPin2BC, distributionType=UNIFORM, field='', magnitude=self.pinLoad, amplitude=UNSET)

