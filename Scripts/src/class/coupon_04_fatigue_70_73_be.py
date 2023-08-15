#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
#####################    CLASS DEFINITION : FATIGUE COUPON : SPECIMEN 70 TO 73, B TO E    #######################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Mar-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


import math
from abaqus import *
from abaqusConstants import *
from caeModules import *

class coupon_04_fatigue_70_73_be(coupon_generic):
    def __init__(self, couponData):
        super(coupon_04_fatigue_70_73_be, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.h1 = couponData['geometry']['h1']
        self.h2 = couponData['geometry']['h2']
        self.h3 = couponData['geometry']['h3']
        self.rad1 = couponData['geometry']['rad1']
        self.rad2 = couponData['geometry']['rad2']
        self.len1 = couponData['geometry']['len1']
        self.len2 = couponData['geometry']['len2']
        self.thetaDeg = couponData['geometry']['thetaDeg']
        self.thickness = couponData['thickness']
        self.lenTol = couponData['lenTol']
        self.partitionVerticalFraction = couponData['partitionVerticalFraction']
        self.seedSizeThickness1 = couponData['elemSize']['thickness1']
        self.seedSizeThickness2 = couponData['elemSize']['thickness2']
        self.seedSizeVerticalOuter = couponData['elemSize']['verticalOuter']
        self.seedSizeVerticalMiddle = couponData['elemSize']['verticalMiddle']
        self.seedSizeVerticalInner = couponData['elemSize']['verticalInner']
        self.seedSizeVertical2 = couponData['elemSize']['vertical2']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.seedSizeLong3 = couponData['elemSize']['long3']
        self.seedSizeLong4 = couponData['elemSize']['long4']
        self.elemTypeHexPart1 = SymbolicConstant(couponData['elemType']['hexPart1'])
        self.elemTypeHexPart2 = SymbolicConstant(couponData['elemType']['hexPart2'])
        self.materialName = couponData['material']['name']
        self.density = couponData['material']['density']
        self.youngsModulus = couponData['material']['youngsModulus']
        self.poissonsRatio = couponData['material']['poissonsRatio']
        self.nlGeom = SymbolicConstant(couponData['step']['nlGeom'])
        self.initIncr = couponData['step']['initIncr']
        self.nominalStress = couponData['step']['nominalStress']
        self.version = couponData['version']
        ## derived quantities
        self.alphaDeg = 90.0-self.thetaDeg/2.0
        self.alphaRad = math.pi/180*self.alphaDeg
        self.partitionVertical = self.partitionVerticalFraction*self.h1/2
        self.endStress = -self.nominalStress*self.h1/self.h3
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        self.createPartition()
        self.createMesh()
        self.createMaterial()
        self.createSection()
        self.createTie()
        self.createStep()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        (self.xo, self.yo) = (self.xO, self.yO) = (0.0, 0.0)
        (self.xa, self.ya) = (self.xA, self.yA) = (0.0, self.h1/2.0)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (0.0, (self.yA+self.rad1))
        (self.xb, self.yb) = (self.xB, self.yB) = (self.rad1*math.sin(self.alphaRad), (self.yA+self.rad1*(1.0-math.cos(self.alphaRad))))
        (self.xc, self.yc) = (self.xC, self.yC) = (self.xB+(self.h2/2.0-self.yB)/math.tan(self.alphaRad), self.h2/2.0)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.len1/2.0-self.len2, self.h3/2.0)
        (self.xd, self.yd) = (self.xD, self.yD) = (self.xE-self.rad2*math.sin(math.acos((self.rad2-(self.yE-self.yC))/self.rad2)), self.yC)
        (self.xc2, self.yc2) = (self.xC2, self.yC2) = (self.xD, self.yD+self.rad2)
        (self.xf, self.yf) = (self.xF, self.yF) = (self.len1/2.0, self.yE)
        (self.xg, self.yg) = (self.xG, self.yG) = (self.xF, 0.0)
        (self.xh, self.yh) = (self.xH, self.yH) = (self.xD, 0.0)
        #################################################################################################################################################
        self.profileSketch = 2*[None]
        ## define sketch ==>> part 1 ==>> area of interest  #############################################################################################
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_1', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)        
        ## horizontal fixed construction line
        self.profileSketch[0].ConstructionLine(point1=(-50.0, 0.0), angle=0.0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[2])
        ## vertical fixed construction line
        self.profileSketch[0].ConstructionLine(point1=(0.0, -25.0), angle=90.0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[3])
        ## inclined fixed construction line
        self.profileSketch[0].ConstructionLine(point1=(0.0, 0.0), angle=self.alphaDeg)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[4])
        ## line OA
        self.profileSketch[0].Line(point1=(self.xO, self.yO), point2=(self.xA, self.yA))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].ObliqueDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[0], textPoint=(-3.0, 0.0), value=self.h1/2.0)
        ## arc AB
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[1].coords, point2=(self.xB, self.yB), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=(0.0, 5.0), radius=self.rad1)
        ## line BC
        self.profileSketch[0].Line(point1=self.profileVertices1[2].coords, point2=(self.xC, self.yC))
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[6], entity2=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[4], entity2=self.profileGeometry1[2], textPoint=(-5.0, 8.0), value=self.h2/2.0)
        self.profileSketch[0].ParallelConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[7])
        ## line CD
        self.profileSketch[0].Line(point1=self.profileVertices1[4].coords, point2=(self.xD, self.yD))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        ## line DH
        self.profileSketch[0].Line(point1=self.profileVertices1[5].coords, point2=(self.xH, self.yH))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], addUndoState=False)
        ## line HO
        self.profileSketch[0].Line(point1=self.profileVertices1[6].coords, point2=self.profileVertices1[0].coords)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[10], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[6], textPoint=(6.0, -5.0), value=self.xD)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xO, self.yO) = self.profileVertices1[0].coords
        (self.xA, self.yA) = self.profileVertices1[1].coords
        (self.xB, self.yB) = self.profileVertices1[2].coords
        (self.xC1, self.yC1) = self.profileVertices1[3].coords
        (self.xC, self.yC) = self.profileVertices1[4].coords
        (self.xD, self.yD) = self.profileVertices1[5].coords
        (self.xH, self.yH) = self.profileVertices1[6].coords
        #######################################################################################################################################################
        ## define sketch ==>> part 2 ==>> away from the area of interest for tet meshing    ###################################################################
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileGeometry2, self.profileVertices2 = self.profileSketch[1].geometry, self.profileSketch[1].vertices
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)        
        ## horizontal fixed construction line
        self.profileSketch[1].ConstructionLine(point1=(-50.0, 0.0), angle=0.0)
        self.profileSketch[1].FixedConstraint(entity=self.profileGeometry2[2])
        ## vertical fixed construction line
        self.profileSketch[1].ConstructionLine(point1=(self.xH, 0.0), angle=90.0)
        self.profileSketch[1].FixedConstraint(entity=self.profileGeometry2[3])
        ## line HD
        self.profileSketch[1].Line(point1=(self.xH, self.yH), point2=(self.xD, self.yD))
        self.profileSketch[1].VerticalConstraint(entity=self.profileGeometry2[4], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[0], entity2=self.profileGeometry2[2], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[1], entity2=self.profileGeometry2[3], addUndoState=False)
        self.profileSketch[1].ObliqueDimension(vertex1=self.profileVertices2[1], vertex2=self.profileVertices2[0], textPoint=(3.0, 0.0), value=self.h2/2.0)
        ## arc DE
        self.profileSketch[1].ArcByCenterEnds(center=(self.xC2, self.yC2), point1=self.profileVertices2[1].coords, point2=(self.xE, self.yE), direction=COUNTERCLOCKWISE)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[5], entity2=self.profileGeometry2[4], addUndoState=False)
        self.profileSketch[1].RadialDimension(curve=self.profileGeometry2[5], textPoint=(12.0, 12.0), radius=self.rad2)
        self.profileSketch[1].VerticalDimension(vertex1=self.profileVertices2[0], vertex2=self.profileVertices2[2], textPoint=(10.0, 25.0), value=self.h3/2.0)
        ## line EF
        self.profileSketch[1].Line(point1=self.profileVertices2[2].coords, point2=(self.xF, self.yF))
        self.profileSketch[1].HorizontalConstraint(entity=self.profileGeometry2[6], addUndoState=False)
        self.profileSketch[1].HorizontalDimension(vertex1=self.profileVertices2[2], vertex2=self.profileVertices2[4], textPoint=(6.0, 5.0), value=self.len2)
        ## line FG
        self.profileSketch[1].Line(point1=self.profileVertices2[4].coords, point2=(self.xG, self.yG))
        self.profileSketch[1].VerticalConstraint(entity=self.profileGeometry2[7], addUndoState=False)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[7], entity2=self.profileGeometry2[6], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[5], entity2=self.profileGeometry2[2], addUndoState=False)
        ## line GH
        self.profileSketch[1].Line(point1=self.profileVertices2[5].coords, point2=self.profileVertices2[0].coords)
        self.profileSketch[1].HorizontalConstraint(entity=self.profileGeometry2[8], addUndoState=False)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[8], entity2=self.profileGeometry2[7], addUndoState=False)
        ###############################################################################################################################################################
        self.profileSketch[1].unsetPrimaryObject()
        ###############################################################################################################################################################
        (self.xE, self.yE) = self.profileVertices2[2].coords
        (self.xC2, self.yC2) = self.profileVertices2[3].coords
        (self.xF, self.yF) = self.profileVertices2[4].coords
        (self.xG, self.yG) = self.profileVertices2[5].coords
        ###############################################################################################################################################################
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
                     ['C2', self.xc2, self.yc2, self.xC2, self.yC2],
                     ['h1', '', self.h1, '', 2*(self.yA-self.yO)],
                     ['h2', '', self.h2, '', 2*(self.yC-self.yO)],
                     ['h3', '', self.h3, '', 2*(self.yE-self.yO)],
                     ['rad1', '', self.rad1, '', ((self.xC1-self.xB)**2+(self.yC1-self.yB)**2)**0.5],
                     ['rad2', '', self.rad2, '', ((self.xC2-self.xE)**2+(self.yC2-self.yE)**2)**0.5],
                     ['len1', '', self.len1, '', 2*(self.xF-self.xO)],
                     ['len2', '', self.len2, '', (self.xF-self.xE)]]
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
        def createPartitionOffset(xRight):
            ## partition face ==>> outer cylinder
            sketchPlane = self.part[0].faces.findAt(((self.lenTol, self.partitionVertical, self.thickness),))
            sketchUpEdge = self.part[0].edges.findAt(((xRight, self.partitionVertical, self.thickness),))
            transform = self.part[0].MakeSketchTransform(sketchPlane=sketchPlane[0], sketchUpEdge=sketchUpEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=50.0, gridSpacing=1.0, transform=transform)
            g, v = self.partitionSketch1.geometry, self.partitionSketch1.vertices
            self.partitionSketch1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch1, filter=COPLANAR_EDGES)
            newGeometryID = len(g)+2
            newVertexID = len(v)
            ## arc
            self.partitionSketch1.ArcByCenterEnds(center=(self.xC1, self.yC1), point1=(self.xA, self.yA-self.yOffset), point2=(self.xB, self.yB-self.yOffset), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.CoincidentConstraint(entity1=g.findAt((self.xA, self.yOffset),1), entity2=v[newVertexID])
            self.partitionSketch1.HorizontalDimension(vertex1=v[newVertexID], vertex2=v[newVertexID+1], textPoint=(0.5, 0.5), value=self.xB)
            self.partitionSketch1.ObliqueDimension(vertex1=v[newVertexID], vertex2=v.findAt((self.xA,self.yA),1), textPoint=(2.5, 0.0), value=self.yOffset)
            ## line
            self.partitionSketch1.Line(point1=v[newVertexID+1].coords, point2=(self.xC, self.yC-self.yOffset))
            self.partitionSketch1.TangentConstraint(entity1=g[newGeometryID], entity2=g[newGeometryID+1], addUndoState=False)
            self.partitionSketch1.HorizontalDimension(vertex1=v[newVertexID+1], vertex2=v[newVertexID+2], textPoint=(0.5, 0.5), value=self.xC-self.xB)
            ## line
            self.partitionSketch1.Line(point1=v[newVertexID+2].coords, point2=(self.xD, self.yD-self.yOffset))
            self.partitionSketch1.ParallelConstraint(entity1=g.findAt(((self.xC+self.xD)/2,self.yC),1), entity2=g[newGeometryID+2])
            self.partitionSketch1.CoincidentConstraint(entity1=g.findAt((self.xD,self.yOffset),1), entity2=v[newVertexID+3])
            self.partitionSketch1.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=sketchUpEdge[0], faces=sketchPlane[0], sketch=self.partitionSketch1)
            ## partition solid ==>> sweep
            sweepPath1 = self.part[0].edges.findAt(((0, 0, self.thickness/2.0),))
            edgesTemp = self.part[0].edges
            edgesForPartition =(edgesTemp[0], edgesTemp[1], edgesTemp[2]) ## hard-coded ==>> directly taken from macro; no easy logic to find coordinate
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath1[0], cells=self.part[0].cells, edges=edgesForPartition)
        def createPartitionThickness():
            ## partition face ==>> inner cylinder
            self.sketchFace = self.part[0].faces.findAt(((0, self.partitionVertical, self.thickness/2.0),))
            self.sketchEdge = self.part[0].edges.findAt(((0, self.partitionVertical, self.thickness),))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch2 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_2', sheetSize=4, transform=self.transform)
            g, v = self.partitionSketch2.geometry, self.partitionSketch2.vertices
            self.partitionSketch2.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch2, filter=COPLANAR_EDGES)
            self.partitionSketch2.Line(point1=(0, self.partitionVertical), point2=(self.thickness, self.partitionVertical))
            self.projectionLine1 = g.findAt((0, self.partitionVertical/2), 1)
            self.projectionLine2 = g.findAt((self.thickness, self.partitionVertical/2.0), 1)
            self.vertexPoint1 = v.findAt((0, self.partitionVertical), 1)
            self.vertexPoint2 = v.findAt((self.thickness, self.partitionVertical), 1)
            self.partitionSketch2.CoincidentConstraint(entity1=self.vertexPoint1, entity2=self.projectionLine1, addUndoState=False)
            self.partitionSketch2.CoincidentConstraint(entity1=self.vertexPoint2, entity2=self.projectionLine2, addUndoState=False)
            self.partitionSketch2.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge[0], faces=self.sketchFace[0], sketch=self.partitionSketch2)
            ## partition solid ==>> sweep
            sweepPath2 = self.part[0].edges.findAt(((self.xO+self.lenTol, 0, 0),))
            edgeForPartition = (self.part[0].edges.findAt(coordinates=(0, self.partitionVertical, self.thickness/2)), )
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath2[0], cells=self.part[0].cells, edges=edgeForPartition)
        def createPartitionLong(thisPart, offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = thisPart.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            thisPart.PartitionCellByDatumPlane(datumPlane=thisPart.datums[self.datumPlane_ID], cells=thisPart.cells)
        self.yOffset = (self.h1/2-self.partitionVertical)/2
        createPartitionOffset(self.xD)
        createPartitionThickness()
        createPartitionLong(self.part[0], self.xB)
        createPartitionLong(self.part[0], self.xC)
        createPartitionLong(self.part[1], self.xE)
    def createMesh(self):
        edgesThickness1 = self.part[0].edges.findAt(((0, 0, self.lenTol),))
        self.part[0].seedEdgeBySize(edges=edgesThickness1, size=self.seedSizeThickness1, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer vertical edge
        edgesVerticalOuter = self.part[0].edges.findAt(((0, self.yA-self.yOffset+self.lenTol, self.thickness),))
        self.part[0].seedEdgeBySize(edges=edgesVerticalOuter, size=self.seedSizeVerticalOuter, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> middle vertical edge
        edgesVerticalMiddle = self.part[0].edges.findAt(((0, self.partitionVertical+self.lenTol, self.thickness),))
        self.part[0].seedEdgeBySize(edges=edgesVerticalMiddle, size=self.seedSizeVerticalMiddle, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> inner vertical edge
        edgesVerticalInner = self.part[0].edges.findAt(((0, self.lenTol, self.thickness),))
        self.part[0].seedEdgeBySize(edges=edgesVerticalInner, size=self.seedSizeVerticalInner, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along AB
        edgesLongAB = self.part[0].edges.findAt(((self.lenTol, 0, self.thickness),))
        self.part[0].seedEdgeBySize(edges=edgesLongAB, size=self.seedSizeLong1, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along BC
        edgesLongBC = self.part[0].edges.findAt(((self.xB+self.lenTol, 0, self.thickness),))
        self.part[0].seedEdgeBySize(edges=edgesLongBC, size=self.seedSizeLong1, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along CD
        pickedEdges1 = self.part[0].edges
        edgesLongCD = self.getEdgeByLength(pickedEdges1, abs(self.xD-self.xC))
        self.seedEdge(self.part[0], 0, self.xC, edgesLongCD, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> arc along DE
        pickedEdges2 = self.part[1].edges
        edgesArcDE = self.getArcEdge(pickedEdges2)
        self.seedEdge(self.part[1], 0, self.xD, edgesArcDE, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        # ## seed ==>> long edge along DE
        edgesLongDE = self.getEdgeByLength(pickedEdges2, abs(self.xE-self.xD))
        biasRatio = self.part[1].getEdgeSeeds(edgesArcDE[0], attribute=BIAS_RATIO)
        elemNum = self.part[1].getEdgeSeeds(edgesArcDE[0], attribute=NUMBER)
        self.seedEdge(self.part[1], 0, self.xD, edgesLongDE, ratio=biasRatio, number=elemNum)
        ## seed ==>> long edges along EF
        edgesLong3 = self.getEdgeByLength(pickedEdges2, abs(self.xF-self.xE))
        self.seedEdge(self.part[1], 0, self.xE, edgesLong3, minSize=self.seedSizeLong3, maxSize=self.seedSizeLong4)
        ## seed ==>> thickness 2
        edgesThickness2 = self.part[1].edges.findAt(coordinates=((self.xD, 0, self.lenTol), ))
        self.part[1].seedEdgeBySize(edges=edgesThickness2, size=self.seedSizeThickness2, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> vertical edge part 2
        edgesVerticalPart2 = self.part[1].edges.findAt(coordinates=((self.xD, self.lenTol, 0), ))
        self.part[1].seedEdgeBySize(edges=edgesVerticalPart2, size=self.seedSizeVertical2, deviationFactor=0.1, constraint=FINER)
        ## set element types
        elemTypeHex1 = mesh.ElemType(elemCode=self.elemTypeHexPart1, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemTypeHex1,))
        elemTypeHex2 = mesh.ElemType(elemCode=self.elemTypeHexPart2, elemLibrary=STANDARD)
        self.part[1].setElementType(regions=(self.part[1].cells,), elemTypes=(elemTypeHex2,))
        ## generate mesh
        self.couponData.update({'elemNum':dict()})
        for i in range(len(self.part)):
            self.part[i].generateMesh()
            self.couponData['elemNum'].update({'part'+str(i+1):len(self.part[i].elements)})
    def createTie(self):
        region = len(self.part)*[None]
        for i in range(len(self.part)):
            surf = self.part[i].faces.getByBoundingBox(xMin=self.xD-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yD+self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
            surfName = 'Surf_Tie_Part_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[i], surf, surfName)
            region[i] = self.instance[i].surfaces[surfName]
        self.model.Tie(name=self.couponName+'_Tie', master=region[1], slave=region[0], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement = SURFACE_TO_SURFACE)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF'))
        self.couponData['step'].update({'endPressure':self.endStress})
        for i in range(len(self.part)):
            ## create BC at negY face
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xF+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
            nsetNameNegY = 'Nset_BC_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at negZ face
            nodesNegZ = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xF+self.lenTol, yMax=self.yF+self.lenTol, zMax=self.lenTol)
            nsetNameNegZ = 'Nset_BC_NegZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegZ, name=nsetNameNegZ)
            region = self.instance[i].sets[nsetNameNegZ]
            self.model.DisplacementBC(name='BC_NegZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==0:
                ## create BC at negX face of Part 1
                nodesNegX = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xA+self.lenTol, yMax=self.yA+self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
                nsetNameNegX = 'Nset_BC_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==(len(self.part)-1):
                ## create pressure load on posX face
                endCellFaceArr = self.part[i].faces.getByBoundingBox(xMin=self.xF-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xF+self.lenTol, yMax=self.yF+self.lenTol, zMax=self.thickness+self.lenTol)
                surfNamePosX = 'Surf_Load_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)

