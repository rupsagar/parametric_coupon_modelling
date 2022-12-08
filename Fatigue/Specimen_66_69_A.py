from abaqus import *
from abaqusConstants import *

class createCouponMarkA():
    def __init__(self, couponData):
        # method to initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.modelName = couponData["modelName"]
        self.partName = couponData["partName"]
        self.sketchName = couponData["sketchName"]
        self.partitionSketchName = couponData["partitionSketchName"]
        self.instanceName = couponData["instanceName"]
        self.phi1 = float(couponData["phi1"])
        self.phi2 = float(couponData["phi2"])
        self.phi3 = float(couponData["phi3"])
        self.rad1 = float(couponData["rad1"])
        self.rad2 = float(couponData["rad2"])
        self.len1 = float(couponData["len1"])
        self.len2 = float(couponData["len2"])
        self.partitionRadiusFraction = float(eval(couponData["partitionRadiusFraction"]))
        self.partitionRadius = float(self.partitionRadiusFraction*self.phi1/2.0)
        self.lenTol = float(couponData["lenTol"])
        self.seedSizeGlobal = float(couponData["seedSizeGlobal"])
        self.seedSizeArc = float(couponData["seedSizeArc"])
        self.seedSizeRadial = float(couponData["seedSizeRadial"])
        self.seedSizeLong = float(couponData["seedSizeLong"])
        # create coupon specimen
        self.__createModel()
        self.__createProfileSketch()
        self.__createSolid()
        self.__createPartition()
        self.__createMesh()
        self.__createAssembly()
    def __createModel(self):
        # define model
        self.model = mdb.Model(name=self.modelName)
        session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
    def __createProfileSketch(self):
        # method to calculate vertex coordinates
        self.coordO = (self.xO, self.yO) = (0, 0)
        self.coordA = (self.xA, self.yA) = (0, self.phi1/2)
        self.coordB = (self.xB, self.yB) = (self.rad1*(1-((self.rad1+self.phi1/2-self.phi2/2)/self.rad1)**2)**0.5, self.phi2/2)
        self.coordC = (self.xC, self.yC) = (self.len1/2, self.phi3/2)
        self.coordD = (self.xD, self.yD) = (self.len2/2, self.phi3/2)
        self.coordE = (self.xE, self.yE) = (self.len2/2, 0)
        self.coordCenter1 = (self.xC1, self.yC1) = (0, self.yA+self.rad1) # center 1
        self.coordCenter2 = (self.xC2, self.yC2) = ((self.xB+self.xC)/2,(self.yB+self.yC)/2) # arbitrary center 2 ==>> true value given by dimension
        # define sketch
        self.profileSketch = self.model.ConstrainedSketch(name=self.sketchName, sheetSize=200.0)
        self.profileGeometry, self.profileVertices = self.profileSketch.geometry, self.profileSketch.vertices
        self.profileSketch.setPrimaryObject(option=STANDALONE)
        # horizontal fixed construction line: self.profileGeometry[2]
        self.profileSketch.ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[2], addUndoState=False)
        self.profileSketch.FixedConstraint(entity=self.profileGeometry[2])
        self.profileSketch.assignCenterline(line=self.profileGeometry[2])
        # vertical fixed construction line: self.profileGeometry[3]
        self.profileSketch.ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.FixedConstraint(entity=self.profileGeometry[3])
        # line OA: self.profileGeometry[4]; vertices: self.profileVertices[0], self.profileVertices[1]; dimension: d[0]
        self.profileSketch.Line(point1=self.coordO, point2=self.coordA)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[4], addUndoState=False)
        self.profileSketch.PerpendicularConstraint(entity1=self.profileGeometry[2], entity2=self.profileGeometry[4], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[0], entity2=self.profileGeometry[2], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[1], entity2=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.ObliqueDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[1], textPoint=(-3, 4), value=self.phi1/2)
        (self.xO, self.yO), (self.xA, self.yA) = self.profileVertices[0].coords, self.profileVertices[1].coords
        # arc AB: self.profileGeometry[5]; vertices: self.profileVertices[1], self.profileVertices[2]; center: self.profileVertices[3]; dimension: d[1], d[2]
        self.profileSketch.ArcByCenterEnds(center=self.coordCenter1, point1=self.coordA, point2=self.coordB, direction=COUNTERCLOCKWISE)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[3], entity2=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.RadialDimension(curve=self.profileGeometry[5], textPoint=(0, 25), radius=self.rad1)
        self.profileSketch.DistanceDimension(entity1=self.profileVertices[2], entity2=self.profileGeometry[2], textPoint=(10, 1), value=self.phi2/2)
        (self.xB, self.yB), (self.xC1, self.yC1) = self.profileVertices[2].coords, self.profileVertices[3].coords
        # arc BC: self.profileGeometry[6]; vertices: self.profileVertices[2], self.profileVertices[4]; center: self.profileVertices[5]; dimension: d[3], d[4], d[5]
        self.profileSketch.ArcByCenterEnds(center=self.coordCenter2, point1=self.coordB, point2=self.coordC, direction=COUNTERCLOCKWISE)
        self.profileSketch.RadialDimension(curve=self.profileGeometry[6], textPoint=(14, 10), radius=self.rad2)
        self.profileSketch.DistanceDimension(entity1=self.profileVertices[4], entity2=self.profileGeometry[2], textPoint=(25, 1), value=self.phi3/2)
        self.profileSketch.HorizontalDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[4], textPoint=(13, 9), value=self.len1/2)
        (self.xC, self.yC), (self.xC2, self.yC2) = self.profileVertices[4].coords, self.profileVertices[5].coords
        # line CD: self.profileGeometry[7]; vertices: self.profileVertices[5], self.profileVertices[6]; dimension: d[6]
        self.profileSketch.Line(point1=self.coordC, point2=self.coordD)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[7], addUndoState=False)
        self.profileSketch.HorizontalDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[6], textPoint=(13, -9), value=self.len2/2)
        (self.xD, self.yD) = self.profileVertices[6].coords
        # line DE: self.profileGeometry[8]; vertices: self.profileVertices[6], self.profileVertices[7]
        self.profileSketch.Line(point1=self.coordD, point2=self.coordE)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[8], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[7], entity2=self.profileGeometry[2], addUndoState=False)
        (self.xE, self.yE) = self.profileVertices[7].coords
        # line EO: self.profileGeometry[9]; vertices: self.profileVertices[7], self.profileVertices[0]
        self.profileSketch.Line(point1=self.coordE, point2=self.coordO)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[9], addUndoState=False)
        self.profileSketch.unsetPrimaryObject()
    def __createSolid(self):
        self.part = self.model.Part(name=self.partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        self.part.BaseSolidRevolve(sketch=self.profileSketch, angle=90, flipRevolveDirection=ON)
        session.viewports['Viewport: 1'].setValues(displayedObject=self.part)
    def __createPartition(self):
        # partition-1
        self.sketchFace = self.part.faces.getByBoundingBox(xMin=-self.xB/2,yMin=-self.phi1, zMin=-self.phi1, xMax=self.xB/2,yMax=self.phi1,zMax=self.phi1)
        self.sketchEdge = self.part.edges.findAt(((0, self.partitionRadius, 0),))
        self.t = self.part.MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
        self.partitionSketch = self.model.ConstrainedSketch(name=self.partitionSketchName, sheetSize=4, transform=self.t)
        self.partitionSketchGeometry, self.partitionSketchVertices = self.partitionSketch.geometry, self.partitionSketch.vertices
        self.partitionSketch.setPrimaryObject(option=SUPERIMPOSE)
        self.part.projectReferencesOntoSketch(sketch=self.partitionSketch, filter=COPLANAR_EDGES)
        self.partitionSketch.ArcByCenterEnds(center=(0, 0), point1=(0, self.partitionRadius), point2=(-self.partitionRadius, 0), direction=COUNTERCLOCKWISE)
        self.projectionLine1 = self.partitionSketchGeometry.findAt((0, self.partitionRadius/2), 1)
        self.projectionLine2 = self.partitionSketchGeometry.findAt((-self.partitionRadius/2, 0), 1)
        self.vertexPoint1 = self.partitionSketchVertices.findAt((0, self.partitionRadius), 1)
        self.vertexPoint2 = self.partitionSketchVertices.findAt((-self.partitionRadius, 0), 1)
        self.partitionSketch.CoincidentConstraint(entity1=self.vertexPoint1, entity2=self.projectionLine1, addUndoState=False)
        self.partitionSketch.CoincidentConstraint(entity1=self.vertexPoint2, entity2=self.projectionLine2, addUndoState=False)
        self.partitionSketch.unsetPrimaryObject()
        self.part.PartitionFaceBySketch(sketchUpEdge=self.sketchEdge[0], faces=self.sketchFace[0], sketch=self.partitionSketch)
        self.partitionEdges = self.part.edges.getByBoundingCylinder((self.xO, 0, 0), (self.xB/2, 0, 0), (self.partitionRadius+self.yA)/2)
        self.pickedEdgesPartition = []
        for eachEdge in self.partitionEdges:
            if abs(eachEdge.getSize(0)-self.partitionRadius) >= self.lenTol:
                self.pickedEdgesPartition.append(eachEdge)
        self.sweepEdges = self.part.edges.getByBoundingCylinder((self.xO, 0, 0), (self.xE, 0, 0), self.partitionRadius/2)
        self.part.PartitionCellBySweepEdge(sweepPath=self.sweepEdges[0], cells=self.part.cells, edges=self.pickedEdgesPartition)
        #p.PartitionCellByExtrudeEdge(line=p.datums[1], cells=p.cells, edges=pickedEdges, sense=FORWARD)
        # partition-2
        self.datumPlane1_ID = self.part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(self.xB+self.xC)/2).id
        self.part.PartitionCellByDatumPlane(datumPlane=self.part.datums[self.datumPlane1_ID], cells=self.part.cells)
        # partition-3
        self.datumPlane1_ID = self.part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=(self.xC+self.xD)/2).id
        self.part.PartitionCellByDatumPlane(datumPlane=self.part.datums[self.datumPlane1_ID], cells=self.part.cells)
    def __createMesh(self):
        # global seed
        self.part.seedPart(size=self.seedSizeGlobal, deviationFactor=0.1, minSizeFactor=0.1)
        # mesh-1 ==>> cylinder
        self.seedEdges = self.part.edges.getByBoundingCylinder((self.xO, 0, 0), (self.xE, 0, 0), (self.partitionRadius+self.yA)/2)
        self.pickedEdgesArc, self.pickedEdgesRadial, self.pickedEdgesLong = [], [], []
        for eachEdge in self.seedEdges:
            try:
                eachEdge.getRadius()
                self.pickedEdgesArc.append(eachEdge)
            except:
                if abs(eachEdge.getSize(0)-self.partitionRadius) <= self.lenTol:
                    self.pickedEdgesRadial.append(eachEdge)
                else:
                    self.pickedEdgesLong.append(eachEdge)
        self.part.seedEdgeBySize(edges=self.pickedEdgesArc, size=self.seedSizeArc, deviationFactor=0.1, constraint=FINER)
        self.part.seedEdgeBySize(edges=self.pickedEdgesRadial, size=self.seedSizeRadial, deviationFactor=0.1, constraint=FINER)
        self.part.seedEdgeBySize(edges=self.pickedEdgesLong, size=self.seedSizeLong, deviationFactor=0.1, constraint=FINER)
        self.pickedCellsCyl = self.part.cells.getByBoundingCylinder((self.xO, 0, 0), (self.xE, 0, 0), (self.partitionRadius+self.yA)/2)
        self.part.generateMesh(regions=self.pickedCellsCyl)
        # mesh-2 ==>> sweep
        self.pickedCellsSweep = self.__getByBoundingHollowCylinder(self.part.cells, (self.xO, 0, 0), (self.xE, 0, 0), (self.partitionRadius+self.yA)/2, (self.yD+self.lenTol))
        self.part.setMeshControls(regions=self.pickedCellsSweep, elemShape=HEX_DOMINATED, technique=SWEEP, algorithm=ADVANCING_FRONT)
        #p.setSweepPath(region=pickedCellsSweep, edge=pickedEdgesArc[0], sense=FORWARD)
        self.part.generateMesh(regions=self.pickedCellsSweep)
    def __createAssembly(self):
        # assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.assembly.Instance(name=self.instanceName, part=self.part, dependent=ON)
    def __getByBoundingHollowCylinder(self, feature, center1, center2, innerRadius, outerRadius):
        pickedFeaturesInner = feature.getByBoundingCylinder(center1, center2, innerRadius)
        pickedFeaturesOuter = feature.getByBoundingCylinder(center1, center2, outerRadius)
        pickedFeatures = []
        for eachFeature in pickedFeaturesOuter:
            if eachFeature not in pickedFeaturesInner:
                pickedFeatures.append(eachFeature)
        return pickedFeatures

couponMarkA_Database = {
    "couponMarkA_Specimen1": {
        "modelName" : "couponMarkA_Specimen1",
        "partName" : "couponMarkA_Specimen1_Part",
        "sketchName" : "couponMarkA_Specimen1_Sketch1",
        "partitionSketchName" : "couponMarkA_Specimen1_Sketch2",
        "instanceName" : "couponMarkA_Specimen1_Sketch1_Instance",
        "phi1" : 2.82,
        "phi2" : 5.0,
        "phi3" : 8.0,
        "rad1" : 20.0,
        "rad2" : 10.0,
        "len1" : 24.0,
        "len2" : 40.0,
        "partitionRadiusFraction" : "2.0/3.0",
        "lenTol" : 1.0e-6,
        "seedSizeGlobal" : 0.1,
        "seedSizeArc" : 0.1,
        "seedSizeRadial" : 0.1,
        "seedSizeLong" : 0.1,
    },
}

p = createCouponMarkA(couponMarkA_Database["couponMarkA_Specimen1"])
couponList = []
couponList.append(p)

############################################################################################################
# sets
#side1Faces = p.faces.findAt(((xB, yB/2, 0),))
#p.Surface(side1Faces=side1Faces, name='Surf-1')
# nodes = p.nodes.getSequenceFromMask(mask=(
#     '[#bae #0:2 #ffc00000 #ffffffff:5 #3f003fff #0 #fffff000', 
#     ' #ffffffff #3ffffff #7ff800 #fffffffe #ffffffff #3f #0', 
#     ' #fffc0000 #ffffffff #7fffff #0:48 #ffffff00 #ffffffff:15 #3fffffff', 
#     ' #0:21 #e0000000 #ffffffff:7 #7f #0:23 #fffffe00 #ffffffff:12', 
#     ' #7f #0:328 #ffff0000 #ffffffff:82 #ffff #0:28 #c0000000', 
#     ' #ffffffff:3 #1f #0:3 #fffffff8 #ffffffff:2 #7 #0:2', 
#     ' #fffffe00 #ffffffff:2 #e33f #0:41 #ffc00000 #ffffffff:38 #3fffff', 
#     ' #0:67 #ffffffe0 #ffffffff:34 #3fff ]', ), )
# p.Set(nodes=nodes, name='Set-1')
