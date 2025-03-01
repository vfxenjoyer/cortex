##########################################################################
#
#  Copyright (c) 2013-2014, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os

import maya.cmds
import maya.OpenMaya as OpenMaya

import IECore
import IECoreScene
import IECoreMaya

import imath

class LiveSceneTest( IECoreMaya.TestCase ) :

	__testFile = "test/liveSceneTest.scc"

	def setUp( self ) :

		maya.cmds.file( new=True, f=True )

	def tearDown( self ) :

		if os.path.exists( LiveSceneTest.__testFile ) :
			os.remove( LiveSceneTest.__testFile )

	def testFileName( self ) :

		scene = IECoreMaya.LiveScene()
		self.assertRaises( RuntimeError, scene.fileName )

	def testChildNames( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		sphere2 = maya.cmds.polySphere( name="pSphere2" )
		sphere3 = maya.cmds.polySphere( name="pSphere3" )

		maya.cmds.parent( "pSphere2", "pSphere1" )
		maya.cmds.parent( "pSphere3", "pSphere1" )

		scene = IECoreMaya.LiveScene()
		child = scene.child( "pSphere1" )

		self.assertEqual( set( child.childNames() ), set( [ "pSphere2", "pSphere3" ] ) )

		self.assertEqual( scene.child( "pSphere1" ).child( "pSphere2" ).childNames(), [] )

	def testHasChild( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		sphere2 = maya.cmds.polySphere( name="pSphere2" )
		sphere3 = maya.cmds.polySphere( name="pSphere3" )

		maya.cmds.parent( "pSphere2", "pSphere1" )
		maya.cmds.parent( "pSphere3", "pSphere1" )

		scene = IECoreMaya.LiveScene()
		child = scene.child( "pSphere1" )

		self.assertEqual( scene.hasChild("pSphere1"), True )

		self.assertEqual( child.hasChild("pSphere1Shape"), False )
		self.assertEqual( child.hasChild("pSphere2"), True )
		self.assertEqual( child.hasChild("pSphere3"), True )
		self.assertEqual( child.hasChild("pSphere3Shape"), False )
		self.assertEqual( child.hasChild("pSphere2Shape"), False )

		self.assertEqual( child.hasChild("asdfasdf"), False )


	def testNames( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		sphere2 = maya.cmds.polySphere( name="pSphere2" )
		sphere3 = maya.cmds.polySphere( name="pSphere3" )

		maya.cmds.parent( "pSphere2", "pSphere1" )
		maya.cmds.parent( "pSphere3", "pSphere1" )

		scene = IECoreMaya.LiveScene()

		sphere1 = scene.child( "pSphere1" )

		sphere2 = sphere1.child( "pSphere2" )

		sphere3 = sphere1.child( "pSphere3" )

		self.assertEqual( str( scene.name() ), "/" )
		self.assertEqual( str( sphere1.name() ), "pSphere1" )

		self.assertEqual( str( sphere2.name() ), "pSphere2" )

		self.assertEqual( str( sphere3.name() ), "pSphere3" )

	def testPaths( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		sphere2 = maya.cmds.polySphere( name="pSphere2" )
		sphere3 = maya.cmds.polySphere( name="pSphere3" )

		maya.cmds.parent( "pSphere2", "pSphere1" )
		maya.cmds.parent( "pSphere3", "pSphere1" )

		scene = IECoreMaya.LiveScene()

		sphere1 = scene.child( "pSphere1" )

		sphere2 = sphere1.child( "pSphere2" )

		sphere3 = sphere1.child( "pSphere3" )

		self.assertEqual( scene.path(), [] )
		self.assertEqual( sphere1.path(), [ "pSphere1" ] )

		self.assertEqual( sphere2.path(), [ "pSphere1", "pSphere2" ] )

		self.assertEqual( sphere3.path(), [ "pSphere1", "pSphere3" ] )

	def testSceneMethod( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		sphere2 = maya.cmds.polySphere( name="pSphere2" )
		sphere3 = maya.cmds.polySphere( name="pSphere3" )

		maya.cmds.parent( "pSphere2", "pSphere1" )
		maya.cmds.parent( "pSphere3", "pSphere1" )

		scene = IECoreMaya.LiveScene()

		self.assertEqual( str( scene.scene( ["pSphere1"] ).name() ), "pSphere1" )

		# does it still return absolute paths if we've gone to another location?
		scene = scene.scene( ["pSphere1"] )
		self.assertEqual( str( scene.scene( [] ).name() ), "/" )
		self.assertEqual( str( scene.scene( ["pSphere1", "pSphere2"] ).name() ), "pSphere2" )
		self.assertEqual( str( scene.scene( ["pSphere1", "pSphere3"] ).name() ), "pSphere3" )

		self.assertEqual( scene.scene( ["idontexist"], IECoreScene.SceneInterface.MissingBehaviour.NullIfMissing ), None )
		self.assertRaises( RuntimeError, IECore.curry( scene.scene, ["idontexist"] ) )

	def testHasObject( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		scene = IECoreMaya.LiveScene()
		child = scene.child( "pSphere1" )

		self.assertEqual( scene.hasObject(), False )
		self.assertEqual( child.hasObject(), True )

	def testReadTransformMethods( self ) :

		# create a little hierarchy
		transfromythingy = maya.cmds.createNode( "transform", name="transform1" )
		maya.cmds.setAttr( "transform1.tx", 0.1 )
		maya.cmds.setAttr( "transform1.ty", 0.2 )
		maya.cmds.setAttr( "transform1.tz", 0.3 )

		maya.cmds.setAttr( "transform1.rx", 0.1 )
		maya.cmds.setAttr( "transform1.ry", 0.2 )
		maya.cmds.setAttr( "transform1.rz", 0.3 )

		maya.cmds.setAttr( "transform1.sx", 0.1 )
		maya.cmds.setAttr( "transform1.sy", 0.2 )
		maya.cmds.setAttr( "transform1.sz", 0.3 )

		sphere = maya.cmds.polySphere( name="pSphere1" )
		maya.cmds.parent( "pSphere1", "transform1" )

		maya.cmds.setAttr( "pSphere1.tx", 1 )
		maya.cmds.setAttr( "pSphere1.ty", 2 )
		maya.cmds.setAttr( "pSphere1.tz", 3 )

		maya.cmds.setAttr( "pSphere1.rx", 10 )
		maya.cmds.setAttr( "pSphere1.ry", 20 )
		maya.cmds.setAttr( "pSphere1.rz", 30 )

		maya.cmds.setAttr( "pSphere1.sx", 4 )
		maya.cmds.setAttr( "pSphere1.sy", 5 )
		maya.cmds.setAttr( "pSphere1.sz", 6 )

		scene = IECoreMaya.LiveScene()
		transformChild = scene.child( "transform1" ).child( "pSphere1" )

		# test it returns the correct transform in local space
		maya.cmds.currentTime( "0.0sec" )
		transform = transformChild.readTransform( 0 ).value

		import math

		self.assertAlmostEqual( transform.translate.x, 1, 5 )
		self.assertAlmostEqual( transform.translate.y, 2, 5 )
		self.assertAlmostEqual( transform.translate.z, 3, 5 )

		self.assertAlmostEqual( transform.rotate.x * 180.0 / math.pi, 10.0, 5 )
		self.assertAlmostEqual( transform.rotate.y * 180.0 / math.pi, 20.0, 5 )
		self.assertAlmostEqual( transform.rotate.z * 180.0 / math.pi, 30.0, 5 )

		self.assertAlmostEqual( transform.scale.x, 4, 5 )
		self.assertAlmostEqual( transform.scale.y, 5, 5 )
		self.assertAlmostEqual( transform.scale.z, 6, 5 )

		self.assertEqual( transform.transform, transformChild.readTransformAsMatrix( 0 ) )

		# Test rotation order
		maya.cmds.setAttr( "pSphere1.rotateOrder", 2 )
		transform = transformChild.readTransform( 0 ).value
		self.assertEqual( transform.rotate.order().name, 'ZXY' )

	def testTimeException( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		maya.cmds.setKeyframe( "pSphere1", attribute="tx", t="0sec", v=1 )
		maya.cmds.setKeyframe( "pSphere1", attribute="ty", t="0sec", v=2 )
		maya.cmds.setKeyframe( "pSphere1", attribute="tz", t="0sec", v=3 )

		maya.cmds.setKeyframe( "pSphere1", attribute="tx", t="1sec", v=4 )
		maya.cmds.setKeyframe( "pSphere1", attribute="ty", t="1sec", v=5 )
		maya.cmds.setKeyframe( "pSphere1", attribute="tz", t="1sec", v=6 )

		scene = IECoreMaya.LiveScene()
		transformChild = scene.child( "pSphere1" )

		# move to frame -1:
		maya.cmds.currentTime( -1 )

		# test it returns the correct transform in local space
		self.assertRaises( RuntimeError, IECore.curry( transformChild.readTransform, 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( transformChild.readTransform, 0.5 ) )
		self.assertRaises( RuntimeError, IECore.curry( transformChild.readTransform, 1.0 ) )


	def testAnimatedTransform( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		maya.cmds.setKeyframe( "pSphere1", attribute="tx", t="0sec", v=1 )
		maya.cmds.setKeyframe( "pSphere1", attribute="ty", t="0sec", v=2 )
		maya.cmds.setKeyframe( "pSphere1", attribute="tz", t="0sec", v=3 )

		maya.cmds.setKeyframe( "pSphere1", attribute="tx", t="1sec", v=4 )
		maya.cmds.setKeyframe( "pSphere1", attribute="ty", t="1sec", v=5 )
		maya.cmds.setKeyframe( "pSphere1", attribute="tz", t="1sec", v=6 )

		scene = IECoreMaya.LiveScene()
		transformChild = scene.child( "pSphere1" )

		# test it returns the correct transform in local space
		maya.cmds.currentTime( "0sec" )
		transform0 = transformChild.readTransform( 0 ).value
		maya.cmds.currentTime( "0.5sec" )
		transform0_5 = transformChild.readTransform( 0.5 ).value
		maya.cmds.currentTime( "1sec" )
		transform1 = transformChild.readTransform( 1 ).value

		self.assertEqual( transform0.translate, imath.V3d( 1, 2, 3 ) )

		self.assertAlmostEqual( transform0_5.translate.x, 2.5, 5 )
		self.assertAlmostEqual( transform0_5.translate.y, 3.5, 5 )
		self.assertAlmostEqual( transform0_5.translate.z, 4.5, 5 )

		self.assertEqual( transform1.translate, imath.V3d( 4, 5, 6 ) )


	def testDeletedDagPath( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		scene = IECoreMaya.LiveScene()
		child = scene.child( "pSphere1" )

		maya.cmds.delete( "pSphere1" )

		self.assertRaises( RuntimeError, IECore.curry( child.child, "pSphereShape1" ) )
		self.assertRaises( RuntimeError, child.childNames )
		self.assertRaises( RuntimeError, IECore.curry( child.hasChild, "asdd" ) )
		self.assertRaises( RuntimeError, child.name )
		self.assertRaises( RuntimeError, child.path )
		self.assertRaises( RuntimeError, child.hasObject )
		self.assertRaises( RuntimeError, IECore.curry( child.readBound, 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( child.readObject, 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( child.readTransform, 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( child.readTransformAsMatrix, 0.0 ) )

		# this doesn't need to throw an exception does it?
		self.assertEqual( child.scene( [ "pSphere1", "pSphereShape1" ], IECoreScene.SceneInterface.MissingBehaviour.NullIfMissing ), None )

		# I guess this does...
		self.assertRaises( RuntimeError, IECore.curry( child.scene, [ "pSphere1", "pSphereShape1" ] ) )

	def testReadMesh( self ) :

		# create a cube:
		maya.cmds.polyCube( name = "pCube1" )

		# transform a bit, so we can check it's returning the mesh in world space:
		maya.cmds.setAttr( "pCube1.tx", 0.1 )
		maya.cmds.setAttr( "pCube1.ty", 0.2 )
		maya.cmds.setAttr( "pCube1.tz", 0.3 )

		maya.cmds.setAttr( "pCube1.rx", 10 )
		maya.cmds.setAttr( "pCube1.ry", 20 )
		maya.cmds.setAttr( "pCube1.rz", 30 )

		scene = IECoreMaya.LiveScene()
		cube = scene.child( "pCube1" )

		# read mesh at time 0:
		maya.cmds.currentTime( "0.0sec" )
		mesh = cube.readObject( 0 )

		vertList = list( mesh["P"].data )

		# check it's got the right length:
		self.assertEqual( len( vertList ), 8 )

		# check it's got the right verts:
		self.assertEqual( vertList.count( imath.V3f( -0.5, -0.5, 0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( 0.5, -0.5, 0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( -0.5, 0.5, 0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( 0.5, 0.5, 0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( -0.5, 0.5, -0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( 0.5, 0.5, -0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( -0.5, -0.5, -0.5 ) ), 1 )
		self.assertEqual( vertList.count( imath.V3f( 0.5, -0.5, -0.5 ) ), 1 )

		# check read primvars
		self.assertEqual( mesh["P"], cube.readObjectPrimitiveVariables( [ "P" ], 0 )["P"] )

	def testAnimatedMesh( self ) :

		cube = maya.cmds.polyCube( name = "pCube1" )

		# create a skin cluster to animate vertex 0:
		maya.cmds.select( cl=True )
		maya.cmds.select( "pCube1.vtx[0]", r=True )
		cluster = maya.mel.eval( 'newCluster "-envelope 1"' )[1]

		maya.cmds.setKeyframe( cluster, attribute="tx", t="0sec" )
		maya.cmds.setKeyframe( cluster, attribute="tx", t="1sec", v=-1 )

		scene = IECoreMaya.LiveScene()
		cube = scene.child( "pCube1" )

		# read mesh at different times:
		maya.cmds.currentTime( "0.0sec" )
		mesh0   = cube.readObject( 0 )
		maya.cmds.currentTime( "0.5sec" )
		mesh0_5 = cube.readObject( 0.5 )
		maya.cmds.currentTime( "1.0sec" )
		mesh1   = cube.readObject( 1 )

		# have we moved vertex 0?
		self.assertEqual( mesh0["P"].data[0].x, -0.5 )
		self.assertEqual( mesh0_5["P"].data[0].x, -1 )
		self.assertEqual( mesh1["P"].data[0].x, -1.5 )

	def testReadBound( self ) :

		# create some cubes:
		maya.cmds.polyCube( name = "pCube1" )
		maya.cmds.polyCube( name = "pCube2" )
		maya.cmds.polyCube( name = "pCube3" )
		maya.cmds.polyCube( name = "pCube4" )

		maya.cmds.parent( "pCube2", "pCube1" )
		maya.cmds.parent( "pCube3", "pCube1" )

		maya.cmds.setAttr( "pCube4.tx", 3 )
		maya.cmds.setAttr( "pCube4.ty", 3 )
		maya.cmds.setAttr( "pCube4.tz", 3 )

		maya.cmds.setAttr( "pCube2.tx", 1 )
		maya.cmds.setAttr( "pCube2.ty", 1 )
		maya.cmds.setAttr( "pCube2.tz", 1 )

		maya.cmds.setAttr( "pCube3.tx", -1 )
		maya.cmds.setAttr( "pCube3.ty", -1 )
		maya.cmds.setAttr( "pCube3.tz", -1 )

		scene = IECoreMaya.LiveScene()
		cube4Transform = scene.child( "pCube4" )
		cube1Transform = scene.child( "pCube1" )

		maya.cmds.currentTime( "0.0sec" )
		self.assertEqual( scene.readBound( 0.0 ), imath.Box3d( imath.V3d( -1.5, -1.5, -1.5 ), imath.V3d( 3.5, 3.5, 3.5 ) ) )

		self.assertEqual( cube4Transform.readBound( 0.0 ), imath.Box3d( imath.V3d( -0.5, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )

		# check it's including its children:
		self.assertEqual( cube1Transform.readBound( 0.0 ), imath.Box3d( imath.V3d( -1.5, -1.5, -1.5 ), imath.V3d( 1.5, 1.5, 1.5 ) ) )

		maya.cmds.setAttr( "pCube1.tx", 1 )
		maya.cmds.setAttr( "pCube1.ty", 1 )
		maya.cmds.setAttr( "pCube1.tz", 1 )

		# should be in object space!!!
		self.assertEqual( cube1Transform.readBound( 0.0 ), imath.Box3d( imath.V3d( -1.5, -1.5, -1.5 ), imath.V3d( 1.5, 1.5, 1.5 ) ) )

		cube2Transform = cube1Transform.child( "pCube2" )
		self.assertEqual( cube2Transform.readBound( 0.0 ), imath.Box3d( imath.V3d( -0.5, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )

		cube3Transform = cube1Transform.child( "pCube3" )
		self.assertEqual( cube3Transform.readBound( 0.0 ), imath.Box3d( imath.V3d( -0.5, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )

	def testAnimatedMeshBound( self ) :

		# Currently fails, because I'm pulling on the boundingBox plugs at arbitrary
		# times, and that doesn't work, although it kind of should!

		maya.cmds.polyCube( name = "pCube2" )

		# create a skin cluster to animate vertex 0:
		maya.cmds.select( cl=True )
		maya.cmds.select( "pCube2.vtx[0]", r=True )
		cluster = maya.mel.eval( 'newCluster "-envelope 1"' )[1]

		maya.cmds.setKeyframe( cluster, attribute="tx", t="0sec" )
		maya.cmds.setKeyframe( cluster, attribute="tx", t="1sec", v=-1 )

		scene = IECoreMaya.LiveScene()
		transformChild = scene.child( "pCube2" )

		maya.cmds.currentTime( "0.0sec" )
		self.assertEqual( transformChild.readBound( 0.0 ), imath.Box3d( imath.V3d( -0.5, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )
		maya.cmds.currentTime( "0.5sec" )
		self.assertEqual( transformChild.readBound( 0.5 ), imath.Box3d( imath.V3d( -1.0, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )
		maya.cmds.currentTime( "1.0sec" )
		self.assertEqual( transformChild.readBound( 1.0 ), imath.Box3d( imath.V3d( -1.5, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )

	def testAnimatedBound( self ) :

		# Currently fails, because I'm pulling on the boundingBox plugs at arbitrary
		# times, and that doesn't work, although it kind of should!

		maya.cmds.polyCube( name = "pCube1" )
		maya.cmds.createNode( "transform", name = "pCube1Parent" )

		maya.cmds.parent( "pCube1", "pCube1Parent" )

		maya.cmds.setKeyframe( "pCube1", attribute="tx", t="0sec", v=0 )
		maya.cmds.setKeyframe( "pCube1", attribute="tx", t="1sec", v=-1 )

		scene = IECoreMaya.LiveScene()
		transformChild = scene.child( "pCube1Parent" )

		maya.cmds.currentTime( "0.0sec" )
		self.assertEqual( transformChild.readBound( 0.0 ), imath.Box3d( imath.V3d( -0.5, -0.5, -0.5 ), imath.V3d( 0.5, 0.5, 0.5 ) ) )
		maya.cmds.currentTime( "0.5sec" )
		self.assertEqual( transformChild.readBound( 0.5 ), imath.Box3d( imath.V3d( -1.0, -0.5, -0.5 ), imath.V3d( 0.0, 0.5, 0.5 ) ) )
		maya.cmds.currentTime( "1.0sec" )
		self.assertEqual( transformChild.readBound( 1.0 ), imath.Box3d( imath.V3d( -1.5, -0.5, -0.5 ), imath.V3d( -0.5, 0.5, 0.5 ) ) )

	def testMeshChange( self ) :

		sphere = maya.cmds.polySphere( name="pSphere1" )

		scene = IECoreMaya.LiveScene()
		sphere = scene.child( "pSphere1" )

		maya.cmds.currentTime( "0.0sec" )
		mesh = sphere.readObject( 0 )

		# should default to 382 verts:
		self.assertEqual( len( mesh["P"].data ), 382 )

		maya.cmds.setAttr( "polySphere1.subdivisionsAxis", 3 )
		maya.cmds.setAttr( "polySphere1.subdivisionsHeight", 3 )

		mesh = sphere.readObject( 0 )

		# should be 8 verts now:
		self.assertEqual( len( mesh["P"].data ), 8 )

	def testWriteExceptions( self ) :

		scene = IECoreMaya.LiveScene()

		self.assertRaises( RuntimeError, IECore.curry( scene.writeBound, imath.Box3d(), 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( scene.writeTransform, IECore.M44dData( imath.M44d() ), 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( scene.writeAttribute, "asdfs", IECore.BoolData( False ), 0.0 ) )
		self.assertRaises( RuntimeError, IECore.curry( scene.writeObject, IECoreScene.SpherePrimitive(), 0.0 ) )

	def testSceneShapeCustomReaders( self ):

		# make sure we are at time 0
		maya.cmds.currentTime( "0sec" )
		scene = IECoreMaya.LiveScene()

		envShape = str( IECoreMaya.FnSceneShape.create( "ieScene1" ).fullPathName() )
		envNode = 'ieScene1'

		envScene = scene.child( envNode )
		self.assertFalse( envScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )

		maya.cmds.setAttr( envShape+'.file', 'test/IECore/data/sccFiles/environment.lscc',type='string' )

		self.assertTrue( envScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )

		spheresShape = str( IECoreMaya.FnSceneShape.create( "ieScene2" ).fullPathName() )
		spheresNode = 'ieScene2'
		maya.cmds.setAttr( spheresShape+'.file', 'test/IECore/data/sccFiles/animatedSpheres.scc',type='string' )

		self.assertEqual( set( scene.childNames() ).intersection([ envNode, spheresNode ]) , set( [ envNode, spheresNode ] ) )
		self.assertTrue( IECoreScene.LinkedScene.linkAttribute in envScene.attributeNames() )
		self.assertEqual( envScene.readAttribute( IECoreScene.LinkedScene.linkAttribute, 0 ), IECore.CompoundData( { "fileName":IECore.StringData('test/IECore/data/sccFiles/environment.lscc'), "root":IECore.InternedStringVectorData() } ) )
		self.assertFalse( envScene.hasObject() )

		spheresScene = scene.child( spheresNode )
		self.assertTrue( spheresScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )
		self.assertEqual( spheresScene.readAttribute( IECoreScene.LinkedScene.linkAttribute, 0 ), IECore.CompoundData( { "fileName":IECore.StringData('test/IECore/data/sccFiles/animatedSpheres.scc'), "root":IECore.InternedStringVectorData() } ) )
		self.assertFalse( spheresScene.hasObject() )

		# expand the scene
		fnSpheres = IECoreMaya.FnSceneShape( spheresShape )
		fnSpheres.expandAll()

		self.assertFalse( spheresScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )
		leafScene = spheresScene.child("A").child("a")
		self.assertTrue( leafScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )
		# When expanding, we connect the child time attributes to their scene shape parent time attribute to propagate time remapping. When checking for time remapping, the scene shape
		# currently only checks the direct connection, so we have here time in the link attributes. Will have to look out for performance issues.
		self.assertEqual( leafScene.readAttribute( IECoreScene.LinkedScene.linkAttribute, 0 ), IECore.CompoundData( { "fileName":IECore.StringData('test/IECore/data/sccFiles/animatedSpheres.scc'), "root":IECore.InternedStringVectorData([ 'A', 'a' ]), 'time':IECore.DoubleData( 0 ) } ) )
		self.assertFalse( leafScene.hasObject() )

		# expand scene to meshes
		fnSpheres.convertAllToGeometry()
		self.assertFalse( leafScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )
		self.assertTrue( leafScene.hasObject() )
		self.assertTrue( isinstance( leafScene.readObject(0), IECoreScene.MeshPrimitive) )

		# test time remapped scene readers...
		spheresShape = str( maya.cmds.createNode( 'ieSceneShape' ) )
		maya.cmds.setAttr( spheresShape+'.file', 'test/IECore/data/sccFiles/animatedSpheres.scc',type='string' )
		maya.cmds.setAttr( spheresShape+'.time', 24.0*10 )

		spheresScene = scene.child( 'ieScene3' )

		self.assertTrue( spheresScene.hasAttribute( IECoreScene.LinkedScene.linkAttribute ) )
		self.assertEqual( spheresScene.readAttribute( IECoreScene.LinkedScene.linkAttribute, 0 ), IECore.CompoundData( { "fileName":IECore.StringData('test/IECore/data/sccFiles/animatedSpheres.scc'), "root":IECore.InternedStringVectorData(), "time":IECore.DoubleData(10.0) } ) )

	def testReadRootAttribute( self ):

		maya.cmds.file( new=True, f=True )
		# make sure we are at time 0
		maya.cmds.currentTime( "0sec" )
		scene = IECoreMaya.LiveScene()

		# tests a bug where calling attributeNames at the root raised an exception
		scene.attributeNames()

	def testTags( self ) :

		t = maya.cmds.createNode( "transform" )
		maya.cmds.addAttr( t, ln="ieTags", dt="string" )
		maya.cmds.setAttr( t + ".ieTags", "pizza burger", type="string" )

		scene = IECoreMaya.LiveScene()
		transformScene = scene.child(str(t))

		self.assertEqual( set( transformScene.readTags() ), set( [IECore.InternedString("pizza"), IECore.InternedString("burger") ] ) )

	def testCustomTags( self ) :

		t = maya.cmds.createNode( "transform" )
		maya.cmds.select( clear = True )
		sphere = maya.cmds.polySphere( name="pSphere" )

		doTest = True

		def hasMyTags( node, tag, tagFilter ) :
			#'archivable' should be on all transforms and 'renderable' only at shape transforms.

			if not doTest:
				return False

			if tag not in ( "renderable", "archivable" ) :
				return False

			if tag == "archivable"  :
				return True

			dagPath = IECoreMaya.StringUtil.dagPathFromString(node)
			try:
				dagPath.extendToShapeDirectlyBelow(0)
			except:
				return False

			if not ( tagFilter & IECoreScene.SceneInterface.TagFilter.LocalTag ) :
				return False

			if dagPath.apiType() != maya.OpenMaya.MFn.kMesh :
				return False

			return dagPath.fullPathName().endswith("Shape")

		def readMyTags( node, tagFilter ) :
			#'archivable' should be on all transforms and 'renderable' only at shape transforms.

			if not doTest:
				return []

			result = [ "archivable" ]

			dagPath = IECoreMaya.StringUtil.dagPathFromString(node)
			try:
				dagPath.extendToShapeDirectlyBelow(0)
			except:
				return result

			if tagFilter & IECoreScene.SceneInterface.TagFilter.LocalTag and dagPath.apiType() == maya.OpenMaya.MFn.kMesh :
				result.append( "renderable" )

			return result

		IECoreMaya.LiveScene.registerCustomTags( hasMyTags, readMyTags )

		scene = IECoreMaya.LiveScene()
		transformScene = scene.child(str(t))
		sphereScene = scene.child('pSphere')
		self.assertFalse( scene.hasTag( 'renderable' ) )
		self.assertFalse( scene.hasTag( 'archivable' ) )
		self.assertEqual( scene.readTags(), [] )
		self.assertFalse( transformScene.hasTag( 'renderable' ) )
		self.assertTrue( transformScene.hasTag( 'archivable' ) )
		self.assertEqual( transformScene.readTags(), [ IECore.InternedString('archivable') ] )
		self.assertEqual( set(sphereScene.readTags()), set([ IECore.InternedString('renderable'), IECore.InternedString('archivable') ]) )
		self.assertEqual( set(sphereScene.readTags( IECoreScene.SceneInterface.TagFilter.EveryTag )), set([ IECore.InternedString('renderable'), IECore.InternedString('archivable') ]) )
		self.assertEqual( sphereScene.readTags( IECoreScene.SceneInterface.TagFilter.AncestorTag ), [ IECore.InternedString('archivable') ] )
		self.assertTrue( sphereScene.hasTag( 'renderable') )
		self.assertTrue( sphereScene.hasTag( 'archivable') )

		# Disable custom tag functions so they don't mess with other tests
		doTest = False

	def testAttributes( self ) :

		maya.cmds.currentTime( "0sec" )
		t = maya.cmds.createNode( "transform", name="t1" )

		maya.cmds.addAttr( t, ln="ieAttr_bool", at="bool" )
		maya.cmds.addAttr( t, ln="ieAttr_float", at="float" )
		maya.cmds.addAttr( t, ln="ieAttr_double", at="double" )
		maya.cmds.addAttr( t, ln="ieAttr_doubleAngle", at="doubleAngle" )
		maya.cmds.addAttr( t, ln="ieAttr_doubleLinear", at="doubleLinear" )
		maya.cmds.addAttr( t, ln="ieAttr_message", at="message" )
		maya.cmds.addAttr( t, ln="ieAttr_time", at="time" )
		maya.cmds.addAttr( t, ln="ieAttr_fltMatrix", at="fltMatrix" )
		maya.cmds.addAttr( t, ln="ieAttr_string", dt="string" )
		maya.cmds.addAttr( t, ln="ieAttr_with__namespace", dt="string" )

		maya.cmds.addAttr( t, ln="ieAttr_enum", at="enum", en="ABC:DEF:"  )
		maya.cmds.addAttr( t, ln="ieAttr_enumAsString", at="enum", en="GHI:JKL:"  )

		# add ieConvertToStringData category
		p = IECoreMaya.plugFromString( t+'.ieAttr_enumAsString' )
		fn = OpenMaya.MFnEnumAttribute( p.attribute() )
		fn.addToCategory( IECoreMaya.FromMayaEnumPlugConverterst.convertToStringCategory )

		scene = IECoreMaya.LiveScene()
		transformScene = scene.child(str(t))

		self.assertEqual( set( transformScene.attributeNames()),
			set( [
				"scene:visible",
				"user:bool",
				"user:enum",
				"user:enumAsString",
				"user:float",
				"user:double",
				"user:doubleAngle",
				"user:doubleLinear",
				"user:message",
				"user:time",
				"user:fltMatrix",
				"user:string",
				"user:with:namespace"
			] )
		)

		self.assertTrue( isinstance( transformScene.readAttribute("user:bool",0), IECore.BoolData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:enum",0), IECore.ShortData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:enumAsString",0), IECore.StringData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:float",0), IECore.FloatData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:double",0), IECore.DoubleData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:doubleAngle",0), IECore.DoubleData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:doubleLinear",0), IECore.DoubleData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:message",0), IECore.NullObject ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:time",0), IECore.DoubleData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:fltMatrix",0), IECore.M44dData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:string",0), IECore.StringData ) )
		self.assertTrue( isinstance( transformScene.readAttribute("user:with:namespace",0), IECore.StringData ) )

	def testHasAttribute( self ):
		maya.cmds.currentTime( '0sec' )
		t = maya.cmds.createNode( 'transform', name='t1' )
		maya.cmds.addAttr( t, longName='ieAttr_bool', attributeType='bool' )

		scene = IECoreMaya.LiveScene()
		transformScene = scene.child( str( t ) )

		self.assertTrue( transformScene.hasAttribute( 'user:bool' ) )

	def testCustomAttributes( self ) :

		t = maya.cmds.createNode( "transform" )
		maya.cmds.select( clear = True )
		sphere = maya.cmds.polySphere( name="pSphere" )
		maya.cmds.currentTime( "0sec" )

		doTest = True

		def myAttributeNames( node ) :

			if not doTest:
				return []
			if not node:
				return ["root"]

			dagPath = IECoreMaya.StringUtil.dagPathFromString(node)
			try:
				dagPath.extendToShapeDirectlyBelow(0)
			except:
				return ["transformAttribute"]

			if dagPath.apiType() != maya.OpenMaya.MFn.kMesh :
				return []

			return ["shapeAttribute"]

		def readMyAttribute( node, attr ) :

			if not doTest:
				return None

			if not node :
				if attr == "root":
					return IECore.BoolData( True )
				return None

			dagPath = IECoreMaya.StringUtil.dagPathFromString(node)
			try:
				dagPath.extendToShapeDirectlyBelow(0)
			except:
				if attr == "shapeAttribute":
					return None
				return IECore.FloatData( 5 )

			if attr == "transformAttribute":
				return None

			if dagPath.apiType() != maya.OpenMaya.MFn.kMesh :
				return None

			return IECore.StringData("mesh")

		try:
			IECoreMaya.LiveScene.registerCustomAttributes( myAttributeNames, readMyAttribute )

			scene = IECoreMaya.LiveScene()
			transformScene = scene.child(str(t))
			sphereScene = scene.child('pSphere')
			self.assertEqual( set( scene.attributeNames() ), set( [ "scene:visible", "root" ] ) )
			self.assertEqual( scene.readAttribute("anyAttr", 0.0), IECore.NullObject.defaultNullObject() )
			self.assertEqual( scene.readAttribute("scene:visible", 0.0), IECore.BoolData(True) )
			self.assertEqual( scene.readAttribute("root", 0.0), IECore.BoolData(True) )

			self.assertEqual( transformScene.attributeNames(), [ IECore.InternedString("scene:visible"), IECore.InternedString("transformAttribute") ] )
			self.assertEqual( transformScene.hasAttribute("shapeAttribute"), False )
			self.assertEqual( transformScene.readAttribute("shapeAttribute", 0.0), IECore.NullObject.defaultNullObject() )
			self.assertEqual( transformScene.readAttribute( "transformAttribute", 0.0), IECore.FloatData(5) )
			self.assertEqual( sphereScene.attributeNames(), [ IECore.InternedString("scene:visible"), IECore.InternedString('shapeAttribute') ] )
			self.assertEqual( sphereScene.readAttribute( "shapeAttribute", 0.0), IECore.StringData("mesh") )

		finally:
			# Disable custom attribute functions so they don't mess with other tests
			doTest = False

	def testCustomAttributesMightHave( self ) :

		t = maya.cmds.createNode( "transform" )
		maya.cmds.select( clear = True )
		sphere = maya.cmds.polySphere( name="pSphere" )
		maya.cmds.currentTime( "0sec" )

		attrFnResult = []
		mightHaveFnResult = []

		doTest = True

		def readMyAttribute( node, attr ) :
			return None

		def myAttributeNames( node ) :
			if not doTest:
				return []

			attrFnResult.append( node )

			return [ "mightHaveAttribute2" ]

		def myAttributeMightHave( node, attr ) :
			if not doTest:
				return False

			mightHaveFnResult.append( ( node, attr ) )

			return attr in [ "mightHaveAttribute1", "mightHaveAttribute2" ]

		try:
			IECoreMaya.LiveScene.registerCustomAttributes( myAttributeNames, readMyAttribute, myAttributeMightHave )

			scene = IECoreMaya.LiveScene()
			transformScene = scene.child(str(t))

			self.assertEqual( transformScene.hasAttribute("nonExistentCustomAttribute"), False )
			self.assertEqual( mightHaveFnResult[0][1], "nonExistentCustomAttribute" ) # myAttributeMightHave() should always be called when specified.
			self.assertEqual( len( attrFnResult ), 0 ) # myAttributeNames() should not have been called because myAttributeMightHave had returned False.

			self.assertEqual( transformScene.hasAttribute("mightHaveAttribute1"), False )
			self.assertEqual( mightHaveFnResult[1][1], "mightHaveAttribute1" )
			self.assertEqual( len( attrFnResult ), 1 ) # myAttributeNames() should have been called because myAttributeMightHave had returned True.

			self.assertEqual( transformScene.hasAttribute("mightHaveAttribute2"), True )
			self.assertEqual( mightHaveFnResult[2][1], "mightHaveAttribute2" )
			self.assertEqual( len( attrFnResult ), 2 )

		finally:
			# Disable custom attribute functions so they don't mess with other tests
			doTest = False

	def testNoDuplicateAttributeNames( self ) :

		t = maya.cmds.createNode( "transform" )
		maya.cmds.currentTime( "0sec" )

		maya.cmds.addAttr( t, ln="ieAttr_test", at="bool" )

		doDuplicateNameTest = True

		def myAttributeNames( node ):
			if not doDuplicateNameTest:
				return []
			return["user:test"]

		def readMyAttribute( node, attr ):
			if not doDuplicateNameTest:
				return None
			if attr == "user:test":
				return IECore.IntData( 1 )

		IECoreMaya.LiveScene.registerCustomAttributes( myAttributeNames, readMyAttribute )

		try:
			scene = IECoreMaya.LiveScene()
			transformScene = scene.child(str(t))

			# we've specified an attribute called "user:test" in two ways - once through an ieAttr_,
			# once through a custom reader. The name "user:test" should only appear once:
			self.assertEqual( len( transformScene.attributeNames() ), 2 )
			self.assertEqual( set( transformScene.attributeNames() ), set( ["scene:visible", "user:test"] ) )

			# The ieAttr_ should override the custom reader
			self.assertTrue( isinstance( transformScene.readAttribute( "user:test", 0 ), IECore.BoolData ) )
		finally:
			doDuplicateNameTest = False

	def testCustomAttributePrecedence( self ) :

		doCustomAttributePrecedenceTest = True

		t = maya.cmds.createNode( "transform" )
		maya.cmds.currentTime( "0sec" )

		def myAttributeNames1( node ):
			if not doCustomAttributePrecedenceTest:
				return []
			return["test"]

		def readMyAttribute1( node, attr ):
			if not doCustomAttributePrecedenceTest:
				return None
			if attr == "test":
				return IECore.IntData( 1 )

		def myAttributeNames2( node ):
			if not doCustomAttributePrecedenceTest:
				return []
			return["test"]

		def readMyAttribute2( node, attr ):
			if not doCustomAttributePrecedenceTest:
				return None
			if attr == "test":
				return IECore.IntData( 2 )

		IECoreMaya.LiveScene.registerCustomAttributes( myAttributeNames1, readMyAttribute1 )
		IECoreMaya.LiveScene.registerCustomAttributes( myAttributeNames2, readMyAttribute2 )

		try:
			scene = IECoreMaya.LiveScene()
			transformScene = scene.child(str(t))

			# The second custom reader we registered should have taken precedence:
			self.assertEqual( transformScene.readAttribute( "test", 0 ), IECore.IntData(2) )
		finally:
			doCustomAttributePrecedenceTest = False


	def testSceneVisible( self ) :

		maya.cmds.createNode( "transform", name = "t1" )

		scene = IECoreMaya.LiveScene()
		t1 = scene.child( "t1" )

		# Root should always be visible
		self.assertEqual( scene.hasAttribute( "scene:visible" ), True )
		self.assertIn( 'scene:visible', scene.attributeNames() )
		self.assertEqual( scene.readAttribute( "scene:visible", 0 ), IECore.BoolData( True ) )

		# Test visibility on transform
		self.assertEqual( t1.attributeNames(), ["scene:visible"] )
		self.assertEqual( t1.hasAttribute( "scene:visible" ), True )
		self.assertEqual( t1.readAttribute( "scene:visible", 0 ), IECore.BoolData( True ) )

		maya.cmds.setAttr( "t1.visibility", False )
		self.assertEqual( t1.readAttribute( "scene:visible", 0 ), IECore.BoolData( False ) )

		# Test override of maya visibility with visibilityOverrideName attribute
		maya.cmds.addAttr( "t1", ln=IECoreMaya.LiveScene.visibilityOverrideName, at="bool" )
		maya.cmds.setAttr( "t1." + IECoreMaya.LiveScene.visibilityOverrideName.value(), True )
		self.assertEqual( t1.readAttribute( "scene:visible", 0 ), IECore.BoolData( True ) )

		maya.cmds.setAttr( "t1.visibility", True )
		maya.cmds.setAttr( "t1." + IECoreMaya.LiveScene.visibilityOverrideName.value(), False )
		self.assertEqual( t1.readAttribute( "scene:visible", 0 ), IECore.BoolData( False ) )

	def testSceneShapeVisible( self ) :

		# make sure we are at time 0
		maya.cmds.currentTime( "0sec" )
		scene = IECoreMaya.LiveScene()

		envShape = str( IECoreMaya.FnSceneShape.create( "ieScene1" ).fullPathName() )
		envNode = 'ieScene1'

		envScene = scene.child( envNode )
		self.assertTrue( IECore.InternedString( "scene:visible" ) in envScene.attributeNames() )

		maya.cmds.setAttr( envShape+'.file', 'test/IECore/data/sccFiles/animatedSpheres.scc',type='string' )
		self.assertTrue( IECore.InternedString( "scene:visible" ) in envScene.attributeNames() )

		maya.cmds.setAttr( "ieScene1.visibility", False )
		self.assertEqual( envScene.readAttribute( "scene:visible", 0 ), IECore.BoolData( False ) )

		maya.cmds.setAttr( "ieScene1.visibility", True )
		self.assertEqual( envScene.readAttribute( "scene:visible", 0 ), IECore.BoolData( True ) )

		# This test asserts that shape nodes no longer affect the transform visibility
		maya.cmds.setAttr( envShape + ".visibility", False )
		self.assertEqual( envScene.readAttribute( "scene:visible", 0 ), IECore.BoolData( True ) )

	def testMultiCurves( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		maya.cmds.curve( d=1, p=[ ( 0, 0, 0 ), ( 1, 0, 0 ) ], k=( 0, 1 ), n="curve1" )
		maya.cmds.curve( d=1, p=[ ( 0, 0, 0 ), ( 0, 0, 1 ) ], k=( 0, 1 ), n="curve2" )
		maya.cmds.curve( d=1, p=[ ( 0, 0, 0 ), ( 0, 0, 1 ) ], k=( 0, 1 ), n="curve2" )

		maya.cmds.select( "curveShape1", "curveShape2", "curveShape3", "sharedParent")
		maya.cmds.parent( s=True, r=True )

		maya.cmds.setAttr( "curveShape3.intermediateObject", 1 )

		scene = IECoreMaya.LiveScene()
		scene = scene.child('sharedParent')
		maya.cmds.currentTime( "0.0sec" )
		mergedCurves = scene.readObject( 0 )
		self.assertEqual( mergedCurves.numCurves(), 2 )

	def testMultiCurvesWithDifferentDegrees( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		maya.cmds.curve( d=3, p=[ ( 0, 0, 0 ), ( 1, 0, 0 ), ( 2, 0, 0 ), ( 3, 0, 0 ) ], k=( 0, 0, 0, 1, 1, 1 ), n="curve1" )
		maya.cmds.curve( d=1, p=[ ( 0, 0, 0 ), ( 0, 0, 1 ) ], k=( 0, 1 ), n="curve2" )
		maya.cmds.curve( d=1, p=[ ( 0, 0, 0 ), ( 0, 0, 1 ) ], k=( 0, 1 ), n="curve3" )

		maya.cmds.select( "curveShape1", "curveShape2", "curveShape3", "sharedParent")
		maya.cmds.parent( s=True, r=True )

		scene = IECoreMaya.LiveScene()
		scene = scene.child('sharedParent')
		maya.cmds.currentTime( "0.0sec" )
		curve = scene.readObject( 0 )
		self.assertEqual( curve.numCurves(), 1 ) # Still has object but curves are not merged.

	def testMultiCurvesWithDifferentForms( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		maya.cmds.curve( d=3, per=True, p=[(0, 0, 0), (3, 5, 6), (5, 6, 7), (9, 9, 9), (0, 0, 0), (3, 5, 6), (5, 6, 7)], k=[-2,-1,0,1,2,3,4,5,6], n="curve1" )
		maya.cmds.curve( d=3, p=[ ( 0, 0, 0 ), ( 1, 0, 0 ), ( 2, 0, 0 ), ( 3, 0, 0 ) ], k=( 0, 0, 0, 1, 1, 1 ), n="curve2" )
		maya.cmds.curve( d=3, p=[ ( 0, 0, 0 ), ( 1, 0, 0 ), ( 2, 0, 0 ), ( 3, 0, 0 ) ], k=( 0, 0, 0, 1, 1, 1 ), n="curve3" )

		maya.cmds.select( "curveShape1", "curveShape2", "curveShape3", "sharedParent")
		maya.cmds.parent( s=True, r=True )

		scene = IECoreMaya.LiveScene()
		scene = scene.child('sharedParent')
		maya.cmds.currentTime( "0.0sec" )
		curve = scene.readObject( 0 )
		self.assertEqual( curve.numCurves(), 1 ) # Still has object but curves are not merged.

	def testMultiMeshes( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		maya.cmds.polyPyramid()
		maya.cmds.polyPyramid()
		maya.cmds.polyPyramid()

		maya.cmds.select( "pPyramidShape1", "pPyramidShape2", "pPyramidShape3", "sharedParent" )
		maya.cmds.parent( s=True, r=True )

		maya.cmds.setAttr( "pPyramidShape3.intermediateObject", 1 )

		scene = IECoreMaya.LiveScene()
		scene = scene.child('sharedParent')
		maya.cmds.currentTime( "0.0sec" )
		mergedMeshes = scene.readObject( 0 )
		self.assertEqual( mergedMeshes.numFaces(), 10 )

	def testSetsWithoutExportAttributeAreNotExported( self ) :
		maya.cmds.createNode( "transform", name="sharedParent" )

		sphere = maya.cmds.polySphere( name="pSphere" )[0]

		maya.cmds.select( sphere )
		maya.cmds.sets(name="mySet")

		root = IECoreMaya.LiveScene()
		tags = root.child('pSphere').readTags()

		self.assertEqual( len(tags), 0)


	def testSetWithExportSetToFalseIsNotExported( self ) :
		maya.cmds.createNode( "transform", name="sharedParent" )

		sphere = maya.cmds.polySphere( name="pSphere" )[0]

		maya.cmds.select( sphere )
		maya.cmds.sets(name="mySet")

		maya.cmds.addAttr("mySet", longName="ieExport", at="bool")
		maya.cmds.setAttr("mySet.ieExport", False)

		root = IECoreMaya.LiveScene()
		tags = root.child('pSphere').readTags()

		self.assertEqual( len(tags), 0)

	def testConvertsMayaSetsToTags( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		sphere = maya.cmds.polySphere( name="pSphere" )[0]

		maya.cmds.select( sphere )
		maya.cmds.sets(name="mySet")

		maya.cmds.addAttr("mySet", longName="ieExport", at="bool")
		maya.cmds.setAttr("mySet.ieExport", True)

		root = IECoreMaya.LiveScene()
		tags = root.child('pSphere').readTags()

		self.assertEqual( len(tags), 1)
		self.assertEqual( tags[0], "mySet")

	def testConvertsMayaSetsOfSetsToTags( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		sphere = maya.cmds.polySphere( name="pSphere" )[0]

		maya.cmds.select( sphere )
		maya.cmds.sets(name="mySet")

		maya.cmds.addAttr("mySet", longName="ieExport", at="bool")
		maya.cmds.setAttr("mySet.ieExport", True)

		maya.cmds.select( "mySet" )
		maya.cmds.sets(name="mySet2")

		maya.cmds.addAttr("mySet2", longName="ieExport", at="bool")
		maya.cmds.setAttr("mySet2.ieExport", True)

		root = IECoreMaya.LiveScene()
		tags = root.child('pSphere').readTags()

		self.assertEqual( len(tags), 2)
		self.assertEqual( set(tags), set([IECore.InternedString("mySet"), IECore.InternedString("mySet2")]))


	def testOnlyObjectInSetIsExported( self ) :

		maya.cmds.createNode( "transform", name="sharedParent" )

		s = maya.cmds.polySphere( name="pSphere" )[0]

		maya.cmds.select( "{0}.f[1]".format(s) )
		maya.cmds.sets(name="mySet")

		maya.cmds.addAttr("mySet", longName="ieExport", at="bool")
		maya.cmds.setAttr("mySet.ieExport", True)

		root = IECoreMaya.LiveScene()
		tags = root.child(IECore.InternedString(str(s))).readTags()

		self.assertEqual( len(tags), 0)

	def testMayaInstancerIsExported( self ):

		def makeScene():

			maya.cmds.polyCube()
			maya.cmds.polySphere()

			maya.cmds.particle( p = [[4, 0, 0], [4, 4, 0], [0, 4, 0], [0, 0, 0]], c = 1 )
			maya.cmds.addAttr( "particleShape1", ln = "rotationPP", dt = "vectorArray" )
			maya.cmds.addAttr( "particleShape1", ln = "instancePP", dt = "doubleArray" )
			maya.cmds.select( ["particle1", "pCube1", "pSphere1"], r = True )
			maya.cmds.particleInstancer( addObject = True, object = ["pCube1","pSphere1"] )
			maya.cmds.particleInstancer( "particleShape1", e = True, name = "instancer1", rotation = "rotationPP" )
			maya.cmds.particleInstancer( "particleShape1", e = True, name = "instancer1", objectIndex = "instancePP" )

			maya.cmds.setAttr( "particleShape1.rotationPP", 4, ( 45, 0, 0 ), ( 0, 45, 0 ), ( 0, 0, 45 ), ( 45, 45, 0 ), type = "vectorArray" )
			maya.cmds.setAttr( "particleShape1.instancePP", [0, 1, 0, 1], type = "doubleArray" )

		makeScene()

		maya.cmds.currentTime( "0.0sec" )

		root = IECoreMaya.LiveScene()
		self.assertTrue( 'instancer1' in root.childNames() )

		instancer1 = root.child("instancer1")

		self.assertTrue( instancer1.hasObject() )

		convertedPoints = instancer1.readObject(0.0)
		self.assertTrue( convertedPoints.isInstanceOf( IECoreScene.TypeId.PointsPrimitive ) )
		self.assertEqual( convertedPoints.numPoints, 4)

	def testRecursiveGeoConvert( self ):
		"""Tests if the recursive geometry conversion works as expected and is only affecting the desired geo
		"""

		def createSCC():
			outScene = IECoreScene.SceneCache( LiveSceneTest.__testFile, IECore.IndexedIO.OpenMode.Write )

			rootSc = outScene.createChild('rootXform')
			expandSc = rootSc.createChild('expand')
			boxASc = expandSc.createChild('boxA')
			boxASc.writeTags(['EXPAND'])

			notExpandSc = rootSc.createChild('notExpand')
			boxBSc = notExpandSc.createChild('boxB')

			mesh = IECoreScene.MeshPrimitive.createBox(imath.Box3f(imath.V3f(0), imath.V3f(1)))
			mesh["Cs"] = IECoreScene.PrimitiveVariable(IECoreScene.PrimitiveVariable.Interpolation.Uniform, IECore.V3fVectorData([imath.V3f(0, 1, 0)] * 6))
			boxASc.writeObject(mesh, 0)
			boxBSc.writeObject(mesh, 0)

		# create test scene
		createSCC()

		# create shape with SCC path
		nodeName = 'sceneFile'
		sceneShape = str(IECoreMaya.FnSceneShape.create(nodeName).fullPathName())
		maya.cmds.setAttr(sceneShape + '.file', LiveSceneTest.__testFile, type='string')
		maya.cmds.setAttr(sceneShape + '.root', '/', type='string')

		# test live scene content
		maya.cmds.currentTime("0sec")
		liveScene = IECoreMaya.LiveScene()
		linkedScene = IECoreScene.LinkedScene(liveScene)
		nodeScene = linkedScene.child(nodeName)

		self.assertEqual(nodeScene.name(), nodeName)
		self.assertFalse(nodeScene.hasAttribute(IECoreScene.LinkedScene.linkAttribute))
		self.assertEqual(nodeScene.childNames(), ['rootXform'])

		fnShape = IECoreMaya.FnSceneShape(sceneShape)
		fnShape.convertAllToGeometry(tagName='EXPAND', preserveNamespace=True)

		expandScene = linkedScene.scene([nodeName, 'rootXform', 'expand'])
		self.assertEqual(expandScene.childNames(), ['boxA'])

		notExpandScene = linkedScene.scene([nodeName, 'rootXform', 'notExpand'])
		self.assertEqual(notExpandScene.childNames(), ['boxB'])
		self.assertEqual(maya.cmds.listRelatives("{}|rootXform|notExpand".format(nodeName), children=True, type='transform') or [], [])

	def testAnimatedPromotedAttributes( self ):
		def setupAnimAttrSCC():
			maya.cmds.file( new=True, force=True )
			scene = IECoreScene.SceneCache( LiveSceneTest.__testFile, IECore.IndexedIO.Write )
			scene.writeAttribute( 'scene:visible', IECore.BoolData( True ), time0 )
			scene.writeAttribute( 'user:testBool', IECore.BoolData( True ), time0 )
			scene.writeAttribute( 'user:testShort', IECore.ShortData( 2 ), time0 )
			scene.writeAttribute( 'user:testInt', IECore.IntData( 3 ), time0 )
			scene.writeAttribute( 'user:testInt64', IECore.Int64Data( 4 ), time0 )
			scene.writeAttribute( 'user:testFloat', IECore.FloatData( 5 ), time0 )
			scene.writeAttribute( 'user:testDouble', IECore.DoubleData( 6 ), time0 )
			scene.writeAttribute( 'user:testString', IECore.StringData( 'seven' ), time0 )
			mat = imath.M44d( ( 8, 9, 10, 11 ), ( 12, 13, 14, 15 ), ( 16, 17, 18, 19 ), ( 20, 21, 22, 23 ) )
			scene.writeAttribute( 'user:testMatrixd', IECore.M44dData(mat), time0 )
			mat = imath.M44f( ( 24, 25, 26, 27 ), ( 28, 29, 30, 31 ), ( 32, 33, 34, 35 ), ( 36, 37, 38, 39 ) )
			scene.writeAttribute( 'user:testMatrixf', IECore.M44fData(mat), time0 )

			scene.writeAttribute( 'scene:visible', IECore.BoolData( False ), time1 )
			scene.writeAttribute( 'user:testBool', IECore.BoolData( False ), time1 )
			scene.writeAttribute( 'user:testShort', IECore.ShortData( 20 ), time1 )
			scene.writeAttribute( 'user:testInt', IECore.IntData( 30 ), time1 )
			scene.writeAttribute( 'user:testInt64', IECore.Int64Data( 40 ), time1 )
			scene.writeAttribute( 'user:testFloat', IECore.FloatData( 50 ), time1 )
			scene.writeAttribute( 'user:testDouble', IECore.DoubleData( 60 ), time1 )
			scene.writeAttribute( 'user:testString', IECore.StringData( 'seventy' ), time1 )
			mat = imath.M44d( ( 80, 90, 100, 110 ), ( 120, 130, 140, 150 ), ( 160, 170, 180, 190 ), ( 200, 210, 220, 230 ) )
			scene.writeAttribute( 'user:testMatrixd', IECore.M44dData(mat), time1 )
			mat = imath.M44f( ( 240, 250, 260, 270 ), ( 280, 290, 300, 310 ), ( 320, 330, 340, 350 ), ( 360, 370, 380, 390 ) )
			scene.writeAttribute( 'user:testMatrixf', IECore.M44fData(mat), time1 )

			childScene = scene.createChild('cube_GEO')
			boxSize = imath.Box3f( imath.V3f( -.5, -.5, -.5 ), imath.V3f( .5, .5, .5 ) )
			childScene.writeObject( IECoreScene.MeshPrimitive.createBox(boxSize), time0 )
			childScene.writeObject( IECoreScene.MeshPrimitive.createBox(boxSize), time1 )

		time0, time1 = 0.0, 1.1
		setupAnimAttrSCC()

		# Prepare the maya scene
		sceneTransform = 'scene'
		sceneShapeFn = IECoreMaya.FnSceneShape.create( sceneTransform )
		sceneShape = sceneShapeFn.fullPathName()
		maya.cmds.setAttr( sceneShape + '.file', LiveSceneTest.__testFile, type='string' )
		maya.cmds.setAttr( sceneShape + '.root', '/', type='string' )

		liveRoot = IECoreMaya.LiveScene()
		liveScene = liveRoot.child( sceneTransform )

		# Read animated attributes before promotion
		maya.cmds.currentTime( str( time0 ) + 'sec' )
		# Not reading scene:visible because LiveScene will ignore the cached value unless it's promoted
		self.assertEqual( liveScene.readAttribute( 'user:testBool', time0 ), IECore.BoolData( True ) )
		self.assertEqual( liveScene.readAttribute( 'user:testShort', time0 ), IECore.ShortData( 2 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt', time0 ), IECore.IntData( 3 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt64', time0 ), IECore.Int64Data( 4 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testFloat', time0 ), IECore.FloatData( 5 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testDouble', time0 ), IECore.DoubleData( 6 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testString', time0 ), IECore.StringData( 'seven' ) )
		mat = imath.M44d( ( 8, 9, 10, 11 ), ( 12, 13, 14, 15 ), ( 16, 17, 18, 19 ), ( 20, 21, 22, 23 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixd', time0 ), IECore.M44dData( mat ) )
		mat = imath.M44f( ( 24, 25, 26, 27 ), ( 28, 29, 30, 31 ), ( 32, 33, 34, 35 ), ( 36, 37, 38, 39 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixf', time0 ), IECore.M44fData( mat ) )

		maya.cmds.currentTime( str( time1 ) + 'sec' )
		# Not reading scene:visible because LiveScene will ignore the cached value unless it's promoted
		self.assertEqual( liveScene.readAttribute( 'user:testBool', time1 ), IECore.BoolData( False ) )
		self.assertEqual( liveScene.readAttribute( 'user:testShort', time1 ), IECore.ShortData( 20 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt', time1 ), IECore.IntData( 30 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt64', time1 ), IECore.Int64Data( 40 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testFloat', time1 ), IECore.FloatData( 50 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testDouble', time1 ), IECore.DoubleData( 60 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testString', time1 ), IECore.StringData( 'seventy' ) )
		mat = imath.M44d( ( 80, 90, 100, 110 ), ( 120, 130, 140, 150 ), ( 160, 170, 180, 190 ), ( 200, 210, 220, 230 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixd', time1 ), IECore.M44dData( mat ) )
		mat = imath.M44f( ( 240, 250, 260, 270 ), ( 280, 290, 300, 310 ), ( 320, 330, 340, 350 ), ( 360, 370, 380, 390 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixf', time1 ), IECore.M44fData( mat ) )

		# Read animated values after promotion
		for attr in sceneShapeFn.promotableAttributeNames():
			sceneShapeFn.promoteAttribute( attr )

		maya.cmds.currentTime( str( time0 ) + 'sec' )
		self.assertEqual( liveScene.readAttribute( 'scene:visible', time0 ), IECore.BoolData( True ) )
		self.assertEqual( liveScene.readAttribute( 'user:testBool', time0 ), IECore.BoolData( True ) )
		self.assertEqual( liveScene.readAttribute( 'user:testShort', time0 ), IECore.ShortData( 2 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt', time0 ), IECore.IntData( 3 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt64', time0 ), IECore.IntData( 4 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testFloat', time0 ), IECore.FloatData( 5 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testDouble', time0 ), IECore.DoubleData( 6 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testString', time0 ), IECore.StringData( 'seven' ) )
		mat = imath.M44d( ( 8, 9, 10, 11 ), ( 12, 13, 14, 15 ), ( 16, 17, 18, 19 ), ( 20, 21, 22, 23 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixd', time0 ), IECore.M44dData( mat ) )
		mat = imath.M44d( ( 24, 25, 26, 27 ), ( 28, 29, 30, 31 ), ( 32, 33, 34, 35 ), ( 36, 37, 38, 39 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixf', time0 ), IECore.M44dData( mat ) )

		maya.cmds.currentTime( str( time1 ) + 'sec' )
		self.assertEqual( liveScene.readAttribute( 'scene:visible', time1 ), IECore.BoolData( False ) )
		self.assertEqual( liveScene.readAttribute( 'user:testBool', time1 ), IECore.BoolData( False ) )
		self.assertEqual( liveScene.readAttribute( 'user:testShort', time1 ), IECore.ShortData( 20 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt', time1 ), IECore.IntData( 30 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt64', time1 ), IECore.IntData( 40 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testFloat', time1 ), IECore.FloatData( 50 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testDouble', time1 ), IECore.DoubleData( 60 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testString', time1 ), IECore.StringData( 'seventy' ) )
		mat = imath.M44d( ( 80, 90, 100, 110 ), ( 120, 130, 140, 150 ), ( 160, 170, 180, 190 ), ( 200, 210, 220, 230 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixd', time1 ), IECore.M44dData( mat ) )
		mat = imath.M44d( ( 240, 250, 260, 270 ), ( 280, 290, 300, 310 ), ( 320, 330, 340, 350 ), ( 360, 370, 380, 390 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixf', time1 ), IECore.M44dData( mat ) )

		# Read overridden animated attributes
		destPlugs = [ attr for attr in maya.cmds.listConnections('sceneSceneShape', plugs=True, source=False, destination=True) if attr.startswith( 'scene.ie' ) ]
		for destPlug in destPlugs:
			sourcePlug = maya.cmds.connectionInfo( destPlug, sourceFromDestination=True )
			maya.cmds.disconnectAttr( sourcePlug, destPlug )

		maya.cmds.currentTime( str( time0 ) + 'sec' )
		maya.cmds.setAttr( sceneTransform + '.' + str( IECoreMaya.LiveScene.visibilityOverrideName ), False )
		maya.cmds.setKeyframe( sceneTransform + '.' + str( IECoreMaya.LiveScene.visibilityOverrideName ) )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testBool' , False )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testBool' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testShort', 20 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testShort' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testInt', 30 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testInt' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testInt64', 40 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testInt64' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testFloat', 50 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testFloat' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testDouble', 60 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testDouble' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testString', 'seventy', type='string' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testMatrixd', [ 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230 ], type='matrix' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testMatrixf', [ 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390 ], type='matrix' )

		maya.cmds.currentTime( str( time1 ) + 'sec' )
		maya.cmds.setAttr( sceneTransform + '.' + str( IECoreMaya.LiveScene.visibilityOverrideName ) , True )
		maya.cmds.setKeyframe( sceneTransform + '.' + str( IECoreMaya.LiveScene.visibilityOverrideName ) )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testBool' , True )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testBool' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testShort', 2 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testShort' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testInt', 3 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testInt' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testInt64', 4 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testInt64' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testFloat', 5 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testFloat' )
		maya.cmds.setAttr( sceneTransform + '.ieAttr_testDouble', 6 )
		maya.cmds.setKeyframe( sceneTransform + '.ieAttr_testDouble' )

		maya.cmds.currentTime( str( time0 ) + 'sec' )
		self.assertEqual( liveScene.readAttribute( 'scene:visible', time0 ), IECore.BoolData( False ) )
		self.assertEqual( liveScene.readAttribute( 'user:testBool', time0 ), IECore.BoolData( False ) )
		self.assertEqual( liveScene.readAttribute( 'user:testShort', time0 ), IECore.ShortData( 20 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt', time0 ), IECore.IntData( 30 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt64', time0 ), IECore.IntData( 40 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testFloat', time0 ), IECore.FloatData( 50 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testDouble', time0 ), IECore.DoubleData( 60 ) )

		# Data attributes are not keyable
		self.assertEqual( liveScene.readAttribute( 'user:testString', time0 ), IECore.StringData( 'seventy' ) )
		mat = imath.M44d( ( 80, 90, 100, 110 ), ( 120, 130, 140, 150 ), ( 160, 170, 180, 190 ), ( 200, 210, 220, 230 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixd', time0 ), IECore.M44dData( mat ) )
		mat = imath.M44d( ( 240, 250, 260, 270 ), ( 280, 290, 300, 310 ), ( 320, 330, 340, 350 ), ( 360, 370, 380, 390 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixf', time0 ), IECore.M44dData( mat ) )

		maya.cmds.currentTime( str( time1 ) + 'sec' )
		self.assertEqual( liveScene.readAttribute( 'scene:visible', time1 ), IECore.BoolData( True ) )
		self.assertEqual( liveScene.readAttribute( 'user:testBool', time1 ), IECore.BoolData( True ) )
		self.assertEqual( liveScene.readAttribute( 'user:testShort', time1 ), IECore.ShortData( 2 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt', time1 ), IECore.IntData( 3 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testInt64', time1 ), IECore.IntData( 4 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testFloat', time1 ), IECore.FloatData( 5 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testDouble', time1 ), IECore.DoubleData( 6 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testString', time1 ), IECore.StringData( 'seventy' ) )
		mat = imath.M44d( ( 80, 90, 100, 110 ), ( 120, 130, 140, 150 ), ( 160, 170, 180, 190 ), ( 200, 210, 220, 230 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixd', time1 ), IECore.M44dData( mat ) )
		mat = imath.M44d( ( 240, 250, 260, 270 ), ( 280, 290, 300, 310 ), ( 320, 330, 340, 350 ), ( 360, 370, 380, 390 ) )
		self.assertEqual( liveScene.readAttribute( 'user:testMatrixf', time1 ), IECore.M44dData( mat ) )

	def testToFromMayaAttributeName( self ):
		cortexUserAttr = 'user:attrName'
		mayaUserAttr = 'ieAttr_attrName'
		self.assertEqual( cortexUserAttr, IECoreMaya.LiveScene.fromMayaAttributeName( mayaUserAttr ) )
		self.assertEqual( mayaUserAttr, IECoreMaya.LiveScene.toMayaAttributeName( cortexUserAttr ) )

		cortexUserAttrWithNameSpace = 'user:ns:attrName'
		mayaUserAttrWithNameSpace = 'ieAttr_ns__attrName'
		self.assertEqual( cortexUserAttrWithNameSpace, IECoreMaya.LiveScene.fromMayaAttributeName( mayaUserAttrWithNameSpace ) )
		self.assertEqual( mayaUserAttrWithNameSpace, IECoreMaya.LiveScene.toMayaAttributeName( cortexUserAttrWithNameSpace ) )

		mayaVisibilityAttr = IECoreMaya.LiveScene.visibilityOverrideName
		cortexVisibilityAttr = IECoreScene.SceneInterface.visibilityName
		self.assertEqual( cortexVisibilityAttr, IECoreMaya.LiveScene.fromMayaAttributeName( mayaVisibilityAttr ) )
		self.assertEqual( mayaVisibilityAttr, IECoreMaya.LiveScene.toMayaAttributeName( cortexVisibilityAttr ) )

		cortexAttrWithoutMayaEquivalent = 'notForMaya:attrName'
		mayaAttrWithoutCortexEquivalent = 'notForCortex'
		self.assertFalse( IECoreMaya.LiveScene.fromMayaAttributeName( mayaAttrWithoutCortexEquivalent ) )
		self.assertFalse( IECoreMaya.LiveScene.toMayaAttributeName( cortexAttrWithoutMayaEquivalent ) )

	def testVisibilityOverrideName( self ) :
		self.assertEqual( IECoreMaya.LiveScene.visibilityOverrideName, 'ieVisibility' )

	def testDagPath( self ):
		group = str( maya.cmds.group( empty=True ) )
		cube = str( maya.cmds.polyCube( constructionHistory=False )[0] )
		maya.cmds.parent( cube, group )

		liveScene = IECoreMaya.LiveScene()
		cubeScene = liveScene.scene( [group, cube] )
		self.assertEqual( cubeScene.dagPath(), '|{}|{}'.format( group, cube ) )

	def testDagPathToPath( self ):
		group = str( maya.cmds.group( empty=True ) )
		cubeTransform = maya.cmds.polyCube( constructionHistory=False )[0]
		maya.cmds.parent( cubeTransform, group )
		cubeTransform = str( maya.cmds.ls( cubeTransform, long=True )[0] )
		cubeShape = str( maya.cmds.listRelatives( cubeTransform, fullPath=True )[0] )

		dagTransform = OpenMaya.MDagPath()
		dagShape = OpenMaya.MDagPath()
		sel = OpenMaya.MSelectionList()
		sel.add( cubeTransform )
		sel.add( cubeShape )
		sel.getDagPath( 0, dagTransform )
		sel.getDagPath( 0, dagShape )

		pathTransform = IECoreMaya.LiveScene.dagPathToPath( dagTransform.fullPathName() )
		self.assertEqual( pathTransform, cubeTransform[1:].split('|') )

		pathShape = IECoreMaya.LiveScene.dagPathToPath( dagShape.fullPathName() )
		self.assertEqual( pathShape, cubeTransform[1:].split('|') )

		pathRoot = IECoreMaya.LiveScene.dagPathToPath( '' )
		self.assertEqual( pathRoot, [] )

		self.assertRaises( Exception, IECoreMaya.LiveScene.dagPathToPath, '|invalid' )

	def testPathToDagPath( self ):
		group = str( maya.cmds.group( empty=True ) )
		cube = str( maya.cmds.polyCube( constructionHistory=False )[0] )
		maya.cmds.parent( cube, group )

		path = [group, cube]
		dagTransform = IECoreMaya.LiveScene.pathToDagPath( path )
		self.assertEqual( dagTransform, '|{}|{}'.format( group, cube ) )

		dagRoot = IECoreMaya.LiveScene.pathToDagPath( [] )
		self.assertEqual( dagRoot, '' )

		self.assertRaises( Exception, IECoreMaya.LiveScene.pathToDagPath, ['invalid'] )


if __name__ == "__main__":
	IECoreMaya.TestProgram( plugins = [ "ieCore" ] )

