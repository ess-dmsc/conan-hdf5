import glob
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class Hdf5Conan(ConanFile):
    name = "hdf5"
    version = "1.10.1"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-hdf5"
    settings = "os", "compiler", "build_type", "arch"
    requires = "zlib/1.2.11@conan/stable"
    generators = "virtualbuildenv"

    def source(self):
        tools.download(
            "https://www.hdfgroup.org/package/gzip/?wpdmdl=4301",
            "hdf5-1.10.1.tar.gz"
        )
        tools.check_md5(
            "hdf5-1.10.1.tar.gz",
            "43a2f9466702fb1db31df98ae6677f15"
        )
        tools.unzip("hdf5-1.10.1.tar.gz")
        os.unlink("hdf5-1.10.1.tar.gz")

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.configure(
            configure_dir="hdf5-1.10.1",
            args=[
                "--prefix=",
                "--enable-cxx",
                "--enable-hl",
                "--disable-sharedlib-rpath"
            ]
        )
        tools.replace_in_file(
            "./libtool",
            '-install_name \$rpath/\$soname',
            '-install_name \$soname'
        )

        env_build.make()

        os.mkdir("install")
        cwd = os.getcwd()
        destdir = os.path.join(cwd, "install")
        env_build.make(args=["install", "DESTDIR="+destdir])

    def package(self):
        self.copy("*", dst="bin", src="install/bin")
        self.copy("*", dst="include", src="install/include")
        self.copy("*", dst="lib", src="install/lib")
        if tools.os_info.is_macos:
            self._change_dylib_install_name()

    def package_info(self):
        self.cpp_info.libs = ["hdf5", "hdf5_cpp", "hdf5_hl"]

    def _change_dylib_install_name(self):
        """Remove absolute path from dynamic shared library install names."""
        libs = os.path.join(self.package_folder, "lib", '*.dylib')
        filenames = glob.glob(libs)

        self.output.info("Removing absolute paths from dynamic libraries")
        for filename in filenames:
            cmd = (
                "otool -D {0} "
                "| tail -n 1 "
                "| xargs basename "
                "| xargs -J % -t "
                "install_name_tool -id % {0}".format(filename)
            )
            os.system(cmd)

        self.output.success("Removed absolute paths from dynamic libraries")
