#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
########################    CLASS DEFINITION : CRACK GROWTH COUPON : SPECIMEN 44 TO 50  #########################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 31-Jul-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import math
from abaqus import *
from abaqusConstants import *
from caeModules import *

class coupon_10_crack_44_50(coupon_generic):
    def __init__(self, couponData):
        super(coupon_10_crack_44_50, self).__init__(couponData)
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.length = self.geometry['Length']
        self.width = self.geometry['Width']
        self.phi1 = self.geometry['Diameter_1']
        self.notchLength = self.geometry['Notch_Length']
        self.notchWidth = self.geometry['Notch_Width']
        self.nHoleRow1 = self.geometry['Num_Hole_Row_1']
        self.nHoleRow2 = self.geometry['Num_Hole_Row_2']
        self.phi2 = self.geometry['Diameter_2']
        self.centerOffsetRow1 = self.geometry['Center_Offset_Row_1']
        self.centerOffsetRow2 = self.geometry['Center_Offset_Row_2']
        self.centerOffsetColumn = self.geometry['Center_Offset_Column']
        self.thickness = self.geometry['Thickness']
        ## derived quantities
        self.nHoleRow1 = int(self.nHoleRow1)
        self.nHoleRow2 = int(self.nHoleRow2)
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
        self.createTie()
        self.createStep()
        self.createLoadBC()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        if self.nHoleRow1!=0 or self.nHoleRow2!=0:
            self.plateCutOut = self.centerOffsetRow1+1.5*self.centerOffsetRow2
        else:
            self.plateCutOut = 0
        self.tieSectionFraction = 0.25
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (0.5*self.width, self.tieSectionFraction*(0.5*self.length-self.plateCutOut))
        (self.xb, self.yb) = (self.xB, self.yB) = (-0.5*self.width, self.tieSectionFraction*(0.5*self.length-self.plateCutOut))
        (self.xc, self.yc) = (self.xC, self.yC) = (-0.5*self.width, -self.tieSectionFraction*(0.5*self.length-self.plateCutOut))
        (self.xd, self.yd) = (self.xD, self.yD) = (0.5*self.width, -self.tieSectionFraction*(0.5*self.length-self.plateCutOut))
        (self.xaa, self.yaa) = (self.xAA, self.yAA) = (0.5*self.width, (0.5*self.length-self.plateCutOut))
        (self.xbb, self.ybb) = (self.xBB, self.yBB) = (-0.5*self.width, (0.5*self.length-self.plateCutOut))
        (self.xcc, self.ycc) = (self.xCC, self.yCC) = (-0.5*self.width, -(0.5*self.length-self.plateCutOut))
        (self.xdd, self.ydd) = (self.xDD, self.yDD) = (0.5*self.width, -(0.5*self.length-self.plateCutOut))
        (self.xe, self.ye) = (self.xE, self.yE) = (0.5*self.notchLength, 0.5*self.notchWidth)
        (self.xf, self.yf) = (self.xF, self.yF) = (-0.5*self.notchLength, 0.5*self.notchWidth)
        (self.xg, self.yg) = (self.xG, self.yG) = (-0.5*self.notchLength, -0.5*self.notchWidth)
        (self.xh, self.yh) = (self.xH, self.yH) = (0.5*self.notchLength, -0.5*self.notchWidth)
        #######################################################################################################################################################
        self.profileSketch = 5*[None]
        ## define sketch ==> plate ############################################################################################################################
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_1', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)
        self.profileSketch[0].rectangle(point1=(self.xA, self.yA), point2=(self.xC, self.yC))
        self.profileSketch[0].unsetPrimaryObject()
        ## define sketch ==> crack hole #######################################################################################################################
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileGeometry2, self.profileVertices2 = self.profileSketch[1].geometry, self.profileSketch[1].vertices
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)
        self.profileSketch[1].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.phi1/2.0, self.yO))
        self.profileSketch[1].unsetPrimaryObject()
        ## define sketch ==> crack edge #######################################################################################################################
        self.profileSketch[2] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_3', sheetSize=200.0)
        self.profileGeometry3, self.profileVertices3 = self.profileSketch[2].geometry, self.profileSketch[2].vertices
        self.profileSketch[2].setPrimaryObject(option=STANDALONE)
        self.profileSketch[2].rectangle(point1=(self.xE, self.yE), point2=(self.xG, self.yG))
        self.profileSketch[2].unsetPrimaryObject()
        ## define sketch ==> tie region 1 #####################################################################################################################
        self.profileSketch[3] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_4', sheetSize=200.0)
        self.profileGeometry4, self.profileVertices4 = self.profileSketch[3].geometry, self.profileSketch[3].vertices
        self.profileSketch[3].setPrimaryObject(option=STANDALONE)
        self.profileSketch[3].rectangle(point1=(self.xA, self.yA), point2=(self.xBB, self.yBB))
        self.profileSketch[3].unsetPrimaryObject()
        ## define sketch ==> tie region 2 #####################################################################################################################
        self.profileSketch[4] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_5', sheetSize=200.0)
        self.profileGeometry5, self.profileVertices5 = self.profileSketch[4].geometry, self.profileSketch[4].vertices
        self.profileSketch[4].setPrimaryObject(option=STANDALONE)
        self.profileSketch[4].rectangle(point1=(self.xD, self.yD), point2=(self.xCC, self.yCC))
        self.profileSketch[4].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xA, self.yA) = self.profileVertices1[0].coords
        (self.xB, self.yB) = self.profileVertices1[3].coords
        (self.xC, self.yC) = self.profileVertices1[2].coords
        (self.xD, self.yD) = self.profileVertices1[1].coords
        (self.xE, self.yE) = self.profileVertices3[0].coords
        (self.xF, self.yF) = self.profileVertices3[3].coords
        (self.xG, self.yG) = self.profileVertices3[2].coords
        (self.xH, self.yH) = self.profileVertices3[1].coords
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
                         ['notchLength', '', self.notchLength, '', (self.xE-self.xF)],
                         ['notchWidth', '', self.notchWidth, '', (self.yE-self.yH)],
                         ['width', '', self.width, '', (self.xA-self.xB)]]
        if self.nHoleRow1!=0 or self.nHoleRow2!=0:
            self.geomData.append(['length', '', self.length, '', (self.yA-self.yD)+2*(self.centerOffsetRow1+1.5*self.centerOffsetRow2)])
        else:
            self.geomData.append(['length', '', self.length, '', (self.yA-self.yD)])
    def createPart(self):
        ## create solid
        self.part = 3*[None]
        self.tempPart = (len(self.profileSketch)-2)*[None]
        for i in range(len(self.tempPart)):
            self.tempPart[i] = self.model.Part(name=self.couponName+'_TempPart_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.tempPart[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
        for i in [1,2]:
            self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i+2], depth=self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.tempPart[0])        
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        newPartName = self.couponName+'_Part_1'
        ## create temporary assembly instances
        self.cuttingInstances = ()
        self.tempInstance = len(self.tempPart)*[None]
        for i in range(len(self.tempInstance)):
            self.tempInstance[i] = self.assembly.Instance(name=self.couponName+'_TempInstance_'+str(i+1), part=self.tempPart[i], dependent=ON)
            if i!=0:
                self.cuttingInstances = self.cuttingInstances+(self.tempInstance[i],)
        self.assembly.InstanceFromBooleanCut(name=newPartName, instanceToBeCut=self.tempInstance[0], cuttingInstances=self.cuttingInstances, originalInstances=DELETE)
        self.part[0] = self.model.parts[newPartName]
        del self.assembly.features[self.couponName+'_Part_1-1']
        self.instance = len(self.part)*[None]
        for i in range(len(self.instance)):
            self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
    def createPartition(self):
        def createPartitionDatumPlane(thisPart, thisPlane, offsetDistance):
            self.datumPlane_ID = thisPart.DatumPlaneByPrincipalPlane(principalPlane=SymbolicConstant(thisPlane), offset=offsetDistance).id
            thisPart.PartitionCellByDatumPlane(datumPlane=thisPart.datums[self.datumPlane_ID], cells=thisPart.cells)
        for i in range(2):
            createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*0.5*self.notchWidth)
            createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*0.5*self.notchLength)
            createPartitionDatumPlane(self.part[0], 'YZPLANE', (-1)**i*0.5*self.notchLength)
        createPartitionDatumPlane(self.part[0], 'XZPLANE', 0)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', 0)
        self.crackedPart = self.part[0].cells.getByBoundingBox(xMin=-(0.5*self.notchLength+self.lenTol), yMin=-(0.5*self.notchLength+self.lenTol), zMin=-self.lenTol, xMax=(0.5*self.notchLength+self.lenTol), yMax=(0.5*self.notchLength+self.lenTol), zMax=self.thickness+self.lenTol)
        self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, 0.5*self.notchLength, 0)), point2=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, -0.5*self.notchLength, 0)), point3=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, 0.5*self.notchLength, self.thickness)), cells=self.crackedPart)
        self.crackedPart = self.part[0].cells.getByBoundingBox(xMin=-(0.5*self.notchLength+self.lenTol), yMin=-(0.5*self.notchLength+self.lenTol), zMin=-self.lenTol, xMax=(0.5*self.notchLength+self.lenTol), yMax=(0.5*self.notchLength+self.lenTol), zMax=self.thickness+self.lenTol)
        self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, 0.5*self.notchLength, 0)), point2=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, -0.5*self.notchLength, 0)), point3=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, 0.5*self.notchLength, self.thickness)), cells=self.crackedPart)
    def createLocalSeed(self):
        ## seed ==>> thickness
        edgesThickness = self.part[0].edges.findAt(coordinates=((0, self.phi1/2, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSize['Thickness_1'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> central hole
        edgesHoleArc1 = self.part[0].edges.getByBoundingCylinder((self.xO, self.yO, -self.lenTol), (self.xO, self.yO, self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesHoleArc1, size=self.seedSize['Arc'], deviationFactor=0.1, constraint=FINER)
        edgesHoleArc2 = self.part[0].edges.getByBoundingCylinder((self.xO, self.yO, self.thickness-self.lenTol), (self.xO, self.yO, self.thickness+self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesHoleArc2, size=self.seedSize['Arc'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> edges long1, long2
        edgesLong1 = self.part[0].edges.findAt(coordinates=((0.5*self.notchLength, (0.5*self.notchWidth+self.lenTol), 0), (0.5*self.notchLength, (0.5*self.notchWidth+self.lenTol), self.thickness), 
                                                            (0.5*self.width, (0.5*self.notchWidth+self.lenTol), 0), (0.5*self.width, (0.5*self.notchWidth+self.lenTol), self.thickness), 
                                                            (-0.5*self.notchLength, (0.5*self.notchWidth+self.lenTol), 0), (-0.5*self.notchLength, (0.5*self.notchWidth+self.lenTol), self.thickness), 
                                                            (-0.5*self.width, (0.5*self.notchWidth+self.lenTol), 0), (-0.5*self.width, (0.5*self.notchWidth+self.lenTol), self.thickness), ))
        self.seedEdge(self.part[0], 1, 0.5*self.notchWidth, edgesLong1, minSize=self.seedSize['Long_1'], maxSize=self.seedSize['Long_2'])
        edgesLong2 = self.part[0].edges.findAt(coordinates=((0.5*self.notchLength, -(0.5*self.notchWidth+self.lenTol), 0), (0.5*self.notchLength, -(0.5*self.notchWidth+self.lenTol), self.thickness), 
                                                            (0.5*self.width, -(0.5*self.notchWidth+self.lenTol), 0), (0.5*self.width, -(0.5*self.notchWidth+self.lenTol), self.thickness), 
                                                            (-0.5*self.notchLength, -(0.5*self.notchWidth+self.lenTol), 0), (-0.5*self.notchLength, -(0.5*self.notchWidth+self.lenTol), self.thickness), 
                                                            (-0.5*self.width, -(0.5*self.notchWidth+self.lenTol), 0), (-0.5*self.width, -(0.5*self.notchWidth+self.lenTol), self.thickness), ))
        self.seedEdge(self.part[0], 1, -0.5*self.notchWidth, edgesLong2, minSize=self.seedSize['Long_1'], maxSize=self.seedSize['Long_2'])
        ## seed ==>> edges long3, long4
        edgesLong3 = self.part[0].edges.findAt(coordinates=((0.5*self.notchLength, (0.5*self.notchLength+self.lenTol), 0), (0.5*self.notchLength, (0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (0.5*self.width, (0.5*self.notchLength+self.lenTol), 0), (0.5*self.width, (0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (-0.5*self.notchLength, (0.5*self.notchLength+self.lenTol), 0), (-0.5*self.notchLength, (0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (-0.5*self.width, (0.5*self.notchLength+self.lenTol), 0), (-0.5*self.width, (0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (0, (0.5*self.notchLength+self.lenTol), 0), (0, (0.5*self.notchLength+self.lenTol), self.thickness), ))
        self.seedEdge(self.part[0], 1, 0.5*self.notchLength, edgesLong3, minSize=self.seedSize['Long_2'], maxSize=self.seedSize['Long_3'])
        edgesLong4 = self.part[0].edges.findAt(coordinates=((0.5*self.notchLength, -(0.5*self.notchLength+self.lenTol), 0), (0.5*self.notchLength, -(0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (0.5*self.width, -(0.5*self.notchLength+self.lenTol), 0), (0.5*self.width, -(0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (-0.5*self.notchLength, -(0.5*self.notchLength+self.lenTol), 0), (-0.5*self.notchLength, -(0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (-0.5*self.width, -(0.5*self.notchLength+self.lenTol), 0), (-0.5*self.width, -(0.5*self.notchLength+self.lenTol), self.thickness), 
                                                            (0, -(0.5*self.notchLength+self.lenTol), 0), (0, -(0.5*self.notchLength+self.lenTol), self.thickness), ))
        self.seedEdge(self.part[0], 1, -0.5*self.notchLength, edgesLong4, minSize=self.seedSize['Long_2'], maxSize=self.seedSize['Long_3'])
        ## seed ==>> edges long5
        edgesLong5 = self.part[0].edges.findAt(coordinates=((0.5*self.notchLength, (self.lenTol), 0), (0.5*self.notchLength, (self.lenTol), self.thickness), 
                                                            (0.5*self.width, (self.lenTol), 0), (0.5*self.width, (self.lenTol), self.thickness), 
                                                            (-0.5*self.notchLength, (self.lenTol), 0), (-0.5*self.notchLength, (self.lenTol), self.thickness), 
                                                            (-0.5*self.width, (self.lenTol), 0), (-0.5*self.width, (self.lenTol), self.thickness), 
                                                            (0.5*self.notchLength, -(self.lenTol), 0), (0.5*self.notchLength, -(self.lenTol), self.thickness), 
                                                            (0.5*self.width, -(self.lenTol), 0), (0.5*self.width, -(self.lenTol), self.thickness), 
                                                            (-0.5*self.notchLength, -(self.lenTol), 0), (-0.5*self.notchLength, -(self.lenTol), self.thickness), 
                                                            (-0.5*self.width, -(self.lenTol), 0), (-0.5*self.width, -(self.lenTol), self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesLong5, size=self.seedSize['Long_1'], deviationFactor=0.1, constraint=FINER)        
        ## seed ==>> edges width1, width2
        edgesWidth1 = self.part[0].edges.findAt(coordinates=(((0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, 0), ((0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, 0), ((0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, 0), ((0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, 0), ((0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), self.yA, 0), ((0.5*self.notchLength+self.lenTol), self.yA, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -self.yA, 0), ((0.5*self.notchLength+self.lenTol), -self.yA, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), 0, 0), ((0.5*self.notchLength+self.lenTol), 0, self.thickness), ))
        self.seedEdge(self.part[0], 0, 0.5*self.notchLength, edgesWidth1, minSize=self.seedSize['Width_1'], maxSize=self.seedSize['Width_2'])
        edgesWidth2 = self.part[0].edges.findAt(coordinates=((-(0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, 0), (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, 0), (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, 0), (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, 0), (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), self.yA, 0), (-(0.5*self.notchLength+self.lenTol), self.yA, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -self.yA, 0), (-(0.5*self.notchLength+self.lenTol), -self.yA, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), 0, 0), (-(0.5*self.notchLength+self.lenTol), 0, self.thickness), ))
        self.seedEdge(self.part[0], 0, -0.5*self.notchLength, edgesWidth2, minSize=self.seedSize['Width_1'], maxSize=self.seedSize['Width_2'])
        ## seed ==>> edge notch square
        edgesNotch = self.part[0].edges.findAt(coordinates=((0, (0.5*self.notchLength-self.lenTol), 0), (0, (0.5*self.notchLength-self.lenTol), self.thickness), 
                                                            (0, -(0.5*self.notchLength-self.lenTol), 0), (0, -(0.5*self.notchLength-self.lenTol), self.thickness), 
                                                            ((0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, 0), ((0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, 0), (-(0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            ((0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, 0), ((0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, 0), (-(0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesNotch, size=self.seedSize['Notch'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> edge thickness of tied part
        numThicknessElem = math.ceil(self.thickness/self.seedSize['Thickness_2'])
        if (numThicknessElem%2)!=0:
            numThicknessElem = numThicknessElem+1
        edgesThicknessPart2 = self.part[1].edges.findAt(coordinates=((self.xAA, self.yAA, self.lenTol), ))
        self.part[1].seedEdgeByNumber(edges= edgesThicknessPart2, number=int(numThicknessElem), constraint=FINER)
        edgesThicknessPart3 = self.part[2].edges.findAt(coordinates=((self.xCC, self.yCC, self.lenTol), ))
        self.part[2].seedEdgeByNumber(edges= edgesThicknessPart3, number=int(numThicknessElem), constraint=FINER)
        ## seed ==>> edge width of tied part
        numWidthElem = math.ceil(self.width/self.seedSize['Width_3'])
        if (numWidthElem%2)!=0:
            numWidthElem = numWidthElem+1
        edgesWidthPart2 = self.part[1].edges.findAt(coordinates=((0, self.yAA, 0), ))
        self.part[1].seedEdgeByNumber(edges= edgesWidthPart2, number=int(numWidthElem), constraint=FINER)
        edgesWidthPart3 = self.part[2].edges.findAt(coordinates=((0, self.yCC, 0), ))
        self.part[2].seedEdgeByNumber(edges= edgesWidthPart3, number=int(numWidthElem), constraint=FINER)
    def createTie(self):
        ## create tie
        region = (len(self.part)-1)*[None]
        for i in [0,1]:
            surf = self.part[i].faces.getByBoundingBox(xMin=self.xB-self.lenTol, xMax=self.xA+self.lenTol, yMin=self.yB-self.lenTol,  yMax=self.yA+self.lenTol, zMin=-self.lenTol, zMax=self.thickness+self.lenTol)
            surfName = 'Surf_Tie_1_Part_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[i], surf, surfName)
            region[i] = self.instance[i].surfaces[surfName]
        self.model.Tie(name=self.couponName+'_Tie_1', master=region[1], slave=region[0], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement=SURFACE_TO_SURFACE)
        for i in [0,2]:
            surf = self.part[i].faces.getByBoundingBox(xMin=self.xC-self.lenTol, xMax=self.xD+self.lenTol, yMin=self.yC-self.lenTol, yMax=self.yD+self.lenTol, zMin=-self.lenTol, zMax=self.thickness+self.lenTol)
            surfName = 'Surf_Tie_2_Part_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[i], surf, surfName)
            if i==0:
                region[i] = self.instance[i].surfaces[surfName]
            elif i==2:
                region[i-1] = self.instance[i].surfaces[surfName]
        self.model.Tie(name=self.couponName+'_Tie_2', master=region[1], slave=region[0], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement=SURFACE_TO_SURFACE)
    def createLoadBC(self):
        ## create load and boundary conditions
        for i in range(len(self.part)):
            if i==1:
                ## load ==> plate PosY
                faceCellPinLoadPosY = self.part[i].faces.getByBoundingBox(xMin=self.xBB-self.lenTol, xMax=self.xAA+self.lenTol, yMin=self.yBB-self.lenTol, yMax=self.yAA+self.lenTol, zMin=-self.lenTol, zMax=self.thickness+self.lenTol)
                nameSurfPinLoadPosY = 'Surf_PosY_Load_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPinLoadPosY, nameSurfPinLoadPosY)
                regionPlateLoad = self.instance[i].surfaces[nameSurfPinLoadPosY]
                self.model.Pressure(name='Load_PosY_Pressure_Instance_'+str(i+1), createStepName='Load', region=regionPlateLoad, distributionType=UNIFORM, field='', magnitude=-self.stepLoad, amplitude=UNSET)
            if i==2:
                ## BC ==> plate NegY
                nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xCC-self.lenTol, xMax=self.xDD+self.lenTol, yMin=self.yCC-self.lenTol, yMax=self.yDD+self.lenTol, zMin=-self.lenTol, zMax=self.thickness+self.lenTol)
                nameNsetPlateBC = 'Nset_NegY_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegY, name=nameNsetPlateBC)
                regionPlateBC = self.instance[i].sets[nameNsetPlateBC]
                self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=regionPlateBC, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=SET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## BC ==> sphere
                nodePlateBC_X_1 = self.part[i].nodes.getByBoundingSphere((0, self.yDD, 0), self.lenTol)
                nodePlateBC_X_2 = self.part[i].nodes.getByBoundingSphere((0, self.yDD, self.thickness), self.lenTol)
                nodePlateBC_X = [nodePlateBC_X_1, nodePlateBC_X_2]
                nsetNamePlateBC_X = 'Nset_BC_X_Part_'+str(i+1)
                self.part[i].Set(nodes=nodePlateBC_X , name=nsetNamePlateBC_X)
                regionPlateBC_X = self.instance[i].sets[nsetNamePlateBC_X]
                self.model.DisplacementBC(name='BC_X_Instance_'+str(i+1), createStepName='Load', region=regionPlateBC_X, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## BC ==> sphere
                nodePlateBC_Z_1 = self.part[i].nodes.getByBoundingSphere((self.xDD, self.yDD, 0.5*self.thickness), self.lenTol)
                nodePlateBC_Z_2 = self.part[i].nodes.getByBoundingSphere((self.xCC, self.yCC, 0.5*self.thickness), self.lenTol)
                nodePlateBC_Z = [nodePlateBC_Z_1, nodePlateBC_Z_2]
                nsetNamePlateBC_Z = 'Nset_BC_Z_Part_'+str(i+1)
                self.part[i].Set(nodes=nodePlateBC_Z , name=nsetNamePlateBC_Z)
                regionPlateBC_Z = self.instance[i].sets[nsetNamePlateBC_Z]
                self.model.DisplacementBC(name='BC_Z_Instance_'+str(i+1), createStepName='Load', region=regionPlateBC_Z, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

