def project = "conan-hdf5"
def centos = docker.image('essdmscdm/centos-build-node:0.4.1')
def container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def conan_remote = "ess-dmsc-local"
def conan_user = "ess-dmsc"
def conan_pkg_channel = "testing"

node('docker') {
    def run_args = "\
       --name ${container_name} \
       --tty \
       --network=host \
       --env http_proxy=${env.http_proxy} \
       --env https_proxy=${env.https_proxy} \
       --env local_conan_server=${env.local_conan_server}"

   try {
        container = centos.run(run_args)

        stage('Checkout') {
            def checkout_script = """
                git clone https://github.com/ess-dmsc/${project}.git \
                    --branch ${env.BRANCH_NAME}
            """
            sh "docker exec ${container_name} sh -c \"${checkout_script}\""
        }

        stage('Conan Setup') {
                withCredentials([string(
                    credentialsId: 'local-conan-server-password',
                    variable: 'CONAN_PASSWORD'
                )])
            {
                def setup_script = """
                    set +x
                    export http_proxy=''
                    export https_proxy=''
                    conan remote add \
                        --insert 0 \
                        ${conan_remote} ${local_conan_server}
                    conan user \
                        --password '${CONAN_PASSWORD}' \
                        --remote ${conan_remote} \
                        ${conan_user} \
                        > /dev/null
                """
                sh "docker exec ${container_name} sh -c \"${setup_script}\""
            }
        }

        stage('Package') {
            def package_script = """
                cd ${project}
                conan create ${conan_user}/${conan_pkg_channel} \
                    --build=missing
            """
            sh "docker exec ${container_name} sh -c \"${package_script}\""
        }

        stage('Upload') {
            def upload_script = """
                export http_proxy=''
                export https_proxy=''
                cd ${project}
                ./upload_package.py \
                    ${conan_remote} \
                    ${conan_user} \
                    ${conan_pkg_channel}
            """
            sh "docker exec ${container_name} sh -c \"${upload_script}\""
        }
    } finally {
        container.stop()
    }
}
