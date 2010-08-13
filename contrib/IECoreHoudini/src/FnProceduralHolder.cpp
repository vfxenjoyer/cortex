//////////////////////////////////////////////////////////////////////////
//
//  Copyright 2010 Dr D Studios Pty Limited (ACN 127 184 954) (Dr. D Studios),
//  its affiliates and/or its licensors.
//
//  Copyright (c) 2010, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of Image Engine Design nor the names of any
//       other contributors to this software may be used to endorse or
//       promote products derived from this software without specific prior
//       written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include <PRM/PRM_Parm.h>
#include <OP/OP_Director.h>
#include <OP/OP_Node.h>
#include <SOP/SOP_Node.h>

#include "FnProceduralHolder.h"
#include "SOP_ProceduralHolder.h"

#include <IECore/ParameterisedProcedural.h>
#include <IECore/NumericParameter.h>
#include <IECorePython/ScopedGILLock.h>

#include <boost/lexical_cast.hpp>

using namespace IECoreHoudini;

FnProceduralHolder::FnProceduralHolder( SOP_Node *sop ) : FnParameterisedHolder()
{
	if ( !sop )
	{
		return;
	}

	if ( getProceduralHolder( sop ) )
	{
		setHolder( sop );
	}
	else
	{
		UT_String path;
		sop->getFullPath( path );
		std::cerr << path << " was not a valid ieProceduralHolder!" << std::endl;
	}
}

FnProceduralHolder::~FnProceduralHolder()
{
}

SOP_ProceduralHolder *FnProceduralHolder::getProceduralHolder( SOP_Node *sop )
{
	SOP_ProceduralHolder *procedural = 0;

	if ( sop )
	{
		procedural = dynamic_cast<SOP_ProceduralHolder*>( sop );
	}

	return procedural;
}

bool FnProceduralHolder::hasParameterised()
{
	if ( hasHolder() )
	{
		SOP_ProceduralHolder *holder = getProceduralHolder( static_cast<SOP_Node*>( m_handle.node() ) );
		if ( holder )
		{
			return holder->hasParameterised();
		}
	}
	
	return false;
}

void FnProceduralHolder::setParameterised( IECore::RunTimeTypedPtr p, const std::string &type, int version )
{
	if ( !p )
	{
		return;
	}

	if ( hasHolder() )
	{
		SOP_ProceduralHolder *holder = getProceduralHolder( static_cast<SOP_Node*>( m_handle.node() ) );
		if ( !holder )
		{
			return;
		}

		// set parameterised on holder
		holder->setParameterised( p, type, version );
	}
}

IECore::RunTimeTypedPtr FnProceduralHolder::getParameterised()
{
	if ( hasHolder() )
	{
		SOP_ProceduralHolder *holder = getProceduralHolder( static_cast<SOP_Node*>( m_handle.node() ) );
		if ( holder )
		{
			return holder->getParameterised();
		}
	}
	
	return 0;
}
