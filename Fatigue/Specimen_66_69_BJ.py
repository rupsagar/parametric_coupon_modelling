from abaqus import *
from abaqusConstants import *
from math import *
s = mdb.models['Model-1'].ConstrainedSketch(name='Test_Sketch', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
theta = pi/6
coordO = (xO, yO) = (0.0,0.0)
coordA = (xA, yA) = (0.0, 1.41)
coordCenter1 = (0.0, (1.41+0.71))
coordB = (xB, yB) = (0.71*sin(theta), (1.41+0.71-0.71*cos(theta)))
coordC = (xC, yC) = (xB+(2.5-yB)/tan(theta), 2.5)
coordE = (xE, yE) = (12.0, 4.0)
coordD = (xD, yD) = ((xC+xE)/2.0, yC)
coordCenter2 = (xD, yD+10)
coordF = (xF, yF) = (20, yE)
coordG = (xG, yG) = (xF, 0.0)
## horizontal construction line
s.ConstructionLine(point1=(-56.25, 0.0), angle=0.0)
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.FixedConstraint(entity=g[2])
s.assignCenterline(line=g[2])
## vertical construction line
s.ConstructionLine(point1=(0.0, -23.75), angle=90.0)
s.VerticalConstraint(entity=g[3], addUndoState=False)
s.FixedConstraint(entity=g[3])
## line OA
s.Line(point1=coordO, point2=coordA)
s.VerticalConstraint(entity=g[4], addUndoState=False)
s.PerpendicularConstraint(entity1=g[2], entity2=g[4], addUndoState=False)
s.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)
s.CoincidentConstraint(entity1=v[1], entity2=g[3], addUndoState=False)
s.ObliqueDimension(vertex1=v[1], vertex2=v[0], textPoint=(-3.0, 0.0), value=1.41)
## arc AB
s.ArcByCenterEnds(center=coordCenter1, point1=coordA, point2=coordB, direction=COUNTERCLOCKWISE)
s.CoincidentConstraint(entity1=v[3], entity2=g[3], addUndoState=False)
s.RadialDimension(curve=g[5], textPoint=(0.0, 5.0), radius=0.71)
# line BC
s.Line(point1=coordB, point2=coordC)
s.TangentConstraint(entity1=g[5], entity2=g[6], addUndoState=False)
s.AngularDimension(line1=g[6], line2=g[3], textPoint=(5.0, 6.0), value=60)
s.DistanceDimension(entity1=v[4], entity2=g[2], textPoint=(-5.0, 8.0), value=2.5)
# line CD
s.Line(point1=coordC, point2=coordD)
s.HorizontalConstraint(entity=g[7], addUndoState=False)
# arc DE
s.ArcByCenterEnds(center=coordCenter2, point1=coordD, point2=coordE, direction=COUNTERCLOCKWISE)
s.TangentConstraint(entity1=g[7], entity2=g[8], addUndoState=False)
s.RadialDimension(curve=g[8], textPoint=(0.0, 5.0), radius=10)
s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(10.0, -3.0), value=12.0)
s.DistanceDimension(entity1=v[6], entity2=g[2], textPoint=(8.0, 25.0), value=4.0)
# line EF
s.Line(point1=coordE, point2=coordF)
s.HorizontalConstraint(entity=g[9], addUndoState=False)
s.HorizontalDimension(vertex1=v[0], vertex2=v[8], textPoint=(6.0, 5.0), value=20.0)
# line FG
s.Line(point1=coordF, point2=coordG)
s.VerticalConstraint(entity=g[10], addUndoState=False)
s.PerpendicularConstraint(entity1=g[9], entity2=g[10], addUndoState=False)
s.CoincidentConstraint(entity1=v[9], entity2=g[2], addUndoState=False)
# line GO
s.Line(point1=coordG, point2=coordO)
s.HorizontalConstraint(entity=g[11], addUndoState=False)
s.PerpendicularConstraint(entity1=g[10], entity2=g[11], addUndoState=False)

s.unsetPrimaryObject()

part = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidRevolve(sketch=s, angle=90, flipRevolveDirection=ON)
session.viewports['Viewport: 1'].setValues(displayedObject=part)
