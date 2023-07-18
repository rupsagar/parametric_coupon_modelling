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
        self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        self.materialName = couponData['material']['name']
        self.density = couponData['material']['density']
        self.youngsModulus = couponData['material']['youngsModulus']
        self.poissonsRatio = couponData['material']['poissonsRatio']
        self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        self.initIncr = couponData['step']['initIncr']
        self.pointLoad = couponData['step']['pointLoad']
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
        # #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        # #######################################################################################################################################################
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
            # self.partitionSketch1.ArcByCenterEnds(center=(0, self.yE), point1=(-self.xD, self.yD-self.yDcirc), point2=(self.xD, self.yD-self.yDcirc), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.ArcByCenterEnds(center=(0, self.yE), point1=(-self.xD, self.yD), point2=(self.xD, self.yD), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.ArcByCenterEnds(center=(0, self.yE), point1=(-(self.xD+self.xE)/2.0, (self.yD+self.yE)/2.0), point2=((self.xD+self.xE)/2.0, (self.yD+self.yE)/2.0), direction=COUNTERCLOCKWISE)
            # self.partitionSketch1.CircleByCenterPerimeter(center=(0, self.yE), point1=(0, self.yE))
            self.partitionSketch1.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge, faces=self.sketchFace, sketch=self.partitionSketch1)
            ## partition solid
            edges1 = self.part[0].edges.getByBoundingCylinder((0, self.yE, self.thickness+self.lenTol), (0, self.yE, self.thickness-self.lenTol), (((((self.xD+self.xE)/2.0)**2+((self.yD+self.yE)/2.0)**2))**0.5+self.lenTol))
            edges1Arc = self.getArcEdge(edges1)
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.part[0].edges.findAt(coordinates=(self.xD, self.yD, self.lenTol)), cells=self.part[0].cells, edges=(edges1Arc[0],))
            edges2 = self.getByCylinderDifference(self.part[0].edges, (0, self.yE, self.thickness+self.lenTol), (0, self.yE, self.thickness-self.lenTol), (((self.xD**2+self.yD**2)**0.5+self.lenTol), (((((self.xD+self.xE)/2.0)**2+((self.yD+self.yE)/2.0)**2))**0.5+self.lenTol)))
            edges2Arc = self.getArcEdge(edges2)
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.part[0].edges.findAt(coordinates=(self.xD, self.yD, self.lenTol)), cells=self.part[0].cells, edges=(edges2Arc[0],))
        def createPartitionLongXZ(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        def createPartitionLongYZ(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        self.yDcirc = self.yD/10
        # createPartitionCyl()
        createPartitionLongXZ(self.yC1)
        # createPartitionLongXZ(self.yE)
        createPartitionLongXZ(self.yB)
        createPartitionLongXZ(self.yC1-abs(self.yC1-self.yB))
        createPartitionLongXZ(self.yE-self.xC1)
        createPartitionLongXZ(self.yD)
        createPartitionLongYZ(self.xO)
        createPartitionLongYZ(self.xC1)
        createPartitionLongYZ(-self.xC1)
        createPartitionLongYZ(self.xD)
        createPartitionLongYZ(-self.xD)
        createPartitionLongYZ((self.xC1+(self.xC1-self.xD)))
        createPartitionLongYZ(-(self.xC1+(self.xC1-self.xD)))
        self.part[0].PartitionCellByExtendFace(extendFace=self.part[0].faces.findAt(coordinates=((self.xA+self.xB)/2.0, (self.yA+self.yB)/2.0, self.lenTol)), cells=self.part[0].cells.findAt(((self.xC, self.yC, 0), )))
        self.part[0].PartitionCellByExtendFace(extendFace=self.part[0].faces.findAt(coordinates=(-(self.xA+self.xB)/2.0, (self.yA+self.yB)/2.0, self.lenTol)), cells=self.part[0].cells.findAt(((-self.xC, self.yC, 0), )))
    def createMesh(self):
        ## edges thickness
        edgesThickness = self.part[0].edges.findAt(coordinates=((self.xE, self.yE, self.lenTol), ))
        self.part[0].seedEdgeBySize(edges=edgesThickness, size=self.seedSizeThickness, deviationFactor=0.1, constraint=FINER)
        ## edges long 1
        edgesLong1 = self.part[0].edges.findAt(coordinates=((self.xE, self.yE-self.lenTol, 0), (self.xE, self.yE-self.lenTol, self.thickness)))
        self.seedEdge(self.part[0], 1, self.yE, edgesLong1, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## edges long 2
        edgesLong2Temp1 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yE-self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp2 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yE-self.xC1-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yE-self.xC1+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp3 = self.part[0].edges.getByBoundingBox(xMin=-(self.xF+self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.yG+self.lenTol, zMax=self.thickness+self.lenTol)
        edgesLong2Temp4 = self.getByDifference(edgesLong2Temp1, edgesLong2Temp2)
        edgesLong2 = self.getByDifference(edgesLong2Temp4, edgesLong2Temp3)
        self.seedEdge(self.part[0], 1, (self.yE-self.xC1), edgesLong2, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## edges long 3
        # edgesLong3Temp1 = self.part[0].edges.getByBoundingBox(xMin=(self.xC1+(self.xC1-self.xD)-self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xF+self.lenTol), yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesLong3Temp2 = self.part[0].edges.getByBoundingBox(xMin=(self.xC1+(self.xC1-self.xD)-self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xC1+(self.xC1-self.xD)+self.lenTol), yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesLong3Temp3 = self.part[0].edges.getByBoundingBox(xMin=(self.xF-self.lenTol), yMin=self.yG-self.lenTol, zMin=-self.lenTol, xMax=(self.xC1+(self.xC1-self.xD)+self.lenTol), yMax=self.lenTol, zMax=self.thickness+self.lenTol)
        # edgesLong3Temp4 = self.getByDifference(edgesLong3Temp1, edgesLong3Temp2)
        # edgesLong3 = self.getByDifference(edgesLong3Temp4, edgesLong3Temp3)
        # self.seedEdge(self.part[0], 0, self.xC1+(self.xC1-self.xD), edgesLong3, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
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
        self.couponData['step'].update({'pointLoad':self.pointLoad})
        ## nset => reference point
        self.assembly.ReferencePoint(point=(self.xC1, self.yC1, self.thickness/2.0))
        self.assembly.Set(referencePoints=(self.assembly.referencePoints.findAt((self.xC1, self.yC1, self.thickness/2.0)),), name='Nset_Coupling_1')
        self.assembly.ReferencePoint(point=(-self.xC1, self.yC1, self.thickness/2.0))
        self.assembly.Set(referencePoints=(self.assembly.referencePoints.findAt((-self.xC1, self.yC1, self.thickness/2.0)),), name='Nset_Coupling_2')
        ## surface
        cylCellFaceArr1 = self.part[0].faces.getByBoundingCylinder((self.xC1+self.lenTol, self.yC1, -self.lenTol), (self.xC1+self.lenTol, self.yC1, self.thickness+self.lenTol), (self.diameter/2.0))
        self.getElemSurfFromCellFace(self.part[0], cylCellFaceArr1, 'Surf_Load_Cyl_1')
        cylCellFaceArr2 = self.part[0].faces.getByBoundingCylinder((-(self.xC1+self.lenTol), self.yC1, -self.lenTol), (-(self.xC1+self.lenTol), self.yC1, self.thickness+self.lenTol), (self.diameter/2.0))
        self.getElemSurfFromCellFace(self.part[0], cylCellFaceArr2, 'Surf_Load_Cyl_2')
        ## nset => load/BC
        nodesCyl1 = self.part[0].nodes.getByBoundingCylinder((self.xC1+self.lenTol, self.yC1, -self.lenTol), (self.xC1+self.lenTol, self.yC1, self.thickness+self.lenTol), (self.diameter/2.0))
        self.part[0].Set(nodes=nodesCyl1, name='Nset_Cyl_1')
        nodesCyl2 = self.part[0].nodes.getByBoundingCylinder((-(self.xC1+self.lenTol), self.yC1, -self.lenTol), (-(self.xC1+self.lenTol), self.yC1, self.thickness+self.lenTol), (self.diameter/2.0))
        self.part[0].Set(nodes=nodesCyl2, name='Nset_Cyl_2')
        nodesNegY_X_1 = self.part[0].nodes.getByBoundingSphere((self.xG, self.yG, 0), self.lenTol)
        nodesNegY_X_2 = self.part[0].nodes.getByBoundingSphere((-self.xG, self.yG, 0), self.lenTol)
        nodesNegY_X_3 = self.part[0].nodes.getByBoundingSphere((self.xG, self.yG, self.thickness), self.lenTol)
        nodesNegY_X_4 = self.part[0].nodes.getByBoundingSphere((-self.xG, self.yG, self.thickness), self.lenTol)
        nodesNegY_X = [nodesNegY_X_1, nodesNegY_X_2, nodesNegY_X_3, nodesNegY_X_4]
        # nodesNegY_X = self.part[0].nodes.getByBoundingBox(xMin=-self.xG-self.lenTol, yMin=self.yH-self.lenTol, zMin=-self.lenTol, xMax=self.xG+self.lenTol, yMax=self.yH+self.lenTol, zMax=self.thickness+self.lenTol)
        self.part[0].Set(nodes=nodesNegY_X , name='Nset_BC_NegY_X')
        ## coupling
        # self.model.Coupling(name='Constraint_Coupling_1', controlPoint=self.assembly.sets['Nset_Coupling_1'], surface=self.instance[0].sets['Nset_Cyl_1'], influenceRadius=WHOLE_SURFACE, couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
        self.model.Coupling(name='Constraint_Coupling_2', controlPoint=self.assembly.sets['Nset_Coupling_2'], surface=self.instance[0].sets['Nset_Cyl_2'], influenceRadius=WHOLE_SURFACE, couplingType=DISTRIBUTING, weightingMethod=UNIFORM, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
        ## create BC
        # self.model.DisplacementBC(name='BC_Coupling_1', createStepName='Load', region=self.assembly.sets['Nset_Coupling_1'], u1=UNSET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET, amplitude=SET, distributionType=UNIFORM, fieldName='', localCsys=None)
        self.model.DisplacementBC(name='BC_Coupling_2', createStepName='Load', region=self.assembly.sets['Nset_Coupling_2'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET, amplitude=SET, distributionType=UNIFORM, fieldName='', localCsys=None)
        # self.model.DisplacementBC(name='BC_NegY_X', createStepName='Load', region=self.instance[0].sets['Nset_BC_NegY_X'], u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create load
        # self.model.ConcentratedForce(name='Point_Load_1', createStepName='Load', region=self.assembly.sets['Nset_Coupling_1'], cf1=self.pointLoad, distributionType=UNIFORM, field='', localCsys=None)
        # self.model.ConcentratedForce(name='Point_Load_2', createStepName='Load', region=self.assembly.sets['Nset_Coupling_2'], cf1=-self.pointLoad, distributionType=UNIFORM, field='', localCsys=None)
        self.model.SurfaceTraction(name='Pressure_Load', createStepName='Load', region=self.instance[0].surfaces['Surf_Load_Cyl_1'], magnitude=250.0, directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), distributionType=UNIFORM, field='', localCsys=None, traction=GENERAL)
        
