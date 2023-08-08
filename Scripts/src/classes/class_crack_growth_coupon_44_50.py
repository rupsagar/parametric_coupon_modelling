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

class crack_growth_coupon_44_50(coupon_generic):
    def __init__(self, couponData):
        super(crack_growth_coupon_44_50, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.length = couponData['geometry']['length']
        self.width = couponData['geometry']['width']
        self.phi1 = couponData['geometry']['phi1']
        self.notchLength = couponData['geometry']['notchLength']
        self.notchThickness = couponData['geometry']['notchThickness']
        self.nHoleRow1 = couponData['geometry']['nHoleRow1']
        self.nHoleRow2 = couponData['geometry']['nHoleRow2']
        self.phi2 = couponData['geometry']['phi2']
        self.centerOffsetRow1 = couponData['geometry']['centerOffsetRow1']
        self.centerOffsetRow2 = couponData['geometry']['centerOffsetRow2']
        self.centerOffsetColumn = couponData['geometry']['centerOffsetColumn']
        self.thickness = couponData['thickness']
        self.lenTol = couponData['lenTol']
        self.seedSizeThickness = couponData['elemSize']['thickness']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeArc = couponData['elemSize']['arc']
        # self.seedSizeLong3 = couponData['elemSize']['long3']
        self.seedSizeNotch = couponData['elemSize']['notch']
        self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        self.materialName = couponData['material']['name']
        self.density = couponData['material']['density']
        self.youngsModulus = couponData['material']['youngsModulus']
        self.poissonsRatio = couponData['material']['poissonsRatio']
        self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        self.initIncr = couponData['step']['initIncr']
        self.pinLoad = couponData['step']['pinLoad']
        self.version = couponData['version']
        ## derived quantities
        self.nHoleRow1 = int(self.nHoleRow1)
        self.nHoleRow2 = int(self.nHoleRow2)
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
        if self.nHoleRow1!=0 or self.nHoleRow2!=0:
            (self.xa, self.ya) = (self.xA, self.yA) = (self.width/2.0, (self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2)/2.0)
            (self.xb, self.yb) = (self.xB, self.yB) = (-self.width/2.0, (self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2)/2.0)
            (self.xc, self.yc) = (self.xC, self.yC) = (-self.width/2.0, -(self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2)/2.0)
            (self.xd, self.yd) = (self.xD, self.yD) = (self.width/2.0, -(self.length-self.centerOffsetRow1-1.5*self.centerOffsetRow2)/2.0)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.notchLength/2.0, self.notchThickness/2.0)
        (self.xf, self.yf) = (self.xF, self.yF) = (-self.notchLength/2.0, self.notchThickness/2.0)
        (self.xg, self.yg) = (self.xG, self.yG) = (-self.notchLength/2.0, -self.notchThickness/2.0)
        (self.xh, self.yh) = (self.xH, self.yH) = (self.notchLength/2.0, -self.notchThickness/2.0)
        # (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.centerOffset2/2.0, -(self.height-self.centerOffset1))
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
        ## define sketch ==>> hole ############################################################################################################################
        # if self.nHoleRow1!=0 or self.nHoleRow2!=0:
        #     self.profileSketch[3] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_4', sheetSize=200.0)
        #     self.profileGeometry4, self.profileVertices4 = self.profileSketch[3].geometry, self.profileSketch[3].vertices
        #     self.profileSketch[3].setPrimaryObject(option=STANDALONE)
        #     self.profileSketch[3].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.phi2/2.0, self.yO))
        #     self.profileSketch[3].unsetPrimaryObject()
        #######################################################################################################################################################
        # (self.xA, self.yA) = self.profileVertices1[0].coords
        # (self.xB, self.yB) = self.profileVertices1[1].coords
        # (self.xC, self.yC) = self.profileVertices1[2].coords
        # (self.xD, self.yD) = self.profileVertices1[3].coords
        # (self.xE, self.yE) = self.profileVertices1[4].coords
        # (self.xF, self.yF) = self.profileVertices1[5].coords
        # (self.xG, self.yG) = self.profileVertices1[6].coords
        # (self.xH, self.yH) = self.profileVertices1[7].coords
        # (self.xC1, self.yC1) = self.profileVertices1[8].coords
        #######################################################################################################################################################
        # self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
        #              ['A', self.xa, self.ya, self.xA, self.yA],
        #              ['B', self.xb, self.yb, self.xB, self.yB],
        #              ['C', self.xc, self.yc, self.xC, self.yC],
        #              ['D', self.xd, self.yd, self.xD, self.yD],
        #              ['E', self.xe, self.ye, self.xE, self.yE],
        #              ['F', self.xf, self.yf, self.xF, self.yF],
        #              ['G', self.xg, self.yg, self.xG, self.yG],
        #              ['H', self.xh, self.yh, self.xH, self.yH],
        #              ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
        #              ['height', '', self.height, '', (self.yA-self.yH)],
        #              ['width', '', self.width, '', 2*(self.xG-self.xH)],
        #              ['centerOffset1', '', self.centerOffset1, '', (self.yC1-self.yH)],
        #              ['notchOffset', '', self.notchOffset, '', (self.yC1-self.yE)],
        #              ['centerOffset2', '', self.centerOffset2, '', 2*self.xC1],
        #              ['notchOpeningTop', '', self.notchOpeningTop, '', 2*self.xA],
        #              ['notchOpeningBottom', '', self.notchOpeningBottom, '', 2*self.xC],
        #              ['notchOpeningDepth', '', self.notchOpeningDepth, '', (self.yA-self.yB)]]
    def createPart(self):
        ## create solid
        self.part = [None]
        self.tempPart = len(self.profileSketch)*[None]
        for i in range(len(self.tempPart)):
            # if i!=(len(self.tempPart)-1) or (i==(len(self.tempPart)-1) and (self.nHoleRow1!=0 or self.nHoleRow2!=0)):
            self.tempPart[i] = self.model.Part(name=self.couponName+'_TempPart_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.tempPart[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.tempPart[0])        
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        newPartName = self.couponName+'_Part_1'
        ## create translation vectors
        # def createVector(numHoleThisRow, yOffset):
        #     for i in range(numHoleThisRow):
        #         for j in range(2):
        #             self.vectorTranslation.append(((-(numHoleThisRow-1)/2.0+i)*self.centerOffsetColumn, (-1)**j*(self.yA-yOffset), 0))
        # self.vectorTranslation = []
        # createVector(self.nHoleRow1, self.centerOffsetRow1)
        # createVector(self.nHoleRow2, (self.centerOffsetRow1+self.centerOffsetRow2))
        ## create temporary assembly instances
        self.cuttingInstances = ()
        # self.tempInstance = (len(self.tempPart)-1+2*(self.nHoleRow1+self.nHoleRow2))*[None]
        self.tempInstance = len(self.tempPart)*[None]
        for i in range(len(self.tempInstance)):
            # if i<(len(self.tempPart)-1):
            self.tempInstance[i] = self.assembly.Instance(name=self.couponName+'_TempInstance_'+str(i+1), part=self.tempPart[i], dependent=ON)
            # else:
            #     self.tempInstance[i] = self.assembly.Instance(name=self.couponName+'_TempInstance_'+str(i+1), part=self.tempPart[3], dependent=ON)
            #     self.assembly.translate(instanceList=(self.tempInstance[i].name, ), vector=self.vectorTranslation[i-4])
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
        # createPartitionCyl()
        for i in range(2):
            # if self.nHoleRow1!=0 or self.nHoleRow2!=0:
            #     createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*(self.yA-self.centerOffsetRow1+0.5*self.centerOffsetRow2))
            #     createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*(self.yA-self.centerOffsetRow1))
            #     createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*(self.yA-self.centerOffsetRow1-0.5*self.centerOffsetRow2))
            #     createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*(self.yA-self.centerOffsetRow1-self.centerOffsetRow2))
            #     createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*(self.yA-self.centerOffsetRow1-1.5*self.centerOffsetRow2))
            createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*0.5*self.notchThickness)
            createPartitionDatumPlane(self.part[0], 'XZPLANE', (-1)**i*0.5*self.notchLength)
            createPartitionDatumPlane(self.part[0], 'YZPLANE', (-1)**i*0.5*self.notchLength)
        createPartitionDatumPlane(self.part[0], 'YZPLANE', 0)
        self.crackedPart = self.part[0].cells.getByBoundingBox(xMin=-(0.5*self.notchLength+self.lenTol), yMin=-(0.5*self.notchLength+self.lenTol), zMin=-self.lenTol, xMax=(0.5*self.notchLength+self.lenTol), yMax=(0.5*self.notchLength+self.lenTol), zMax=self.thickness+self.lenTol)
        self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, 0.5*self.notchLength, 0)), point2=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, -0.5*self.notchLength, 0)), point3=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, 0.5*self.notchLength, self.thickness)), cells=self.crackedPart)
        self.crackedPart = self.part[0].cells.getByBoundingBox(xMin=-(0.5*self.notchLength+self.lenTol), yMin=-(0.5*self.notchLength+self.lenTol), zMin=-self.lenTol, xMax=(0.5*self.notchLength+self.lenTol), yMax=(0.5*self.notchLength+self.lenTol), zMax=self.thickness+self.lenTol)
        self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, 0.5*self.notchLength, 0)), point2=self.part[0].vertices.findAt(coordinates=(0.5*self.notchLength, -0.5*self.notchLength, 0)), point3=self.part[0].vertices.findAt(coordinates=(-0.5*self.notchLength, 0.5*self.notchLength, self.thickness)), cells=self.crackedPart)
        # count = 0
        # for thisVector in self.vectorTranslation:
        #     if count%2==0:
        #         createPartitionDatumPlane(self.part[0], 'YZPLANE', thisVector[0])
        #     count=count+1
    def createMesh(self):
        ## seed ==>> global
        self.part[0].seedPart(size=max(self.seedSizeThickness, self.seedSizeArc, self.seedSizeLong1, self.seedSizeLong2, self.seedSizeNotch), deviationFactor=0.1, minSizeFactor=0.1)
        ## seed ==>> thickness
        edgesThickness = self.part[0].edges.findAt(coordinates=((0, self.phi1/2, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> central hole
        edgesHoleArc1 = self.part[0].edges.getByBoundingCylinder((self.xO, self.yO, -self.lenTol), (self.xO, self.yO, self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesHoleArc1, size=self.seedSizeArc, deviationFactor=0.1, constraint=FINER)
        edgesHoleArc2 = self.part[0].edges.getByBoundingCylinder((self.xO, self.yO, self.thickness-self.lenTol), (self.xO, self.yO, self.thickness+self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesHoleArc2, size=self.seedSizeArc, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> edges long1, long2
        edgesLong1 = self.part[0].edges.findAt(coordinates=(((0.5*self.notchLength+self.lenTol), 0.5*self.notchThickness, 0), ((0.5*self.notchLength+self.lenTol), 0.5*self.notchThickness, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -0.5*self.notchThickness, 0), ((0.5*self.notchLength+self.lenTol), -0.5*self.notchThickness, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, 0), ((0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, 0), ((0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), self.yA, 0), ((0.5*self.notchLength+self.lenTol), self.yA, self.thickness), 
                                                            ((0.5*self.notchLength+self.lenTol), -self.yA, 0), ((0.5*self.notchLength+self.lenTol), -self.yA, self.thickness), ))
        self.seedEdge(self.part[0], 0, 0.5*self.notchLength, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        edgesLong2 = self.part[0].edges.findAt(coordinates=((-(0.5*self.notchLength+self.lenTol), 0.5*self.notchThickness, 0), (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchThickness, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchThickness, 0), (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchThickness, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, 0), (-(0.5*self.notchLength+self.lenTol), 0.5*self.notchLength, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, 0), (-(0.5*self.notchLength+self.lenTol), -0.5*self.notchLength, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), self.yA, 0), (-(0.5*self.notchLength+self.lenTol), self.yA, self.thickness), 
                                                            (-(0.5*self.notchLength+self.lenTol), -self.yA, 0), (-(0.5*self.notchLength+self.lenTol), -self.yA, self.thickness), ))
        self.seedEdge(self.part[0], 0, -0.5*self.notchLength, edgesLong2, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> edge notch square
        edgesNotch = self.part[0].edges.findAt(coordinates=((0, (0.5*self.notchLength-self.lenTol), 0), (0, (0.5*self.notchLength-self.lenTol), self.thickness), 
                                                            (0, -(0.5*self.notchLength-self.lenTol), 0), (0, -(0.5*self.notchLength-self.lenTol), self.thickness), 
                                                            ((0.5*self.notchLength-self.lenTol), 0.5*self.notchThickness, 0), ((0.5*self.notchLength-self.lenTol), 0.5*self.notchThickness, self.thickness), 
                                                            (-(0.5*self.notchLength-self.lenTol), 0.5*self.notchThickness, 0), (-(0.5*self.notchLength-self.lenTol), 0.5*self.notchThickness, self.thickness), 
                                                            ((0.5*self.notchLength-self.lenTol), -0.5*self.notchThickness, 0), ((0.5*self.notchLength-self.lenTol), -0.5*self.notchThickness, self.thickness), 
                                                            (-(0.5*self.notchLength-self.lenTol), -0.5*self.notchThickness, 0), (-(0.5*self.notchLength-self.lenTol), -0.5*self.notchThickness, self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesNotch, size=self.seedSizeNotch, deviationFactor=0.1, constraint=FINER)
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

