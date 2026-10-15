pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        APP_VERSION = "${env.BUILD_NUMBER}"
        DB_PASSWORD = credentials('db-password')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build image') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Unit tests') {
            steps {
                sh 'docker compose run --rm --no-deps web python -m unittest discover -v'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose up -d'
            }
        }

        stage('Health check') {
            steps {
                sh '''
                    for i in $(seq 1 12); do
                      if curl -fs http://localhost:5000/health; then
                        echo
                        exit 0
                      fi
                      echo "App not ready yet, waiting..."
                      sleep 10
                    done
                    echo "Health check failed"
                    exit 1
                '''
            }
        }
    }

    post {
        failure {
            sh 'docker compose logs --tail=50 || true'
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}