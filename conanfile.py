import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException


class ConfigurationException(Exception):
    pass


class Hdf5Conan(ConanFile):
    name = "hdf5"
    version = "1.12.1"
    lib_version = f"{version}"  # The package version can change separately
    description = "HDF5 C and C++ libraries"
    license = "https://support.hdfgroup.org/ftp/HDF5/releases/COPYING"
    url = "https://github.com/ess-dmsc/conan-hdf5"
    exports = ["files/CHANGES", "files/HDF5options.cmake"]
    settings = "os", "compiler", "build_type", "arch"
    requires = "zlib/1.2.11"
    options = {
        "cxx": [True, False],
        "shared": [True, False],
        "parallel": [True, False]
    }
    default_options = (
        "cxx=False",
        "shared=False",
        "parallel=False",
        "zlib:shared=False"
    )
    generators = "virtualbuildenv"
    source_subfolder = "source_subfolder"

    windows_source_folder = f"CMake-hdf5-{lib_version}"
    windows_archive_name = f"{windows_source_folder}.zip"


    def configure(self):
        if self.options.cxx and self.options.parallel:
            msg = "The cxx and parallel options are not compatible"
            raise ConfigurationException(msg)

    def source(self):
        major_minor_version = ".".join(self.lib_version.split(".")[:2])
        if tools.os_info.is_windows:
            tools.download(
                f"https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-{major_minor_version}/hdf5-{self.lib_version}/src/CMake-hdf5-{self.lib_version}.zip",
                self.windows_archive_name
            )
            tools.unzip(self.windows_archive_name)
            os.unlink(self.windows_archive_name)
            os.rename(self.windows_source_folder, self.source_subfolder)
        else:
            tools.get(f"https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-{major_minor_version}/hdf5-{self.lib_version}/src/hdf5-{self.lib_version}.tar.gz")
            os.rename(f"hdf5-{self.lib_version}", self.source_subfolder)


    def build(self):
        configure_args = [
            "--prefix=",
            "--enable-hl",
            "--disable-sharedlib-rpath"
        ]

        if self.settings.build_type == "Debug":
            configure_args.append("--enable-build-mode=debug")

        if self.options.cxx:
            configure_args.append("--enable-cxx")

        if self.options.shared:
            configure_args.append("--enable-shared")
            configure_args.append("--disable-static")
        else:
            configure_args.append("--disable-shared")
            configure_args.append("--enable-static")

        if self.options.parallel:
            if os.environ.get("CC") is None:
                os.environ["CC"] = os.environ.get("MPICC", "mpicc")
            if os.environ.get("CXX") is None:
                os.environ["CXX"] = os.environ.get("MPICXX", "mpic++")
            configure_args.append("--enable-parallel")

        if tools.os_info.is_linux and self.options.shared:
            val = os.environ.get("LDFLAGS", "")
            os.environ["LDFLAGS"] = val + " -Wl,-rpath='$$ORIGIN/../lib'"

        if tools.os_info.is_windows:
            cwd = os.getcwd()
            os.chdir(os.path.join(self.source_folder, self.source_subfolder))

            # Override build settings using our own options file
            shutil.copyfile(
                os.path.join(self.source_folder, "files", "HDF5options.cmake"),
                "HDF5options.cmake"
            )

            static_option = "No" if self.options.shared else "Yes"
            try:
                if self.settings.compiler.version == "14":
                    compiler_year = "2015"
                elif self.settings.compiler.version == "15":
                    compiler_year = "2017"
                elif self.settings.compiler.version == "16":
                    compiler_year = "2019"
                else:
                    raise Exception("Only MSVC versions 14, 15 and 16 are currently supported by the recipe")
                self.run(f"ctest -S HDF5config.cmake,BUILD_GENERATOR=VS{compiler_year}64,STATIC_ONLY={static_option} -C {self.settings.build_type} -V -O hdf5.log")
            except ConanException:
                # Allowed to "fail" on having no tests to run, because we purposely aren't building the tests
                pass

            install_package_name = f"HDF5-{self.lib_version}-win64"
            install_package = f"HDF5-{self.lib_version}-win64.zip"
            os.chdir("build")
            tools.unzip(install_package)
            os.unlink(install_package)
            shutil.copytree(install_package_name, os.path.join("..", "..", "install"))
            os.chdir(os.path.join("..", "..", "install"))

        else:
            os.mkdir("install")

            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(
                configure_dir=self.source_subfolder,
                args=configure_args
            )

            if tools.os_info.is_macos and self.options.shared:
                tools.replace_in_file(
                    r"./libtool",
                    r"-install_name \$rpath/\$soname",
                    r"-install_name @rpath/\$soname"
                )

            env_build.make()

            cwd = os.getcwd()
            destdir = os.path.join(cwd, "install")
            env_build.make(args=["install", "DESTDIR="+destdir])

            # The paths in the HDF5 compiler wrapper are hard-coded, so
            # substitute the prefix by a variable named H5CC_PREFIX to be
            # passed to it. The compiler wrapper can be called h5cc or h5pcc.
            if self.options.parallel:
                hdf5_compiler_wrapper = os.path.join(destdir, "bin", "h5pcc")
            else:
                hdf5_compiler_wrapper = os.path.join(destdir, "bin", "h5cc")

            tools.replace_in_file(
                hdf5_compiler_wrapper,
                'prefix=""',
                'prefix="$(cd "$( dirname "$0" )" && pwd)/.."'
            )

            if tools.os_info.is_macos and self.options.shared:
                self._add_rpath_to_executables(os.path.join(destdir, "bin"))

            os.chdir(self.source_subfolder)
            os.rename("COPYING_LBNL_HDF5", "LICENSE.hdf5_LBNL")
            shutil.copyfile(
            os.path.join(self.source_folder, "files", "CHANGES"),
            "CHANGES.hdf5"
        )

        os.rename("COPYING", "LICENSE.hdf5")
        os.chdir(cwd)

    def _add_rpath_to_executables(self, path):
        executables = [
            "gif2h5", "h52gif", "h5clear", "h5copy", "h5debug", "h5diff",
            "h5dump", "h5format_convert", "h5import", "h5jam", "h5ls",
            "h5mkgrp", "h5perf_serial", "h5repack", "h5repart", "h5stat",
            "h5unjam", "h5watch"
        ]
        cwd = os.getcwd()
        os.chdir(path)
        for executable in executables:
            cmd = "install_name_tool -add_rpath @executable_path/../lib {executable}"
            os.system(cmd)

        os.chdir(cwd)

    def package(self):
        self.copy("*", dst="bin", src="install/bin")
        self.copy("*", dst="include", src="install/include")
        self.copy("*", dst="lib", src="install/lib")
        if not tools.os_info.is_windows:
            self.copy("LICENSE.*", src=self.source_subfolder)
            self.copy("CHANGES.*", src=self.source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["hdf5", "hdf5_hl"]
        if self.options.cxx:
            self.cpp_info.libs.append("hdf5_cpp")
        if tools.os_info.is_windows:
            self.cpp_info.defines = ["H5_BUILT_AS_DYNAMIC_LIB"]
