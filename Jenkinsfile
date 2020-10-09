pipeline {
    agent any
    environment {
       GIT_TARGET_BRANCH = "test_aws"
       VM_IP = "3.9.185.8"
   }
    stages {
        stage('Build image') {
            steps {
                // Print all the environment variables.
                sh 'printenv'
                sh 'echo $GIT_BRANCH'
                sh 'echo $GIT_COMMIT'
                echo 'Building'
                sh 'docker build -t edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID .'
                sh 'docker tag edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID tbellini01/edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID'
            }
        }

        stage('Push image build') {
             steps {
                sh 'docker push edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID'
            }
        }

        stage('Push image as latest to registry') {
            steps {
                sh 'docker tag edilcloud_back-$GIT_TARGET_BRANCH:$BUILD_ID tbellini01/edilcloud_back-$GIT_TARGET_BRANCH:latest'
                sh 'docker push edilcloud_back-$GIT_TARGET_BRANCH:latest'
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