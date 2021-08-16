@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder
import ecdcpipeline.PipelineBuilder

project = "conan-hdf5"
conan_user = "ess-dmsc"
conan_pkg_channel = "stable"

def num_artifacts_to_keep
if (env.BRANCH_NAME == 'master') {
  num_artifacts_to_keep = '3'
} else {
  num_artifacts_to_keep = '1'
}

// Set number of old builds to keep.
properties([[
  $class: 'BuildDiscarderProperty',
  strategy: [
    $class: 'LogRotator',
    artifactDaysToKeepStr: '',
    artifactNumToKeepStr: num_artifacts_to_keep,
    daysToKeepStr: '',
    numToKeepStr: num_artifacts_to_keep
  ]
]]);

containerBuildNodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian10'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu1804-gcc8')
]
archivingBuildNodes = [
  'centos-archive': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8')
]

// Main packaging pipeline
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

// Archiving pipeline
pipelineBuilder = new PipelineBuilder(this, archivingBuildNodes)
archivingBuilders = pipelineBuilder.createBuilders { container ->
  pipelineBuilder.stage("${container.key}: Checkout") {
    dir(pipelineBuilder.project) {
      scmVars = checkout scm
    }
    container.copyTo(pipelineBuilder.project, pipelineBuilder.project)
  }  // stage

  pipelineBuilder.stage("${container.key}: Install") {
    container.sh """
      cd ${pipelineBuilder.project}/archiving
      ./generate-conanfile.sh ${conan_user} ${conan_pkg_channel}

      conan remote add \
        --insert 0 \
        ess-dmsc-local ${local_conan_server}

      mkdir hdf5
      cd hdf5
      conan install ..
    """
  }  // stage

  pipelineBuilder.stage("${container.key}: Archive") {
    container.sh """
      # Create file with build information
      cd ${pipelineBuilder.project}/archiving/hdf5
      touch BUILD_INFO
      echo 'Repository: ${pipelineBuilder.project}/${env.BRANCH_NAME}' >> BUILD_INFO
      echo 'Commit: ${scmVars.GIT_COMMIT}' >> BUILD_INFO
      echo 'Jenkins build: ${env.BUILD_NUMBER}' >> BUILD_INFO

      # Remove additional files generated by Conan
      rm conan*
      rm graph_info.json

      cd ..
      tar czvf hdf5.tar.gz hdf5
    """
    container.copyFrom("${pipelineBuilder.project}/archiving/hdf5.tar.gz", ".")
    archiveArtifacts "hdf5.tar.gz"
  }  // stage
}

node {
  checkout scm

  builders['macOS'] = get_macos_pipeline()
  builders['windows10'] = get_win10_pipeline()

  parallel builders
  parallel archivingBuilders

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
