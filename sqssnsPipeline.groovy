pipeline{
    agent { node { label SLAVE_LABEL}}
    environment{
        PATH = "/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    }
    stages{
        stage("Slave Check"){
            steps{
                script{
                    echo SLAVE_LABEL
                }
            }
        }
        stage('Start Virtual Environment'){
            steps{
                script{
                        sh "python3 -m venv venv"
                        sh ". venv/bin/activate"
                        sh "pip3 install boto3"
                }
            }
        }
        stage('SQS Creation'){
            steps{
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-creds',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]){
                        sh "curl https://raw.githubusercontent.com/jks08/AWSLearn/master/DirectProvisionCloudFormation.py -o DirectProvisionCloudFormation.py"
                        sh "python3 DirectProvisionCloudFormation.py ${params.ENVIRONMENT} ${params.QUEUE_NAME} ${params.DeadLetter_Queue_Name} ${params.maxReceiveCount} ${params.LOB} ${params.REF_ID} ${params.Application_Name} ${params.SNS_TOPIC_NAME} ${params.SNS_SUBSCRIPTION_REQUIRED} ${params.StackName}"
                    }
            }
        }
    }
}