pipeline {
    agent any
    environment {
       GIT_TARGET_BRANCH = "test_aws"
       VM_IP = "3.9.185.8"
       registry = "tbellini01/edilcloud-back"
       registryCredential = 'docker_tbellini01'
       dockerImage = ''
   }
    stages {
         stage('Cloning our Git') {
            steps {
                git 'https://tommasobellini:Oneplus3t2@github.com/edilcloud/edilcloud-back.git'
            }
        }
        stage('Building our image') {
            steps {
                script {
                    dockerImage = docker.build registry + ":$BUILD_NUMBER"
                }
            }
        }
        stage('Deploy our image') {
            steps {
                script {
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                    }
                }
            }
        }
        stage('Update services with new image') {
             steps {
                 sh 'docker service update --force --image tbellini01/edilcloud-back'+ ":$BUILD_NUMBER"+ ' edilcloud2_web'
             }
        }
        stage('Cleaning up') {
            steps {
                sh "docker rmi $registry:$BUILD_NUMBER"
            }
        }
        /* stage('Build image') {
            steps {
                // Print all the environment variables.
                sh 'printenv'
                sh 'echo $GIT_BRANCH'
                sh 'echo $GIT_COMMIT'
                echo 'Building'
                sh 'docker build -t edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID .'
                sh 'docker tag edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID 3.9.185.8:10000/edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID'
            }
        }

        stage('Push image as latest to registry') {
            steps {
                sh 'docker push 3.9.185.8:10000/edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID'
                sh 'docker tag edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID 3.9.185.8:10000/edilcloud_back-$GIT_TARGET_BRANCH:latest'
            }
        }

         stage('Update services with new image') {
             steps {
                 sh 'docker service update --force --image 3.9.185.8:10000/edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID edilcloud_web'
             }
        } */
    }


//      post {
//         success {
//             slackSend(color: '#43ab39', message: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
//         }
//         aborted {
//             slackSend(color: '#c6bfbe', message: "ABORTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
//         }
//         failure {
//             slackSend(color: '#f45342', message: "FAILURE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
//         }
//     }
}