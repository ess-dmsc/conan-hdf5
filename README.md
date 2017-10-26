# conan-hdf5

Conan package for HDF5.


## Executables and shared libraries

When the package is compiled with the `shared=True` option, the _rpath_ for
executables is set to _$ORIGIN/../lib_ on Linux and _@executable_path/../lib_
on macOS.
