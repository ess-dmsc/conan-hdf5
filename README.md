# conan-hdf5

[![Build Status](https://jenkins.esss.dk/dm/job/ess-dmsc/job/conan-hdf5/job/master/badge/icon)](https://jenkins.esss.dk/dm/job/ess-dmsc/job/conan-hdf5/job/master/)

Conan package for HDF5.

## Using the package

See the DMSC [conan-configuration repository](https://github.com/ess-dmsc/conan-configuration) for how to configure your remote.

In `conanfile.txt`:

```
hdf5/1.12.1@ess-dmsc/stable
```

## Executables and shared libraries

When the package is compiled with the `shared=True` option, the _rpath_ for
executables is set to _$ORIGIN/../lib_ on Linux and _@executable_path/../lib_
on macOS.


## Parallel HDF5

Parallel libraries can be compiled with the `parallel=True` option, **but in
this case the C++ libraries are not compiled**. This option requires MPICH and
assumes the C and C++ compilers are available on the path as _mpicc_ and
_mpic++_. If this is not the case, the compilers can be set using the _CC_ and
_CXX_ environment variables, respectively. Tested with _mpich-3.2-devel_
installed with yum on CentOS 7 and _mpich_ installed with MacPorts on macOS.
