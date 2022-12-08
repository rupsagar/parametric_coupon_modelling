from abaqus import *
from abaqusConstants import *
s = mdb.models['Model-1'].ConstrainedSketch(name='Test_Sketch', sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
## horizontal construction line
s.ConstructionLine(point1=(-56.25, 0.0), angle=0.0)
s.HorizontalConstraint(entity=g[2], addUndoState=False)
s.FixedConstraint(entity=g[2])
## vertical construction line
s.ConstructionLine(point1=(0.0, -23.75), angle=90.0)
s.VerticalConstraint(entity=g[3], addUndoState=False)
s.FixedConstraint(entity=g[3])
## line OA
s.Line(point1=(0.0, 0.0), point2=(0.0, 4.90000152587891))
s.VerticalConstraint(entity=g[4], addUndoState=False)
s.PerpendicularConstraint(entity1=g[2], entity2=g[4], addUndoState=False)
s.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)
s.CoincidentConstraint(entity1=v[1], entity2=g[3], addUndoState=False)
## arc AB
s.ArcByCenterEnds(center=(0.0, 15.0), point1=(0.0, 4.90000152587891), point2=(8.75, 7.5), direction=COUNTERCLOCKWISE)
s.CoincidentConstraint(entity1=v[3], entity2=g[3], addUndoState=False)
# line BC
s.Line(point1=(7.66849052535586, 8.42700812112355), point2=(12.2310549929855, 13.75))
s.TangentConstraint(entity1=g[5], entity2=g[6], addUndoState=False)
# line CD
s.Line(point1=(12.2310549929855, 13.75), point2=(35.0, 13.75))
s.HorizontalConstraint(entity=g[7], addUndoState=False)
# arc DE
s.ArcByCenterEnds(center=(35.0, 25.0), point1=(35.0, 13.75), point2=(45.0, 21.25), direction=COUNTERCLOCKWISE)
s.TangentConstraint(entity1=g[7], entity2=g[8], addUndoState=False)
# line EF
s.Line(point1=(45.5337032476518, 21.0498612821306), point2=(65.0, 21.0498612821306))
s.HorizontalConstraint(entity=g[9], addUndoState=False)
# line FG
s.Line(point1=(65.0, 21.0498612821306), point2=(65.0, 0.0))
s.VerticalConstraint(entity=g[10], addUndoState=False)
s.PerpendicularConstraint(entity1=g[9], entity2=g[10], addUndoState=False)
s.CoincidentConstraint(entity1=v[9], entity2=g[2], addUndoState=False)
# line GO
s.Line(point1=(65.0, 0.0), point2=(0.0, 0.0))
s.HorizontalConstraint(entity=g[11], addUndoState=False)
s.PerpendicularConstraint(entity1=g[10], entity2=g[11], addUndoState=False)
## set dimension
s.ObliqueDimension(vertex1=v[1], vertex2=v[0], textPoint=(-11.9687423706055, 0.0), value=1.41)
s.RadialDimension(curve=g[5], textPoint=(0.0, 15.0), radius=0.71)
s.AngularDimension(line1=g[6], line2=g[3], textPoint=(7.55055284500122, 23.6966972351074), value=60)
s.DistanceDimension(entity1=v[4], entity2=g[2], textPoint=(72.856689453125, 8.725417137146), value=2.5)
s.RadialDimension(curve=g[8], textPoint=(0.0, 15.0), radius=10)
s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(11.3766393661499, -9.80960273742676), value=12.0)
s.DistanceDimension(entity1=v[8], entity2=g[2], textPoint=(72.856689453125, 8.725417137146), value=4.0)
s.HorizontalDimension(vertex1=v[0], vertex2=v[9], textPoint=(11.3766393661499, -9.80960273742676), value=20.0)
#s.HorizontalDimension(vertex1=v[4], vertex2=v[5], textPoint=(11.3766393661499, -9.80960273742676), value=6.0)

s.ObliqueDimension(vertex1=v[1], vertex2=v[0], textPoint=(-11.9687423706055, 0.0), value=4.90000152587891)
s.RadialDimension(curve=g[5], textPoint=(0.0, 15.0), radius=10.0999984741211)
s.undo()
s.RadialDimension(curve=g[5], textPoint=(0.0, 10.7603483200073), 
    radius=10.0999984741211)
s.undo()
s.RadialDimension(curve=g[5], textPoint=(10.0176773071289, -7.69938373565674), 
    radius=10.0999984741211)
s.AngularDimension(line1=g[6], line2=g[3], textPoint=(7.55055284500122, 
    23.6966972351074), value=40.6012946451364)
s.DistanceDimension(entity1=v[4], entity2=g[2], textPoint=(-38.3088607788086, 
    -3.77487277984619), value=13.75)
s.undo()
s.redo()
s.RadialDimension(curve=g[8], textPoint=(37.156005859375, 21.2257118225098), 
    radius=11.25)
s.HorizontalDimension(vertex1=v[0], vertex2=v[5], textPoint=(33.6730041503906, 
    -13.9495286941528), value=35.0)
s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(72.856689453125, 
    8.725417137146), value=21.0498612821306)
s.ObliqueDimension(vertex1=v[0], vertex2=v[9], textPoint=(65.455322265625, 
    -20.7810821533203), value=65.0)
#: Warning: The types of entities do not match.
#: Warning: The types of entities do not match.
#: Warning: The types of entities do not match.
#: Warning: The types of entities do not match.
s.CoincidentConstraint(entity1=g[9], entity2=v[6])
s.CoincidentConstraint(entity1=g[9], entity2=v[6])
s.delete(objectList=(d[5], ))
s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(37.5794410705566, 
    -14.9029569625854), value=45.5337032476518)
d[8].setValues(value=12, )
d[0].setValues(value=1.41, )
d[4].setValues(value=0.71, )
d[2].setValues(value=60, )
d[3].setValues(value=2.5, )
d[6].setValues(value=4, )
d[7].setValues(value=20, )
s.delete(objectList=(d[8], ))
d[4].setValues(value=10, )
d[1].setValues(value=0.71, )
s.delete(objectList=(g[8], ))
s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(11.3766393661499, 
    -9.80960273742676), value=12.0)
s.delete(objectList=(c[21], ))
s.delete(objectList=(g[7], ))
s.delete(objectList=(d[3], ))
s.delete(objectList=(d[0], ))
s.delete(objectList=(d[7], ))
s.delete(objectList=(d[1], ))
s.delete(objectList=(d[9], ))
s.delete(objectList=(d[6], ))
s.delete(objectList=(d[2], ))
s.ObliqueDimension(vertex1=v[1], vertex2=v[0], textPoint=(-1.22840213775635, 
    0.0), value=1.41)
s.AngularDimension(line1=g[6], line2=g[3], textPoint=(2.32786226272583, 
    4.49307250976563), value=60.0)
s.RadialDimension(curve=g[5], textPoint=(0.0, 2.12), radius=0.710000000000001)
s.HorizontalDimension(vertex1=v[0], vertex2=v[6], textPoint=(10.9902830123901, 
    -2.46271371841431), value=12.0)
s.HorizontalDimension(vertex1=v[0], vertex2=v[9], textPoint=(19.7792129516602, 
    -3.90624475479126), value=20.0)
s.ArcByCenterEnds(center=(8.75, 7.5), point1=(12.0, 4.0), point2=(
    9.0120677947998, 3.28310441970825), direction=CLOCKWISE)
s.Line(point1=(2.07817930687618, 2.5), point2=(9.04625806659737, 
    2.73295362326146))
s.HorizontalConstraint(entity=g[13])
s.TangentConstraint(entity1=g[13], entity2=g[12])
s.RadialDimension(curve=g[12], textPoint=(8.75993256267104, 7.50919691689717), 
    radius=4.77624329363571)
d[15].setValues(value=10, )
s.CoincidentConstraint(entity1=v[2], entity2=v[4])
s.undo()
s.undo()
s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(23.5185203552246, 
    2.47002792358398), value=3.99999999999999)
d[15].setValues(value=10, )
s.DistanceDimension(entity1=g[13], entity2=g[2], textPoint=(-10.3912420272827, 
    -0.0513620376586914), value=5.0)
s.delete(objectList=(d[15], ))
s.delete(objectList=(g[12], ))
d[17].setValues(value=2.5, )
s.ArcByCenterEnds(center=(6.25, 8.75), point1=(12.0, 4.0), point2=(
    5.21628476998583, 2.5), direction=CLOCKWISE)
s.CoincidentConstraint(entity1=v[12], entity2=g[13], addUndoState=False)
s.undo()
s.ArcByCenterEnds(center=(5.0, 10.0), point1=(12.0, 4.0), point2=(
    5.21628476998583, 2.5), direction=CLOCKWISE)
s.CoincidentConstraint(entity1=v[12], entity2=g[13], addUndoState=False)
s.RadialDimension(curve=g[14], textPoint=(6.43621349334717, 8.46325302124023), 
    radius=10.0)
s.TangentConstraint(entity1=g[14], entity2=g[13])
s.CoincidentConstraint(entity1=v[10], entity2=v[12])
