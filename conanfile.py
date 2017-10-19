import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class Hdf5Conan(ConanFile):
    name = "hdf5"
    version = "1.10.1"
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-hdf5"
    settings = "os", "compiler", "build_type", "arch"
    requires = "zlib/1.2.11@conan/stable"
    options = {"shared": [True, False]}
    default_options = "shared=False", "zlib:shared=False"
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
        configure_args = [
            "--prefix=",
            "--enable-cxx",
            "--enable-hl",
            "--disable-sharedlib-rpath"
        ]

        if self.settings.build_type == "Debug":
            configure_args.append("--enable-build-mode=debug")

        if self.options.shared:
            configure_args.append("--enable-shared")
            configure_args.append("--disable-static")
        else:
            configure_args.append("--disable-shared")
            configure_args.append("--enable-static")

        env_build = AutoToolsBuildEnvironment(self)
        env_build.configure(
            configure_dir="hdf5-1.10.1",
            args=configure_args
        )

        if tools.os_info.is_macos:
            tools.replace_in_file(
                r"./libtool",
                r"-install_name \$rpath/\$soname",
                r"-install_name \$soname"
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

    def package_info(self):
        self.cpp_info.libs = ["hdf5", "hdf5_cpp", "hdf5_hl"]
