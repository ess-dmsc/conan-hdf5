project = "conan-hdf5"

conan_remote = "ess-dmsc-local"
conan_user = "ess-dmsc"
conan_pkg_channel = "testing"

images = [
  'centos': [
    'name': 'essdmscdm/centos-build-node:0.9.4',
    'sh': 'sh'
  ],
  'centos-gcc6': [
    'name': 'essdmscdm/centos-gcc6-build-node:0.3.4',
    'sh': '/usr/bin/scl enable rh-python35 devtoolset-6 -- /bin/bash'
  ],
/*
  'fedora': [
    'name': 'essdmscdm/fedora-build-node:0.4.2',
    'sh': 'sh'
  ],
*/
  'debian': [
    'name': 'essdmscdm/debian-build-node:0.1.1',
    'sh': 'sh'
  ],
  'ubuntu1604': [
    'name': 'essdmscdm/ubuntu16.04-build-node:0.0.2',
    'sh': 'sh'
  ],
  'ubuntu1710': [
    'name': 'essdmscdm/ubuntu17.10-build-node:0.0.3',
    'sh': 'sh'
  ]
]

base_container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def get_pipeline(image_key) {
  return {
    node('docker && dmbuild03.dm.esss.dk') {
      def container_name = "${base_container_name}-${image_key}"
      try {
        def image = docker.image(images[image_key]['name'])
        def custom_sh = images[image_key]['sh']
        def container = image.run("\
          --name ${container_name} \
          --tty \
          --cpus=2 \
          --memory=4GB \
          --network=host \
          --env http_proxy=${env.http_proxy} \
          --env https_proxy=${env.https_proxy} \
          --env local_conan_server=${env.local_conan_server} \
        ")

        stage("${image_key}: Checkout") {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            git clone \
              --branch ${env.BRANCH_NAME} \
              https://github.com/ess-dmsc/${project}.git
          \""""
        }  // stage

        stage("${image_key}: Conan setup") {
          withCredentials([
            string(
              credentialsId: 'local-conan-server-password',
              variable: 'CONAN_PASSWORD'
            )
          ]) {
            sh """docker exec ${container_name} ${custom_sh} -c \"
              set +x
              conan remote add \
                --insert 0 \
                ${conan_remote} ${local_conan_server} && \
              conan user \
                --password '${CONAN_PASSWORD}' \
                --remote ${conan_remote} \
                ${conan_user} \
                > /dev/null
            \""""
          }  // withCredentials
        }  // stage

        stage("${image_key}: Package") {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Debug \
              --options hdf5:shared=False \
              --build=missing
          \""""

          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Debug \
              --options hdf5:shared=True \
              --build=missing
          \""""

          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Release \
              --options hdf5:shared=False \
              --build=missing
          \""""

          sh """docker exec ${container_name} ${custom_sh} -c \"
            cd ${project}
            conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Release \
              --options hdf5:shared=True \
              --build=missing
          \""""

          // Build parallel libraries only on CentOS.
          if (['centos', 'centos-gcc6'].contains(image_key)) {
            sh """docker exec ${container_name} ${custom_sh} -c \"
              cd ${project}
              CC=/usr/lib64/mpich-3.2/bin/mpicc \
              CXX=/usr/lib64/mpich-3.2/bin/mpic++ \
              conan create ${conan_user}/${conan_pkg_channel} \
                --settings hdf5:build_type=Release \
                --options hdf5:cxx=False \
                --options hdf5:shared=True \
                --options hdf5:parallel=True \
                --build=missing
            \""""
          }  // if
        }  // stage

        stage("${image_key}: Upload") {
          sh """docker exec ${container_name} ${custom_sh} -c \"
            upload_conan_package.sh ${project}/conanfile.py \
              ${conan_remote} \
              ${conan_user} \
              ${conan_pkg_channel}
          \""""
        }  // stage
      } finally {
        sh "docker stop ${container_name}"
        sh "docker rm -f ${container_name}"
      }  // finally
    }  // node
  }  // return
}  // def

def get_osx_pipeline() {
  return {
    node('macos') {
      cleanWs()
      dir("${project}") {
        stage("OSX: Checkout") {
          checkout scm
        }  // stage

        stage("OSX: Conan setup") {
          withCredentials([
            string(
              credentialsId: 'local-conan-server-password',
              variable: 'CONAN_PASSWORD'
            )
          ]) {
            sh "conan user \
                --password '${CONAN_PASSWORD}' \
                --remote ${conan_remote} \
                ${conan_user} \
                > /dev/null"
          }  // withCredentials
        }  // stage

        stage("OSX: Package") {
          sh "conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Debug \
              --options hdf5:shared=False \
              --build=missing"

          sh "conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Debug \
              --options hdf5:shared=True \
              --build=missing"

          sh "conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Release \
              --options hdf5:shared=False \
              --build=missing"

          sh "conan create ${conan_user}/${conan_pkg_channel} \
              --settings hdf5:build_type=Release \
              --options hdf5:shared=True \
              --build=missing"
        }  // stage

        stage("OSX: Upload") {
          sh "upload_conan_package.sh conanfile.py \
                ${conan_remote} \
                ${conan_user} \
                ${conan_pkg_channel}"
        }
      }
    }  // node
  }  // return
}  // def

node {
  checkout scm

  def builders = [:]
  for (x in images.keySet()) {
    def image_key = x
    builders[image_key] = get_pipeline(image_key)
  }
  //builders['MacOSX'] = get_osx_pipeline()
  parallel builders

  // Delete workspace when build is done.
  cleanWs()
}
