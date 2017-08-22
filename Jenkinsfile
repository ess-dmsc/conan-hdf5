def project = "conan-hdf5"
def centos = docker.image('essdmscdm/centos-build-node:0.2.5')
def container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

node('docker') {
    def run_args = "\
       --name ${container_name} \
       --tty \
       --env http_proxy=${env.http_proxy} \
       --env https_proxy=${env.https_proxy}"

   try {
        container = centos.run(run_args)

        stage('Checkout') {
            def checkout_script = """
                git clone https://github.com/ess-dmsc/${project}.git \
                    --branch ${env.BRANCH_NAME}
            """
            sh "docker exec ${container_name} sh -c \"${checkout_script}\""
        }

        stage('Package') {
            def package_script = """
                cd ${project}
                conan create ess-dmsc/testing --build=missing
            """
            sh "docker exec ${container_name} sh -c \"${package_script}\""
        }
    } finally {
        container.stop()
    }
}
