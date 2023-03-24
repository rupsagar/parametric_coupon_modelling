#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
#####################    CLASS DEFINITION : FATIGUE COUPON : SPECIMEN 66 TO 69, B TO J    #######################
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

class fatigue_coupon_66_69_bj(coupon_generic):
    def __init__(self, couponData):
        super(fatigue_coupon_66_69_bj, self).__init__()
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.phi1 = couponData['geometry']['phi1']
        self.phi2 = couponData['geometry']['phi2']
        self.phi3 = couponData['geometry']['phi3']
        self.rad1 = couponData['geometry']['rad1']
        self.rad2 = couponData['geometry']['rad2']
        self.len1 = couponData['geometry']['len1']
        self.len2 = couponData['geometry']['len2']
        self.thetaDeg = couponData['geometry']['thetaDeg']
        self.givenKt = couponData['givenKt']
        self.lenTol = couponData['lenTol']
        self.partitionRadialFraction = couponData['partitionRadialFraction']
        self.seedSizePart2 = couponData['elemSize']['part2']
        self.seedSizeArcOuter = couponData['elemSize']['arcOuter']
        self.seedRadialOuter = couponData['elemSize']['radialOuter']
        self.seedRadialMiddle = couponData['elemSize']['radialMiddle']
        self.seedRadialInner = couponData['elemSize']['radialInner']
        self.seedSizeLong1 = couponData['elemSize']['long1']
        self.seedSizeLong2 = couponData['elemSize']['long2']
        self.elemTypeHex = SymbolicConstant(couponData['elemType']['hex'])
        self.elemTypeTet = SymbolicConstant(couponData['elemType']['tet'])
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
        self.partitionRadius = self.partitionRadialFraction*self.phi1/2
        self.endStress = -self.nominalStress*(self.phi1/self.phi3)**2
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
        (self.xa, self.ya) = (self.xA, self.yA) = (0.0, self.phi1/2.0)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (0.0, (self.yA+self.rad1))
        (self.xb, self.yb) = (self.xB, self.yB) = (self.rad1*math.sin(self.alphaRad), (self.yA+self.rad1*(1.0-math.cos(self.alphaRad))))
        (self.xc, self.yc) = (self.xC, self.yC) = (self.xB+(self.phi2/2.0-self.yB)/math.tan(self.alphaRad), self.phi2/2.0)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.len1/2.0, self.phi3/2.0)
        (self.xd, self.yd) = (self.xD, self.yD) = (self.xE-self.rad2*math.sin(math.acos((self.rad2-(self.yE-self.yC))/self.rad2)), self.yC)
        (self.xc2, self.yc2) = (self.xC2, self.yC2) = (self.xD, self.yD+self.rad2)
        (self.xf, self.yf) = (self.xF, self.yF) = (self.len2/2.0, self.yE)
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
        self.profileSketch[0].assignCenterline(line=self.profileGeometry1[2])
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
        self.profileSketch[0].ObliqueDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[0], textPoint=(-3.0, 0.0), value=self.phi1/2.0)
        ## arc AB
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[1].coords, point2=(self.xB, self.yB), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=(0.0, 5.0), radius=self.rad1)
        ## line BC
        self.profileSketch[0].Line(point1=self.profileVertices1[2].coords, point2=(self.xC, self.yC))
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[6], entity2=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[4], entity2=self.profileGeometry1[2], textPoint=(-5.0, 8.0), value=self.phi2/2.0)
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
        self.profileSketch[1].assignCenterline(line=self.profileGeometry2[2])
        ## vertical fixed construction line
        self.profileSketch[1].ConstructionLine(point1=(self.xH, 0.0), angle=90.0)
        self.profileSketch[1].FixedConstraint(entity=self.profileGeometry2[3])
        ## line HD
        self.profileSketch[1].Line(point1=(self.xH, self.yH), point2=(self.xD, self.yD))
        self.profileSketch[1].VerticalConstraint(entity=self.profileGeometry2[4], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[0], entity2=self.profileGeometry2[2], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[1], entity2=self.profileGeometry2[3], addUndoState=False)
        self.profileSketch[1].ObliqueDimension(vertex1=self.profileVertices2[1], vertex2=self.profileVertices2[0], textPoint=(3.0, 0.0), value=self.phi2/2.0)
        ## arc DE
        self.profileSketch[1].ArcByCenterEnds(center=(self.xC2, self.yC2), point1=self.profileVertices2[1].coords, point2=(self.xE, self.yE), direction=COUNTERCLOCKWISE)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[5], entity2=self.profileGeometry2[4], addUndoState=False)
        self.profileSketch[1].RadialDimension(curve=self.profileGeometry2[5], textPoint=(12.0, 12.0), radius=self.rad2)
        self.profileSketch[1].VerticalDimension(vertex1=self.profileVertices2[0], vertex2=self.profileVertices2[2], textPoint=(10.0, 25.0), value=self.phi3/2.0)
        ## line EF
        self.profileSketch[1].Line(point1=self.profileVertices2[2].coords, point2=(self.xF, self.yF))
        self.profileSketch[1].HorizontalConstraint(entity=self.profileGeometry2[6], addUndoState=False)
        self.profileSketch[1].HorizontalDimension(vertex1=self.profileVertices2[1], vertex2=self.profileVertices2[4], textPoint=(6.0, 5.0), value=(self.len2/2.0-self.xD))
        ## line FG
        self.profileSketch[1].Line(point1=self.profileVertices2[4].coords, point2=(self.xG, self.yG))
        self.profileSketch[1].VerticalConstraint(entity=self.profileGeometry2[7], addUndoState=False)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[7], entity2=self.profileGeometry2[6], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[5], entity2=self.profileGeometry2[2], addUndoState=False)
        ## line GH
        self.profileSketch[1].Line(point1=self.profileVertices2[5].coords, point2=(self.xH, self.yH))
        self.profileSketch[1].HorizontalConstraint(entity=self.profileGeometry2[8], addUndoState=False)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[8], entity2=self.profileGeometry2[7], addUndoState=False)
        ###############################################################################################################################################################
        self.profileSketch[1].unsetPrimaryObject()
        ###############################################################################################################################################################
        (self.xE, self.yE) = self.profileVertices2[2].coords
        (self.xC2, self.yC2) = self.profileVertices2[3].coords
        (self.xF, self.yF) = self.profileVertices2[4].coords
        (self.xG, self.yG) = self.profileVertices2[5].coords
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
                     ['C2', self.xc2, self.yc2, self.xC2, self.yC2],
                     ['phi1', '', self.phi1, '', 2*(self.yA-self.yO)],
                     ['phi2', '', self.phi2, '', 2*(self.yC-self.yO)],
                     ['phi3', '', self.phi3, '', 2*(self.yE-self.yO)],
                     ['rad1', '', self.rad1, '', ((self.xC1-self.xB)**2+(self.yC1-self.yB)**2)**0.5],
                     ['rad2', '', self.rad2, '', ((self.xC2-self.xE)**2+(self.yC2-self.yE)**2)**0.5],
                     ['len1', '', self.len1, '', 2*(self.xE-self.xO)],
                     ['len2', '', self.len2, '', 2*(self.xF-self.xO)]]
    def createPart(self):
        ## create solid
        self.part = len(self.profileSketch)*[None]
        for i in range(len(self.part)):
            self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
            self.part[i].BaseSolidRevolve(sketch=self.profileSketch[i], angle=90.0, flipRevolveDirection=ON)
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
            sketchPlane = self.part[0].faces.findAt(((self.lenTol, self.partitionRadius, 0),))
            sketchUpEdge = self.part[0].edges.findAt(((xRight, self.partitionRadius, 0),))
            transform = self.part[0].MakeSketchTransform(sketchPlane=sketchPlane[0], sketchUpEdge=sketchUpEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=50.0, gridSpacing=1.0, transform=transform)
            g, v = self.partitionSketch1.geometry, self.partitionSketch1.vertices
            self.partitionSketch1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch1, filter=COPLANAR_EDGES)
            newGeometryID = len(g)+2
            newVertexID = len(v)
            ## arc
            self.partitionSketch1.ArcByCenterEnds(center=(self.xC1, self.yC1), point1=(self.xA, self.yA-self.yOffset), point2=(self.xB, self.yB-self.yOffset), direction=COUNTERCLOCKWISE)
            self.partitionSketch1.CoincidentConstraint(entity1=g.findAt((self.xA,self.yOffset),1), entity2=v[newVertexID])
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
            edges = self.getByCylinderDifference(self.part[0].edges, (self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA+self.lenTol), (self.yA-self.lenTol))
            sweepPath1 = self.getArcEdge(edges)
            edgesTemp = self.part[0].edges
            edgesForPartition =(edgesTemp[0], edgesTemp[1], edgesTemp[2]) ## hard-coded ==>> directly taken from macro; no easy logic to find coordinate
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath1[0], cells=self.part[0].cells, edges=edgesForPartition)
        def createPartitionCyl(xRight):
            ## partition face ==>> inner cylinder
            self.sketchFace = self.part[0].faces.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA-self.yOffset+self.lenTol))
            self.sketchEdge = self.part[0].edges.findAt(((0, self.partitionRadius, 0),))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch2 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_2', sheetSize=4, transform=self.transform)
            g, v = self.partitionSketch2.geometry, self.partitionSketch2.vertices
            self.partitionSketch2.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch2, filter=COPLANAR_EDGES)
            self.partitionSketch2.ArcByCenterEnds(center=(0, 0), point1=(0, self.partitionRadius), point2=(-self.partitionRadius, 0), direction=COUNTERCLOCKWISE)
            self.projectionLine1 = g.findAt((0, self.partitionRadius/2), 1)
            self.projectionLine2 = g.findAt((-self.partitionRadius/2, 0), 1)
            self.vertexPoint1 = v.findAt((0, self.partitionRadius), 1)
            self.vertexPoint2 = v.findAt((-self.partitionRadius, 0), 1)
            self.partitionSketch2.CoincidentConstraint(entity1=self.vertexPoint1, entity2=self.projectionLine1, addUndoState=False)
            self.partitionSketch2.CoincidentConstraint(entity1=self.vertexPoint2, entity2=self.projectionLine2, addUndoState=False)
            self.partitionSketch2.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge[0], faces=self.sketchFace[0], sketch=self.partitionSketch2)
            ## partition solid ==>> sweep
            sweepPath2 = self.part[0].edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius-self.lenTol))
            edgesTemp = self.part[0].edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            edgeArcForPartition = self.getArcEdge(edgesTemp)
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath2[0], cells=self.part[0].cells, edges=edgeArcForPartition)
        def createPartitionLong(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)     
        self.yOffset = (self.phi1/2-self.partitionRadius)/2
        createPartitionOffset(self.xD)
        createPartitionCyl(self.xD)
        createPartitionLong(self.xB)
        createPartitionLong(self.xC)
    def createMesh(self):
        def seedRadial(radiusOuter, radiusInner, seedSize, **kwargs):
            edgesOuterCyl = self.getByCylinderDifference(self.part[0].edges, (self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), radiusOuter, radiusInner)
            edgesOuterArc = self.getArcEdge(edgesOuterCyl)
            edgesOuterRadial = self.getByDifference(edgesOuterCyl, edgesOuterArc)
            self.part[0].seedEdgeBySize(edges=edgesOuterRadial, size=seedSize, deviationFactor=0.1, **kwargs)
        def seedLong(xLeft, xRight, **kwargs):
            pickedEdges = self.part[0].edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.yF+self.lenTol))
            edgesLong = self.getEdgeByLength(pickedEdges, abs(xRight-xLeft))
            self.seedEdge(self.part[0], 0, xLeft, edgesLong, **kwargs)
        def seedInnerCyl(xLeft, xRight):
            cellsInnerCyl = self.part[0].cells.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            self.part[0].setMeshControls(regions=cellsInnerCyl, elemShape=HEX, technique=SWEEP, algorithm=ADVANCING_FRONT)
            edgesSweepPath = self.part[0].edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), self.lenTol)
            self.part[0].setSweepPath(region=cellsInnerCyl[0], edge=edgesSweepPath[0], sense=FORWARD)
        def seedCylRight():
            cellsRight = self.part[1].cells.getByBoundingCylinder((self.xD-self.lenTol, 0, 0), (self.xF+self.lenTol, 0, 0), (self.yF+self.lenTol))
            self.part[1].setMeshControls(regions=cellsRight, elemShape=TET, technique=FREE, allowMapped=False, sizeGrowthRate=1.05)
            edgesPicked = self.part[1].edges.getByBoundingCylinder((self.xD-self.lenTol, 0, 0), (self.xD+self.lenTol, 0, 0), (self.yF+self.lenTol))
            arcEdges = self.getArcEdge(edgesPicked)
            self.part[1].seedEdgeBySize(edges=arcEdges, size=self.seedSizePart2/self.phi3*self.phi2, deviationFactor=0.1, constraint=FINER)
            remainingEdges = self.getByDifference(self.part[1].edges, arcEdges)
            self.part[1].seedEdgeBySize(edges=remainingEdges, size=self.seedSizePart2, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer arc edge AA'
        edgesOuterCyl = self.getByCylinderDifference(self.part[0].edges, (self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA+self.lenTol), (self.partitionRadius+self.yOffset+self.lenTol))
        edgesOuterArc = self.getArcEdge(edgesOuterCyl)
        self.part[0].seedEdgeBySize(edges=edgesOuterArc, size=self.seedSizeArcOuter, deviationFactor=0.1, constraint=FINER)
        ## seed radial edges
        seedRadial((self.yA+self.lenTol), (self.yA-self.yOffset+self.lenTol), self.seedRadialOuter, constraint=FIXED) ## outer radial edge
        seedRadial((self.yA-self.lenTol), (self.partitionRadius+self.lenTol), self.seedRadialMiddle, constraint=FIXED) ## mid radial edge
        seedRadial((self.partitionRadius+self.lenTol), (self.partitionRadius-self.lenTol), self.seedRadialInner, constraint=FIXED) ## inner radial edge
        ## seed long edges
        seedLong(self.xA, self.xB, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong1)
        seedLong(self.xB, self.xC, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong1)
        seedLong(self.xC, self.xD, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed and set mesh ==>> inner cylinder
        seedInnerCyl(self.xA, self.xB)
        seedInnerCyl(self.xB, self.xC)
        seedInnerCyl(self.xC, self.xD)
        ## seed and set mesh ==>> part-2 ==>> region away from area of interest
        seedCylRight()
        ## set element types
        elemType1 = mesh.ElemType(elemCode=self.elemTypeHex, elemLibrary=STANDARD)
        self.part[0].setElementType(regions=(self.part[0].cells,), elemTypes=(elemType1,))
        elemType3 = mesh.ElemType(elemCode=self.elemTypeTet, elemLibrary=STANDARD)
        self.part[1].setElementType(regions=(self.part[1].cells,), elemTypes=(elemType3,))
        ## generate mesh
        self.couponData.update({'elemNum':dict()})
        for i in range(len(self.part)):
            self.part[i].generateMesh()
            self.couponData['elemNum'].update({'part'+str(i+1):len(self.part[i].elements)})
    def createTie(self):
        region = len(self.part)*[None]
        for i in range(len(self.part)):
            surf = self.part[i].faces.getByBoundingCylinder((self.xD-self.lenTol, 0, 0), (self.xD+self.lenTol, 0, 0), (self.yD+self.lenTol))
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
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin=-self.lenTol, zMin=-self.yF-self.lenTol, xMax=self.xG+self.lenTol, yMax=self.lenTol, zMax=self.lenTol)
            nsetNameNegY = 'Nset_BC_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at posZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xG+self.lenTol, yMax=self.yF+self.lenTol, zMax=self.lenTol)
            nsetNamePosZ = 'Nset_BC_PosZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesPosZ, name=nsetNamePosZ)
            region = self.instance[i].sets[nsetNamePosZ]
            self.model.DisplacementBC(name='BC_PosZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==0:
                ## create BC at negX face of Part 1
                nodesNegX = self.part[i].nodes.getByBoundingCylinder((self.xO-self.lenTol, 0, 0), (self.xO+self.lenTol, 0, 0), (self.yA+self.lenTol))
                nsetNameNegX = 'Nset_BC_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==(len(self.part)-1):
                ## create pressure load on posX face
                endCellFaceArr = self.part[i].faces.getByBoundingCylinder((self.xG-self.lenTol, 0, 0), (self.xG+self.lenTol, 0, 0), (self.yF+self.lenTol))
                surfNamePosX = 'Surf_Load_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
    
