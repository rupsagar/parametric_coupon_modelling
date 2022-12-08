from abaqus import *
from abaqusConstants import *

def couponModel(modelName, partName, sketchName, partitionSketchName, phi1, phi2, phi3, rad1, rad2, len1, len2, theta,
    partitionRadius, edgeLengthTol, seedSizeArc, seedSizeRadial, seedSizeLong, seedNumArc, seedNumRadial, seedNumLong):
    # all dimenional inputs converted to float to avoid truncation while division
    phi1 = float(phi1)
    phi2 = float(phi2)
    phi3 = float(phi3)
    rad1 = float(rad1)
    rad2 = float(rad2)
    len1 = float(len1)
    len2 = float(len2)
    theta = float(theta)
    partitionRadius = float(partitionRadius)
    edgeLengthTol = float(edgeLengthTol)
    seedSizeArc = float(seedSizeArc)
    seedSizeRadial = float(seedSizeRadial)
    seedSizeLong = float(seedSizeLong)
    # all edge seed points converted to int
    seedNumArc = int(seedNumArc)
    seedNumRadial = int(seedNumRadial)
    seedNumLong = int(seedNumLong)
    ############################################################################################################
    # vertex coordinate calculation
    coordO = (xO, yO) = (0, 0)
    coordA = (xA, yA) = (0, phi1/2)
    coordB = (xB, yB) = (rad1*(1-((rad1+phi1/2-phi2/2)/rad1)**2)**0.5, phi2/2)
    coordC = (xC, yC) = (len1/2, phi3/2)
    coordD = (xD, yD) = (len2/2, phi3/2)
    coordE = (xE, yE) = (len2/2, 0)
    coordCenterad1 = (xC1, yC1) = (0, yA+rad1) # center 1
    coordCenterad2 = (xC2, yC2) = ((xB+xC)/2,(yB+yC)/2) # arbitrary center 2 ==>> true value given by dimension
    ############################################################################################################
    # create model
    model = mdb.Model(name=modelName)
    ############################################################################################################
    # 2D sketch
    s = model.ConstrainedSketch(name=sketchName, sheetSize=200.0)
    g, v = s.geometry, s.vertices
    s.setPrimaryObject(option=STANDALONE)
    ############################################################################################################
    # horizontal fixed construction line: g[2]
    s.ConstructionLine(point1=(-80, 0), angle=0)
    s.HorizontalConstraint(entity=g[2], addUndoState=False)
    s.FixedConstraint(entity=g[2])
    ############################################################################################################
    # vertical fixed construction line: g[3]
    s.ConstructionLine(point1=(0, -30), angle=90)
    s.VerticalConstraint(entity=g[3], addUndoState=False)
    s.FixedConstraint(entity=g[3])
    ############################################################################################################
    # line OA: g[4]; vertices: v[0], v[1]; dimension: d[0]
    s.Line(point1=coordO, point2=coordA)
    s.VerticalConstraint(entity=g[4], addUndoState=False)
    s.PerpendicularConstraint(entity1=g[2], entity2=g[4], addUndoState=False)
    s.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)
    s.CoincidentConstraint(entity1=v[1], entity2=g[3], addUndoState=False)
    s.ObliqueDimension(vertex1=v[0], vertex2=v[1], textPoint=(-3, 4), value=phi1/2)
    (xO, yO) = v[0].coords
    (xA, yA) = v[1].coords
    ############################################################################################################
    # arc AB: g[5]; vertices: v[1], v[2]; center: v[3]; dimension: d[1], d[2]
    s.ArcByCenterEnds(center=coordCenterad1, point1=coordA, point2=coordB, direction=COUNTERCLOCKWISE)
    s.CoincidentConstraint(entity1=v[3], entity2=g[3], addUndoState=False)
    s.RadialDimension(curve=g[5], textPoint=(0, 25), radius=rad1)
    s.DistanceDimension(entity1=v[2], entity2=g[2], textPoint=(10, 1), value=phi2/2)
    (xB, yB) = v[2].coords
    (xC1, yC1) = v[3].coords
    ############################################################################################################
    # arc BC: g[6]; vertices: v[2], v[4]; center: v[5]; dimension: d[3], d[4], d[5]
    s.ArcByCenterEnds(center=coordCenterad2, point1=coordB, point2=coordC, direction=COUNTERCLOCKWISE)
    s.RadialDimension(curve=g[6], textPoint=(14, 10), radius=rad2)
    s.DistanceDimension(entity1=v[4], entity2=g[2], textPoint=(25, 1), value=phi3/2)
    s.HorizontalDimension(vertex1=v[0], vertex2=v[4], textPoint=(13, 9), value=len1/2)
    (xC, yC) = v[4].coords
    (xC2, yC2) = v[5].coords
    ############################################################################################################
    # line CD: g[7]; vertices: v[5], v[6]; dimension: d[6]
    s.Line(point1=coordC, point2=coordD)
    s.HorizontalConstraint(entity=g[7], addUndoState=False)
    s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(13, -9), value=len2/2)
    (xD, yD) = v[6].coords
    ############################################################################################################
    # line DE: g[8]; vertices: v[6], v[7]
    s.Line(point1=coordD, point2=coordE)
    s.VerticalConstraint(entity=g[8], addUndoState=False)
    s.CoincidentConstraint(entity1=v[7], entity2=g[2], addUndoState=False)
    (xE, yE) = v[7].coords
    ############################################################################################################
    # line EO: g[9]; vertices: v[7], v[0]
    s.Line(point1=coordE, point2=coordO)
    s.HorizontalConstraint(entity=g[9], addUndoState=False)
    ############################################################################################################
    s.sketchOptions.setValues(constructionGeometry=ON)
    s.assignCenterline(line=g[2])
    s.unsetPrimaryObject()
    ############################################################################################################
    # 3D solid model
    p = model.Part(name=partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidRevolve(sketch=s, angle=90, flipRevolveDirection=ON)
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    ############################################################################################################
    # create partition-1
    sketchFace = p.faces.getByBoundingBox(xMin=-xB/2,yMin=-phi1, zMin=-phi1, xMax=xB/2,yMax=phi1,zMax=phi1)
    sketchEdge = p.edges.findAt(((0, partitionRadius, 0),))
    t = p.MakeSketchTransform(sketchPlane=sketchFace[0], sketchUpEdge=sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
    s1 = model.ConstrainedSketch(name=partitionSketchName, sheetSize=4, gridSpacing=0.1, transform=t)
    g1, v1 = s1.geometry, s1.vertices
    s1.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
    s1.ArcByCenterEnds(center=(0, 0), point1=(0, partitionRadius), point2=(-partitionRadius, 0), direction=COUNTERCLOCKWISE)
    projectionLine1 = g1.findAt((0, partitionRadius/2), 1)
    projectionLine2 = g1.findAt((-partitionRadius/2, 0), 1)
    vertexPoint1 = v1.findAt((0, partitionRadius), 1)
    vertexPoint2 = v1.findAt((-partitionRadius, 0), 1)
    s1.CoincidentConstraint(entity1=vertexPoint1, entity2=projectionLine1, addUndoState=False)
    s1.CoincidentConstraint(entity1=vertexPoint2, entity2=projectionLine2, addUndoState=False)
    s1.unsetPrimaryObject()
    p.PartitionFaceBySketch(sketchUpEdge=sketchEdge[0], faces=sketchFace[0], sketch=s1)
    partitionEdges = p.edges.getByBoundingCylinder((xO, 0, 0), (xB/2, 0, 0), partitionRadius)
    pickedEdgesPartition = []
    for eachEdge in partitionEdges:
        if abs(eachEdge.getSize(0)-partitionRadius) >= edgeLengthTol:
            pickedEdgesPartition.append(eachEdge)
    pass
    sweepEdges = p.edges.getByBoundingCylinder((xO, 0, 0), (xE, 0, 0), partitionRadius/2)
    p.PartitionCellBySweepEdge(sweepPath=sweepEdges[0], cells=p.cells, edges=pickedEdgesPartition)
    #p.PartitionCellByExtrudeEdge(line=p.datums[1], cells=p.cells, edges=pickedEdges, sense=FORWARD)
    ############################################################################################################
    # create partition-2
    datumPlane1_ID = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(xB+xC)/2).id
    p.PartitionCellByDatumPlane(datumPlane=p.datums[datumPlane1_ID], cells=p.cells)
    ############################################################################################################
    # create partition-3
    datumPlane1_ID = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(xC+xD)/2).id
    p.PartitionCellByDatumPlane(datumPlane=p.datums[datumPlane1_ID], cells=p.cells)
    ############################################################################################################
    # create mesh-1
    seedEdges = p.edges.getByBoundingCylinder((xO, 0, 0), (xE, 0, 0), partitionRadius)
    pickedEdgesArc = []
    pickedEdgesRadial = []
    pickedEdgesLong = []
    for eachEdge in seedEdges:
        try:
            eachEdge.getRadius(0)
            pickedEdgesArc.append(eachEdge)
        except:
            edgeLength = eachEdge.getSize(0)
            if abs(edgeLength-partitionRadius) <= edgeLengthTol:
                pickedEdgesRadial.append(eachEdge)
            else :
                pickedEdgesLong.append(eachEdge)
    pass
    p.seedEdgeBySize(edges=pickedEdgesArc, size=seedSizeArc, deviationFactor=0.1, constraint=FINER)
    p.seedEdgeBySize(edges=pickedEdgesRadial, size=seedSizeRadial, deviationFactor=0.1, constraint=FINER)
    p.seedEdgeBySize(edges=pickedEdgesLong, size=seedSizeLong, deviationFactor=0.1, constraint=FINER)
    #p.seedEdgeByNumber(edges=pickedEdgesArc, number=seedNumArc, constraint=FINER)
    #p.seedEdgeByNumber(edges=pickedEdgesRadial, number=seedNumRadial, constraint=FINER)
    #p.seedEdgeByNumber(edges=pickedEdgesLong, number=seedNumLong, constraint=FINER)
    pickedCellsRegion1 = p.cells.getByBoundingCylinder((xO, 0, 0), (xE, 0, 0), (partitionRadius+yA)/2)
    cellIndex1 = []
    for eachCell in pickedCellsRegion1:
        cellIndex1.append(eachCell.index)
    pass
    p.generateMesh(regions=pickedCellsRegion1)
    ############################################################################################################
    # create mesh-2
    pickedCellsAll = p.cells.getByBoundingCylinder((xO, 0, 0), (xE, 0, 0), yD)
    cellIndexAll = []
    for eachCell in pickedCellsAll:
        cellIndexAll.append(eachCell.index)
    pass
    cellIndexTemp = cellIndex1+cellIndexAll
    cellIndexTemp.sort()
    pickedCellsRegion2 = []
    for index in range(1,len(cellIndexTemp)-1):
        if cellIndexTemp[index-1] != cellIndexTemp[index] and cellIndexTemp[index] != cellIndexTemp[index+1]:
            pickedCellsRegion2.append(pickedCellsAll[cellIndexTemp[index]])
    pass
    p.generateMesh(regions=pickedCellsRegion2)

modelName = "Model-1"
partName = "Part-1"
sketchName = "Sketch-1"
partitionSketchName = 'Sketch-2'
phi1 = 2.82
phi2 = 6.0
phi3 = 8.0
rad1 = 2.0
rad2 = 10.0
len1 = 24.0
len2 = 40.0
theta = 30.0
partitionRadius = phi1/4.0
edgeLengthTol = 1.0e-6
seedSizeArc = 0.1
seedSizeRadial = 0.1
seedSizeLong = 0.1
seedNumArc = 7.0
seedNumRadial = 5.0
seedNumLong = 20.0

couponModel(modelName, partName, sketchName, partitionSketchName, phi1, phi2, phi3, rad1, rad2, len1, len2, theta, 
    partitionRadius, edgeLengthTol, seedSizeArc, seedSizeRadial, seedSizeLong, seedNumArc, seedNumRadial, seedNumLong)
