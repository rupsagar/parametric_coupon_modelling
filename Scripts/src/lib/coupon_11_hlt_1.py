#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
################################    CLASS DEFINITION : HLT1 : SPECIMEN 123    ###################################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 04-Oct-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import math
from abaqus import *
from abaqusConstants import *
from caeModules import *

class coupon_11_hlt_1(coupon_generic):
    def __init__(self, couponData):
        super(coupon_11_hlt_1, self).__init__(couponData)
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.phi = self.geometry['Diameter']
        self.fastLength = self.geometry['Fastener_Length']
        self.fastHeadDia= self.geometry['Head_Diameter']
        self.fastHeadHeight= self.geometry['Head_Height']
        self.fastNutDia= self.geometry['Nut_Diameter']
        self.fastNutHeight= self.geometry['Nut_Height']
        ## derived quantities
        # self.endStress = -self.stepLoad*(self.b/self.B)
        self.len1 = 28.0*self.phi+max(140.0,16.0*self.phi)
        self.len2 = max(70.0,8.0*self.phi)
        self.radius = 10*self.phi
        self.thickness = [0.79*self.phi, 2.4*0.79*self.phi, 0.79*self.phi]
        self.maxDia = max(self.fastHeadDia, self.fastNutDia)
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
        self.createContact()
        # self.createStep()
        # self.createLoadBC()
        # self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (-4.0*self.phi, 0)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.xA, 2.0*self.phi)
        (self.xc, self.yc) = (self.xC, self.yC) = (8.0*self.phi, self.yB)
        (self.xd, self.yd) = (self.xD, self.yD) = ((self.len1/2.0-self.len2), 4.0*self.phi)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.len1/2.0, self.yD)
        (self.xf, self.yf) = (self.xF, self.yF) = (self.xE, 0)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (self.xC, self.yC+self.radius)
        #################################################################################################################################################
        self.profileSketch = 5*[None]
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
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[3], textPoint=(-2.5*self.phi, -self.phi), value=4*self.phi)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[1], textPoint=(-5*self.phi, self.phi), value=2*self.phi)        
        ## line BC
        self.profileSketch[0].Line(point1=self.profileVertices1[1].coords, point2=(self.xC, self.yC))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[3], textPoint=(4*self.phi, 3*self.phi), value=8*self.phi)
        ## arc FG
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[2].coords, point2=(self.xD, self.yD), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[5], entity2=self.profileGeometry1[6], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=((self.xC+self.xD)/2.0,(self.yC+self.yC1)/2.0), radius=self.radius)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[2], textPoint=(self.xD, 2*self.phi), value=4*self.phi)        
        ## line DE
        self.profileSketch[0].Line(point1=self.profileVertices1[3].coords, point2=(self.xE, self.yE))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[3], vertex2=self.profileVertices1[5], textPoint=((self.xD+self.xE)/2.0, 5*self.phi), value=self.len2)
        ## line EF
        self.profileSketch[0].Line(point1=self.profileVertices1[5].coords, point2=(self.xF, self.yF))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], addUndoState=False)
        ## copy and mirror
        self.profileSketch[0].copyMirror(mirrorLine=self.profileGeometry1[2], objectList=(self.profileGeometry1[4], self.profileGeometry1[5], self.profileGeometry1[6], 
                                                                                          self.profileGeometry1[7], self.profileGeometry1[8]))
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        ## sketch 2
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileGeometry2, self.profileVertices2 = self.profileSketch[1].geometry, self.profileSketch[1].vertices
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)
        self.profileSketch[1].rectangle(point1=(self.xD, self.yD), point2=(self.xE, -self.yE))
        self.profileSketch[1].unsetPrimaryObject()
        #######################################################################################################################################################
        ## define sketch ==>> fastener head circle ############################################################################################################################
        self.profileSketch[2] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_3', sheetSize=200.0)
        self.profileGeometry3, self.profileVertices3 = self.profileSketch[2].geometry, self.profileSketch[2].vertices
        self.profileSketch[2].setPrimaryObject(option=STANDALONE)
        self.profileSketch[2].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.fastHeadDia/2.0, self.yO))
        self.profileSketch[2].unsetPrimaryObject()
        #######################################################################################################################################################
        # ## define sketch ==>> nut inner circle ############################################################################################################################
        # self.profileSketch[4] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_5', sheetSize=200.0)
        # self.profileGeometry5, self.profileVertices5 = self.profileSketch[4].geometry, self.profileSketch[4].vertices
        # self.profileSketch[4].setPrimaryObject(option=STANDALONE)
        # self.profileSketch[4].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.phi/2.0, self.yO))
        # self.profileSketch[4].unsetPrimaryObject()
        #######################################################################################################################################################
        ## define sketch ==>> nut head circle ############################################################################################################################
        self.profileSketch[3] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_4', sheetSize=200.0)
        self.profileGeometry4, self.profileVertices4 = self.profileSketch[3].geometry, self.profileSketch[3].vertices
        self.profileSketch[3].setPrimaryObject(option=STANDALONE)
        self.profileSketch[3].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.fastNutDia/2.0, self.yO))
        self.profileSketch[3].unsetPrimaryObject()
        #######################################################################################################################################################
        ## define sketch ==>> fastener inner circle ############################################################################################################################
        self.profileSketch[4] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_5', sheetSize=200.0)
        self.profileGeometry5, self.profileVertices5 = self.profileSketch[4].geometry, self.profileSketch[4].vertices
        self.profileSketch[4].setPrimaryObject(option=STANDALONE)
        self.profileSketch[4].CircleByCenterPerimeter(center=(self.xO, self.yO), point1=(self.xO+self.phi/2.0, self.yO))
        self.profileSketch[4].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xA, self.yA) = self.profileVertices1[0].coords
        (self.xB, self.yB) = self.profileVertices1[1].coords
        (self.xC, self.yC) = self.profileVertices1[2].coords
        (self.xD, self.yD) = self.profileVertices1[3].coords
        (self.xC1, self.yC1) = self.profileVertices1[4].coords
        (self.xE, self.yE) = self.profileVertices1[5].coords
        (self.xF, self.yF) = self.profileVertices1[6].coords
        #######################################################################################################################################################
        # self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
        #                  ['A', self.xa, self.ya, self.xA, self.yA],
        #                  ['B', self.xb, self.yb, self.xB, self.yB],
        #                  ['C', self.xc, self.yc, self.xC, self.yC],
        #                  ['D', self.xd, self.yd, self.xD, self.yD],
        #                  ['E', self.xe, self.ye, self.xE, self.yE],
        #                  ['F', self.xf, self.yf, self.xF, self.yF],
        #                  ['Center1', self.xc1, self.yc1, self.xC1, self.yC1],
        #                  ['lt1', '', self.lt, '', (self.xD-self.xK)],
        #                  ['lt2', '', self.lt, '', (self.xE-self.xJ)],
        #                  ['b1', '', self.b, '', (self.yA-self.yH)],
        #                  ['b2', '', self.b, '', (self.yB-self.yG)],
        #                  ['B1', '', self.B, '', (self.yD-self.yE)],
        #                  ['B2', '', self.B, '', (self.yK-self.yJ)],
        #                  ['R1', '', self.R, '', ((self.xC1-self.xC)**2+(self.yC1-self.yC)**2)**0.5],
        #                  ['R2', '', self.R, '', ((self.xC2-self.xF)**2+(self.yC2-self.yF)**2)**0.5],
        #                  ['R3', '', self.R, '', ((self.xC3-self.xI)**2+(self.yC3-self.yI)**2)**0.5],
        #                  ['R4', '', self.R, '', ((self.xC4-self.xL)**2+(self.yC4-self.yL)**2)**0.5],
        #                  ['C1', '', self.C, '', (self.xD-self.xC)],
        #                  ['C2', '', self.C, '', (self.xL-self.xK)],
        #                  ['lc1', '', self.lc, '', (self.xB-self.xA)],
        #                  ['lc2', '', self.lc, '', (self.xG-self.xH)]]
    def createPart(self):
        ## create solid
        self.part = 6*[None]
        for i in range(len(self.part)):
            self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            if i==0 or i==1:
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[0], depth=self.thickness[i])
            elif i==2:
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[1], depth=self.thickness[1])
            elif i==3:
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[2], depth=self.fastHeadHeight)
            elif i==4:
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[3], depth=self.fastNutHeight)
            elif i==5:
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[4], depth=self.fastLength)
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        ## create temporary instances for boolean operation on the fastener
        self.instanceFastTemp1 = 2*[None]
        for i in range(len(self.instanceFastTemp1)):
            if i==0:
                self.instanceFastTemp1[i] = self.assembly.Instance(name=self.couponName+'_Instance_Fast_Temp1_'+str(i+1), part=self.part[3], dependent=ON)
            else:
                self.instanceFastTemp1[i] = self.assembly.Instance(name=self.couponName+'_Instance_Fast_Temp1_'+str(i+1), part=self.part[5], dependent=ON)
        self.mergingFastInstances = (self.instanceFastTemp1[0], self.instanceFastTemp1[1], )
        newFastName = self.couponName+'_Part_'+str(4)
        self.assembly.InstanceFromBooleanMerge(name=newFastName, instances=self.mergingFastInstances, originalInstances=DELETE, domain=GEOMETRY)
        self.part[3] = self.model.parts[newFastName]
        del self.assembly.features[self.couponName+'_Part_'+str(4)+'-1']
        ## create temporary instances for boolean operation on the nut
        self.instanceNutTemp = 2*[None]
        for i in range(len(self.instanceNutTemp)):
            self.instanceNutTemp[i] = self.assembly.Instance(name=self.couponName+'_Instance_Nut_Temp1_'+str(i+1), part=self.part[i+4], dependent=ON)
        self.cuttingNutInstances = (self.instanceNutTemp[1], )
        newNutName = self.couponName+'_Part_'+str(5)
        # self.assembly.InstanceFromBooleanMerge(name=newFastName, instances=self.mergingFastInstances, originalInstances=DELETE, domain=GEOMETRY)
        self.assembly.InstanceFromBooleanCut(name=newNutName, instanceToBeCut=self.instanceNutTemp[0], cuttingInstances=self.cuttingNutInstances, originalInstances=DELETE)
        self.part[4] = self.model.parts[newNutName]
        del self.assembly.features[self.couponName+'_Part_'+str(5)+'-1']
        ## create temporary instances for boolean operation on the plate
        self.instanceTemp = 2*[None]
        for i in range(len(self.instanceTemp)):
            self.instanceTemp[i] = self.assembly.Instance(name=self.couponName+'_Instance_Temp_'+str(i+1), part=self.part[i], dependent=ON)
            self.instanceFastTemp2 = 2*[None]
            for j in range(len(self.instanceFastTemp2)):
                self.instanceFastTemp2[j] = self.assembly.Instance(name=self.couponName+'_Instance_Fast_Temp2_'+str(j+1), part=self.part[5], dependent=ON)
            self.assembly.translate(instanceList=(self.instanceFastTemp2[0].name, ), vector=(-2*self.phi, 0, -self.fastHeadHeight))
            self.assembly.translate(instanceList=(self.instanceFastTemp2[1].name, ), vector=(2*self.phi, 0, -self.fastHeadHeight))
            self.cuttingInstances = (self.instanceFastTemp2[0], self.instanceFastTemp2[1], )
            newPartName = self.couponName+'_Part_'+str(i+1)
            self.assembly.InstanceFromBooleanCut(name=newPartName, instanceToBeCut=self.instanceTemp[i], cuttingInstances=self.cuttingInstances, originalInstances=DELETE)
            self.part[i] = self.model.parts[newPartName]
            del self.assembly.features[self.couponName+'_Part_'+str(i+1)+'-1']
        ## create true instances
        self.instance = 8*[None]
        for i in range(len(self.instance)):
            if i==0 or i==1:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[0], dependent=ON)
            elif i==2:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[1], dependent=ON)
            elif i==3:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[2], dependent=ON)
            elif i==4 or i==5:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[3], dependent=ON)
            elif i==6 or i==7:
                self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[4], dependent=ON)
        ## translation
        self.assembly.translate(instanceList=(self.instance[1].name, ), vector=(0, 0, self.thickness[0]+self.thickness[1]))
        self.assembly.translate(instanceList=(self.instance[2].name, ), vector=(0, 0, self.thickness[0]))
        self.assembly.translate(instanceList=(self.instance[3].name, ), vector=(-self.len1/2.0-self.xD, 0, self.thickness[0]))
        self.assembly.translate(instanceList=(self.instance[4].name, ), vector=(-2*self.phi, 0, -self.fastHeadHeight))
        self.assembly.translate(instanceList=(self.instance[5].name, ), vector=(2*self.phi, 0, -self.fastHeadHeight))
        self.assembly.translate(instanceList=(self.instance[6].name, ), vector=(-2*self.phi, 0, sum(self.thickness)))
        self.assembly.translate(instanceList=(self.instance[7].name, ), vector=(2*self.phi, 0, sum(self.thickness)))
        ## rotation
        self.assembly.rotate(instanceList=(self.instance[0].name, ), axisPoint=(0, 0, 0), axisDirection=(0, 0, 1), angle=180.0)
        self.assembly.rotate(instanceList=(self.instance[1].name, ), axisPoint=(0, 0, 0), axisDirection=(0, 0, 1), angle=180.0)
        del self.model.parts[self.part[5].name]
        self.part.pop(5)
    def createPartition(self):
        def createFacePartition():
            for i in range(2):
                for j in range(2):
                    sketchPlane = self.part[i].faces.findAt(coordinates=((-1)**(j+1)*self.lenTol, 0, 0))
                    sketchUpEdge = self.part[i].edges.findAt(coordinates=(self.xA+j*4*self.phi, self.yA+self.lenTol, 0.0))
                    t = self.part[i].MakeSketchTransform(sketchPlane=sketchPlane, sketchUpEdge=sketchUpEdge, sketchPlaneSide=SIDE1, origin=(0, 0, 0))
                    s1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_'+str(i)+'_'+str(j), sheetSize=50.0, gridSpacing=1.0, transform=t)
                    s1.setPrimaryObject(option=SUPERIMPOSE)
                    self.part[i].projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
                    s1.CircleByCenterPerimeter(center=(2*self.phi-j*4*self.phi, 0), point1=(2*self.phi-j*4*self.phi, self.maxDia/2.0))
                    ## create sketch
                    self.part[i].PartitionFaceBySketch(sketchUpEdge=sketchUpEdge, faces=sketchPlane, sketch=s1)
                    s1.unsetPrimaryObject()
                    ## circular partition
                    edgesTemp1= self.part[i].edges.getByBoundingCylinder((-2*self.phi+j*4*self.phi, 0, -self.lenTol), (-2*self.phi+j*4*self.phi, 0, self.lenTol), (self.maxDia/2.0+self.lenTol))
                    edgesForPartition1 = self.getArcEdge(edgesTemp1)
                    sweepPath1 = self.part[i].edges.findAt(coordinates=(self.xB+j*4*self.phi, self.yB, self.lenTol))
                    self.part[i].PartitionCellBySweepEdge(sweepPath=sweepPath1, cells=self.part[i].cells, edges=(edgesForPartition1[0],))
                    ## diagonal partition
                    pickedCells1 = self.part[i].cells.getByBoundingBox(xMin=self.xA+j*4*self.phi-self.lenTol, xMax=self.xA+j*4*self.phi+4*self.phi+self.lenTol, yMin=-self.yB-self.lenTol, yMax=self.yB+self.lenTol, zMin=-self.lenTol, zMax=self.thickness[i]+self.lenTol)
                    self.part[i].PartitionCellByPlaneThreePoints(point1=self.part[i].vertices.findAt(coordinates=(self.xA+j*4*self.phi, self.yB, 0)), 
                                                                point2=self.part[i].vertices.findAt(coordinates=(self.xA+j*4*self.phi+4*self.phi, -self.yB, 0)), 
                                                                point3=self.part[i].vertices.findAt(coordinates=(self.xA+j*4*self.phi+4*self.phi, -self.yB, self.thickness[i])), 
                                                                cells=pickedCells1)
                    pickedCells2 = self.part[i].cells.getByBoundingBox(xMin=self.xA+j*4*self.phi-self.lenTol, xMax=self.xA+j*4*self.phi+4*self.phi+self.lenTol, yMin=-self.yB-self.lenTol, yMax=self.yB+self.lenTol, zMin=-self.lenTol, zMax=self.thickness[i]+self.lenTol)
                    self.part[i].PartitionCellByPlaneThreePoints(point1=self.part[i].vertices.findAt(coordinates=(self.xA+j*4*self.phi, -self.yB, 0)), 
                                                                point2=self.part[i].vertices.findAt(coordinates=(self.xA+j*4*self.phi+4*self.phi, self.yB, 0)), 
                                                                point3=self.part[i].vertices.findAt(coordinates=(self.xA+j*4*self.phi+4*self.phi, self.yB, self.thickness[i])), 
                                                                cells=pickedCells2)
        def createPartitionOnFast():
            # thisdatumLine = self.part[3].DatumAxisByTwoPoint(point1=self.part[3].InterestingPoint(edge=self.part[3].edges.findAt(coordinates=(0.0, self.phi/2, self.fastLength)), rule=CENTER), 
            #                                                  point2=self.part[3].InterestingPoint(edge=self.part[3].edges.findAt(coordinates=(0.0, self.fastHeadDia/2, 0.0)), rule=CENTER))
            # d = self.part[3].datums
            edgesTemp2= self.part[3].edges.getByBoundingCylinder((0, 0, self.fastHeadHeight-self.lenTol), (0, 0, self.fastHeadHeight+self.lenTol), (self.phi/2.0+self.lenTol))
            # self.part[3].PartitionCellByExtrudeEdge(line=d[3], cells=self.part[3].cells, edges=edgesTemp2, sense=FORWARD)
            edgesForPartition2 = self.getArcEdge(edgesTemp2)
            sweepPath2 = self.part[3].edges.findAt(coordinates=(0, 0, self.lenTol))
            cellsTemp2 = self.part[3].cells.getByBoundingCylinder((0, 0, -self.lenTol), (0, 0, self.fastHeadHeight+self.lenTol), (self.fastHeadDia/2.0+self.lenTol))
            self.part[3].PartitionCellBySweepEdge(sweepPath=sweepPath2, cells=cellsTemp2, edges=(edgesForPartition2[0],edgesForPartition2[1],edgesForPartition2[2],edgesForPartition2[3],)) 
        for i in range(2):
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'YZPLANE', 0)
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'YZPLANE', 4*self.phi)
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'YZPLANE', self.xC)
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'YZPLANE', self.xD)
        createFacePartition()
        for i in range(2):
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'YZPLANE', -2*self.phi)
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'YZPLANE', 2*self.phi)
            self.createPartitionByDatumPlane(self.part[i], self.part[i].cells, 'XZPLANE', 0)
        self.createPartitionByDatumPlane(self.part[3], self.part[3].cells, 'XYPLANE', self.fastHeadHeight)
        self.createPartitionByDatumPlane(self.part[3], self.part[3].cells, 'XZPLANE', 0)
        self.createPartitionByDatumPlane(self.part[3], self.part[3].cells, 'YZPLANE', 0)
        self.createPartitionByDatumPlane(self.part[4], self.part[4].cells, 'XZPLANE', 0)
        self.createPartitionByDatumPlane(self.part[4], self.part[4].cells, 'YZPLANE', 0)
        createPartitionOnFast()
    def createLocalSeed(self):
        ## seed ==>> thickness direction
        edgesThicknessPlate1 = self.part[0].edges.findAt(coordinates=((self.xB, self.yB, self.lenTol), (self.xC, self.yC, self.lenTol), 
                                                                      (self.xD, self.yD, self.lenTol), (self.xE, self.yE, self.lenTol)))
        self.part[0].seedEdgeBySize(edges=edgesThicknessPlate1, size=self.seedSize['Thickness_Plate_1'], deviationFactor=0.1, constraint=FINER)
        edgesThicknessPlate2 = self.part[1].edges.findAt(coordinates=((self.xB, self.yB, self.lenTol), (self.xC, self.yC, self.lenTol), 
                                                                      (self.xD, self.yD, self.lenTol), (self.xE, self.yE, self.lenTol)))
        self.part[0].seedEdgeBySize(edges=edgesThicknessPlate2, size=self.seedSize['Thickness_Plate_2'], deviationFactor=0.1, constraint=FINER)
        edgesThicknessShim = self.part[2].edges.findAt(coordinates=((self.xB, self.yB, self.lenTol), (self.xC, self.yC, self.lenTol), 
                                                                      (self.xD, self.yD, self.lenTol), (self.xE, self.yE, self.lenTol)))
        self.part[0].seedEdgeBySize(edges=edgesThicknessShim, size=self.seedSize['Thickness_Shim'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> vertical direction
        for i in range(2):
            edgesVertical1 = self.part[i].edges.findAt(coordinates=((-4*self.phi, self.lenTol, 0), (-4*self.phi, self.lenTol, self.thickness[i]), 
                                                                    (-4*self.phi, -self.lenTol, 0), (-4*self.phi, -self.lenTol, self.thickness[i]), 
                                                                    (0, self.lenTol, 0), (0, self.lenTol, self.thickness[i]), 
                                                                    (0, -self.lenTol, 0), (0, -self.lenTol, self.thickness[i]), 
                                                                    (4*self.phi, self.lenTol, 0), (4*self.phi, self.lenTol, self.thickness[i]), 
                                                                    (4*self.phi, -self.lenTol, 0), (4*self.phi, -self.lenTol, self.thickness[i]), ))
            self.part[i].seedEdgeBySize(edges=edgesVertical1, size=self.seedSize['Vertical'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges long 1 around area of interest
        for i in range(2):
            edgesLong1 = self.part[i].edges.findAt(coordinates=((-2*self.phi+self.lenTol, self.yB, 0), (-2*self.phi+self.lenTol, self.yB, self.thickness[i]), 
                                                                (-2*self.phi+self.lenTol, -self.yB, 0), (-2*self.phi+self.lenTol, -self.yB, self.thickness[i]), 
                                                                (2*self.phi+self.lenTol, self.yB, 0), (2*self.phi+self.lenTol, self.yB, self.thickness[i]), 
                                                                (2*self.phi+self.lenTol, -self.yB, 0), (2*self.phi+self.lenTol, -self.yB, self.thickness[i]), 
                                                                (-2*self.phi-self.lenTol, self.yB, 0), (-2*self.phi-self.lenTol, self.yB, self.thickness[i]), 
                                                                (-2*self.phi-self.lenTol, -self.yB, 0), (-2*self.phi-self.lenTol, -self.yB, self.thickness[i]), 
                                                                (2*self.phi-self.lenTol, self.yB, 0), (2*self.phi-self.lenTol, self.yB, self.thickness[i]), 
                                                                (2*self.phi-self.lenTol, -self.yB, 0), (2*self.phi-self.lenTol, -self.yB, self.thickness[i]), ))
            self.part[i].seedEdgeBySize(edges=edgesLong1, size=self.seedSize['Long1'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges long 2 bias
        for i in range(2):
            edgesLong2 = self.part[i].edges.findAt(coordinates=((self.xC-self.lenTol, 0, 0), (self.xC-self.lenTol, 0, self.thickness[i]), 
                                                                (self.xC-self.lenTol, self.yC, 0), (self.xC-self.lenTol, self.yC, self.thickness[i]), 
                                                                (self.xC-self.lenTol, -self.yC, 0), (self.xC-self.lenTol, -self.yC, self.thickness[i]), ))
            self.seedEdge(self.part[i], 0, self.xC-4*self.phi, edgesLong2, minSize=self.seedSize['Long1'], maxSize=self.seedSize['Long2'])
        ## seed ==>> long edges long 3 bias
        for i in range(2):
            edgesLong3 = self.part[i].edges.findAt(coordinates=((self.xD+self.lenTol, 0, 0), (self.xD+self.lenTol, 0, self.thickness[i]), 
                                                                (self.xD+self.lenTol, self.yD, 0), (self.xD+self.lenTol, self.yD, self.thickness[i]), 
                                                                (self.xD+self.lenTol, -self.yD, 0), (self.xD+self.lenTol, -self.yD, self.thickness[i]), ))
            self.seedEdge(self.part[i], 0, self.xD, edgesLong3, minSize=self.seedSize['Long2'], maxSize=self.seedSize['Long3'])
        ## seed ==>> long edges fastener and nut
        edgesLongFast = self.part[3].edges.findAt(coordinates=((0, self.phi/2, self.fastHeadHeight+self.lenTol), ))
        self.part[3].seedEdgeBySize(edges=edgesLongFast, size=self.seedSize['LongFast'], deviationFactor=0.1, constraint=FINER)
        edgesLongNut = self.part[4].edges.findAt(coordinates=((0, self.phi/2, self.lenTol), ))
        self.part[4].seedEdgeBySize(edges=edgesLongNut, size=self.seedSize['LongFast'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> diameter fastener
        edgesDiaFast = self.part[3].edges.findAt(coordinates=((0, self.phi/2-self.lenTol, 0), (0, self.phi/2+self.lenTol, 0), 
                                                              (0, -(self.phi/2-self.lenTol), 0), (0, -(self.phi/2+self.lenTol), 0), 
                                                              (self.phi/2-self.lenTol, 0, 0), (self.phi/2+self.lenTol, 0, 0), 
                                                              (-(self.phi/2-self.lenTol), 0, 0), (-(self.phi/2+self.lenTol), 0, 0), ))
        self.part[3].seedEdgeBySize(edges=edgesDiaFast, size=self.seedSize['DiaFast'], deviationFactor=0.1, constraint=FINER)
        edgesDiaNut = self.part[4].edges.findAt(coordinates=((0, self.phi/2+self.lenTol, 0), (0, -(self.phi/2+self.lenTol), 0), 
                                                              (self.phi/2+self.lenTol, 0, 0), (-(self.phi/2+self.lenTol), 0, 0), ))
        self.part[4].seedEdgeBySize(edges=edgesDiaNut, size=self.seedSize['DiaFast'], deviationFactor=0.1, constraint=FINER)
        ## seed ==>> arc diameter
        edgesArcFastTemp= self.part[3].edges.getByBoundingCylinder((0, 0, -self.lenTol), (0, 0, self.lenTol), (self.phi/2.0+self.lenTol))
        edgesArcFast = self.getArcEdge(edgesArcFastTemp)
        self.part[3].seedEdgeBySize(edges=edgesArcFast, size=self.seedSize['ArcFast'], deviationFactor=0.1, constraint=FINER)
        edgesArcNutTemp= self.part[4].edges.getByBoundingCylinder((0, 0, -self.lenTol), (0, 0, self.lenTol), (self.phi/2.0+self.lenTol))
        edgesArcNut = self.getArcEdge(edgesArcNutTemp)
        self.part[4].seedEdgeBySize(edges=edgesArcNut, size=self.seedSize['ArcFast'], deviationFactor=0.1, constraint=FINER)
        # edgesTemp3 = self.part[0].edges.findAt(coordinates=((self.xA-self.lenTol, 0, 0), ))
        # ratioBias = self.part[0].getEdgeSeeds(edgesTemp3[0], attribute=BIAS_RATIO)
        # elemNum = self.part[0].getEdgeSeeds(edgesTemp3[0], attribute=NUMBER)
        # edgesTemp4 = self.part[0].edges.getByBoundingBox(xMin=self.xI-self.lenTol, yMin=self.yI-self.lenTol, zMin=-self.lenTol, xMax=self.xA+self.lenTol, yMax=self.yL+self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesArc2 = self.getArcEdge(edgesTemp4)
        # self.seedEdge(self.part[0], 0, self.xA, edgesArc2, ratio=ratioBias, number=elemNum)
        # ## seed ==>> long edges along CD
        # edgesLong3 = self.part[0].edges.findAt(coordinates=((self.xC+self.lenTol, self.yC, 0), (self.xC+self.lenTol, self.yC, self.thickness), 
        #                                                     (self.xF+self.lenTol, self.yF, 0), (self.xF+self.lenTol, self.yF, self.thickness), 
        #                                                     (self.xC+self.lenTol, self.yO, 0), (self.xC+self.lenTol, self.yO, self.thickness), 
        #                                                     (self.xL-self.lenTol, self.yL, 0), (self.xL-self.lenTol, self.yL, self.thickness), 
        #                                                     (self.xI-self.lenTol, self.yI, 0), (self.xI-self.lenTol, self.yI, self.thickness),
        #                                                     (self.xL-self.lenTol, self.yO, 0), (self.xL-self.lenTol, self.yO, self.thickness), ))
        # self.seedEdge(self.part[0], 0, self.xC, edgesLong3, minSize=self.seedSizeLong3, maxSize=self.seedSizeLong4)
        # self.seedEdge(self.part[0], 0, self.xL, edgesLong3, minSize=self.seedSizeLong3, maxSize=self.seedSizeLong4)
    def createTie(self):
        ## create tie
        region = 2*[None]
        for i in [0,1]:
            surf = self.part[0].faces.getByBoundingBox(xMin=self.xD-self.lenTol, xMax=self.xE+self.lenTol, yMin=-self.yD-self.lenTol,  yMax=self.yD+self.lenTol, zMin=(1-i)*self.thickness[0]-self.lenTol, zMax=(1-i)*self.thickness[0]+self.lenTol)
            surfName = 'Surf_Tie_Part_1_Surf_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[0], surf, surfName)
            region[i] = self.instance[i].surfaces[surfName]
        shimRegion = 2*[None]
        for i in [0,1]:
            surf = self.part[2].faces.getByBoundingBox(xMin=self.xD-self.lenTol, xMax=self.xE+self.lenTol, yMin=-self.yD-self.lenTol,  yMax=self.yD+self.lenTol, zMin=i*self.thickness[1]-self.lenTol, zMax=i*self.thickness[1]+self.lenTol)
            surfName = 'Surf_Tie_Part_3_Surf_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[2], surf, surfName)
            shimRegion[i] = self.instance[3].surfaces[surfName]
        self.model.Tie(name=self.couponName+'_Tie_1', master=shimRegion[0], slave=region[0], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement=SURFACE_TO_SURFACE)
        self.model.Tie(name=self.couponName+'_Tie_2', master=shimRegion[1], slave=region[1], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement=SURFACE_TO_SURFACE)
    def createContact(self):
        ## create contact
        self.isContactEnforced = True
        regionContactSurf = 6*[None]
        contactSurfID = 0
        for i in [0,1]:
            for j in [0,1]:
                ## contact surface ==> plate
                faceCellPlate = self.part[i].faces.getByBoundingBox(xMin=self.xB-self.lenTol, xMax=self.xB+8*self.phi+self.lenTol, yMin=-self.yB-self.lenTol,  yMax=self.yB+self.lenTol, zMin=j*self.thickness[i]-self.lenTol, zMax=j*self.thickness[i]+self.lenTol)
                nameSurfPlate = 'Surf_Contact_Part_'+str(i+1)+'_Surf_'+str(j+1)
                self.getElemSurfFromCellFace(self.part[i], faceCellPlate, nameSurfPlate)
            if i==0:
                for k in [0,1]:
                    regionContactSurf[contactSurfID] = self.instance[k].surfaces[nameSurfPlate]
                    contactSurfID = contactSurfID+1
            elif i==1:
                for k in [0]:
                    regionContactSurf[contactSurfID] = self.instance[k].surfaces[nameSurfPlate]
                    contactSurfID = contactSurfID+1
        self.contactProperty = self.model.ContactProperty(self.couponName+'_Contact_Property')
        self.contactProperty.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact_1', createStepName='Initial', master=regionContactSurf[1], slave=regionContactSurf[4], sliding=SMALL, thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=0.0, datumAxis=None, clearanceRegion=None)
        self.model.SurfaceToSurfaceContactStd(name=self.couponName+'_Contact_2', createStepName='Initial', master=regionContactSurf[2], slave=regionContactSurf[5], sliding=SMALL, thickness=ON, interactionProperty=self.contactProperty.name, adjustMethod=NONE, initialClearance=0.0, datumAxis=None, clearanceRegion=None)
    def createLoadBC(self):
        ## create load and boundary conditions
        self.couponData['Step'].update({'End_Pressure':self.endStress})
        for i in range(len(self.part)):
            if i==0:
                ## create BC at negX face
                nodesNegX = self.part[i].nodes.getByBoundingBox(xMin=self.xJ-self.lenTol, yMin=self.yJ-self.lenTol, zMin=-self.lenTol, xMax=self.xK+self.lenTol, yMax=self.yK+self.lenTol, zMax=self.thickness+self.lenTol)
                nsetNameNegX = 'Nset_BC_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## create BC at negX face at Y=0, Z=0
                nodesNegX_YZ_1 = self.part[i].nodes.getByBoundingSphere((self.xK, self.yK, 0), self.lenTol)
                nodesNegX_YZ_2 = self.part[i].nodes.getByBoundingSphere((self.xK, self.yK, self.thickness), self.lenTol)
                nodesNegX_YZ_3 = self.part[i].nodes.getByBoundingSphere((self.xJ, self.yJ, 0), self.lenTol)
                nodesNegX_YZ_4 = self.part[i].nodes.getByBoundingSphere((self.xJ, self.yJ, self.thickness), self.lenTol)
                nodesNegX_YZ = [nodesNegX_YZ_1, nodesNegX_YZ_2, nodesNegX_YZ_3, nodesNegX_YZ_4]
                nsetNameNegX_YZ = 'Nset_BC_NegX_YZ_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX_YZ , name=nsetNameNegX_YZ)
                region = self.instance[i].sets[nsetNameNegX_YZ]
                self.model.DisplacementBC(name='BC_NegX_YZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
                ## create pressure load on posX face
                endCellFaceArr1 = self.part[i].faces.getByBoundingBox(xMin=self.xE-self.lenTol, yMin=self.yE-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.thickness+self.lenTol)
                surfNamePosX = 'Surf_Load_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr1, surfNamePosX)
                region1 = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region1, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
        
