import json
import math

from abaqus import *
from abaqusConstants import *
from caeModules import *

class fatigue_coupon_74_75():
    def __init__(self, couponData):
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.couponData = couponData
        self.couponName = couponData['couponName']
        self.len = couponData['geometry']['len']
        self.width = couponData['geometry']['width']
        self.thickness = couponData['geometry']['thickness']
        self.phi = couponData['geometry']['phi']
        self.chamferEdgeLength = couponData['geometry']['chamferEdgeLength']
        self.chamferAngle = couponData['geometry']['chamferAngle']
        self.isChamfer = couponData['isChamfer']
        self.givenKt = couponData['givenKt']
        self.lenTol = couponData['lenTol']
        self.seedSizeThickness1 = couponData['elemSize']['thickness1']
        self.seedSizeThickness2 = couponData['elemSize']['thickness2']
        self.seedSizeArc = couponData['elemSize']['arc']
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
        self.thetaRad = math.pi/180*self.chamferAngle
        self.endStress = -self.nominalStress*(self.width-self.phi)/self.width
        self.tieDistance = 2.0*self.phi
        if (self.tieDistance-self.width/2)<=self.lenTol:
            self.tieDistance = self.tieDistance+self.width/2
        if isinstance(self.isChamfer, float):
            self.isChamfer = str(self.isChamfer)
        if self.isChamfer.lower() in ['1.0', 'true', 'yes', 'on']:
            self.provideChamfer = True
        elif self.isChamfer.lower() in ['0.0', 'false', 'no', 'off', '']:
            self.provideChamfer = False
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
        self.coordA = (self.xA, self.yA) = (0.0, self.phi/2.0)
        self.coordB = (self.xB, self.yB) = (self.phi/2.0, 0.0)
        self.coordC = (self.xC, self.yC) = (0.0, self.width/2.0)
        self.coordD = (self.xD, self.yD) = (self.tieDistance, 0.0)
        self.coordE = (self.xE, self.yE) = (self.xD, self.width/2.0)
        self.coordF = (self.xF, self.yF) = (self.len/2.0, 0.0)
        self.coordG = (self.xG, self.yG) = (self.len/2.0, self.width/2.0)
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
        ## arc AB
        self.profileSketch[0].ArcByCenterEnds(center=self.coordO, point1=self.coordA, point2=self.coordB, direction=CLOCKWISE)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[0], entity2=self.profileGeometry1[3], addUndoState=False)
        self.profileSketch[0].CoincidentConstraint(entity1=self.profileVertices1[1], entity2=self.profileGeometry1[2], addUndoState=False)
        self.profileSketch[0].RadialDimension(curve=self.profileGeometry1[4], textPoint=(0.0, 5.0), radius=self.phi/2.0)
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[2])
        self.profileSketch[0].PerpendicularConstraint(entity1=self.profileGeometry1[4], entity2=self.profileGeometry1[3])
        ## line AC
        self.profileSketch[0].Line(point1=self.coordA, point2=self.coordC)
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[5], addUndoState=False)
        self.profileSketch[0].VerticalDimension(vertex1=self.profileVertices1[2], vertex2=self.profileVertices1[3], textPoint=(-15.0, 15.0), value=self.width/2.0)
        ## line BD
        self.profileSketch[0].Line(point1=self.coordB, point2=self.coordD)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[6], addUndoState=False)
        self.profileSketch[0].HorizontalDimension(vertex1=self.profileVertices1[2], vertex2=self.profileVertices1[4], textPoint=(50.0, -5.0), value=self.xD)
        ## line CE
        self.profileSketch[0].Line(point1=self.coordC, point2=self.coordE)
        self.profileSketch[0].HorizontalConstraint(entity=self.profileGeometry1[7], addUndoState=False)
        ## line DE
        self.profileSketch[0].Line(point1=self.coordD, point2=self.coordE)
        self.profileSketch[0].VerticalConstraint(entity=self.profileGeometry1[8], addUndoState=False)
        #######################################################################################################################################################
        self.profileSketch[0].unsetPrimaryObject()
        #######################################################################################################################################################
        ## define sketch ==>> part 2 ==>> away from area of interest  #########################################################################################
        self.profileSketch[1] = self.model.ConstrainedSketch(name=self.couponName+'_Profile_Sketch_2', sheetSize=200.0)
        self.profileSketch[1].setPrimaryObject(option=STANDALONE)        
        self.profileSketch[1].rectangle(point1=self.coordD, point2=self.coordG)
        self.profileSketch[1].unsetPrimaryObject()
        if self.provideChamfer==True:
            ## calculate vertex coordinates for chamfer ###########################################################################################################
            self.coordODash = (self.xODash, self.yODash) = (0.0, 0.0)
            self.coordADash = (self.xADash, self.yADash) = (-self.chamferEdgeLength, self.chamferEdgeLength*math.tan(self.thetaRad))
            self.coordBDash = (self.xBDash, self.yBDash) = (0.0, self.yADash)
            #######################################################################################################################################################
            self.sketchChamferSweepPath = self.model.ConstrainedSketch(name=self.couponName+'_Temp_Sweep_Path', sheetSize=200.0)
            self.sketchChamferSweepPath.setPrimaryObject(option=STANDALONE)
            self.sketchChamferSweepPath.ArcByCenterEnds(center=self.coordO, point1=self.coordA, point2=self.coordB, direction=CLOCKWISE)
            self.sketchChamferSweepPath.unsetPrimaryObject()
            ## define sketch ==>> temp part chamfer    ###################################################################
            self.sketchChamferProfile = self.model.ConstrainedSketch(name=self.couponName+'_Temp_Profile_Sketch', sheetSize=200.0, transform=(0.0, -1.0, 0.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            self.profileGeometryChamfer, self.profileVerticesChamfer = self.sketchChamferProfile.geometry, self.sketchChamferProfile.vertices
            self.sketchChamferProfile.setPrimaryObject(option=SUPERIMPOSE)
            ## horizontal fixed construction line
            self.sketchChamferProfile.ConstructionLine(point1=(-50.0, 0.0), angle=0.0)
            self.sketchChamferProfile.FixedConstraint(entity=self.profileGeometryChamfer[2])
            ## vertical fixed construction line
            self.sketchChamferProfile.ConstructionLine(point1=(0.0, -25.0), angle=90.0)
            self.sketchChamferProfile.FixedConstraint(entity=self.profileGeometryChamfer[3])
            ## line O'A'
            self.sketchChamferProfile.Line(point1=self.coordODash, point2=self.coordADash)
            self.sketchChamferProfile.CoincidentConstraint(entity1=self.profileVerticesChamfer[0], entity2=self.profileGeometryChamfer[2], addUndoState=False)
            ## line A'B'
            self.sketchChamferProfile.Line(point1=self.coordADash, point2=self.coordBDash)
            self.sketchChamferProfile.HorizontalConstraint(entity=self.profileGeometryChamfer[5], addUndoState=False)
            ## line O'B'
            self.sketchChamferProfile.Line(point1=self.coordODash, point2=self.coordBDash)
            self.sketchChamferProfile.VerticalConstraint(entity=self.profileGeometryChamfer[6], addUndoState=False)
            self.sketchChamferProfile.unsetPrimaryObject()
    def createPart(self):
        ## create solid
        self.part = len(self.profileSketch)*[None]
        for i in range(len(self.part)):
            if i==0 and self.provideChamfer==True:
                self.tempPart = 2*[None]
                for j in range(len(self.tempPart)):
                    self.tempPart[j] = self.model.Part(name=self.couponName+'_Part_1_Temp_'+str(j+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.tempPart[0].BaseSolidExtrude(sketch=self.profileSketch[0], depth=self.thickness/2.0)
                self.tempPart[1].BaseSolidSweep(sketch=self.sketchChamferProfile, path=self.sketchChamferSweepPath)
            elif (i==0 and self.provideChamfer==False) or i==1:
                self.part[i] = self.model.Part(name=self.couponName+'_Part_'+str(i+1), dimensionality=THREE_D, type=DEFORMABLE_BODY)
                self.part[i].BaseSolidExtrude(sketch=self.profileSketch[i], depth=self.thickness/2.0)
    def createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        ## create temporary assembly instances for model with chamfer
        if self.provideChamfer==True:
            self.tempInstance = len(self.tempPart)*[None]
            for i in range(len(self.tempInstance)):
                self.tempInstance[i] = self.assembly.Instance(name=self.couponName+'_Instance_1_Temp_'+str(i+1), part=self.tempPart[i], dependent=ON)
            self.assembly.translate(instanceList=(self.tempInstance[1].name, ), vector=(0.0, 0.0, (self.thickness/2.0-self.chamferEdgeLength*math.tan(self.thetaRad))))
            newPartName = self.couponName+'_Part_1'
            self.assembly.InstanceFromBooleanCut(name=newPartName, instanceToBeCut=self.tempInstance[0], cuttingInstances=(self.tempInstance[1], ), originalInstances=DELETE)
            del self.assembly.features[self.couponName+'_Part_1-1']
            self.part[0] = self.model.parts[newPartName]
        session.viewports[session.currentViewportName].setValues(displayedObject=self.part[0])
        ## create actual assembly instances
        self.instance = len(self.part)*[None]
        for i in range(len(self.part)):
            self.instance[i] = self.assembly.Instance(name=self.couponName+'_Instance_'+str(i+1), part=self.part[i], dependent=ON)
    def createPartition(self):
        def createFacePartition():
            sketchPlane = self.part[0].faces.findAt(coordinates=(self.phi/2.0+self.lenTol, self.phi/2.0+self.lenTol, 0))
            sketchUpEdge = self.part[0].edges.findAt(coordinates=(self.lenTol, self.width/2.0, 0))
            t = self.part[0].MakeSketchTransform(sketchPlane=sketchPlane, sketchUpEdge=sketchUpEdge, sketchPlaneSide=SIDE1, origin=(0, 0, 0))
            s1 = self.model.ConstrainedSketch(name=self.couponName+'_Partition_Sketch_1', sheetSize=50.0, gridSpacing=1.0, transform=t)
            g, v = s1.geometry, s1.vertices
            s1.setPrimaryObject(option=SUPERIMPOSE)
            self.part[0].projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
            s1.ArcByCenterEnds(center=(0.0, 0.0), point1=(0.0, (self.phi+self.width)/4.0), point2=((self.phi+self.width)/4.0, 0.0), direction=CLOCKWISE)
            s1.CoincidentConstraint(entity1=v.findAt((0.0, (self.phi+self.width)/4.0)), entity2=g.findAt((0.0, (self.phi+self.width)/4.0+self.lenTol)), addUndoState=False)
            s1.CoincidentConstraint(entity1=v.findAt(((self.phi+self.width)/4.0, 0.0)), entity2=g.findAt(((self.phi+self.width)/4.0+self.lenTol, 0.0)), addUndoState=False)
            s1.Line(point1=(self.width/2.0, self.width/2.0), point2=(self.phi/2.0*math.sin(math.pi/4.0), self.phi/2.0*math.cos(math.pi/4.0)))
            s1.EqualDistanceConstraint(entity1=v.findAt((0.0, self.phi/2.0)), entity2=v.findAt((self.phi/2.0, 0.0)), midpoint=v.findAt((self.width/2.0, self.width/2.0)), addUndoState=False)
            self.part[0].PartitionFaceBySketch(sketchUpEdge=sketchUpEdge, faces=sketchPlane, sketch=s1)
            s1.unsetPrimaryObject()
        def createPartitionLong(thisPart, offsetDistance):
            ## partition by YZ plane
            self.datumPlane_ID = thisPart.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=offsetDistance).id
            thisPart.PartitionCellByDatumPlane(datumPlane=thisPart.datums[self.datumPlane_ID], cells=thisPart.cells)
        createPartitionLong(self.part[0], self.width/2.0)
        createFacePartition()
        ## partition solid ==>> sweep 1
        sweepPath1 = self.part[0].edges.findAt(coordinates=(self.width/2.0, 0, self.lenTol))
        edgesForPartitionTemp1 = self.getByCylinderDifference(self.part[0].edges, (0, 0, -self.lenTol), (0, 0, self.lenTol), ((self.phi+self.width)/4.0+self.lenTol), ((self.phi+self.width)/4.0-self.lenTol))
        edgesForPartition1 = self.getArcEdge(edgesForPartitionTemp1)
        self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath1, cells=self.part[0].cells, edges=edgesForPartition1)
        ## partition solid ==>> sweep 2
        sweepPath2 = self.part[0].edges.findAt(coordinates=(self.width/2.0, 0, self.lenTol))
        edgesForPartition2 = (self.part[0].edges.findAt(coordinates=(self.width/2.0-self.lenTol, self.width/2.0-self.lenTol, 0)), )
        self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath2, cells=self.part[0].cells, edges=edgesForPartition2)
        ## partition solid ==>> sweep 3
        sweepPath3 = self.part[0].edges.findAt(coordinates=(self.width/2.0, 0, self.lenTol))
        edgesForPartition3 = (self.part[0].edges.findAt(coordinates=(self.phi/2.0+self.lenTol, self.phi/2.0+self.lenTol, 0)), )
        self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath3, cells=self.part[0].cells, edges=edgesForPartition3)
        ## partition solid ==>> sweep 4
        if self.provideChamfer==True:
            sweepPath4 = self.part[0].edges.findAt(coordinates=(self.width/2.0, 0, self.lenTol))
            edgesForPartitionTemp4 = self.getByCylinderDifference(self.part[0].edges, (0, 0, self.thickness/2-self.lenTol), (0, 0, self.thickness/2+self.lenTol), (self.phi/2+self.chamferEdgeLength+self.lenTol), (self.phi/2+self.chamferEdgeLength-self.lenTol))
            edgesForPartition4 = self.getArcEdge(edgesForPartitionTemp4)
            self.part[0].PartitionCellBySweepEdge(sweepPath=sweepPath4, cells=self.part[0].cells, edges=edgesForPartition4)
    def createMesh(self):
        if self.provideChamfer==True:
            self.chamferOffset = self.chamferEdgeLength
        elif self.provideChamfer==False:
            self.chamferOffset = 0
        ## seed ==>> thickness1 direction
        edgesThickness1 = self.part[0].edges.findAt(coordinates=((self.phi/2+self.chamferOffset, 0, self.lenTol), (0, self.phi/2+self.chamferOffset, self.lenTol)))
        self.part[0].seedEdgeBySize(edges=edgesThickness1, size=self.seedSizeThickness1, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> arc direction
        edgesArc = self.part[0].edges.getByBoundingCylinder((0, 0, 0), (0, 0 , self.lenTol), (self.phi/2+self.lenTol))
        self.part[0].seedEdgeBySize(edges=edgesArc, size=self.seedSizeArc, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along BB'
        if self.provideChamfer==True:
            edgesLong1 = self.part[0].edges.findAt(coordinates=((self.phi/2+self.lenTol, 0, 0), (0, self.phi/2+self.lenTol, 0)))
            self.part[0].seedEdgeBySize(edges=edgesLong1, size=self.seedSizeLong1, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edges along B'B''
        pickedEdges1 = self.part[0].edges.getByBoundingCylinder((0, 0, -self.lenTol), (0, 0, self.thickness/2+self.lenTol), ((self.phi+self.width)/4.0+self.lenTol))
        pickedEdgesArc = self.getArcEdge(pickedEdges1)
        pickedEdgesStraight = self.getByDifference(pickedEdges1, pickedEdgesArc)
        edgesLong2 = self.getEdgeByLength(pickedEdgesStraight, abs((self.width-self.phi)/4-self.chamferOffset))
        self.seedEdge(self.part[0], 0, (self.phi/2+self.chamferOffset), edgesLong2, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        self.seedEdge(self.part[0], 1, (self.phi/2+self.chamferOffset), edgesLong2, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        self.seedEdge(self.part[0], 0, (self.phi/2+self.chamferOffset)*math.cos(math.pi/4), edgesLong2, minSize=self.seedSizeLong1, maxSize=self.seedSizeLong2)
        ## seed ==>> long edges B''C'
        pickedEdges2 = self.part[0].edges.getByBoundingBox(xMin=-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.width/2+self.lenTol, yMax=self.width/2+self.lenTol, zMax=self.thickness/2+self.lenTol)
        edgesLongTemp1 = self.getByDifference(pickedEdges2, pickedEdges1)
        edgesLongTemp2 = self.getEdgeByLength(edgesLongTemp1, self.thickness/2)
        edgesLong3 = self.getByDifference(edgesLongTemp1, edgesLongTemp2)
        self.part[0].seedEdgeBySize(edges=edgesLong3, size=self.seedSizeLong2, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edge along C'D
        edgesLong4 = self.part[0].edges.findAt(coordinates=((self.width/2+self.lenTol, 0, 0), (self.width/2+self.lenTol, self.width/2, 0), (self.width/2+self.lenTol, 0, self.thickness/2), (self.width/2+self.lenTol, self.width/2, self.thickness/2)))
        self.seedEdge(self.part[0], 0, self.width/2, edgesLong4, minSize=self.seedSizeLong2, maxSize=self.seedSizeLong3)
        ## seed ==>> thickness2 direction
        edgesThickness2 = self.part[1].edges.findAt(coordinates=((self.xD, 0, self.lenTol), (self.xD, self.lenTol, 0)))
        self.part[1].seedEdgeBySize(edges=edgesThickness2, size=self.seedSizeThickness2, deviationFactor=0.1, constraint=FINER)
        ## seed ==>> long edge along DF
        edgesLong5 = self.part[1].edges.findAt(coordinates=((self.xD+self.lenTol, 0, 0), (self.xD+self.lenTol, self.width/2, 0), (self.xD+self.lenTol, 0, self.thickness/2), (self.xD+self.lenTol, self.width/2, self.thickness/2)))
        self.seedEdge(self.part[1], 0, self.xD, edgesLong5, minSize=self.seedSizeLong3, maxSize=self.seedSizeLong4)
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
            surf = self.part[i].faces.getByBoundingBox(xMin=self.xD-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xD+self.lenTol, yMax=self.yE+self.yC+self.lenTol, zMax=self.thickness/2+self.lenTol)
            surfName = 'Surf_Tie_Part_'+str(i+1)
            self.getElemSurfFromCellFace(self.part[i], surf, surfName)
            region[i] = self.instance[i].surfaces[surfName]
        self.model.Tie(name=self.couponName+'_Tie', master=region[1], slave=region[0], positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, thickness=ON, constraintEnforcement=SURFACE_TO_SURFACE)
    def createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=self.nlGeom, initialInc=self.initIncr, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        for i in range(len(self.part)):
            ## create BC at negY face
            nodesNegY = self.part[i].nodes.getByBoundingBox(xMin=-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xG+self.lenTol, yMax=self.lenTol, zMax=self.thickness/2+self.lenTol)
            nsetNameNegY = 'Nset_NegY_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesNegY, name=nsetNameNegY)
            region = self.instance[i].sets[nsetNameNegY]
            self.model.DisplacementBC(name='BC_NegY_Part_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
            ## create BC at negZ face
            nodesPosZ = self.part[i].nodes.getByBoundingBox(xMin=-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xG+self.lenTol, yMax=self.yG+self.lenTol, zMax=self.lenTol)
            nsetNamePosZ = 'Nset_NegZ_Part_'+str(i+1)
            self.part[i].Set(nodes=nodesPosZ, name=nsetNamePosZ)
            region = self.instance[i].sets[nsetNamePosZ]
            self.model.DisplacementBC(name='BC_NegZ_Part_'+str(i+1), createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at negX face of Part 1
        nodesNegX = self.part[0].nodes.getByBoundingBox(xMin=-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.lenTol, yMax=self.yC+self.lenTol, zMax=self.thickness/2+self.lenTol)
        nsetNameNegX = 'Nset_NegX_Part_1'
        self.part[0].Set(nodes=nodesNegX , name=nsetNameNegX)
        region = self.instance[0].sets[nsetNameNegX]
        self.model.DisplacementBC(name='BC_NegX_Part_1', createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create pressure load on posX face
        endCellFaceArr = self.part[1].faces.getByBoundingBox(xMin=self.xG-self.lenTol, yMin=-self.lenTol, zMin=-self.lenTol, xMax=self.xG+self.lenTol, yMax=self.yG+self.lenTol, zMax=self.thickness/2+self.lenTol)
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

