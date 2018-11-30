//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2018, Image Engine Design Inc. All rights reserved.
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

// This include needs to be the very first to prevent problems with warnings
// regarding redefinition of _POSIX_C_SOURCE
#include "boost/python.hpp"

#include "IECorePython/CancellerBinding.h"

#include "IECore/Canceller.h"

using namespace boost::python;
using namespace IECore;

namespace
{

PyObject *g_cancelledClass = nullptr;

struct CancelledFromPython
{

	static void registerConverter()
	{
		boost::python::converter::registry::push_back(
			&convertible,
			&construct,
			boost::python::type_id<Cancelled>()
		);
	}

	private :

		static void *convertible( PyObject *obj )
		{
			return PyObject_IsInstance( obj, g_cancelledClass ) ? obj : nullptr;
		}

		static void construct( PyObject *obj, boost::python::converter::rvalue_from_python_stage1_data *data )
		{
			void *storage = ( (converter::rvalue_from_python_storage<Cancelled>*) data )->storage.bytes;
			new( storage ) Cancelled();
			data->convertible = storage;
		}

};

} // namespace

namespace IECorePython
{

void bindCanceller()
{

	class_<Canceller, boost::noncopyable>( "Canceller" )
		.def( "cancel", &Canceller::cancel )
		.def( "check", &Canceller::check )
		.staticmethod( "check" )
	;

	register_ptr_to_python<std::shared_ptr<Canceller>>();

	g_cancelledClass = PyErr_NewException( (char *)"IECore.Cancelled", PyExc_RuntimeError, nullptr );

	register_exception_translator<Cancelled>(
		[]( const Cancelled &e ) {
			PyObject *value = PyObject_CallFunction( g_cancelledClass, nullptr );
			PyErr_SetObject( g_cancelledClass, value );
		}
	);

	scope().attr( "Cancelled" ) = object( borrowed( g_cancelledClass ) );

	CancelledFromPython::registerConverter();

}

} // namespace IECorePython

