#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
###################    CLASS DEFINITION : STATIC COUPON : BEARING SPECIMEN 18 TO 21    ##########################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Mar-2023 |               BC added to the pin               |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


from abaqus import *
from abaqusConstants import *
from caeModules import *

class static_coupon_18_21(coupon_generic):
    def __init__(self, couponData):
        super(static_coupon_18_21, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.len1 = couponData['geometry']['len1']
        self.len2 = couponData['geometry']['len2']
        self.width = couponData['geometry']['width']
        self.phi1 = couponData['geometry']['phi1']
        self.E = couponData['geometry']['E']
        self.phi2 = couponData['geometry']['phi2']
        self.pinExtension = couponData['geometry']['pinExtension']
        self.thickness = couponData['thickness']
        self.lenTol = couponData['lenTol']
        self.seedSizeArc = couponData['elemSize']['arc']
        self.seedSizeInnerRadial = couponData['elemSize']['radialInner']
        self.seedSizeOuterRadial = couponData['elemSize']['radialOuter']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeLong3 = couponData['elemSize']['long3']
        self.seedSizeThickness1 = couponData['elemSize']['thickness1']
        self.seedSizeThickness2 = couponData['elemSize']['thickness2']
        self.seedSizeVertical1 = couponData['elemSize']['vertical1']
        self.seedSizeVertical2 = couponData['elemSize']['vertical2']
        self.seedSizeVertical3 = couponData['elemSize']['vertical3']
        self.seedSizePinDia = couponData['elemSize']['pinDia']
        self.seedSizePinLength = couponData['elemSize']['pinLength']
        self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        self.elemTypeHexPart2 = SymbolicConstant(couponData['elemType']['hexPart2'])
        self.elemTypeHexPart3 = SymbolicConstant(couponData['elemType']['hexPart3'])
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
        self.nominalStress = couponData['step']['nominalStress']
        self.version = couponData['version']
        ## derived quantities
        self.tieDistance = self.len1/2.0*0.25
        self.pinPressure = self.nominalStress*self.thickness/(2*self.pinExtension)
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
        self.createTie()
        self.createContact()
        self.createStep()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (0, self.width/2.0)
        (self.xd, self.yd) = (self.xD, self.yD) = (0, -self.yA)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.len1/2.0, self.yA)
        (self.xf, self.yf) = (self.xF, self.yF) = (self.xE, -self.yE)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.tieDistance, self.yE)
        (self.xc, self.yc) = (self.xC, self.yC) = (self.xB, self.yF)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.E, 0) # center 1
        (self.xg, self.yg) = (self.xG, self.yG) = (self.xC1-self.phi1/2.0, 0)
        #################################################################################################################################################
        self.profileSketch = 3*[None]
        ## define sketch
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_1', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)
        ## rectangle ABCD
        self.profileSketch[0].rectangle(point1=(self.xA, self.yA), point2=(self.xC, self.yC))
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xA, self.yA) = self.profileVertices1[0].coords
        (self.xD, self.yD) = self.profileVertices1[1].coords
        (self.xC, self.yC) = self.profileVertices1[2].coords
        (self.xB, self.yB) = self.profileVertices1[3].coords
        #######################################################################################################################################################
        ## define sketch ==>> away from region of interest
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileGeometry2, self.profileVertices2 = self.profileSketch[1].geometry, self.profileSketch[1].vertices
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)
        ## rectangle BCFE
        self.profileSketch[1].rectangle(point1=(self.xB, self.yB), point2=(self.xF, self.yF))
        self.profileSketch[1].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xB, self.yB) = self.profileVertices2[0].coords
        (self.xC, self.yC) = self.profileVertices2[1].coords
        (self.xF, self.yF) = self.profileVertices2[2].coords
        (self.xE, self.yE) = self.profileVertices2[3].coords
        #######################################################################################################################################################
        ## define sketch ==>> hole #####s#######################################################################################################################
        self.profileSketch[2] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_3', sheetSize=200.0)
        self.profileGeometry3, self.profileVertices3 = self.profileSketch[2].geometry, self.profileSketch[2].vertices
        self.profileSketch[2].setPrimaryObject(option=STANDALONE)
        self.profileSketch[2].CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(self.xG, self.yG))
        self.profileSketch[2].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xC1, self.yC1) = self.profileVertices3[0].coords
        #######################################################################################################################################################
        self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
                         ['A', self.xa, self.ya, self.xA, self.yA],
                         ['B', self.xb, self.yb, self.xB, self.yB],
                         ['C', self.xc, self.yc, self.xC, self.yC],
                         ['D', self.xd, self.yd, self.xD, self.yD],
                         ['E', self.xe, self.ye, self.xE, self.yE],
                         ['F', self.xf, self.yf, self.xF, self.yF],
                         ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
                         ['G', self.xg, self.yg, self.xG, self.yG],
                         ['len1', '', self.len1, '', 2*(self.xE-self.xA)],
                         ['width', '', self.width, '', (self.yA-self.yD)],
                         ['E', '', self.E, '', (self.xC1-self.xA)],
                         ['phi1', '', self.phi1, '', 2*(self.xC1-self.xG)]]
    def createPart(self):
        ## create solid
        self.part = len(self.profileSketch)*[None]
        self.tempPart = 1*[None]
        for i in range(len(self.part)):
            if i==0:
                self.tempPart[i] = self.model.Part(name=self.couponName+'_Temp_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.tempPart[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
            elif i==1:
                self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness)
            elif i==2:
                self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=2*self.pinExtension+self.thickness)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.tempPart[0])
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.instance = len(self.part)*[None]
        for i in range(len(self.part)):
            if i==0:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Temp_Instance_'+str(i+1), part=self.tempPart[i], dependent=ON)
            else:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
        newPartName = self.couponName+'_Part_1'
        self.assembly.InstanceFromBooleanCut(name=newPartName, instanceToBeCut=self.instance[0], cuttingInstances=(self.instance[2], ), originalInstances=DELETE)
        del self.assembly.features[newPartName+'-1']
        self.part[0] = self.model.parts[newPartName]
        for i in range(len(self.part)):
            self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
        self.assembly.translate(instanceList=(self.instance[2].name, ), vector=(0.0, 0.0, -self.pinExtension))
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])
    def createPartition(self):
        def createFacePartition():
            sketchPlane = self.part[0].faces.findAt(coordinates=(self.lenTol, self.lenTol, 0))
            sketchUpEdge = self.part[0].edges.findAt(coordinates=(0, 0, 0))
            t = self.part[0].MakeSketchTransform(sketchPlane=sketchPlane, sketchUpEdge=sketchUpEdge, sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            s1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=50.0, gridSpacing=1.0, transform=t)
            s1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
            xMid = ((self.xC1-self.phi1/2.0)+self.xO)/2.0
            s1.CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(xMid, 0))
            self.partitionRadius = self.xC1-xMid
            ## create sketch
            self.part[0].PartitionFaceBySketch(sketchUpEdge=sketchUpEdge, faces=sketchPlane, sketch=s1)
            s1.unsetPrimaryObject()
            ## circular partition
            edgesTemp1= self.getByCylinderDifference(self.part[0].edges, (self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.lenTol), (self.partitionRadius+self.lenTol), (self.phi1/2.0+self.lenTol))
            edgesForPartition1 = self.getArcEdge(edgesTemp1)
            sweepPath1 = self.part[0].edges.findAt(coordinates=(self.xA, self.xC1, self.lenTol))
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath1, cells=self.part[0].cells, edges=edgesForPartition1)
            ## diagonal partition
            pickedCells1 = self.part[0].cells.getByBoundingBox(xMin=-self.lenTol, yMin=-self.xC1-self.lenTol, zMin=-self.lenTol, xMax=2*self.xC1+self.lenTol, yMax=self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
            self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(0, -self.xC1, 0)), point2=self.part[0].vertices.findAt(coordinates=(2*self.xC1, self.xC1, 0)), point3=self.part[0].vertices.findAt(coordinates=(0, -self.xC1, self.thickness)), cells=pickedCells1)
            pickedCells2 = self.part[0].cells.getByBoundingBox(xMin=-self.lenTol, yMin=-self.xC1-self.lenTol, zMin=-self.lenTol, xMax=2*self.xC1+self.lenTol, yMax=self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
            self.part[0].PartitionCellByPlaneThreePoints(point1=self.part[0].vertices.findAt(coordinates=(0, self.xC1, 0)), point2=self.part[0].vertices.findAt(coordinates=(2*self.xC1, -self.xC1, 0)), point3=self.part[0].vertices.findAt(coordinates=(0, self.xC1, self.thickness)), cells=pickedCells2)
        def createPartitionByDatumPlane(part, offsetDistance, **kwargs):
            ## partition by YZ plane
            self.datumPlane_ID = part.DatumPlaneByPrincipalPlane(offset=offsetDistance, **kwargs).id
            part.PartitionCellByDatumPlane(datumPlane=part.datums[self.datumPlane_ID], cells=part.cells)
        createPartitionByDatumPlane(self.part[0], 2*self.xC1, principalPlane=YZPLANE)
        createPartitionByDatumPlane(self.part[0], self.xC1, principalPlane=XZPLANE)
        createPartitionByDatumPlane(self.part[0], -self.xC1, principalPlane=XZPLANE)
        createFacePartition()
        createPartitionByDatumPlane(self.part[0], self.xC1, principalPlane=YZPLANE)
        createPartitionByDatumPlane(self.part[0], self.yO, principalPlane=XZPLANE)
        ## pin partition
        createPartitionByDatumPlane(self.part[2], self.xC1, principalPlane=YZPLANE)
        createPartitionByDatumPlane(self.part[2], self.pinExtension, principalPlane=XYPLANE)
        createPartitionByDatumPlane(self.part[2], self.thickness+self.pinExtension, principalPlane=XYPLANE)
    def createMesh(self):
        ## seed ==>> thickness direction
        edgesThickness1 = self.part[0].edges.findAt(coordinates=((0, 0, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness1, size=self.seedSizeThickness1, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> inner arc
        edgesInnerArc = self.part[0].edges.getByBoundingCylinder((self.xC1, self.yC1, self.thickness-self.lenTol), (self.xC1, self.yC1, self.thickness+self.lenTol), (self.phi1/2.0+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesInnerArc, size=self.seedSizeArc, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer arc
        elemNum = self.part[0].getEdgeSeeds(edgesInnerArc[0], attribute=NUMBER)
        edgesTemp1 = self.getByCylinderDifference(self.part[0].edges, (self.xC1, self.yC1, self.thickness-self.lenTol), (self.xC1, self.yC1, self.thickness+self.lenTol), (self.partitionRadius+self.lenTol), (self.phi1/2.0+self.lenTol))
        edgesOuterArc1 = self.getArcEdge(edgesTemp1)
        self.part[0].seedEdgeByNumber(edges=edgesOuterArc1, number=elemNum, constraint=FIXED)
        edgesTemp2 = self.getByCylinderDifference(self.part[0].edges, (self.xC1, self.yC1, -self.lenTol), (self.xC1, self.yC1, self.lenTol), (self.partitionRadius+self.lenTol), (self.phi1/2.0+self.lenTol))
        edgesOuterArc2 = self.getArcEdge(edgesTemp2)
        self.part[0].seedEdgeByNumber(edges=edgesOuterArc2, number=elemNum, constraint=FIXED)
        ## seed ==>> inner radial
        edgesInnerRadial1 = self.getByDifference(edgesTemp1, edgesOuterArc1)
        self.part[0].seedEdgeBySize(edges=edgesInnerRadial1, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        edgesInnerRadial2 = self.getByDifference(edgesTemp2, edgesOuterArc2)
        self.part[0].seedEdgeBySize(edges=edgesInnerRadial2, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer radial
        edgesOuterRadial = self.part[0].edges.findAt(coordinates=((self.xC1, (self.partitionRadius+self.lenTol), 0), (self.xC1, (self.partitionRadius+self.lenTol), self.thickness), 
                                                                  (self.xC1, -(self.partitionRadius+self.lenTol), 0), (self.xC1, -(self.partitionRadius+self.lenTol), self.thickness), 
                                                                  (self.xC1-(self.partitionRadius+self.lenTol), 0, 0), (self.xC1-(self.partitionRadius+self.lenTol), 0, self.thickness), 
                                                                  (self.xC1+(self.partitionRadius+self.lenTol), 0, 0), (self.xC1+(self.partitionRadius+self.lenTol), 0, self.thickness), ))
        self.part[0].seedEdgeBySize(edges=edgesOuterRadial, size=self.seedSizeOuterRadial, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> vertical 1 direction
        edgesVertical1 = self.part[0].edges.findAt(coordinates=((0, self.xC1+self.lenTol, 0), (0, self.xC1+self.lenTol, self.thickness), 
                                                                (self.xC1, self.xC1+self.lenTol, 0), (self.xC1, self.xC1+self.lenTol, self.thickness), 
                                                                (2*self.xC1, self.xC1+self.lenTol, 0), (2*self.xC1, self.xC1+self.lenTol, self.thickness), 
                                                                (self.xB, self.xC1+self.lenTol, 0), (self.xB, self.xC1+self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, self.xC1, edgesVertical1, minSize=self.seedSizeVertical1, maxSize=self.seedSizeVertical2)
        ## seed ==>> vertical 2 direction
        edgesVertical2 = self.part[0].edges.findAt(coordinates=((0, -self.xC1-self.lenTol, 0), (0, -self.xC1-self.lenTol, self.thickness), 
                                                                (self.xC1, -self.xC1-self.lenTol, 0), (self.xC1, -self.xC1-self.lenTol, self.thickness), 
                                                                (2*self.xC1, -self.xC1-self.lenTol, 0), (2*self.xC1, -self.xC1-self.lenTol, self.thickness), 
                                                                (self.xB, -self.xC1-self.lenTol, 0), (self.xB, -self.xC1-self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, -self.xC1, edgesVertical2, minSize=self.seedSizeVertical1, maxSize=self.seedSizeVertical2)
        ## seed ==>> long edges along B'B
        pickedEdges1 = self.part[0].edges.getByBoundingBox(xMin=2*self.xC1-self.lenTol, yMin=self.yD-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.yB+self.lenTol, zMax=self.thickness+self.lenTol)
        pickedEdges2 = self.part[0].edges.findAt(coordinates=((2*self.xC1, self.xC1-self.lenTol, 0), (2*self.xC1, self.xC1-self.lenTol, self.thickness),
                                                              (2*self.xC1, -(self.xC1-self.lenTol), 0), (2*self.xC1, -(self.xC1-self.lenTol), self.thickness)))
        pickedEdges3 = self.getByDifference(pickedEdges1, pickedEdges2)
        edgesLong1 = self.getEdgeByLength(pickedEdges3, abs(self.xB-2*self.xC1))
        self.seedEdge(self.part[0], 0, 2*self.xC1, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> vertical edge plate away from region of interest
        edgesVertical3 = self.part[1].edges.findAt(coordinates=((self.xB, 0, 0), ))
        self.part[1].seedEdgeBySize(edges=edgesVertical3, size=self.seedSizeVertical3, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> thickness edge plate away from region of interest
        edgesThickness2 = self.part[1].edges.findAt(coordinates=((self.xB, self.yB, self.lenTol), ))
        self.part[1].seedEdgeBySize(edges=edgesThickness2, size=self.seedSizeThickness2, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edge plate away from region of interest
        edgesLong2 = self.part[1].edges.findAt(coordinates=((self.xB+self.lenTol, self.yB, 0), (self.xB+self.lenTol, self.yB, self.thickness), 
                                                            (self.xC+self.lenTol, self.yC, 0), (self.xC+self.lenTol, self.yC, self.thickness)))
        self.seedEdge(self.part[1], 0, self.xB, edgesLong2, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> pin circumference portion
        self.part[2].seedEdgeBySize(edges=self.getArcEdge(self.part[2].edges), size=self.seedSizePinDia, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin diameter portion
        diaEdges = self.part[2].edges.findAt(coordinates=((self.xC1, 0, 0), (self.xC1, 0, self.pinExtension), (self.xC1, 0, self.pinExtension+self.thickness), (self.xC1, 0, 2*self.pinExtension+self.thickness)))
        self.part[2].seedEdgeBySize(edges=diaEdges, size=self.seedSizePinDia, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> pin length portion
        lenEdges = self.part[2].edges.findAt(coordinates=((self.xC1, self.phi1/2, self.lenTol), (self.xC1, -self.phi1/2, self.lenTol), 
                                                          (self.xC1, self.phi1/2, self.pinExtension+self.lenTol), (self.xC1, -self.phi1/2, self.pinExtension+self.lenTol), 
                                                          (self.xC1, self.phi1/2, 2*self.pinExtension+self.thickness-self.lenTol), (self.xC1, -self.phi1/2, 2*self.pinExtension+self.thickness-self.lenTol)))
        self.part[2].seedEdgeBySize(edges=lenEdges, size=self.seedSizePinLength, deviationFactor=0.1, constraint=FINER)
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHexPart1, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1, ))
        elemType2 = mesh.ElemType(elemCode=self.elemTypeHexPart2, elemLibrary=STANDARD)
        self.part[1].setElementType(regions=(self.part[1].cells,), elemTypes=(elemType2, ))
        elemType3 = mesh.ElemType(elemCode=self.elemTypeHexPart3, elemLibrary=STANDARD)
        self.part[2].setElementType(regions=(self.part[2].cells,), elemTypes=(elemType3, ))
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
            if i==2:
                pickedRegion = self.part[i].Set(elements=self.part[i].elements, name='Elset_All_Part_'+str(i+1))
                self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.sectionPin.name, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
            else:
                pickedRegion = self.part[i].Set(elements=self.part[i].elements, name='Elset_All_Part_'+str(i+1))
                self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.sectionPlate.name, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def createEquation(self):
        i=2
        nodesEqnPosY = self.part[i].nodes.getByBoundingSphere((self.xC1, self.phi1/2, 0), self.lenTol)
        nsetNameEqnPosY = 'Nset_Eqn_PosY_Part_'+str(i+1)
        self.part[i].Set(nodes=nodesEqnPosY, name=nsetNameEqnPosY)
        nodesEqnNegY = self.part[i].nodes.getByBoundingSphere((self.xC1, -self.phi1/2, 0), self.lenTol)
        nsetNameEqnNegY = 'Nset_Eqn_NegY_Part_'+str(i+1)
        self.part[i].Set(nodes=nodesEqnNegY, name=nsetNameEqnNegY)
        self.model.Equation(name=self.couponName+'_Equation', terms=((1.0, self.instance[i].name+'.'+nsetNameEqnPosY, 1), (-1.0, self.instance[i].name+'.'+nsetNameEqnNegY, 1)))
    def createTie(self):
        region = (len(self.part)-1)*[None]
        for i in range(len(region)):
            surf = self.part[i].faces.getByBoundingBox(xMin=self.xC-self.lenTol, yMin=self.yC-self.lenTol, zMin=-self.lenTol, xMax=self.xB+self.lenTol, yMax=self.yB+self.lenTol, zMax=self.thickness+self.lenTol)
            surfName = 'Surf_Tie_Part_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[i], surf, surfName)
            region[i] = self.instance[i].surfaces[surfName]
        self.model.Tie(name=self.couponName+'_Tie', master=region[1], slave=region[0], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement=SURFACE_TO_SURFACE)
    def createContact(self):
        for i in range(len(self.part)):
            if i==0:
                ## plate contact surface
                surfFacePlateContact = self.part[i].faces.getByBoundingCylinder((self.xC1, 0, -self.lenTol), (self.xC1, 0, self.thickness+self.lenTol), (self.phi1/2+self.lenTol))
                surfNamePlateContact = 'Surf_Contact_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], surfFacePlateContact, surfNamePlateContact)
                region1 = self.instance[i].surfaces[surfNamePlateContact]
            if i==2:
                # pin contact surface
                surfFacePinContact = self.part[i].faces.findAt(coordinates=((self.xC1-self.phi1/2, 0, self.pinExtension+self.lenTol), (self.xC1+self.phi1/2, 0, self.pinExtension+self.lenTol)))
                surfNamePinContact = 'Surf_Contact_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], surfFacePinContact, surfNamePinContact)
                region2 = self.instance[i].surfaces[surfNamePinContact]
        self.contactProperty = self.model.ContactProperty(self.couponName+'_Contact_Property')
        self.contactProperty.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact', createStepName='Initial', master=region2, slave=region1, sliding=FINITE, 
                                              thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=OMIT, datumAxis=None, clearanceRegion=None)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF'))
        self.couponData['step'].update({'pinPressure':self.pinPressure})
        for i in range(len(self.part)):
            if i==1:
                ## create BC at posX face
                nodesPosX = self.part[i].nodes.getByBoundingBox(xMin=self.xF-self.lenTol, yMin=self.yF-self.lenTol, zMin=-self.lenTol, xMax=self.xE+self.lenTol, yMax=self.yE+self.lenTol, zMax=self.thickness+self.lenTol)
                nsetNamePosX = 'Nset_BC_PosX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesPosX, name=nsetNamePosX)
                region = self.instance[i].sets[nsetNamePosX]
                self.model.DisplacementBC(name='BC_PosX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==2:
                ## create BC at negZ face of Part 3
                nodesNegZ = self.part[i].nodes.getByBoundingCylinder((self.xC1, 0, 0), (self.xC1, 0, self.lenTol), (self.phi1+self.lenTol))
                nsetNameNegZ = 'Nset_BC_NegZ_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegZ , name=nsetNameNegZ)
                region = self.instance[i].sets[nsetNameNegZ]
                self.model.DisplacementBC(name='BC_NegZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## create BC at posZ face of Part 3
                nodesPosZ = self.part[i].nodes.getByBoundingCylinder((self.xC1, 0, self.thickness+2*self.pinExtension), (self.xC1, 0, self.thickness+2*self.pinExtension+self.lenTol), (self.phi1+self.lenTol))
                nsetNamePosZ = 'Nset_BC_PosZ_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesPosZ , name=nsetNamePosZ)
                region = self.instance[i].sets[nsetNamePosZ]
                self.model.DisplacementBC(name='BC_PosZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## create pressure load on pin NegZ portion
                endCellFaceArr1 = self.part[i].faces.findAt(coordinates=((self.xC1+self.phi1/2, 0, self.lenTol), ))
                surfNameNegZ = 'Surf_Load_NegZ_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr1, surfNameNegZ)
                region1 = self.instance[i].surfaces[surfNameNegZ]
                self.model.Pressure(name='Load_NegZ_Instance_'+str(i+1), createStepName='Load', region=region1, distributionType=UNIFORM, field='', magnitude=self.pinPressure, amplitude=UNSET)
                ## create pressure load on pin NegZ portion
                endCellFaceArr2 = self.part[i].faces.findAt(coordinates=((self.xC1+self.phi1/2, 0, self.pinExtension+self.thickness+self.lenTol), ))
                surfNamePosZ = 'Surf_Load_PosZ_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr2, surfNamePosZ)
                region2 = self.instance[i].surfaces[surfNamePosZ]
                self.model.Pressure(name='Load_PosZ_Instance_'+str(i+1), createStepName='Load', region=region2, distributionType=UNIFORM, field='', magnitude=self.pinPressure, amplitude=UNSET)

