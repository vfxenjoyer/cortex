//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2021, Image Engine Design Inc. All rights reserved.
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

#ifndef IECOREUSD_ATTRIBUTEALGO_H
#define IECOREUSD_ATTRIBUTEALGO_H

#include "IECoreUSD/Export.h"

#include "IECoreScene/SceneInterface.h"

IECORE_PUSH_DEFAULT_VISIBILITY
#include "pxr/base/tf/token.h"
IECORE_POP_DEFAULT_VISIBILITY

// AttributeAlgo is suite of utilities for loading/writing Cortex/USD Attributes.

namespace IECoreUSD
{

namespace AttributeAlgo
{

IECOREUSD_API pxr::TfToken cortexPrimitiveVariableMetadataToken();
IECOREUSD_API pxr::TfToken toUSD( const std::string& name );
IECOREUSD_API IECore::InternedString fromUSD( const std::string& name );
IECOREUSD_API IECore::InternedString primVarPrefix();
IECOREUSD_API std::string userPrefix();
IECOREUSD_API std::string renderPrefix();

} // namespace AttributeAlgo

} // namespace IECoreUSD

#endif // IECOREUSD_ATTRIBUTEALGO_H