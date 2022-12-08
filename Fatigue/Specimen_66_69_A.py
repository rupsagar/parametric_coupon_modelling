## provide path and file name for the json database of the coupon models
couponDatabasePath = r'Z:\Rupsagar\04_COUPON_MODELLING\01_WIP\Script_Files\Coupon_Mark_A'
couponDatabaseJsonFileName = r'Coupon_Mark_A_Database.json'

import os
import json
import ast

from abaqus import *
from abaqusConstants import *
from caeModules import *

class createCouponMarkA():
    def __init__(self, couponData):
        ## initialize the user-defined parameters; dimensional inputs converted to float to avoid truncation while division
        self.specimenName = couponData['specimenName']
        self.phi1 = float(couponData['phi1'])
        self.phi2 = float(couponData['phi2'])
        self.phi3 = float(couponData['phi3'])
        self.rad1 = float(couponData['rad1'])
        self.rad2 = float(couponData['rad2'])
        self.len1 = float(couponData['len1'])
        self.len2 = float(couponData['len2'])
        self.partitionRadialFraction = float(eval(couponData['partitionRadialFraction']))
        self.partitionRadius = float(self.partitionRadialFraction*self.phi1/2.0)
        self.lenTol = abs(float(couponData['lenTol']))
        self.seedSizeGlobal = float(couponData['seedSizeGlobal'])
        self.seedSizeOuterArc = float(couponData['seedSizeOuterArc'])
        self.seedSizeLong1 = float(couponData['seedSizeLong1'])
        self.seedSizeLong2 = float(couponData['seedSizeLong2'])
        self.seedSizeLong3 = float(couponData['seedSizeLong3'])
        self.elemTypeHex = couponData['elemTypeHex']
        self.elemTypePenta = couponData['elemTypePenta']
        self.elemTypeTetra = couponData['elemTypeTetra']
        self.materialName = couponData['materialName']
        self.density = float(couponData['density'])
        self.youngsModulus = float(couponData['youngsModulus'])
        self.poissonsRatio = float(couponData['poissonsRatio'])
        ## derived quantities
        self.modelName = self.specimenName+'_Model'
        self.partName = self.specimenName+'_Part'
        self.sketchName = self.specimenName+'_Profile_Sketch'
        self.partitionSketchName = self.specimenName+'_Partition_Sketch'
        self.sectionName = self.specimenName+'_Section'
        self.instanceName = self.specimenName+'_Instance'
        self.jobName = self.specimenName+'_Job'
        self.seedSizeOuterRadialMin = self.seedSizeOuterArc*self.partitionRadialFraction
        self.seedSizeInnerRadial = self.seedSizeOuterArc*self.partitionRadialFraction #self.seedSizeGlobal
        ## create coupon specimen
        self.__createModel()
        self.__createProfileSketch()
        self.__createSolid()
        self.__createPartition()
        self.__createMesh()
        self.__createMaterial()
        self.__createSection()
        self.__createAssembly()
        self.__createStep()
        self.__createJob()
    def __createModel(self):
        ## define model
        #session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
        self.model = mdb.Model(name=self.modelName)
    def __createProfileSketch(self):
        ## method to draw sketch of coupon profile
        ## calculate vertex coordinates
        self.coordO = (self.xO, self.yO) = (0, 0)
        self.coordA = (self.xA, self.yA) = (0, self.phi1/2)
        self.coordB = (self.xB, self.yB) = (self.rad1*(1-((self.rad1+self.phi1/2-self.phi2/2)/self.rad1)**2)**0.5, self.phi2/2)
        self.coordC = (self.xC, self.yC) = (self.len1/2, self.phi3/2)
        self.coordD = (self.xD, self.yD) = (self.len2/2, self.phi3/2)
        self.coordE = (self.xE, self.yE) = (self.len2/2, 0)
        self.coordC1 = (self.xC1, self.yC1) = (0, self.yA+self.rad1) # center 1
        self.coordC2 = (self.xC2, self.yC2) = ((self.xB+self.xC)/2,(self.yB+self.yC)/2) # arbitrary center 2 ==>> true value set by dimension method on arc
        ## define sketch
        self.profileSketch = self.model.ConstrainedSketch(name=self.sketchName, sheetSize=200.0)
        self.profileGeometry, self.profileVertices = self.profileSketch.geometry, self.profileSketch.vertices
        self.profileSketch.setPrimaryObject(option=STANDALONE)
        ## horizontal fixed construction line ==>> self.profileGeometry[2]
        self.profileSketch.ConstructionLine(point1=(-80, 0), angle=0)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[2], addUndoState=False)
        self.profileSketch.FixedConstraint(entity=self.profileGeometry[2])
        self.profileSketch.assignCenterline(line=self.profileGeometry[2])
        ## vertical fixed construction line ==>> self.profileGeometry[3]
        self.profileSketch.ConstructionLine(point1=(0, -30), angle=90)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.FixedConstraint(entity=self.profileGeometry[3])
        ## line OA: self.profileGeometry[4]; vertices ==>> self.profileVertices[0], self.profileVertices[1]; dimension: d[0]
        self.profileSketch.Line(point1=self.coordO, point2=self.coordA)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[4], addUndoState=False)
        self.profileSketch.PerpendicularConstraint(entity1=self.profileGeometry[2], entity2=self.profileGeometry[4], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[0], entity2=self.profileGeometry[2], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[1], entity2=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.ObliqueDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[1], textPoint=(-3, 4), value=self.phi1/2)
        (self.xO, self.yO), (self.xA, self.yA) = self.profileVertices[0].coords, self.profileVertices[1].coords
        ## arc AB: self.profileGeometry[5]; vertices ==>> self.profileVertices[1], self.profileVertices[2]; center: self.profileVertices[3]; dimension: d[1], d[2]
        self.profileSketch.ArcByCenterEnds(center=self.coordC1, point1=self.coordA, point2=self.coordB, direction=COUNTERCLOCKWISE)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[3], entity2=self.profileGeometry[3], addUndoState=False)
        self.profileSketch.RadialDimension(curve=self.profileGeometry[5], textPoint=(0, 25), radius=self.rad1)
        self.profileSketch.DistanceDimension(entity1=self.profileVertices[2], entity2=self.profileGeometry[2], textPoint=(10, 1), value=self.phi2/2)
        (self.xB, self.yB), (self.xC1, self.yC1) = self.profileVertices[2].coords, self.profileVertices[3].coords
        ## arc BC: self.profileGeometry[6]; vertices ==>> self.profileVertices[2], self.profileVertices[4]; center: self.profileVertices[5]; dimension: d[3], d[4], d[5]
        self.profileSketch.ArcByCenterEnds(center=self.coordC2, point1=self.coordB, point2=self.coordC, direction=COUNTERCLOCKWISE)
        self.profileSketch.RadialDimension(curve=self.profileGeometry[6], textPoint=(14, 10), radius=self.rad2)
        self.profileSketch.DistanceDimension(entity1=self.profileVertices[4], entity2=self.profileGeometry[2], textPoint=(25, 1), value=self.phi3/2)
        self.profileSketch.HorizontalDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[4], textPoint=(13, 9), value=self.len1/2)
        (self.xC, self.yC), (self.xC2, self.yC2) = self.profileVertices[4].coords, self.profileVertices[5].coords
        ## line CD: self.profileGeometry[7]; vertices ==>> self.profileVertices[5], self.profileVertices[6]; dimension: d[6]
        self.profileSketch.Line(point1=self.coordC, point2=self.coordD)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[7], addUndoState=False)
        self.profileSketch.HorizontalDimension(vertex1=self.profileVertices[0], vertex2=self.profileVertices[6], textPoint=(13, -9), value=self.len2/2)
        (self.xD, self.yD) = self.profileVertices[6].coords
        ## line DE: self.profileGeometry[8]; vertices ==>> self.profileVertices[6], self.profileVertices[7]
        self.profileSketch.Line(point1=self.coordD, point2=self.coordE)
        self.profileSketch.VerticalConstraint(entity=self.profileGeometry[8], addUndoState=False)
        self.profileSketch.CoincidentConstraint(entity1=self.profileVertices[7], entity2=self.profileGeometry[2], addUndoState=False)
        (self.xE, self.yE) = self.profileVertices[7].coords
        ## line EO: self.profileGeometry[9]; vertices ==>> self.profileVertices[7], self.profileVertices[0]
        self.profileSketch.Line(point1=self.coordE, point2=self.coordO)
        self.profileSketch.HorizontalConstraint(entity=self.profileGeometry[9], addUndoState=False)
        self.profileSketch.unsetPrimaryObject()
    def __createSolid(self):
        ## create solid
        self.part = self.model.Part(name=self.partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        self.part.BaseSolidRevolve(sketch=self.profileSketch, angle=90, flipRevolveDirection=ON)
        session.viewports['Viewport: 1'].setValues(displayedObject=self.part)
    def __createPartition(self):
        ## partition ==>> inner cylinder
        self.sketchFace = self.part.faces.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA+self.lenTol))
        self.sketchEdge = self.part.edges.findAt(((0, self.partitionRadius, 0),))
        self.transform = self.part.MakeSketchTransform(sketchPlane=self.sketchFace[0], sketchUpEdge=self.sketchEdge[0], sketchPlaneSide=SIDE1, origin=(0, 0, 0))
        self.partitionSketch = self.model.ConstrainedSketch(name=self.partitionSketchName, sheetSize=4, transform=self.transform)
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
        edgesTemp = self.part.edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        self.edgesArcForPartition = self.__getArcEdge(edgesTemp)
        self.sweepEdges = self.part.edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.partitionRadius-self.lenTol))
        self.part.PartitionCellBySweepEdge(sweepPath=self.sweepEdges[0], cells=self.part.cells, edges=self.edgesArcForPartition)
        ## partition ==>> at section B
        self.datumPlane1_ID = self.part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=self.xB).id
        self.part.PartitionCellByDatumPlane(datumPlane=self.part.datums[self.datumPlane1_ID], cells=self.part.cells)
        ## partition ==>> at section C
        self.datumPlane1_ID = self.part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=self.xC).id
        self.part.PartitionCellByDatumPlane(datumPlane=self.part.datums[self.datumPlane1_ID], cells=self.part.cells)
    def __createMesh(self):
        ## seed ==>> global
        self.part.seedPart(size=self.seedSizeGlobal, deviationFactor=0.1, minSizeFactor=0.1)
        ## seed ==>> outer arc edge AA'
        self.edgesOuterCyl = self.__getByCylinderDifference(self.part.edges, (self.xA-self.lenTol, 0, 0), (self.xA+self.lenTol, 0, 0), (self.yA+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArc = self.__getArcEdge(self.edgesOuterCyl)
        self.part.seedEdgeBySize(edges=self.edgesOuterArc, size=self.seedSizeOuterArc, deviationFactor=0.1, constraint=FIXED)
        ## seed ==>> outer radial edges
        self.edgesOuterRadial = self.__getByDifference(self.edgesOuterCyl, self.edgesOuterArc)
        self.__seedOuterRadial((0.0, self.partitionRadius+self.lenTol, 0.0), minSize=self.seedSizeOuterRadialMin, maxSize=self.seedSizeOuterArc)
        self.__seedOuterRadial((0.0, 0.0, -(self.partitionRadius+self.lenTol)), minSize=self.seedSizeOuterRadialMin, maxSize=self.seedSizeOuterArc)
        ## seed ==>> edge Bb ==>> not applied; seeding with increase the element size at the surface by small amount
        self.edgesOuterCylAtB = self.__getByCylinderDifference(self.part.edges, (self.xB-self.lenTol, 0, 0), (self.xB+self.lenTol, 0, 0), (self.yB+self.lenTol), (self.partitionRadius+self.lenTol))
        self.edgesOuterArcAtB = self.__getArcEdge(self.edgesOuterCylAtB)
        self.edgesOuterRadialAtB = self.__getByDifference(self.edgesOuterCylAtB, self.edgesOuterArcAtB)
        ratioBias = self.part.getEdgeSeeds(self.edgesOuterRadial[0], attribute=BIAS_RATIO)
        elemNum = self.part.getEdgeSeeds(self.edgesOuterRadial[0], attribute=NUMBER)
        #self.__seedOuterRadial((self.xB, self.partitionRadius+self.lenTol, 0.0), ratio=ratioBias, number=elemNum)
        #self.__seedOuterRadial((self.xB, 0.0, -(self.partitionRadius+self.lenTol)), ratio=ratioBias, number=elemNum)
        ## seed ==>> longitudinal edges
        self.__seedLongEdges(self.xA, self.xB, self.seedSizeLong1)
        self.__seedLongEdges(self.xB, self.xC, self.seedSizeLong2)
        self.__seedLongEdges(self.xC, self.xD, self.seedSizeLong3)
        ## seed ==>> inner radial edges
        self.edgesInnerCyl = self.part.edges.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xB-self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        self.edgesInnerArc = self.__getArcEdge(self.edgesInnerCyl)
        self.edgesInnerRadial = self.__getByDifference(self.edgesInnerCyl, self.edgesInnerArc)
        self.part.seedEdgeBySize(edges=self.edgesInnerRadial, size=self.seedSizeInnerRadial, deviationFactor=0.1, constraint=FINER)
        ## sweep path ==>> inner cylinder
        self.__setInnerCylSweepPath(self.xA, self.xB)
        self.__setInnerCylSweepPath(self.xB, self.xC)
        self.__setInnerCylSweepPath(self.xC, self.xD)
        ## mesh ==>> outer cylinder
        self.cellsOuterCyl = self.__getByCylinderDifference(self.part.cells, (self.xA-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.yD+self.lenTol), (self.partitionRadius+self.lenTol))
        self.part.generateMesh(regions=self.cellsOuterCyl)
        ## mesh ==>> inner cylinder
        self.cellsInnerCyl = self.part.cells.getByBoundingCylinder((self.xA-self.lenTol, 0, 0), (self.xD+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        self.part.generateMesh(regions=self.cellsInnerCyl)
        ## set element types
        if self.elemTypeHex == 'C3D8HS':
            elemType1 = mesh.ElemType(elemCode=C3D8HS, elemLibrary=STANDARD)
        if self.elemTypePenta == 'C3D6':
            elemType2 = mesh.ElemType(elemCode=C3D6, elemLibrary=STANDARD, secondOrderAccuracy=OFF, distortionControl=DEFAULT)
        if self.elemTypeTetra == 'C3D4':
            elemType3 = mesh.ElemType(elemCode=C3D4, elemLibrary=STANDARD, secondOrderAccuracy=OFF, distortionControl=DEFAULT)
        self.part.setElementType(regions=(self.part.cells,), elemTypes=(elemType1, elemType2, elemType3))
    def __createMaterial(self):
        ## material definition
        self.model.Material(name=self.materialName)
        self.model.materials[self.materialName].Density(table=((self.density, ), ))
        self.model.materials[self.materialName].Elastic(table=((self.youngsModulus, self.poissonsRatio), ))
    def __createSection(self):
        ## section definition
        self.model.HomogeneousSolidSection(name=self.sectionName, material=self.materialName, thickness=None)
        ## assign section property to elements
        pickedRegion = self.part.Set(elements=self.part.elements, name='Elements_All')
        #pickedRegion = regionToolset.Region(cells=self.part.cells)   
        self.part.SectionAssignment(region=pickedRegion, sectionName=self.sectionName, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    def __createAssembly(self):
        ## create assembly
        self.assembly = self.model.rootAssembly
        self.assembly.DatumCsysByDefault(CARTESIAN)
        self.instance = self.assembly.Instance(name=self.instanceName, part=self.part, dependent=ON)
    def __createStep(self):
        ## create step for load and boundary conditions
        self.model.StaticStep(name='Load', previous='Initial', nlgeom=OFF, initialInc=0.1, timePeriod=1.0, minInc=1e-4, maxInc=1.0)
        ## create BC at negY face
        nodesNegY = self.part.nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin = -self.lenTol, zMin = -self.yD-self.lenTol, xMax = self.xE+self.lenTol, yMax = self.lenTol, zMax = self.lenTol)
        nsetNameNegY = 'Nset_NegY'
        self.part.Set(nodes=nodesNegY, name=nsetNameNegY)
        region = self.instance.sets[nsetNameNegY]
        self.model.DisplacementBC(name='BC_NegY', createStepName='Load', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at posZ face
        nodesPosZ = self.part.nodes.getByBoundingBox(xMin=self.xO-self.lenTol, yMin = -self.lenTol, zMin = -self.lenTol, xMax = self.xE+self.lenTol, yMax = self.yD+self.lenTol, zMax = self.lenTol)
        nsetNamePosZ = 'Nset_PosZ'
        self.part.Set(nodes=nodesPosZ, name=nsetNamePosZ)
        region = self.instance.sets[nsetNamePosZ]
        self.model.DisplacementBC(name='BC_PosZ', createStepName='Load', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create BC at negX face
        nodesNegX = self.part.nodes.getByBoundingCylinder((self.xO-self.lenTol, 0, 0), (self.xO+self.lenTol, 0, 0), (self.yA+self.lenTol))
        nsetNameNegX = 'Nset_NegX'
        self.part.Set(nodes=nodesNegX , name=nsetNameNegX)
        region = self.instance.sets[nsetNameNegX]
        self.model.DisplacementBC(name='BC_NegX', createStepName='Load', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
        ## create pressure load on posX face
        endCellFaceArr = self.part.faces.getByBoundingCylinder((self.xE-self.lenTol, 0, 0), (self.xE+self.lenTol, 0, 0), (self.yD+self.lenTol))
        surfNamePosX = 'Surf_PosX'
        self.__getElemSurfFromCellFace(endCellFaceArr, surfNamePosX)
        region = self.instance.surfaces[surfNamePosX]
        self.model.Pressure(name='Load_PosX', createStepName='Load', region=region, distributionType=UNIFORM, field='', magnitude=-28.0, amplitude=UNSET)
    def __createJob(self):
        ## create job
        self.job = mdb.Job(name=self.jobName, model=self.modelName, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
        memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=2, numDomains=2, numGPUs=1)
        self.job.writeInput(consistencyChecking=OFF)
    def __getByDifference(self, listA, listB):
        ## method to return list with elements of difference of two lists
        differenceList = []
        for thisItem in listA:
            if thisItem not in listB:
                differenceList.append(thisItem)
        return differenceList
    def __getByCylinderDifference(self, feature, center1, center2, outerRadius, innerRadius):
        ## method to return list with geometric features by subtraction of two bounding cylinders
        featureOuter = feature.getByBoundingCylinder(center1, center2, outerRadius)
        featureInner = feature.getByBoundingCylinder(center1, center2, innerRadius)
        pickedFeatures = self.__getByDifference(featureOuter, featureInner)
        return pickedFeatures
    def __getArcEdge(self, edgeList):
        ## method to return edge list containing only arc edges from a given edge list
        arcEdge = []
        for thisEdge in edgeList:
            try:
                thisEdge.getRadius()
                arcEdge.append(thisEdge)
            except:
                pass
        return arcEdge
    def __getEdgeByLength(self, edgeList, length):
        ## method to return edge list of a desired length from a given edge list
        pickedEdges = []
        for thisEdge in edgeList:
            if abs(thisEdge.getSize(0)-length) < self.lenTol:
                pickedEdges.append(thisEdge)
        return pickedEdges
    def __getElemSurfFromCellFace(self, cellFaceArr, surfName):
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
        self.part.Surface(**surfDict)
    def __seedOuterRadial(self, pointOnRadius, **kwargs):
        ## method to seed the outer radial edge at sections through A and B
        edgesOuterRadial = self.part.edges.findAt((pointOnRadius, ))  
        edgesRadialVertexIDPair = edgesOuterRadial[0].getVertices()
        for thisVertexID in edgesRadialVertexIDPair:
            vertexCoord = self.part.vertices[thisVertexID].pointOn
            if abs(abs(vertexCoord[0][1])-self.partitionRadius) < self.lenTol or abs(abs(vertexCoord[0][2])-self.partitionRadius) < self.lenTol or abs(abs(vertexCoord[0][2])-self.partitionRadius) < self.lenTol:
                if edgesRadialVertexIDPair.index(thisVertexID) == 0:
                    if 'minSize' in kwargs.keys():
                        self.part.seedEdgeByBias(biasMethod=SINGLE, end1Edges=edgesOuterRadial, minSize=kwargs['minSize'], maxSize=kwargs['maxSize'], constraint=FIXED)
                    elif 'ratio' in kwargs.keys():
                        self.part.seedEdgeByBias(biasMethod=SINGLE, end1Edges=edgesOuterRadial, ratio=kwargs['ratio'], number=kwargs['number'], constraint=FIXED)
                elif edgesRadialVertexIDPair.index(thisVertexID) == 1:
                    if 'minSize' in kwargs.keys():
                        self.part.seedEdgeByBias(biasMethod=SINGLE, end2Edges=edgesOuterRadial, minSize=kwargs['minSize'], maxSize=kwargs['maxSize'], constraint=FIXED)
                    elif 'ratio' in kwargs.keys():
                        self.part.seedEdgeByBias(biasMethod=SINGLE, end2Edges=edgesOuterRadial, ratio=kwargs['ratio'], number=kwargs['number'], constraint=FIXED)
    def __seedLongEdges(self, xLeft, xRight, seedSize):
        ## method to seed the longitudinal edges
        edgesInnerArcLong = self.part.edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        edgesInnerArc = self.__getArcEdge(edgesInnerArcLong)
        edgesStraight = self.__getByDifference(edgesInnerArcLong, edgesInnerArc)
        edgesInnerRadial = self.__getEdgeByLength(edgesStraight, self.partitionRadius)
        edgesLong = self.__getByDifference(edgesStraight, edgesInnerRadial)
        self.part.seedEdgeBySize(edges=edgesLong, size=seedSize, deviationFactor=0.1, constraint=FIXED)
    def __setInnerCylSweepPath(self, xLeft, xRight):
        ## method to set the sweep path for the inner cylindrical mesh
        cellsInnerCyl = self.part.cells.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), (self.partitionRadius+self.lenTol))
        edgesSweepPath = self.part.edges.getByBoundingCylinder((xLeft-self.lenTol, 0, 0), (xRight+self.lenTol, 0, 0), self.lenTol)
        self.part.setMeshControls(regions=cellsInnerCyl, technique=SWEEP, algorithm=ADVANCING_FRONT)
        self.part.setSweepPath(region=cellsInnerCyl[0], edge=edgesSweepPath[0], sense=FORWARD)


## read json database
fileJson = open(os.path.join(couponDatabasePath, couponDatabaseJsonFileName), 'r')
couponMarkADatabaseUnicode = json.load(fileJson)
fileJson.close
couponMarkADatabase = ast.literal_eval(json.dumps(couponMarkADatabaseUnicode))

## create instance of the coupon
# couponModelList = []
# for thisCoupon in couponMarkADatabase:
#     couponModelList.append(createCouponMarkA(couponMarkADatabase[thisCoupon]))

self = createCouponMarkA(couponMarkADatabase['CouponMarkASpecimen2'])
