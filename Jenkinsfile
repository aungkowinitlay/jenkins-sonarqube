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
        stage('Build Backend Image') {
            steps {
                sh "docker build -t ${BACKEND_IMAGE} -f backend/Dockerfile ./backend"
            }
        }
        stage('Build Frontend Image') {
            steps {
                sh "docker build -t ${FRONTEND_IMAGE} -f frontend/Dockerfile ./frontend"
            }
        }
        stage('Test Backend') {
            steps {
                sh """
                    echo "Running backend tests..."
                    # Example: docker run --rm ${BACKEND_IMAGE} pytest
                """
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }
        stage('Login to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'DOCKERHUB_CREDENTIALS', usernameVariable: 'DOCKERHUB_USR', passwordVariable: 'DOCKERHUB_PSW')]) {
                        sh "echo \$DOCKERHUB_PSW | docker login -u \$DOCKERHUB_USR --password-stdin"
                    }
                }
            }
        }
        stage('Push Images') {
            steps {
                sh "docker push ${BACKEND_IMAGE}"
                sh "docker push ${FRONTEND_IMAGE}"
            }
        }
        stage('Deploy') {
            steps {
                sh """
                    docker rm -f flask-backend || true
                    docker rm -f nginx-frontend || true
                    docker run -d --name flask-backend -p 5000:5000 ${BACKEND_IMAGE}
                    docker run -d --name nginx-frontend -p 80:80 ${FRONTEND_IMAGE}
                """
            }
        }
    }
    post {
        always {
            sh "docker logout"
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}