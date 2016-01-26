.. module:: dll
   :synopsis: DLL loading

dll - DLL loading
=================

The :mod:`dll` module is not intended for consumers of your specific
application or library. It is a helper module for loading the 3rd party
libraries used by your project itself.

.. class:: DLL(libinfo : string, libnames : string or dict[, path=None])

   A simple wrapper class for loading shared libraries through ctypes.

   The *libinfo* argument is a descriptive name of the library, that is
   recommended to be platform neutral, since it is shown to the user on
   errors. *libnames* can be a list of shared library names or a dictionary
   consisting of platform->library name mappings. *path* is the explicit
   library path to be used, if any. *path* acts as the first location to be
   used for loading the library, before the standard mechanisms of
   :mod:`ctypes` will be used  
   
   .. attribute:: libfile

      Gets the filename of the loaded library.

   .. method:: bind_function(funcname : string[, args=None[, returns=None[,optfunc=None]]]) -> function

      Tries to resolve the passed function name and, if found, binds the
      list of *args*, to its ``argtypes`` and the *returns* value to its
      ``restype``. If the function is not found, *optfunc* will be used
      instead, without the assignment of *args* and *returns*.
