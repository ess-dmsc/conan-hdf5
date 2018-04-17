import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class ConfigurationException(Exception):
    pass


class Hdf5Conan(ConanFile):
    name = "hdf5"
    sha256 = "bfec1be8c366965a99812cf02ddc97e4b708c1754fccba5414d4adccdc073866"

    version = "1.10.2"
    description = "HDF5 C and C++ libraries"
    license = "https://support.hdfgroup.org/ftp/HDF5/releases/COPYING"
    url = "https://github.com/ess-dmsc/conan-hdf5"
    exports = "files/CHANGES"
    settings = "os", "compiler", "build_type", "arch"
    requires = "zlib/1.2.11@conan/stable"
    options = {
        "cxx": [True, False],
        "shared": [True, False],
        "parallel": [True, False]
    }
    default_options = (
        "cxx=True",
        "shared=False",
        "parallel=False",
        "zlib:shared=False"
    )
    generators = "virtualbuildenv"

    folder_name = "hdf5-1.10.2"
    archive_name = "%s.tar.gz" % folder_name

    def configure(self):
        if self.options.cxx and self.options.parallel:
            msg = "The cxx and parallel options are not compatible"
            raise ConfigurationException(msg)

    def source(self):
        if tools.os_info.is_windows:
            tools.download(
                "https://www.hdfgroup.org/package/source-cmake-windows-2/?wpdmdl=11820",
                self.archive_name
            )
        else:
            tools.download(
                "https://www.hdfgroup.org/package/source-gzip-2/?wpdmdl=11810",
                self.archive_name
            )
            tools.check_sha256(self.archive_name, self.sha256)
        tools.unzip(self.archive_name)
        os.unlink(self.archive_name)

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
            cmake_directory = "CMake-" + self.folder_name
            os.chdir(cmake_directory)
            static_option = "No" if self.options.shared else "Yes"
            self.run("ctest -S HDF5config.cmake,BUILD_GENERATOR=VS201564,STATIC_ONLY=%s -C %s -V -O hdf5.log" % (static_option, self.settings.build_type))
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(
                configure_dir=self.folder_name,
                args=configure_args
            )

            if tools.os_info.is_macos and self.options.shared:
                tools.replace_in_file(
                    r"./libtool",
                    r"-install_name \$rpath/\$soname",
                    r"-install_name @rpath/\$soname"
                )

            env_build.make()

            os.mkdir("install")
            cwd = os.getcwd()
            destdir = os.path.join(cwd, "install")
            env_build.make(args=["install", "DESTDIR="+destdir])

            if tools.os_info.is_macos and self.options.shared:
                self._add_rpath_to_executables(os.path.join(destdir, "bin"))

        os.chdir(self.folder_name)
        os.rename("COPYING", "LICENSE.hdf5")
        os.rename("COPYING_LBNL_HDF5", "LICENSE.hdf5_LBNL")
        shutil.copyfile(
            os.path.join(self.source_folder, "files", "CHANGES"),
            "CHANGES.hdf5"
        )
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
        for e in executables:
            cmd = "install_name_tool -add_rpath {0} {1}".format(
                "@executable_path/../lib", e
            )
            os.system(cmd)

        os.chdir(cwd)

    def package(self):
        self.copy("*", dst="bin", src="install/bin")
        self.copy("*", dst="include", src="install/include")
        self.copy("*", dst="lib", src="install/lib")
        self.copy("LICENSE.*", src=self.folder_name)
        self.copy("CHANGES.*", src=self.folder_name)

    def package_info(self):
        self.cpp_info.libs = ["hdf5", "hdf5_hl"]
        if self.options.cxx:
            self.cpp_info.libs.append("hdf5_cpp")
