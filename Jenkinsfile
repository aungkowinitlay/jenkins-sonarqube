pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root'
        }
    }
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
                        apt-get update && apt-get install -y python3-venv
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install pytest==7.4.0 pytest-cov==4.1.0
                        pip install -r requirements.txt || { echo "pip install failed"; exit 1; }
                        pip list
                    '''
                }
            }
        }
        stage('Run Tests and Coverage') {
            steps {
                dir('backend') {
                    sh '''
                        . venv/bin/activate
                        which pytest || echo "pytest not found"
                        pytest --version || echo "pytest version check failed"
                        pytest --cov=./ --cov-report=xml --junitxml=test-results.xml
                        ls -l coverage.xml || echo "coverage.xml not found"
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
                    docker network create my-app-network || true
                    docker rm -f flask-backend || true
                    docker rm -f nginx-frontend || true
                    docker run -d --name flask-backend --network my-app-network -p 5000:5000 ${BACKEND_IMAGE}
                    docker run -d --name nginx-frontend --network my-app-network -p 80:80 ${FRONTEND_IMAGE}
                '''
            }
        }
    }
    post {
        always {
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