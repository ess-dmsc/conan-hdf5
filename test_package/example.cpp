#include <iostream>
#include <H5Cpp.h>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Missing file name" << std::endl;
        return 1;
    }

    H5::H5File file(argv[1], H5F_ACC_RDONLY);
    H5::DataSet dataset = file.openDataSet("a/b/data");

    int value;
    dataset.read(&value, H5::PredType::NATIVE_INT);
    std::cout << value << std::endl;

    return 0;
}
