#################################################################################################################
###################                 ABAQUS PARAMETRIC COUPON MODEL                     ##########################
#################################################################################################################
#######################    CLASS DEFINITION : FATIGUE COUPON : SPECIMEN 66 TO 69, A    ##########################
#################################################################################################################
## +------------------------------------------------------------------------------------------------------------+
## |            PROGRAMMER          |  VERSION  |    DATE     |                     COMMENTS                    |
## +------------------------------------------------------------------------------------------------------------+
## |        Rupsagar Chatterjee     |   v1.0    | 21-Mar-2023 |                                                 |
## |        Rupsagar Chatterjee     |   v2.0    | 24-Aug-2023 |                                                 |
## |                                |           |             |                                                 |
## |                                |           |             |                                                 |
## +------------------------------------------------------------------------------------------------------------+
#################################################################################################################


from abaqus import *
from abaqusConstants import *
from caeModules import *

class coupon_01_fatigue_66_69_a(coupon_generic):
    def __init__(self, couponData):
        super(coupon_01_fatigue_66_69_a, self).__init__(couponData)
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.phi1 = self.geometry['phi1']
        self.phi2 = self.geometry['phi2']
        self.phi3 = self.geometry['phi3']
        self.rad1 = self.geometry['rad1']
        self.rad2 = self.geometry['rad2']
        self.len1 = self.geometry['len1']
        self.len2 = self.geometry['len2']
        self.seedSizeArcOuter = self.seedSize['arcOuter']
        self.seedSizeLong1 = self.seedSize['long1']
        self.seedSizeLong2 = self.seedSize['long2']
        self.seedSizeLong3 = self.seedSize['long3']
        ## derived quantities
        self.partitionRadialFraction = 0.67
        self.partitionRadius = self.partitionRadialFraction*self.phi1/2
        self.endStress = -self.stepLoad*(self.phi1/self.phi3)**2
        self.seedSizeOuterRadialMin = self.seedSizeArcOuter*self.partitionRadialFraction
        self.seedSizeInnerRadial = self.seedSizeArcOuter*self.partitionRadialFraction
        ## create coupon
        self.createModel()
        self.createProfileSketch()
        self.createPart()
        self.createAssembly()
        self.createPartition()
        self.createLocalSeed()
        self.createMesh()
        self.createMaterial()
        self.createSection()
        self.createStep()
        self.createLoadBC()
        self.createJob()
    def createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates
        (self.xo, self.yo) = (self.xO, self.yO) = (0, 0)
        (self.xa, self.ya) = (self.xA, self.yA) = (0, self.phi1/2)
        (self.xb, self.yb) = (self.xB, self.yB) = (self.rad1*(1-((self.rad1+self.phi1/2-self.phi2/2)/self.rad1)**2)**0.5, self.phi2/2)
        (self.xc, self.yc) = (self.xC, self.yC) = (self.len1/2, self.phi3/2)
        (self.xd, self.yd) = (self.xD, self.yD) = (self.len2/2, self.phi3/2)
        (self.xe, self.ye) = (self.xE, self.yE) = (self.len2/2, 0)
        (self.xc1, self.yc1) = (self.xC1, self.yC1) = (0, self.yA+self.rad1) # center 1
        (self.xc2, self.yc2) = (self.xC2, self.yC2) = (self.xB, (self.yB+self.rad2))
        #################################################################################################################################################
        self.profileSketch = 1*[None]
        ## define sketch ==>> area of interest  #########################################################################################################
        self.profileSketch[0] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_1', sheetSize=200.0)
        self.profileGeometry1, self.profileVertices1 = self.profileSketch[0].geometry, self.profileSketch[0].vertices
        self.profileSketch[0].setPrimaryObject(option=STANDALONE)
        ## horizontal fixed construction line ==>> self.profileGeometry1[2]
        self.profileSketch[0].ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[2])
        self.profileSketch[0].assignCenterline(line=self.profileGeometry1[2])
        ## vertical fixed construction line ==>> self.profileGeometry1[3]
        self.profileSketch[0].ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[3])
        ## line OA: self.profileGeometry1[4]; vertices ==>> self.profileVertices1[0], self.profileVertices1[1]; dimension: d[0]
        self.profileSketch[0].Line(point1=(self.xO, self.yO), point2=(self.xA, self.yA))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[2], entity2=self.profileGeometry1[4], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].ObliqueDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[1], textPoint=(-3, 4), value=self.phi1/2)
        ## arc AB: self.profileGeometry1[5]; vertices ==>> self.profileVertices1[1], self.profileVertices1[2]; center: self.profileVertices1[3]; dimension: d[1], d[2]
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC1, self.yC1), point1=self.profileVertices1[1].coords, point2=(self.xB, self.yB), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[3], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[5], textPoint=(0, 25), radius=self.rad1)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[2], entity2=self.profileGeometry1[2], textPoint=(10, 1), value=self.phi2/2)
        ## horizontal fixed construction line at point B ==>> self.profileGeometry1[6]
        self.profileSketch[0].ConstructionLine(point1=self.profileVertices1[2].coords, angle=0)
        self.profileSketch[0].FixedConstraint(entity=self.profileGeometry1[6])
        ## arc BC: self.profileGeometry1[6]; vertices ==>> self.profileVertices1[2], self.profileVertices1[4]; center: self.profileVertices1[5]; dimension: d[3], d[4], d[5]
        self.profileSketch[0].ArcByCenterEnds(center=(self.xC2, self.yC2), point1=self.profileVertices1[2].coords, point2=(self.xC, self.yC), direction=COUNTERCLOCKWISE)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[7], textPoint=(14, 10), radius=self.rad2)
        self.profileSketch[0].DistanceDimension(entity1=self.profileVertices1[4], entity2=self.profileGeometry1[2], textPoint=(25, 1), value=self.phi3/2)
        self.profileSketch[0].TangentConstraint(entity1=self.profileGeometry1[6], entity2=self.profileGeometry1[7], addUndoState=False)
        ## line CD: self.profileGeometry1[7]; vertices ==>> self.profileVertices1[5], self.profileVertices1[6]; dimension: d[6]
        self.profileSketch[0].Line(point1=self.profileVertices1[4].coords, point2=(self.xD, self.yD))
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[0], vertex2=self.profileVertices1[6], textPoint=(13, -9), value=self.len2/2)
        ## line DE: self.profileGeometry1[8]; vertices ==>> self.profileVertices1[6], self.profileVertices1[7]
        self.profileSketch[0].Line(point1=self.profileVertices1[6].coords, point2=(self.xE, self.yE))
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[9], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[7], entity2=self.profileGeometry1[2], addUndoState=False)
        ## line EO: self.profileGeometry1[9]; vertices ==>> self.profileVertices1[7], self.profileVertices1[0]
        self.profileSketch[0].Line(point1=self.profileVertices1[7].coords, point2=self.profileVertices1[0].coords)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[10], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        (self.xO, self.yO) = self.profileVertices1[0].coords
        (self.xA, self.yA) = self.profileVertices1[1].coords
        (self.xB, self.yB) = self.profileVertices1[2].coords
        (self.xC1, self.yC1) = self.profileVertices1[3].coords
        (self.xC, self.yC) = self.profileVertices1[4].coords
        (self.xC2, self.yC2) = self.profileVertices1[5].coords
        (self.xD, self.yD) = self.profileVertices1[6].coords
        (self.xE, self.yE) = self.profileVertices1[7].coords
        #######################################################################################################################################################
        self.geomData = [['O', self.xo, self.yo, self.xO, self.yO],
                     ['A', self.xa, self.ya, self.xA, self.yA],
                     ['B', self.xb, self.yb, self.xB, self.yB],
                     ['C', self.xc, self.yc, self.xC, self.yC],
                     ['D', self.xd, self.yd, self.xD, self.yD],
                     ['E', self.xe, self.ye, self.xE, self.yE],
                     ['C1', self.xc1, self.yc1, self.xC1, self.yC1],
                     ['C2', self.xc2, self.yc2, self.xC2, self.yC2],
                     ['phi1', '', self.phi1, '', 2*(self.yA-self.yO)],
                     ['phi2', '', self.phi2, '', 2*(self.yB-self.yO)],
                     ['phi3', '', self.phi3, '', 2*(self.yC-self.yO)],
                     ['rad1', '', self.rad1, '', ((self.xC1-self.xB)**2+(self.yC1-self.yB)**2)**0.5],
                     ['rad2', '', self.rad2, '', ((self.xC2-self.xB)**2+(self.yC2-self.yB)**2)**0.5],
                     ['len1', '', self.len1, '', 2*(self.xC-self.xO)],
                     ['len2', '', self.len2, '', 2*(self.xD-self.xO)]]
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
        def createPartitionCyl():
            ## partition ==>> inner cylinder
            self.sketchFace = self.part[0].faces.getByBoundingCylinder((-self.lenTol, 0, 0), (self.lenTol, 0, 0), (self.yA+self.lenTol))
            self.sketchEdge = self.part[0].edges.findAt(((0, self.partitionRadius, 0),))
            self.transform = self.part[0].MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            self.partitionSketch = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch', sheetSize=4, transform=self.transform)
            self.partitionSketchGeometry, self.partitionSketchVertices = self.partitionSketch.geometry, self.partitionSketch.vertices
            self.partitionSketch.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=self.partitionSketch, filter=COPLANAR_EDGES)
            self.partitionSketch.ArcByCenterEnds(center=(0, 0), point1=(0, self.partitionRadius), point2=(-self.partitionRadius, 0), direction=COUNTERCLOCKWISE)
            self.projectionLine1 = self.partitionSketchGeometry.findAt((0, self.partitionRadius/2), 1)
            self.projectionLine2 = self.partitionSketchGeometry.findAt((-self.partitionRadius/2, 0), 1)
            self.vertexPoint1 = self.partitionSketchVertices.findAt((0, self.partitionRadius), 1)
            self.vertexPoint2 = self.partitionSketchVertices.findAt((-self.partitionRadius, 0), 1)
            self.partitionSketch.CoincidentConstraint(entity1=self.vertexPoint1, entity2=self.projectionLine1, addUndoState=False)
            self.partitionSketch.CoincidentConstraint(entity1=self.vertexPoint2, entity2=self.projectionLine2, addUndoState=False)
            self.partitionSketch.unsetPrimaryObject()
            self.part[0].PartitionFaceBySketch(sketchUpEdge=self.sketchEdge[0], faces=self.sketchFace[0], sketch=self.partitionSketch)
            edgesTemp = self.part[0].edges.getByBoundingCylinder((-self.lenTol, 0, 0), (self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            self.edgesArcForPartition = self.getArcEdge(edgesTemp)
            self.sweepEdges = self.part[0].edges.getByBoundingCylinder((-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.partitionRadius-self.lenTol))
            self.part[0].PartitionCellBySweepEdge(sweepPath=self.sweepEdges[0], cells=self.part[0].cells, edges=self.edgesArcForPartition)
        def createPartitionLong(offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = self.part[0].DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            self.part[0].PartitionCellByDatumPlane(datumPlane=self.part[0].datums[self.datumPlane_ID], cells=self.part[0].cells)
        createPartitionCyl()
        createPartitionLong(self.xB)
        createPartitionLong(self.xC)
    def createLocalSeed(self):
        def seedOuterRadial(pointOnRadius, **kwargs):
            ## method to seed the outer radial edge at sections through A and B
            edgesOuterRadial = self.part[0].edges.findAt((pointOnRadius, ))  
            edgesRadialVertexIDPair = edgesOuterRadial[0].getVertices()
            for thisVertexID in edgesRadialVertexIDPair:
                vertexCoord = self.part[0].vertices[thisVertexID].pointOn
                if abs(abs(vertexCoord[0][1])-self.partitionRadius) < self.lenTol or abs(abs(vertexCoord[0][2])-self.partitionRadius) < self.lenTol or abs(abs(vertexCoord[0][2])-self.partitionRadius) < self.lenTol:
                    if edgesRadialVertexIDPair.index(thisVertexID) == 0:
                        if 'minSize' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end1Edges=edgesOuterRadial, minSize=kwargs['minSize'], maxSize=kwargs['maxSize'], constraint=FIXED)
                        elif 'ratio' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end1Edges=edgesOuterRadial, ratio=kwargs['ratio'], number=kwargs['number'], constraint=FIXED)
                    elif edgesRadialVertexIDPair.index(thisVertexID) == 1:
                        if 'minSize' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end2Edges=edgesOuterRadial, minSize=kwargs['minSize'], maxSize=kwargs['maxSize'], constraint=FIXED)
                        elif 'ratio' in kwargs.keys():
                            self.part[0].seedEdgeByBias(biasMethod=SINGLE, end2Edges=edgesOuterRadial, ratio=kwargs['ratio'], number=kwargs['number'], constraint=FIXED)
        def seedLongEdges(xLeft, xRight, seedSize):
            ## method to seed the longitudinal edges
            edgesInnerArcLong = self.part[0].edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.yD+self.lenTol))
            edgesInnerArc = self.getArcEdge(edgesInnerArcLong)
            edgesStraight = self.getByDifference(edgesInnerArcLong, edgesInnerArc)
            edgesLong = self.getEdgeByLength(edgesStraight, abs(xRight-xLeft))
            self.part[0].seedEdgeBySize(edges=edgesLong, size=seedSize, deviationFactor=0.1, constraint=FINER)
        def setInnerCylSweepPath(xLeft, xRight):
            ## method to set the sweep path for the inner cylindrical mesh
            cellsInnerCyl = self.part[0].cells.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
            edgesSweepPath = self.part[0].edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), self.lenTol)
            self.part[0].setMeshControls(regions=cellsInnerCyl, technique=SWEEP, algorithm=ADVANCING_FRONT)
            self.part[0].setSweepPath(region=cellsInnerCyl[0], edge=edgesSweepPath[0], sense=FORWARD)
        ## seed ==>> outer arc edge AA'
        self.edgesOuterCyl = self.getByCylinderDifference(self.part[0].edges, (self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArc = self.getArcEdge(self.edgesOuterCyl)
        self.part[0].seedEdgeBySize(edges=self.edgesOuterArc, size=self.seedSizeArcOuter, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> outer radial edges
        self.edgesOuterRadial = self.getByDifference(self.edgesOuterCyl, self.edgesOuterArc)
        seedOuterRadial((0.0, self.partitionRadius+self.lenTol, 0.0), minSize=self.seedSizeOuterRadialMin, maxSize=self.seedSizeArcOuter)
        seedOuterRadial((0.0, 0.0, -(self.partitionRadius+self.lenTol)), minSize=self.seedSizeOuterRadialMin, maxSize=self.seedSizeArcOuter)
        ## seed ==>> edge Bb ==>> not applied; seeding with increase the element size at the surface by small amount
        self.edgesOuterCylAtB = self.getByCylinderDifference(self.part[0].edges, (self.xB-self.lenTol, 0, 0), (self.xB+self.lenTol, 0, 0), (self.yB+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArcAtB = self.getArcEdge(self.edgesOuterCylAtB)
        self.edgesOuterRadialAtB = self.getByDifference(self.edgesOuterCylAtB, self.edgesOuterArcAtB)
        ratioBias = self.part[0].getEdgeSeeds(self.edgesOuterRadial[0], attribute=BIAS_RATIO)
        elemNum = self.part[0].getEdgeSeeds(self.edgesOuterRadial[0], attribute=NUMBER)
        #seedOuterRadial((self.xB, self.partitionRadius+self.lenTol, 0.0), ratio=ratioBias, number=elemNum)
        #seedOuterRadial((self.xB, 0.0, -(self.partitionRadius+self.lenTol)), ratio=ratioBias, number=elemNum)
        ## seed ==>> longitudinal edges
        seedLongEdges(self.xA, self.xB, self.seedSizeLong1)
        seedLongEdges(self.xB, self.xC, self.seedSizeLong2)
        seedLongEdges(self.xC, self.xD, self.seedSizeLong3)
        ## seed ==>> inner radial edges
        self.edgesInnerCyl = self.part[0].edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xB-self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        self.edgesInnerArc = self.getArcEdge(self.edgesInnerCyl)
        self.edgesInnerRadial = self.getByDifference(self.edgesInnerCyl, self.edgesInnerArc)
        self.part[0].seedEdgeBySize(edges=self.edgesInnerRadial, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        ## sweep path ==>> inner cylinder
        setInnerCylSweepPath(self.xA, self.xB)
        setInnerCylSweepPath(self.xB, self.xC)
        setInnerCylSweepPath(self.xC, self.xD)
    def createLoadBC(self):
        ## create load and boundary conditions
        self.couponData['Step'].update({'End_Pressure':self.endStress})
        for i in range(len(self.part)):
            ## create BC at negY face
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin=-self.lenTol, zMin=-self.yD-self.lenTol, xMax=self.xE+self.lenTol, yMax=self.lenTol, zMax=self.lenTol)
            nsetNameNegY = 'Nset_BC_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at posZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xE+self.lenTol, yMax=self.yD+self.lenTol, zMax=self.lenTol)
            nsetNamePosZ = 'Nset_BC_PosZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesPosZ, name=nsetNamePosZ)
            region = self.instance[i].sets[nsetNamePosZ]
            self.model.DisplacementBC(name='BC_PosZ_Instance_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==0:
                ## create BC at negX face
                nodesNegX = self.part[i].nodes.getByBoundingCylinder((self.xO-self.lenTol, 0, 0), (self.xO+self.lenTol, 0, 0), (self.yA+self.lenTol))
                nsetNameNegX = 'Nset_BC_NegX_Part_'+str(i+1)
                self.part[i].Set(nodes=nodesNegX , name=nsetNameNegX)
                region = self.instance[i].sets[nsetNameNegX]
                self.model.DisplacementBC(name='BC_NegX_Instance_'+str(i+1), createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
            if i==(len(self.part)-1):
                ## create pressure load on posX face
                endCellFaceArr = self.part[i].faces.getByBoundingCylinder((self.xE-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.yD+self.lenTol))
                surfNamePosX = 'Surf_Load_PosX_Part_'+str(i+1)
                self.getElemSurfFromCellFace(self.part[i], endCellFaceArr, surfNamePosX)
                region = self.instance[i].surfaces[surfNamePosX]
                self.model.Pressure(name='Load_PosX_Instance_'+str(i+1), createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=self.endStress, amplitude=UNSET)
    
