import json
import math

from abaqus import *
from abaqusConstants import *
from caeModules import *

class fatigue_coupon_70_73_be():
    def __init__(self, couponData):
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
        self.thickness = couponData['geometry']['thickness']
        self.givenKt = couponData['givenKt']
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
    def createModel(self):
        ## define model
        session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
        self.model = mdb.Model(name=self.couponName+'_Model')
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates #################################################################################################################
        self.coordO = (self.xO, self.yO) = (0.0, 0.0)
        self.coordA = (self.xA, self.yA) = (0.0, self.h1/2.0)
        self.coordC1 = (self.xC1, self.yC1) = (0.0, (self.yA+self.rad1))
        self.coordB = (self.xB, self.yB) = (self.rad1*math.sin(self.alphaRad), (self.yA+self.rad1*(1.0-math.cos(self.alphaRad))))
        self.coordC = (self.xC, self.yC) = (self.xB+(self.h2/2.0-self.yB)/math.tan(self.alphaRad), self.h2/2.0)
        self.coordE = (self.xE, self.yE) = (self.len1/2.0-self.len2, self.h3/2.0)
        self.coordD = (self.xD, self.yD) = (self.xE-self.rad2*math.sin(math.acos((self.rad2-(self.yE-self.yC))/self.rad2)), self.yC)
        self.coordC2 = (self.xC2, self.yC2) = (self.xD, self.yD+self.rad2)
        self.coordF = (self.xF, self.yF) = (self.len1/2.0, self.yE)
        self.coordG = (self.xG, self.yG) = (self.xF, 0.0)
        self.coordH = (self.xH, self.yH) = (self.xD, 0.0)
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
        self.profileSketch[0].Line(point1=self.coordO, point2=self.coordA)
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].ObliqueDimension(vertex1=self.profileVertices1[1], vertex2=self.profileVertices1[0], textPoint=(-3.0, 0.0), value=self.h1/2.0)
        (self.xO, self.yO), (self.xA, self.yA) = self.profileVertices1[0].coords, self.profileVertices1[1].coords
        ## arc AB
        self.profileSketch[0].ArcByCenterEnds(center=self.coordC1, point1=self.coordA, point2=self.coordB, direction=COUNTERCLOCKWISE)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[6], textPoint=(0.0, 5.0), radius=self.rad1)
        (self.xB, self.yB), (self.xC1, self.yC1) = self.profileVertices1[2].coords, self.profileVertices1[3].coords
        ## line BC
        self.profileSketch[0].Line(point1=self.coordB, point2=self.coordC)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[6], entity2=self.profileGeometry1[7], addUndoState=False)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[4], entity2=self.profileGeometry1[2], textPoint=(-5.0, 8.0), value=self.h2/2.0)
        self.profileSketch[0].ParallelConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[7])
        (self.xC, self.yC) = self.profileVertices1[4].coords
        ## line CD
        self.profileSketch[0].Line(point1=self.coordC, point2=self.coordD)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        (self.xD, self.yD) = self.profileVertices1[5].coords
        ## line DH
        self.profileSketch[0].Line(point1=self.coordD, point2=self.coordH)
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[6], entity2=self.profileGeometry1[2], addUndoState=False)
        (self.xH, self.yH) = self.profileVertices1[6].coords
        ## line HO
        self.profileSketch[0].Line(point1=self.coordH, point2=self.coordO)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[10], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[6], textPoint=(6.0, -5.0), value=self.xD)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
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
        self.profileSketch[1].Line(point1=self.coordH, point2=self.coordD)
        self.profileSketch[1].VerticalConstraint(entity=self.profileGeometry2[4], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[0], entity2=self.profileGeometry2[2], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[1], entity2=self.profileGeometry2[3], addUndoState=False)
        self.profileSketch[1].ObliqueDimension(vertex1=self.profileVertices2[1], vertex2=self.profileVertices2[0], textPoint=(3.0, 0.0), value=self.h2/2.0)
        ## arc DE
        self.profileSketch[1].ArcByCenterEnds(center=self.coordC2, point1=self.coordD, point2=self.coordE, direction=COUNTERCLOCKWISE)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[5], entity2=self.profileGeometry2[4], addUndoState=False)
        self.profileSketch[1].RadialDimension(curve=self.profileGeometry2[5], textPoint=(12.0, 12.0), radius=self.rad2)
        self.profileSketch[1].VerticalDimension(vertex1=self.profileVertices2[0], vertex2=self.profileVertices2[2], textPoint=(10.0, 25.0), value=self.h3/2.0)
        (self.xE, self.yE), (self.xC2, self.yC2) = self.profileVertices2[2].coords, self.profileVertices2[3].coords
        ## line EF
        self.profileSketch[1].Line(point1=self.coordE, point2=self.coordF)
        self.profileSketch[1].HorizontalConstraint(entity=self.profileGeometry2[6], addUndoState=False)
        self.profileSketch[1].HorizontalDimension(vertex1=self.profileVertices2[2], vertex2=self.profileVertices2[4], textPoint=(6.0, 5.0), value=self.len2)
        (self.xF, self.yF) = self.profileVertices2[4].coords
        ## line FG
        self.profileSketch[1].Line(point1=self.coordF, point2=self.coordG)
        self.profileSketch[1].VerticalConstraint(entity=self.profileGeometry2[7], addUndoState=False)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[7], entity2=self.profileGeometry2[6], addUndoState=False)
        self.profileSketch[1].CoincidentConstraint(entity1=self.profileVertices2[5], entity2=self.profileGeometry2[2], addUndoState=False)
        (self.xG, self.yG) = self.profileVertices2[5].coords
        ## line GO
        self.profileSketch[1].Line(point1=self.coordG, point2=self.coordH)
        self.profileSketch[1].HorizontalConstraint(entity=self.profileGeometry2[8], addUndoState=False)
        self.profileSketch[1].PerpendicularConstraint(entity1=self.profileGeometry2[8], entity2=self.profileGeometry2[7], addUndoState=False)
        ###############################################################################################################################################################
        self.profileSketch[1].unsetPrimaryObject()
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
        for i in range(len(self.part)):
            self.part[i].generateMesh()
        self.couponData.update({'elemNum':{'part1':len(self.part[0].elements), 'part2':len(self.part[1].elements)}})
    def createMaterial(self):
        ## material definition
        self.model.Material(name=self.materialName)
        self.model.materials[self.materialName].Density(table=((self.density, ), ))
        self.model.materials[self.materialName].Elastic(table=((self.youngsModulus, self.poissonsRatio), ))
    def createSection(self):
        ## section definition and assigning section property to elements
        self.model.HomogeneousSolidSection(name=self.couponName+'_Section', material=self.materialName, thickness=None)
        for i in range(len(self.part)):
            pickedRegion = self.part[i].Set(elements=self.part[i].elements, name='All_Elements_Part_'+str(i+1))
            self.part[i].SectionAssignment(region=pickedRegion, sectionName=self.couponName+'_Section', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
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
        for i in range(len(self.part)):
            ## create BC at negY face
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xF+self.lenTol, yMax=self.lenTol, zMax=self.thickness+self.lenTol)
            nsetNameNegY = 'Nset_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Part_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at posZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=self.thickness-self.lenTol, xMax=self.xF+self.lenTol, yMax=self.yF+self.lenTol, zMax=self.thickness+self.lenTol)
            nsetNamePosZ = 'Nset_PosZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesPosZ, name=nsetNamePosZ)
            region = self.instance[i].sets[nsetNamePosZ]
            self.model.DisplacementBC(name='BC_PosZ_Part_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at negX face of Part 1
        nodesNegX = self.part[0].nodes.getByBoundingBox(xMin=self.xA-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xA+self.lenTol, yMax=self.yA+self.yC+self.lenTol, zMax=self.thickness+self.lenTol)
        nsetNameNegX = 'Nset_NegX_Part_1'
        self.part[0].Set(nodes=nodesNegX , name=nsetNameNegX)
        region = self.instance[0].sets[nsetNameNegX]
        self.model.DisplacementBC(name='BC_NegX_Part_1', createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create pressure load on posX face
        endCellFaceArr = self.part[1].faces.getByBoundingBox(xMin=self.xF-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xF+self.lenTol, yMax=self.yF+self.lenTol, zMax=self.thickness+self.lenTol)
        surfNamePosX = 'Surf_PosX_Part_2'
        self.getElemSurfFromCellFace(self.part[1], endCellFaceArr, surfNamePosX)
        region = self.instance[1].surfaces[surfNamePosX]
        self.model.Pressure(name='Load_PosX', createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
        self.model.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RF'))
    def createJob(self):
        ## create job
        self.job = mdb.Job(name=self.couponName+'_Job'+self.version, model=self.model, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, 
            getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
            scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=2, numDomains=2, numGPUs=1)
        self.job.writeInput(consistencyChecking=OFF)
        ## save cae file
        mdb.saveAs(pathName=self.model.name+self.version)
        ## write json data of the model
        couponString = json.dumps(self.couponData, indent=4, sort_keys=True)
        couponJson = open(self.couponName+'_Data'+self.version+'.json', 'w')
        couponJson.write(couponString)
        couponJson.close()
    def getByDifference(self, listA, listB):
        ## method to return list with elements of difference of two lists
        differenceList = []
        for thisItem in listA:
            if thisItem not in listB:
                differenceList.append(thisItem)
        return differenceList
    def getByCylinderDifference(self, feature, center1, center2, outerRadius, innerRadius):
        ## method to return list with geometric features by subtraction of two bounding cylinders
        featureOuter = feature.getByBoundingCylinder(center1, center2, outerRadius)
        featureInner = feature.getByBoundingCylinder(center1, center2, innerRadius)
        pickedFeatures = self.getByDifference(featureOuter, featureInner)
        return pickedFeatures
    def getArcEdge(self, edgeList):
        ## method to return edge list containing only arc edges from a given edge list
        arcEdge = []
        for thisEdge in edgeList:
            try:
                thisEdge.getRadius()
                arcEdge.append(thisEdge)
            except:
                pass
        return arcEdge
    def getEdgeByLength(self, edgeList, length):
        ## method to return edge list of a desired length from a given edge list
        pickedEdges = []
        for thisEdge in edgeList:
            if abs(thisEdge.getSize(0)-length) < self.lenTol:
                pickedEdges.append(thisEdge)
        return pickedEdges
    def seedEdge(self, part, index, distance, edges, **kwargs):
            for thisEdge in edges:
                edgeVertices = thisEdge.getVertices()
                for thisVertexID in edgeVertices:
                    vertexCoord = part.vertices[thisVertexID].pointOn
                    if abs(abs(vertexCoord[0][index])-distance) < self.lenTol:
                        if edgeVertices.index(thisVertexID) == 0:
                            part.seedEdgeByBias(biasMethod=SINGLE, end1Edges=(thisEdge,), constraint=FINER, **kwargs)
                        elif edgeVertices.index(thisVertexID) == 1:
                            part.seedEdgeByBias(biasMethod=SINGLE, end2Edges=(thisEdge,), constraint=FINER, **kwargs)
    def getElemSurfFromCellFace(self, part, cellFaceArr, surfName):
        ## method to create element based surface from cell face
        elemWithFace = [[], [], [], [], [], []]
        for thisCellFace in cellFaceArr:
            elemFaceArr = thisCellFace.getElementFaces()   
            for thisElem in elemFaceArr:
                for thisfaceID in range(6):
                    if thisElem.face == SymbolicConstant('FACE'+str(thisfaceID+1)):
                        elemWithFace[thisfaceID].append(thisElem)
                        break
        surfDict = {'name':surfName}
        for thisfaceID in range(6):
            if len(elemWithFace[thisfaceID]) > 0:
                elemWithFace[thisfaceID] = mesh.MeshFaceArray(elemWithFace[thisfaceID])
                surfDict.update({'face'+str(thisfaceID+1)+'Elements':elemWithFace[thisfaceID]})
        part.Surface(**surfDict)

