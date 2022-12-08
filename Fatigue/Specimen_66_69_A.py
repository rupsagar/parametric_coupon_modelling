from abaqus import *
from abaqusConstants import *

modelName = "Model-1"
partName = "Part-1"
sketchName = "sketch"
phi1 = 2.82
phi2 = 5.0
phi3 = 8.0
rad1 = 20.0
rad2 = 10.0
len1 = 24.0
len2 = 40.0
theta = 30.0

#def createCoupon(modelName, partName, sketchName, phi1, phi2, phi3, rad1, rad2, len1, len2, theta):
# all inputs converted to float to avoid truncation while division
phi1 = float(phi1)
phi2 = float(phi2)
phi3 = float(phi3)
rad1 = float(rad1)
rad2 = float(rad2)
len1 = float(len1)
len2 = float(len2)
theta = float(theta)
############################################################################################################
# vertex coordinate calculation
coordO = (0.0, 0.0)
coordA = (0.0, phi1/2.0)
coordB = (rad1*(1-((rad1+phi1/2-phi2/2)/rad1)**2.0)**0.5, phi2/2.0)
coordC = (len1/2.0, phi3/2.0)
coordD = (len2/2.0, phi3/2.0)
coordE = (len2/2.0,0.0)
coordCenterad1 = (0.0,phi1/2.0+rad1) # center 1
coordCenterad2 = ((coordB[0]+coordC[0])/2.0,(coordB[1]+coordC[1])/2.0) # arbitrary center 2 ==>> true value given by dimension
############################################################################################################
# model
model = mdb.Model(name=modelName)
############################################################################################################
# 2D sketch
s = mdb.models[modelName].ConstrainedSketch(name=sketchName, sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
############################################################################################################
# horizontal fixed construction line: g[2]
s.ConstructionLine(point1=(-80.0, 0.0), angle=0.0)
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.FixedConstraint(entity=g[2])
############################################################################################################
# vertical fixed construction line: g[3]
s.ConstructionLine(point1=(0.0, -30.0), angle=90.0)
s.VerticalConstraint(entity=g[3], addUndoState=False)
s.FixedConstraint(entity=g[3])
############################################################################################################
# line OA: g[4]; vertices: v[0], v[1]; dimension: d[0]
s.Line(point1=coordO, point2=coordA)
s.VerticalConstraint(entity=g[4], addUndoState=False)
s.PerpendicularConstraint(entity1=g[2], entity2=g[4], addUndoState=False)
s.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)
s.CoincidentConstraint(entity1=v[1], entity2=g[3], addUndoState=False)
s.ObliqueDimension(vertex1=v[0], vertex2=v[1], textPoint=(-3.0, 4.0), value=phi1/2.0)
############################################################################################################
# arc AB: g[5]; vertices: v[1], v[2]; center: v[3]; dimension: d[1], d[2]
s.ArcByCenterEnds(center=coordCenterad1, point1=coordA, point2=coordB, direction=COUNTERCLOCKWISE)
s.CoincidentConstraint(entity1=v[3], entity2=g[3], addUndoState=False)
s.RadialDimension(curve=g[5], textPoint=(0.0, 25.0), radius=rad1)
s.DistanceDimension(entity1=v[2], entity2=g[2], textPoint=(10.0, 1.0), value=phi2/2.0)
############################################################################################################
# arc BC: g[6]; vertices: v[2], v[4]; center: v[5]; dimension: d[3], d[4], d[5]
s.ArcByCenterEnds(center=coordCenterad2, point1=coordB, point2=coordC, direction=COUNTERCLOCKWISE)
s.RadialDimension(curve=g[6], textPoint=(14.0, 10.0), radius=rad2)
s.DistanceDimension(entity1=v[4], entity2=g[2], textPoint=(25.0, 1.0), value=phi3/2.0)
s.HorizontalDimension(vertex1=v[0], vertex2=v[4], textPoint=(13.0, 9.0), value=len1/2.0)
############################################################################################################
# line CD: g[7]; vertices: v[5], v[6]; dimension: d[6]
s.Line(point1=coordC, point2=coordD)
s.HorizontalConstraint(entity=g[7], addUndoState=False)
s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(13.0, -9.0), value=len2/2.0)
############################################################################################################
# line DE: g[8]; vertices: v[6], v[7]
s.Line(point1=coordD, point2=coordE)
s.VerticalConstraint(entity=g[8], addUndoState=False)
s.CoincidentConstraint(entity1=v[7], entity2=g[2], addUndoState=False)
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
p = mdb.models[modelName].Part(name=partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseSolidRevolve(sketch=s, angle=90.0, flipRevolveDirection=ON)
session.viewports['Viewport: 1'].setValues(displayedObject=p)
#del mdb.models[modelName].sketches[sketchName]
############################################################################################################
# partitioning
f, e, dt = p.faces, p.edges, p.datums
face = f.findAt(((0, phi1/4.0, -phi1/4.0),))
face2 = f.getByBoundingBox(xMin=-len1/4.0,yMin=-phi1, zMin=-phi1, xMax=len1/4.0,yMax=phi1,zMax=phi1)
t = p.MakeSketchTransform(sketchPlane=face2[0], sketchUpEdge=e[13], sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=4.0, gridSpacing=0.1, transform=t)
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.ArcByCenterEnds(center=(0.0, 0.0), point1=(phi1/4.0, 0.0), point2=(0.0, -phi1/4.0), direction=COUNTERCLOCKWISE)
s1.CoincidentConstraint(entity1=v1[3], entity2=g1[3], addUndoState=False)
s1.CoincidentConstraint(entity1=v1[4], entity2=g1[2], addUndoState=False)
f = p.faces
pickedFaces = f.getSequenceFromMask(mask=('[#10 ]', ), )
e, d1 = p.edges, p.datums
p.PartitionFaceBySketch(sketchUpEdge=e[13], faces=pickedFaces, sketch=s1)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']




#createCoupon(modelName, partName, sketchName, phi1, phi2, phi3, rad1, rad2, len1, len2, theta)
