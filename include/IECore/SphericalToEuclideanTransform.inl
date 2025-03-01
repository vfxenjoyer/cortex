//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2009-2010, Image Engine Design Inc. All rights reserved.
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

#ifndef IE_CORE_SPHERICALTOEUCLIDEANTRANSFORM_INL
#define IE_CORE_SPHERICALTOEUCLIDEANTRANSFORM_INL

#include "IECore/Export.h"
#include "IECore/VectorTraits.h"

IECORE_PUSH_DEFAULT_VISIBILITY
#include "OpenEXR/ImathMatrix.h"
#include "OpenEXR/ImathVec.h"
IECORE_POP_DEFAULT_VISIBILITY

#include <cassert>

namespace IECore
{

template<typename F, typename T>
SphericalToEuclideanTransform<F, T>::SphericalToEuclideanTransform()
{
}

template<typename F, typename T>
T SphericalToEuclideanTransform<F, T>::transform( const F &f )
{
	typedef typename VectorTraits< T >::BaseType V;
	V sinTheta = std::sin( f.y );
	T res( sinTheta * std::cos( f.x ), sinTheta * std::sin( f.x ), std::cos( f.y ) );
	if ( TypeTraits::IsVec3<F>::value )
	{
		res *= f[2];
	}
	return res;
}

template<typename F, typename T>
typename SphericalToEuclideanTransform<F, T>::InverseType SphericalToEuclideanTransform<F, T>::inverse() const
{
	return InverseType();
}


} // namespace IECore

#endif // IE_CORE_SPHERICALTOEUCLIDEANTRANSFORM_INL

