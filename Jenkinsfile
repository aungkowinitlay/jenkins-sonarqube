pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('DOCKERHUB_CREDENTIALS')
        BACKEND_IMAGE = "aungkowin/flask-backend:latest"
        FRONTEND_IMAGE = "aungkowin/nginx-frontend:latest"
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/aungkowinitlay/jenkins-sonarqube.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        stage('Run Tests and Coverage') {
            steps {
                dir('backend') {
                    sh '''
                        . venv/bin/activate
                        pytest --cov=./ --cov-report=xml --junitxml=test-results.xml
                    '''
                }
            }
        }
        stage('SonarQube Analysis') {
            steps {
                dir('backend') {
                    withSonarQubeEnv('SonarQube') {
                        sh 'sonar-scanner'
                    }
                }
            }
        }
        stage('Build Backend Image') {
            steps {
                dir('backend') {
                    sh "docker build -t ${BACKEND_IMAGE} -f Dockerfile ."
                }
            }
        }
        stage('Build Frontend Image') {
            steps {
                dir('frontend') {
                    sh "docker build -t ${FRONTEND_IMAGE} -f Dockerfile ."
                }
            }
        }
        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CREDENTIALS', usernameVariable: 'DOCKERHUB_USR', passwordVariable: 'DOCKERHUB_PSW')]) {
                    sh "echo \$DOCKERHUB_PSW | docker login -u \$DOCKERHUB_USR --password-stdin"
                }
            }
        }
        stage('Push Images') {
            steps {
                sh "docker push ${BACKEND_IMAGE}"
                sh "docker push ${FRONTEND_IMAGE}"
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f flask-backend || true
                    docker rm -f nginx-frontend || true
                    docker run -d --name flask-backend -p 5000:5000 ${BACKEND_IMAGE}
                    docker run -d --name nginx-frontend -p 80:80 --link flask-backend ${FRONTEND_IMAGE}
                '''
            }
        }
    }
    post {
        always {
            sh "docker logout"
            archiveArtifacts artifacts: 'backend/coverage.xml,backend/test-results.xml', allowEmptyArchive: true
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}