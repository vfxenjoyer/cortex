//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2021, Image Engine Design. All rights reserved.
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

#include "IECoreUSD/ShaderAlgo.h"

#include "IECoreUSD/DataAlgo.h"

#include "IECore/MessageHandler.h"

#include "boost/algorithm/string/replace.hpp"

namespace
{

	IECore::InternedString readShaderNetworkWalk( const pxr::SdfPath &anchorPath, const pxr::UsdShadeShader &usdShader, IECoreScene::ShaderNetwork &shaderNetwork )
	{
		IECore::InternedString handle( usdShader.GetPath().MakeRelativePath( anchorPath ).GetAsString() );

		if( shaderNetwork.getShader( handle ) )
		{
			return handle;
		}

		IECoreScene::ShaderPtr r = new IECoreScene::Shader();

		pxr::TfToken id;
		if( usdShader.GetShaderId( &id ) )
		{
			std::string name = id.GetString();
			size_t colonPos = name.find( ":" );
			if( colonPos != std::string::npos )
			{
				std::string prefix = name.substr( 0, colonPos );
				name = name.substr( colonPos + 1 );
				if( prefix == "arnold" )
				{
					prefix = "ai";
				}
				r->setType( prefix + ":shader" );
			}
			r->setName( name );
		}

		std::vector< std::tuple< IECore::InternedString, pxr::UsdShadeConnectableAPI, IECore::InternedString > > connections;
		std::vector< pxr::UsdShadeInput > inputs = usdShader.GetInputs();
		for( pxr::UsdShadeInput &i : usdShader.GetInputs() )
		{
			pxr::UsdShadeConnectableAPI usdSource;
			pxr::TfToken usdSourceName;
			pxr::UsdShadeAttributeType usdSourceType;

			if( IECore::DataPtr d = IECoreUSD::DataAlgo::fromUSD( pxr::UsdAttribute( i ) ) )
			{
				r->parameters()[ i.GetBaseName().GetString() ] = d;
			}

			if( i.GetConnectedSource( &usdSource, &usdSourceName, &usdSourceType ) )
			{
				connections.push_back( { i.GetBaseName().GetString(), usdSource, usdSourceName.GetString() } );
			}
		}

		shaderNetwork.addShader( handle, std::move( r ) );

		for( const auto &c : connections )
		{
			IECore::InternedString attributeName;
			pxr::UsdShadeConnectableAPI usdSource;
			IECore::InternedString sourceAttributeName;
			std::tie( attributeName, usdSource, sourceAttributeName ) = c;
			IECore::InternedString sourceHandle = readShaderNetworkWalk( anchorPath, pxr::UsdShadeShader( usdSource.GetPrim() ), shaderNetwork );

			if( sourceAttributeName == "DEFAULT_OUTPUT" )
			{
				shaderNetwork.addConnection( IECoreScene::ShaderNetwork::Connection(
						{ sourceHandle, "" },
						{ handle, attributeName }
				) );
			}
			else
			{
				shaderNetwork.addConnection( IECoreScene::ShaderNetwork::Connection(
						{ sourceHandle, sourceAttributeName },
						{ handle, attributeName }
				) );
			}
		}

		return handle;
	}

} // namespace

pxr::UsdShadeOutput IECoreUSD::ShaderAlgo::writeShaderNetwork( const IECoreScene::ShaderNetwork *shaderNetwork, pxr::UsdPrim shaderContainer )
{
	IECoreScene::ShaderNetwork::Parameter networkOutput = shaderNetwork->getOutput();
	if( networkOutput.shader.string() == "" )
	{
		// This could theoretically happen, but a shader network with no output is not useful in any way
		IECore::msg(
			IECore::Msg::Warning, "IECoreUSD::ShaderAlgo::writeShaderNetwork",
			"No output shader in network"
		);
	}

	pxr::UsdShadeOutput networkOutUsd;
	for( const auto &shader : shaderNetwork->shaders() )
	{
		pxr::SdfPath usdShaderPath = shaderContainer.GetPath().AppendChild( pxr::TfToken( pxr::TfMakeValidIdentifier( shader.first.string() ) ) );
		pxr::UsdShadeShader usdShader = pxr::UsdShadeShader::Define( shaderContainer.GetStage(), usdShaderPath );
		if( !usdShader )
		{
			throw IECore::Exception( "Could not create shader at: " + shaderContainer.GetPath().GetString() + " / " + shader.first.string() );
		}
		std::string type = shader.second->getType();
		std::string typePrefix;
		size_t typeColonPos = type.find( ":" );
		if( typeColonPos != std::string::npos )
		{
			typePrefix = type.substr( 0, typeColonPos ) + ":";
			if( typePrefix == "ai:" )
			{
				typePrefix = "arnold:";
			}
		}
		usdShader.SetShaderId( pxr::TfToken( typePrefix + shader.second->getName() ) );


		for( const auto &p : shader.second->parameters() )
		{
			pxr::UsdShadeInput input = usdShader.CreateInput(
				pxr::TfToken( p.first.string() ),
				DataAlgo::valueTypeName( p.second.get() )
			);
			input.Set( DataAlgo::toUSD( p.second.get() ) );
		}

		if( networkOutput.shader == shader.first )
		{
			pxr::TfToken outName( networkOutput.name.string() );
			if( outName.GetString().size() == 0 )
			{
				outName = pxr::TfToken( "DEFAULT_OUTPUT" );
			}

			// \todo - we should probably be correctly tracking the output type if it is typed?
			// Currently, we don't really track output types in Gaffer.
			networkOutUsd = usdShader.CreateOutput( outName, pxr::SdfValueTypeNames->Token );
		}

	}

	for( const auto &shader : shaderNetwork->shaders() )
	{
		pxr::UsdShadeShader usdShader = pxr::UsdShadeShader::Get( shaderContainer.GetStage(), shaderContainer.GetPath().AppendChild( pxr::TfToken( pxr::TfMakeValidIdentifier( shader.first.string() ) ) ) );
		for( const auto &c : shaderNetwork->inputConnections( shader.first ) )
		{
			pxr::UsdShadeInput dest = usdShader.GetInput( pxr::TfToken( c.destination.name.string() ) );
			if( ! dest.GetPrim().IsValid() )
			{
				dest = usdShader.CreateInput( pxr::TfToken( c.destination.name.string() ), pxr::SdfValueTypeNames->Token );
			}

			pxr::UsdShadeShader sourceUsdShader = pxr::UsdShadeShader::Get( shaderContainer.GetStage(), shaderContainer.GetPath().AppendChild( pxr::TfToken( pxr::TfMakeValidIdentifier( c.source.shader.string() ) ) ) );
			std::string sourceOutputName = c.source.name.string();
			if( sourceOutputName.size() == 0 )
			{
				sourceOutputName = "DEFAULT_OUTPUT";
			}
			pxr::UsdShadeOutput source = sourceUsdShader.CreateOutput( pxr::TfToken( sourceOutputName ), dest.GetTypeName() );
			dest.ConnectToSource( source );
		}

	}

	return networkOutUsd;
}

IECoreScene::ShaderNetworkPtr IECoreUSD::ShaderAlgo::readShaderNetwork( const pxr::SdfPath &anchorPath, const pxr::UsdShadeShader &outputShader, const pxr::TfToken &outputParameter )
{
	IECoreScene::ShaderNetworkPtr result = new IECoreScene::ShaderNetwork();
	IECore::InternedString outputHandle = readShaderNetworkWalk( anchorPath, outputShader, *result );

	// For the output shader, set the type to "ai:surface" if it is "ai:shader".
	// This is complete nonsense - there is nothing to suggest that this shader is
	// of type surface - it could be a simple texture or noise, or even a
	// displacement or volume shader.
	//
	// But arbitrarily setting the type on the output to "ai:surface" matches our
	// current Gaffer convention, so it allows round-tripping.
	// In the long run, the fact this is working at all appears to indicate that we
	// don't use the suffix of the shader type for anything, and we should just set
	// everything to prefix:shader ( aside from lights, which are a bit of a
	// different question )
	if( result->getShader( outputHandle )->getType() == "ai:shader" )
	{
		IECoreScene::ShaderPtr o = result->getShader( outputHandle )->copy();
		o->setType( "ai:surface" );
		result->setShader( outputHandle, std::move( o ) );
	}

	// handles[0] is the handle of the first shader added, which is always the output shader
	if( outputParameter.GetString() != "DEFAULT_OUTPUT" )
	{
		result->setOutput( IECoreScene::ShaderNetwork::Parameter( outputHandle, outputParameter.GetString() ) );
	}
	else
	{
		result->setOutput( IECoreScene::ShaderNetwork::Parameter( outputHandle ) );
	}

	return result;
}
