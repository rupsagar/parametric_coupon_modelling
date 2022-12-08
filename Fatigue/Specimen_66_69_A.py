from abaqus import *
from abaqusConstants import *
import math

modelName = "couponTest"
sketchName = "sketch1"
partName = "specimenOne"
l = 24.0
d1 = 2.8
d2 = 5.0
d3 = 8.0
r1 = 16.0
r2 = 3.0
model = mdb.Model(name=modelName)
#def createCoupon(modelName, partName, l, d1, d2, d3, r1, r2):
yA = d1/2
yCenter1 = r1-d1/2
yB = d2/2
xB = r1*math.sqrt(1-pow(r1+d1/2-d2/2,2)/pow(r1,2))
coordO = (0, 0)
coordA = (0, yA)
coordB = (xB,yB)
coordCenter1 = (0, yCenter1)
coordC = (21.25, 13.75)
coordD = (30.25, 13.75)
coordE = (30.25, 0)
##
sketch = mdb.models[modelName].ConstrainedSketch(name=sketchName, sheetSize=200.0)
g, v, d, c = sketch.geometry, sketch.vertices, sketch.dimensions, sketch.constraints
sketch.setPrimaryObject(option=STANDALONE)
sketch.ConstructionLine(point1=(0, -100), point2=(0, 100))
sketch.FixedConstraint(entity=g[2])
sketch.ConstructionLine(point1=(-100, 0), point2=(100, 0))
sketch.FixedConstraint(entity=g[3])
# line OA
sketch.Line(point1=coordO, point2=coordA)
sketch.VerticalConstraint(entity=g[4], addUndoState=False)
sketch.ParallelConstraint(entity1=g[2], entity2=g[4], addUndoState=False)
sketch.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)
# arc AB
sketch.ArcByCenterEnds(center=coordCenter1, point1=coordA, point2=coordB, direction=COUNTERCLOCKWISE)
sketch.CoincidentConstraint(entity1=v[3], entity2=g[2], addUndoState=False)
# arc BC
sketch.ArcByCenterEnds(center=(12.5, 20.0), point1=coordB, point2=coordC, direction=COUNTERCLOCKWISE)
sketch.CoincidentConstraint(entity1=v[2], entity2=v[4], addUndoState=False)
# line CD
sketch.Line(point1=coordC, point2=coordD)
sketch.HorizontalConstraint(entity=g[7], addUndoState=False)
sketch.CoincidentConstraint(entity1=v[5], entity2=v[7], addUndoState=False)
# line DE
sketch.Line(point1=coordD, point2=coordE)
sketch.VerticalConstraint(entity=g[8], addUndoState=False)
sketch.PerpendicularConstraint(entity1=g[7], entity2=g[8], addUndoState=False)
sketch.CoincidentConstraint(entity1=v[9], entity2=g[3], addUndoState=False)
#line EO
sketch.Line(point1=coordE, point2=coordO)
sketch.HorizontalConstraint(entity=g[9], addUndoState=False)
sketch.PerpendicularConstraint(entity1=g[8], entity2=g[9], addUndoState=False)
sketch.sketchOptions.setValues(constructionGeometry=ON)
sketch.assignCenterline(line=g[3])
solid = mdb.models[modelName].Part(name=partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
solid = mdb.models[modelName].parts[partName]
solid.BaseSolidRevolve(sketch=sketch, angle=90.0, flipRevolveDirection=ON)
sketch.unsetPrimaryObject()
solid = mdb.models[modelName].parts[partName]
session.viewports['Viewport: 1'].setValues(displayedObject=solid)
del mdb.models[modelName].sketches['__profile__']


#createCoupon(modelName, partName, l, d1, d2, d3, r1, r2)
