from conans import ConanFile, CMake, RunEnvironment, tools
import os


class Hdf5TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports = "sample.h5"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package".
        cmake.configure(source_dir=self.source_folder, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("")

    def test(self):
        run_env = RunEnvironment(self)
        hdf5_file = os.path.join(self.source_folder, "sample.h5")
        os.chdir("bin")
        with tools.environment_append(run_env.vars):
            self.run(".%sexample %s" % (os.sep, hdf5_file))
