from abaqus import *
from abaqusConstants import *

modelName = "coupon"
partName = "specimen"
d1 = 2.82
r1 = 20.0
d2 = 5.0
r2 = 10.0
d3 = 8.0
l1 = 24.0
l2 = 1.0
l3 = 40.0
theta = 30.0

#model = mdb.Model(name=modelName)

#def createCoupon(modelName, partName, d1, r1, d2, r2, d3, l):
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
############################################################################################################
# horizontal construction line: g[2]
s.ConstructionLine(point1=(-80.0, 0.0), angle=0.0)
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.FixedConstraint(entity=g[2])
############################################################################################################
# vertical construction line: g[3]
s.ConstructionLine(point1=(0.0, -30.0), angle=90.0)
s.VerticalConstraint(entity=g[3], addUndoState=False)
s.FixedConstraint(entity=g[3])
############################################################################################################
# line OA: g[4]; vertices: v[0], v[1]; dimension: d[0]
s.Line(point1=(0.0, 0.0), point2=(0.0, 9.69879531860352))
s.VerticalConstraint(entity=g[4], addUndoState=False)
s.PerpendicularConstraint(entity1=g[2], entity2=g[4], addUndoState=False)
s.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)
s.CoincidentConstraint(entity1=v[1], entity2=g[3], addUndoState=False)
s.ObliqueDimension(vertex1=v[0], vertex2=v[1], textPoint=(-2.74313879013062, 4.107253074646), value=9.69879531860352)
############################################################################################################
# arc AB: g[5]; vertices: v[1], v[2]; center: v[3]; dimension: d[1], d[2]
s.ArcByCenterEnds(center=(0.0, 25.0), point1=(0.0, 9.69879531860352), point2=(12.5, 16.25), direction=COUNTERCLOCKWISE)
s.CoincidentConstraint(entity1=v[3], entity2=g[3], addUndoState=False)
s.RadialDimension(curve=g[5], textPoint=(0.0, 25.0), radius=15.3012046813965)
s.DistanceDimension(entity1=v[2], entity2=g[2], textPoint=(10.2107276916504, 0.387263298034668), value=16.2253352918232)
############################################################################################################
# arc BC: g[6]; vertices: v[2], v[4]; center: v[5]; dimension: d[3], d[4], d[5]
s.ArcByCenterEnds(center=(14.28, 20.4), point1=(12.5352352973954, 16.2253352918232), point2=(18.105, 18.36), direction=COUNTERCLOCKWISE)
s.RadialDimension(curve=g[6], textPoint=(14.28, 20.4), radius=4.52460266688154)
s.DistanceDimension(entity1=v[4], entity2=g[2], textPoint=(25.1469917297363, 0.726455688476563), value=18.2707752155852)
s.HorizontalDimension(vertex1=v[0], vertex2=v[4], textPoint=(13.597843170166, 9.39514636993408), value=17.9790121344733)
############################################################################################################
# line CD: g[7]; vertices: v[6], v[7];
s.Line(point1=(18.2722964707778, 18.2707752155852), point2=(22.88, 18.2707752155851))
s.HorizontalConstraint(entity=g[7], addUndoState=False)
s.CoincidentConstraint(entity1=v[4], entity2=v[6], addUndoState=False)
############################################################################################################
# line DE: g[8]; vertices: v[8], v[9]
s.Line(point1=(22.88, 18.2707752155851), point2=(25.0, 15.0))
s.CoincidentConstraint(entity1=v[7], entity2=v[8], addUndoState=False)
############################################################################################################
# line EF: g[9]; vertices: v[10], v[11]; dimension: d[6]
s.Line(point1=(25.0, 15.0), point2=(27.0926570892334, 15.0))
s.HorizontalConstraint(entity=g[9], addUndoState=False)
s.CoincidentConstraint(entity1=v[9], entity2=v[10], addUndoState=False)
s.HorizontalDimension(vertex1=v[9], vertex2=v[11], textPoint=(26.26096534729, 21.753303527832), value=2.0926570892334)
############################################################################################################
# line FG: g[10]; vertices: v[12], v[13]; dimension: d[7], d[8]
s.Line(point1=(27.0926570892334, 15.0), point2=(27.0926570892334, 0.0))
s.VerticalConstraint(entity=g[10], addUndoState=False)
s.PerpendicularConstraint(entity1=g[9], entity2=g[10], addUndoState=False)
s.CoincidentConstraint(entity1=v[11], entity2=v[12], addUndoState=False)
s.CoincidentConstraint(entity1=v[13], entity2=g[2], addUndoState=False)
s.AngularDimension(line1=g[8], line2=g[10], textPoint=(28.1420307159424, 4.75175142288208), value=32.9498701354191)
s.ObliqueDimension(vertex1=v[12], vertex2=v[13], textPoint=(37.2293167114258, 7.5186595916748), value=15.0)
############################################################################################################
# line GO: g[11]; vertices: v[14]; dimension: d[9]
s.Line(point1=(27.0926570892334, 0.0), point2=(0.0, 0.0))
s.CoincidentConstraint(entity1=v[13], entity2=v[14], addUndoState=False)
s.HorizontalConstraint(entity=g[11], addUndoState=False)
s.PerpendicularConstraint(entity1=g[10], entity2=g[11], addUndoState=False)
s.HorizontalDimension(vertex1=v[14], vertex2=v[0], textPoint=(6.52166271209717, 12.40220642089844), value=26.7993727529289)
############################################################################################################
s.sketchOptions.setValues(constructionGeometry=ON)
s.assignCenterline(line=g[2])
############################################################################################################
d[0].setValues(value=d1/2, ) # d1/2
d[1].setValues(value=r1, ) # r1
d[2].setValues(value=d2/2, ) # d2/2
d[3].setValues(value=r2, ) # r2
d[4].setValues(value=d3/2, ) # d3/2
d[5].setValues(value=l1/2, ) # l1/2
d[6].setValues(value=l2, ) # l2
d[7].setValues(value=theta, ) # theta
d[8].setValues(value=(d3-3.0)/2.0, ) # theta
d[9].setValues(value=l3/2, ) # l3/2

############################################################################################################
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseSolidRevolve(sketch=s, angle=90.0, flipRevolveDirection=ON)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
#del mdb.models['Model-1'].sketches['__profile__']

#createCoupon(modelName, partName, d1, r1, d2, r2, d3, l)
