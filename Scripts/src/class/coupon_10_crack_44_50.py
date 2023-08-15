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


import re
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
        self.createStep()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        if self.nHoleRow1!=0 or self.nHoleRow2!=0:
            (self.xa, self.ya) = (self.xA, self.yA) = (self.width/2.0, (0.5*self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2))
            (self.xb, self.yb) = (self.xB, self.yB) = (-self.width/2.0, (0.5*self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2))
            (self.xc, self.yc) = (self.xC, self.yC) = (-self.width/2.0, -(0.5*self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2))
            (self.xd, self.yd) = (self.xD, self.yD) = (self.width/2.0, -(0.5*self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2))
        else:
            (self.xa, self.ya) = (self.xA, self.yA) = (self.width/2.0, self.length/2.0)
            (self.xb, self.yb) = (self.xB, self.yB) = (-self.width/2.0, self.length/2.0)
            (self.xc, self.yc) = (self.xC, self.yC) = (-self.width/2.0, -self.length/2.0)
            (self.xd, self.yd) = (self.xD, self.yD) = (self.width/2.0, -self.length/2.0)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.notchLength/2.0, self.notchWidth/2.0)
        (self.xf, self.yf) = (self.xF, self.yF) = (-self.notchLength/2.0, self.notchWidth/2.0)
        (self.xg, self.yg) = (self.xG, self.yG) = (-self.notchLength/2.0, -self.notchWidth/2.0)
        (self.xh, self.yh) = (self.xH, self.yH) = (self.notchLength/2.0, -self.notchWidth/2.0)
        #######################################################################################################################################################
        self.profileSketch = 3*[None]
        ## define sketch ==> plate
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
        self.part = [None]
        self.tempPart = len(self.profileSketch)*[None]
        for i in range(len(self.tempPart)):
            self.tempPart[i] = self.model.Part(name=self.couponName+'_TempPart_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.tempPart[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
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
        createPartitionDatumPlane(self.part[0], 'YZPLANE', 0)
        self.crackedPart = self.part[0].cells.getByBoundingBox(xMin=-(0.5*self.notchLength+self.lenTol), yMin=-(0.5*self.notchLength+self.lenTol), zMin=-self.lenTol, xMax=(0.5*self.notchLength+self.lenTol), yMax=(0.5*self.notchLength+self.lenTol), zMax=self.thickness+self.lenTol)
        self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, 0.5*self.notchLength, 0)), point2=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, -0.5*self.notchLength, 0)), point3=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, 0.5*self.notchLength, self.thickness)), cells=self.crackedPart)
        self.crackedPart = self.part[0].cells.getByBoundingBox(xMin=-(0.5*self.notchLength+self.lenTol), yMin=-(0.5*self.notchLength+self.lenTol), zMin=-self.lenTol, xMax=(0.5*self.notchLength+self.lenTol), yMax=(0.5*self.notchLength+self.lenTol), zMax=self.thickness+self.lenTol)
        self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, 0.5*self.notchLength, 0)), point2=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, -0.5*self.notchLength, 0)), point3=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, 0.5*self.notchLength, self.thickness)), cells=self.crackedPart)
    def createLocalSeed(self):
        ## seed ==>> thickness
        edgesThickness = self.part[0].edges.findAt(coordinates=((0, self.phi1/2, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSize['Thickness'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> central hole
        edgesHoleArc1 = self.part[0].edges.getByBoundingCylinder((self.xO, self.yO, -self.lenTol), (self.xO, self.yO, self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesHoleArc1, size=self.seedSize['Arc'], deviationFactor=0.1, constraint=FINER)
        edgesHoleArc2 = self.part[0].edges.getByBoundingCylinder((self.xO, self.yO, self.thickness-self.lenTol), (self.xO, self.yO, self.thickness+self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesHoleArc2, size=self.seedSize['Arc'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> edges long1, long2
        edgesLong1 = self.part[0].edges.findAt(coordinates=(((0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, 0), ((0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, 0), ((0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, 0), ((0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, 0), ((0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), self.yA, 0), ((0.5*self.notchLength+self.lenTol), self.yA, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -self.yA, 0), ((0.5*self.notchLength+self.lenTol), -self.yA, self.thickness), ))
        self.seedEdge(self.part[0], 0, 0.5*self.notchLength, edgesLong1, minSize=self.seedSize['Long_1'], maxSize=self.seedSize['Long_2'])
        edgesLong2 = self.part[0].edges.findAt(coordinates=((-(0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, 0), (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, 0), (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, 0), (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, 0), (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), self.yA, 0), (-(0.5*self.notchLength+self.lenTol), self.yA, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -self.yA, 0), (-(0.5*self.notchLength+self.lenTol), -self.yA, self.thickness), ))
        self.seedEdge(self.part[0], 0, -0.5*self.notchLength, edgesLong2, minSize=self.seedSize['Long_1'], maxSize=self.seedSize['Long_2'])
        ## seed ==>> edge notch square
        edgesNotch = self.part[0].edges.findAt(coordinates=((0, (0.5*self.notchLength-self.lenTol), 0), (0, (0.5*self.notchLength-self.lenTol), self.thickness), 
                                                            (0, -(0.5*self.notchLength-self.lenTol), 0), (0, -(0.5*self.notchLength-self.lenTol), self.thickness), 
                                                            ((0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, 0), ((0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, 0), (-(0.5*self.notchLength-self.lenTol), 0.5*self.notchWidth, self.thickness), 
                                                            ((0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, 0), ((0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, self.thickness), 
                                                            (-(0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, 0), (-(0.5*self.notchLength-self.lenTol), -0.5*self.notchWidth, self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesNotch, size=self.seedSize['Notch'], deviationFactor=0.1, constraint=FINER)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=SymbolicConstant(self.couponData['Step']['NLGEOM']), initialInc=self.couponData['Step']['Initial_Increment'], timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=self.outputFieldVariables)
        for i in range(len(self.part)):
            if i==0:
                ## BC ==> plate NegY
                nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xC-self.lenTol, xMax=self.xD+self.lenTol, yMin=self.yC-self.lenTol, yMax=self.yD+self.lenTol, zMin=-self.lenTol, zMax=self.thickness+self.lenTol)
                nameNsetPlateBC = 'Nset_NegY_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegY, name=nameNsetPlateBC)
                regionPlateBC = self.instance[i].sets[nameNsetPlateBC]
                self.model.DisplacementBC(name='BC_NegY_Instance_'+str(1), createStepName='Load', region=regionPlateBC, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=SET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## load ==> plate PosY
                faceCellPinLoadPosY = self.part[i].faces.getByBoundingBox(xMin=self.xB-self.lenTol, xMax=self.xA+self.lenTol, yMin=self.yB-self.lenTol, yMax=self.yA+self.lenTol, zMin=-self.lenTol, zMax=self.thickness+self.lenTol)
                nameSurfPinLoadPosY = 'Surf_PosY_Load_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPinLoadPosY, nameSurfPinLoadPosY)
                regionPlateLoad = self.instance[i].surfaces[nameSurfPinLoadPosY]
                self.model.Pressure(name='Load_PosY_Pressure_Instance_'+str(2), createStepName='Load', region=regionPlateLoad, distributionType=UNIFORM, field='', magnitude=-self.couponData['Step']['Load'], amplitude=UNSET)

