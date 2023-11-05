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

class coupon_09_fracture_22_36(coupon_generic):
    def __init__(self, couponData):
        super(coupon_09_fracture_22_36, self).__init__(couponData)
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.height = self.geometry['Height']
        self.width = self.geometry['Width']
        self.thickness = self.geometry['Thickness']
        self.phi = self.geometry['Diameter']
        self.centerOffset1 = self.geometry['Center_Offset_1']
        self.notchOffset = self.geometry['Notch_Offset']
        self.centerOffset2 = self.geometry['Center_Offset_2']
        self.notchOpening1Angle = self.geometry['Notch_Opening_Angle_1']
        self.notchOpening2Angle = self.geometry['Notch_Opening_Angle_2']
        self.notchTipAngle = self.geometry['Notch_Tip_Angle']
        self.notchOpeningTop = self.geometry['Notch_Opening_Top']
        self.notchOpeningBottom = self.geometry['Notch_Opening_Bottom']
        self.notchOpeningDepth = self.geometry['Notch_Opening_Depth']
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
        self.createLocalSeed()
        self.createMesh()
        self.createMaterial()
        self.createSection()
        self.createEquation()
        self.createContact()
        self.createStep()
        self.createLoadBC()
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
        self.profileSketch[0].CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(self.xC1, self.yC1-self.phi/2.0))
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileVertices1[8], textPoint=(self.xC1, self.yC1/2.0), value=self.centerOffset1)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[3], entity2=self.profileVertices1[8], textPoint=(self.xC1/2.0, self.yC1), value=self.centerOffset2/2.0)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[13], textPoint=(self.xC1+self.phi, self.yC1), radius=self.phi/2.0)
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
        self.profileSketch[1].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.phi/2.0, self.yO))
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
        def createPartitionDatumPlane(thisPart, thisCells, thisPlane, offsetDistance):
            self.datumPlane_ID = thisPart.DatumPlaneByPrincipalPlane(principalPlane=SymbolicConstant(thisPlane), offset=offsetDistance).id
            thisPart.PartitionCellByDatumPlane(datumPlane=thisPart.datums[self.datumPlane_ID], cells=thisCells)
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'XZPLANE', self.yC1)
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'XZPLANE', self.yB)
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'XZPLANE', self.yC)
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'XZPLANE', self.yC1-abs(self.yC1-self.yC))
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'XZPLANE', self.yE-self.xC1)
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'XZPLANE', self.yD)
        createPartitionDatumPlane(self.part[0], self.part[0].cells, 'YZPLANE', self.xO)
        for i in range(2):
            createPartitionDatumPlane(self.part[0], self.part[0].cells, 'YZPLANE', (-1)**i*self.xC1)
            createPartitionDatumPlane(self.part[0], self.part[0].cells, 'YZPLANE', (-1)**i*(self.xC1+(self.xC1-self.xD)))
            cellLowerBox = self.part[0].cells.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yD+self.lenTol, zMax=self.thickness+self.lenTol)
            createPartitionDatumPlane(self.part[0], cellLowerBox, 'YZPLANE', (-1)**i*self.xD)
        createPartitionDatumPlane(self.part[1], self.part[1].cells, 'YZPLANE', self.xO)
        createPartitionDatumPlane(self.part[1], self.part[1].cells, 'XYPLANE', self.pinLenFactor/2.0*self.thickness)
        createPartitionDatumPlane(self.part[1], self.part[1].cells, 'XYPLANE', (1+self.pinLenFactor/2.0)*self.thickness)
    def createLocalSeed(self):
        ## seed ==>> edges thickness
        numThicknessElem = math.ceil(self.thickness/self.seedSize['Thickness'])
        if (numThicknessElem%2)!=0:
            numThicknessElem = numThicknessElem+1
        edgesThickness = self.part[0].edges.findAt(coordinates=((self.xE, self.yE, self.lenTol), ))
        self.part[0].seedEdgeByNumber(edges=edgesThickness, number=int(numThicknessElem), constraint=FINER)
        ## seed ==>> edges long 1
        edgesLong1 = self.part[0].edges.findAt(coordinates=((self.xE, self.yE-self.lenTol, 0), (self.xE, self.yE-self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, self.yE, edgesLong1, minSize=self.seedSize['Long_1'], maxSize=self.seedSize['Long_2'])
        elemNum = self.part[0].getEdgeSeeds(edgesLong1[0], attribute=NUMBER)
        edgesLong1_2 = self.part[0].edges.findAt(coordinates=((self.xD, self.yD-self.lenTol, 0), (-self.xD, self.yD-self.lenTol, 0), (self.xD, self.yD-self.lenTol, self.thickness), (-self.xD, self.yD-self.lenTol, self.thickness)))
        self.part[0].seedEdgeByNumber(edges=edgesLong1_2, number=elemNum, constraint=FIXED)
        ## seed ==>> edges long 2
        edgesLong2Temp1 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yE-self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp2 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yE-self.xC1-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yE-self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp3 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yG+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp4 = self.getByDifference(edgesLong2Temp1, edgesLong2Temp2)
        edgesLong2 = self.getByDifference(edgesLong2Temp4, edgesLong2Temp3)
        self.seedEdge(self.part[0], 1, (self.yE-self.xC1), edgesLong2, minSize=self.seedSize['Long_2'], maxSize=self.seedSize['Long_3'])
        ## seed ==>> notch edge
        edgesNotch = self.part[0].edges.findAt(coordinates=(((self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), 0), 
                                                            (-(self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), 0), 
                                                            ((self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), self.thickness), 
                                                            (-(self.xE+self.lenTol*math.sin(self.notchTipAngleRad/2.0)), self.yE+self.lenTol*math.cos(self.notchTipAngleRad/2.0), self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesNotch, size=self.seedSize['Notch'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin circumference portion
        self.part[1].seedEdgeBySize(edges=self.getArcEdge(self.part[1].edges), size=self.seedSize['Pin_Dia'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin length portion
        edgesPin1 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, -self.lenTol), (self.xO, self.yO, self.lenTol), (self.phi/2.0+self.lenTol))
        edgesPin2 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol-self.lenTol), (self.xO, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol), (self.phi/2.0+self.lenTol))
        edgesPin3 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, (1+self.pinLenFactor/2.0)*self.thickness-self.lenTol), (self.xO, self.yO, (1+self.pinLenFactor/2.0)*self.thickness+self.lenTol), (self.phi/2.0+self.lenTol))
        edgesPin4 = self.part[1].edges.getByBoundingCylinder((self.xO, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol), (self.xO, self.yO, (1+self.pinLenFactor)*self.thickness+self.lenTol), (self.phi/2.0+self.lenTol))
        edgesPinTemp1 = self.getByCylinderDifference(self.part[1].edges, (self.xO, self.yO, -self.lenTol), (self.xO, self.yO, (1+self.pinLenFactor)*self.thickness+self.lenTol), (self.phi/2.0+self.lenTol), (self.phi/2.0-self.lenTol))
        edgesPinTemp2 = self.getByDifference(edgesPinTemp1, edgesPin1)
        edgesPinTemp3 = self.getByDifference(edgesPinTemp2, edgesPin2)
        edgesPinTemp4 = self.getByDifference(edgesPinTemp3, edgesPin3)
        edgesPin = self.getByDifference(edgesPinTemp4, edgesPin4)
        self.part[1].seedEdgeBySize(edges=edgesPin, size=self.seedSize['Pin_Length'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin diameter portion
        numDiaElem = math.ceil(self.phi/self.seedSize['Pin_Dia'])
        if (numDiaElem%2)!=0:
            numDiaElem = numDiaElem+1
        diaEdges = self.part[1].edges.findAt(coordinates=((self.xO, self.yO, 0), (self.xO, self.yO, self.pinLenFactor/2.0*self.thickness), (self.xO, self.yO, (1+self.pinLenFactor/2.0)*self.thickness), (self.xO, self.yO, (1+self.pinLenFactor)*self.thickness)))
        self.part[1].seedEdgeByNumber(edges=diaEdges, number=int(numDiaElem), constraint=FIXED)
    def createEquation(self):
        ## create equation
        i=1
        nodesEqnPosY = self.part[i].nodes.getByBoundingSphere((self.xO, self.phi/2.0, 0), self.lenTol)
        nsetNameEqnPosY = 'Nset_Eqn_Part_'+str(i+1)+'_PosY'
        self.part[i].Set(nodes=nodesEqnPosY, name=nsetNameEqnPosY)
        nodesEqnNegY = self.part[i].nodes.getByBoundingSphere((self.xO, -self.phi/2.0, 0), self.lenTol)
        nsetNameEqnNegY = 'Nset_Eqn_Part_'+str(i+1)+'_NegY'
        self.part[i].Set(nodes=nodesEqnNegY, name=nsetNameEqnNegY)
        self.model.Equation(name=self.couponName+'_Equation_1', terms=((1.0, self.instance[1].name+'.'+nsetNameEqnPosY, 1), (-1.0, self.instance[1].name+'.'+nsetNameEqnNegY, 1)))
        self.model.Equation(name=self.couponName+'_Equation_2', terms=((1.0, self.instance[2].name+'.'+nsetNameEqnPosY, 1), (-1.0, self.instance[2].name+'.'+nsetNameEqnNegY, 1)))
    def createContact(self):
        ## create contact
        self.isContactEnforced = True
        for i in range(len(self.part)):
            if i==0:
                ## contact surface ==> plate cyl1
                faceCellPlateCyl1 = self.part[0].faces.getByBoundingCylinder((self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.thickness+self.lenTol), (self.phi/2.0+self.lenTol))
                nameSurfPlateCyl1 = 'Surf_Contact_Part_'+str(i+1)+'_Cyl_1'
                self.getElemSurfFromCellFace(self.part[i], faceCellPlateCyl1, nameSurfPlateCyl1)
                regionPlateCyl1 = self.instance[0].surfaces[nameSurfPlateCyl1]
                ## plate contact surface ==> cyl2
                faceCellPlateCyl2 = self.part[0].faces.getByBoundingCylinder((-self.xC1, self.yC1, -self.lenTol), (-self.xC1, self.yC1, self.thickness+self.lenTol), (self.phi/2.0+self.lenTol))
                nameSurfPlateCyl2 = 'Surf_Contact_Part_'+str(i+1)+'_Cyl_2'
                self.getElemSurfFromCellFace(self.part[i], faceCellPlateCyl2, nameSurfPlateCyl2)
                regionPlateCyl2 = self.instance[0].surfaces[nameSurfPlateCyl2]
            if i==1:
                # contact surface ==> pin
                faceCellPin = self.part[i].faces.findAt(coordinates=((self.xO-self.phi/2.0, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol), (self.xO+self.phi/2.0, self.yO, self.pinLenFactor/2.0*self.thickness+self.lenTol)))
                nameSurfPin = 'Surf_Contact_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPin, nameSurfPin)
                regionPin1 = self.instance[1].surfaces[nameSurfPin]
                regionPin2 = self.instance[2].surfaces[nameSurfPin]
        self.contactProperty = self.model.ContactProperty(self.couponName+'_Contact_Property')
        self.contactProperty.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact_1', createStepName='Initial', master=regionPin1, slave=regionPlateCyl1, sliding=SMALL, thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=0.0, datumAxis=None, clearanceRegion=None)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact_2', createStepName='Initial', master=regionPin2, slave=regionPlateCyl2, sliding=SMALL, thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=0.0, datumAxis=None, clearanceRegion=None)
    def createLoadBC(self):
        ## create load and boundary conditions
        for i in range(len(self.part)):
            if i==0:
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
                regionPin2BC_Z = self.instance[2].sets[nsetNamePinBC_Z]
                self.model.DisplacementBC(name='BC_Z_Instance_'+str(3), createStepName='Load', region=regionPin2BC_Z, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                faceCellPinLoadNegX = self.part[i].faces.findAt(coordinates=((self.xO-self.phi/2.0, self.yO, self.lenTol), (self.xO-self.phi/2.0, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol)))
                nameSurfPinLoadNegX = 'Surf_NegX_Load_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPinLoadNegX, nameSurfPinLoadNegX)
                regionPin1BC = self.instance[1].surfaces[nameSurfPinLoadNegX]
                faceCellPinLoadPosX = self.part[i].faces.findAt(coordinates=((self.xO+self.phi/2.0, self.yO, self.lenTol), (self.xO+self.phi/2.0, self.yO, (1+self.pinLenFactor)*self.thickness-self.lenTol)))
                nameSurfPinLoadPosX = 'Surf_PosX_Load_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPinLoadPosX, nameSurfPinLoadPosX)
                regionPin2BC = self.instance[2].surfaces[nameSurfPinLoadPosX]
                self.model.Pressure(name='Load_NegX_Pressure_Instance_'+str(2), createStepName='Load', region=regionPin1BC, distributionType=UNIFORM, field='', magnitude=-self.stepLoad, amplitude=UNSET)
                self.model.Pressure(name='Load_PosX_Pressure_Instance_'+str(3), createStepName='Load', region=regionPin2BC, distributionType=UNIFORM, field='', magnitude=-self.stepLoad, amplitude=UNSET)

