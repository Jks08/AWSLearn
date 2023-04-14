pipeline{
    agent {label 'root-python-slave-1'}
    stages{
        stage ('Stage 1 : Pull from Github'){
            steps{
                echo 'Pulling from Github...'
                git branch:'main', url:'https://github.com/Jks08/Movie-Review-Sentiment-Analysis-.git'
                echo 'Pulling from Github...Done'
                echo '$WORKSPACE'
            }
        }
        stage ('Stage 2 : Creating Requirements.txt'){
            steps{
                script{
                    if (!fileExists('requirements.txt')){
                        echo 'Creating requirements.txt'
                        sh 'pip freeze > requirements.txt'
                        echo 'Creating requirements.txt...Done'
                    }
                }
            }
        }
        stage ('Stage 3 : Printing requirements.txt'){
            steps{
                echo 'Printing requirements.txt'
                sh 'cat requirements.txt'
                echo 'Printing requirements.txt...Done'
            }
        }
    }
}