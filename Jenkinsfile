@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder

project = "conan-hdf5"

conan_user = "ess-dmsc"
conan_pkg_channel = "testing"

containerBuildNodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian10'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu1804-gcc8')
]

packageBuilder = new ConanPackageBuilder(this, containerBuildNodes, conan_pkg_channel)
packageBuilder.defineRemoteUploadNode('centos')

builders = packageBuilder.createPackageBuilders { container ->
  packageBuilder.addConfiguration(container, [
    'settings': [
      'hdf5:build_type': 'Debug'
    ],
    'options': [
      'hdf5:shared': 'False',
      'hdf5:cxx': 'False'
    ]
  ])

  packageBuilder.addConfiguration(container, [
    'settings': [
      'hdf5:build_type': 'Debug'
    ],
    'options': [
      'hdf5:shared': 'True',
      'hdf5:cxx': 'False'
    ]
  ])

  packageBuilder.addConfiguration(container, [
    'settings': [
      'hdf5:build_type': 'Release'
    ],
    'options': [
      'hdf5:shared': 'True',
      'hdf5:cxx': 'False'
    ]
  ])

  packageBuilder.addConfiguration(container, [
    'settings': [
      'hdf5:build_type': 'Release'
    ],
    'options': [
      'hdf5:shared': 'True',
      'hdf5:cxx': 'False'
    ]
  ])

  if (container.key == 'centos') {
    packageBuilder.addConfiguration(container, [
      'settings': [
      'hdf5:build_type': 'Release'
      ],
      'options': [
        'hdf5:shared': 'True',
        'hdf5:cxx': 'False',
        'hdf5:parallel': 'True'
      ],
      'env': [
        'CC': '/usr/lib64/mpich-3.2/bin/mpicc',
        'CXX': '/usr/lib64/mpich-3.2/bin/mpic++'
      ]
    ])
  }

  packageBuilder.addConfiguration(container, [
    'options': [
      'zlib:fPIC': 'True',
      'zlib:minizip': 'False',
      'zlib:shared': 'False'
    ]
  ])

  packageBuilder.addConfiguration(container)
}

node {
  checkout scm

  builders['macOS'] = get_macos_pipeline()
  builders['windows10'] = get_win10_pipeline()
  parallel builders

  // Delete workspace when build is done.
  cleanWs()
}

def get_macos_pipeline() {
  return {
    node('macos') {
      cleanWs()
      dir("${project}") {
        stage("macOS: Checkout") {
          checkout scm
        }  // stage

        stage("macOS: Package") {
          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings hdf5:build_type=Debug \
            --options hdf5:shared=False \
            --build=outdated"

          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings hdf5:build_type=Debug \
            --options hdf5:shared=True \
            --build=outdated"

          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings hdf5:build_type=Release \
            --options hdf5:shared=False \
            --build=outdated"

          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --settings hdf5:build_type=Release \
            --options hdf5:shared=True \
            --build=outdated"
        }  // stage
      }  // dir
    }  // node
  }  // return
}  // def

def get_win10_pipeline() {
  return {
    node('windows10') {
      // Use custom location to avoid Win32 path length issues
      ws('c:\\jenkins\\') {
      cleanWs()
      dir("${project}") {
        stage("win10: Checkout") {
          checkout scm
        }  // stage

        stage("win10: Package") {
          bat """C:\\Users\\dmgroup\\AppData\\Local\\Programs\\Python\\Python36\\Scripts\\conan.exe \
            create . ${conan_user}/${conan_pkg_channel} \
            --settings hdf5:build_type=Release \
            --options hdf5:shared=True \
            --build=outdated"""
        }  // stage
      }  // dir
      }  // ws
    }  // node
  }  // return
} // def
