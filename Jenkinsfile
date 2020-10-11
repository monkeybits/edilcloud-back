pipeline {
    agent any
    environment {
       GIT_TARGET_BRANCH = "dev_project_refactor"
       VM_IP = "35.176.179.55"
   }
    stages {
        stage('Build image') {
            steps {
                // Print all the environment variables.
                sh 'printenv'
                sh 'echo $GIT_BRANCH'
                sh 'echo $GIT_COMMIT'
                echo 'Building'
                sh 'docker build -t web-$GIT_TARGET_BRANCH:$BUILD_ID .'
                sh 'docker tag web-$GIT_TARGET_BRANCH:$BUILD_ID'
            }
        }

        stage('Push image build') {
             steps {
                sh 'docker push web-$GIT_TARGET_BRANCH:$BUILD_ID'
            }
        }

        stage('Push image as latest to registry') {
            steps {
                sh 'docker tag web-$GIT_TARGET_BRANCH:$BUILD_ID web-$GIT_TARGET_BRANCH:latest'
                sh 'docker push web-$GIT_TARGET_BRANCH:latest'
        }
        }

//          stage('Update services with new image') {
//             steps {
//                 sh 'sudo ssh jenkins01@$VM_IP "sudo -S docker service update --force --image web-$GIT_TARGET_BRANCH:$BUILD_ID web"'
//           }
        //}
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