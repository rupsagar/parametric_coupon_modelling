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
        self.createAssembly()
        self.createPartition()
        self.createMesh()
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
        self.profileSketch[0].AngularDimension(line1=self.profileGeometry1[3], line2=self.profileGeometry1[9], textPoint=(self.lenTol, (self.yD+self.yE)/2.0), value=self.notchTipAngle/2.0)
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
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[7], entity2=self.profileGeometry1[3])
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileGeometry1[2], textPoint=(-(self.xG+self.xC1)/2.0, self.yG), value=self.width)
        ## circle
        self.profileSketch[0].CircleByCenterPerimeter(center=(self.xC1, self.yC1), point1=(self.xC1, self.yC1-self.diameter/2.0))
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[12], entity2=self.profileVertices1[8], textPoint=(self.xC1, self.yC1/2.0), value=self.centerOffset1)
        self.profileSketch[0].DistanceDimension(entity1=self.profileGeometry1[3], entity2=self.profileVertices1[8], textPoint=(self.xC1/2.0, self.yC1), value=self.centerOffset2/2.0)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[13], textPoint=(self.xC1+self.diameter, self.yC1), radius=self.diameter/2.0)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[4], vertex2=self.profileVertices1[8], textPoint=(-self.xC1, (self.yE-self.yC1)/2.0), value=self.notchOffset)
        ## copy and mirror
        self.profileSketch[0].copyMirror(mirrorLine=self.profileGeometry1[3], objectList=(self.profileGeometry1[6], self.profileGeometry1[7], self.profileGeometry1[8], self.profileGeometry1[9], 
                                                                    self.profileGeometry1[10], self.profileGeometry1[11], self.profileGeometry1[12], self.profileGeometry1[13]))
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
        def createPartitionCyl():
            ## partition face
            self.sketchFace = self.part[0].faces.findAt(coordinates=(self.xA+self.lenTol, self.yA-self.lenTol, self.thickness))
            self.sketchEdge = self.part[0].edges.findAt(coordinates=(self.xF, self.yF-self.lenTol, self.thickness))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace, sketchUpEdge=self.sketchEdge, sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=200, transform=self.transform)
            self.partitionSketch1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch1, filter=COPLANAR_EDGES)
            # self.partitionSketch1.ArcByCenterEnds(center=(0, self.yC2), point1=(-self.xD, self.yD-self.yDcirc), point2=(self.xD, self.yD-self.yDcirc), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.ArcByCenterEnds(center=(0, self.yC2), point1=(-self.xD, self.yD), point2=(self.xD, self.yD), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.ArcByCenterEnds(center=(0, self.yC2), point1=(-(self.xD+self.xE)/2.0, (self.yD+self.yE)/2.0), point2=((self.xD+self.xE)/2.0, (self.yD+self.yE)/2.0), direction=COUNTERCLOCKWISE)
            # self.partitionSketch1.CircleByCenterPerimeter(center=(0, self.yC2), point1=(0, self.yE))
            self.partitionSketch1.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge, faces=self.sketchFace, sketch=self.partitionSketch1)
            ## partition solid
            edges1 = self.part[0].edges.getByBoundingCylinder((0, self.yC2, self.thickness+self.lenTol), (0, self.yC2, self.thickness-self.lenTol), ((self.xD**2+(self.yD-self.yDcirc-self.yC2)**2)**0.5+self.lenTol))
            edges2 = self.getArcEdge(edges1)
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.part[0].edges.findAt(coordinates=(self.xE, self.yE, self.lenTol)), cells=self.part[0].cells, edges=edges2)
        def createPartitionLongXZ(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        def createPartitionLongYZ(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        self.yC2 = self.yE
        self.yDcirc = self.yD/10
        createPartitionCyl()
        createPartitionLongXZ(self.yC1)
        createPartitionLongXZ(self.yC2)
        createPartitionLongXZ(self.yB)
        createPartitionLongXZ((self.yC1-self.diameter/2.0+self.yD)/2.0)
        createPartitionLongXZ(self.yC2-self.xC1)
        createPartitionLongYZ(self.xO)
        createPartitionLongYZ(self.xC1)
        createPartitionLongYZ(-self.xC1)
        createPartitionLongYZ((self.xC1+(self.xC1-self.xD)))
        createPartitionLongYZ(-(self.xC1+(self.xC1-self.xD)))
        self.part[0].PartitionCellByExtendFace(extendFace=self.part[0].faces.findAt(coordinates=((self.xA+self.xB)/2.0, (self.yA+self.yB)/2.0, self.lenTol)), cells=self.part[0].cells.findAt(((self.xC, self.yC, 0), )))
        self.part[0].PartitionCellByExtendFace(extendFace=self.part[0].faces.findAt(coordinates=(-(self.xA+self.xB)/2.0, (self.yA+self.yB)/2.0, self.lenTol)), cells=self.part[0].cells.findAt(((-self.xC, self.yC, 0), )))
    def createMesh(self):
        cellsInnerCyl = self.part[0].cells.getByBoundingCylinder((0, self.yC2, self.thickness+self.lenTol), (0, self.yC2, -self.lenTol), ((self.xD**2+(self.yD-self.yDcirc-self.yC2)**2)**0.5+self.lenTol))
        self.part[0].setMeshControls(regions=cellsInnerCyl, elemShape=HEX_DOMINATED, technique=SWEEP, algorithm=ADVANCING_FRONT)
        ## generate mesh
        # self.couponData.update({'elemNum':dict()})
        # for i in range(len(self.part)):
        #     self.part[i].generateMesh()
        #     self.couponData['elemNum'].update({'part'+str(i+1):len(self.part[i].elements)})
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
                
