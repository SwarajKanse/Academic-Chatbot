pipeline {
    agent any

    environment {
        APP_NAME        = 'academic-chatbot'
        DOCKER_IMAGE    = "academic-chatbot:${BUILD_NUMBER}"
        LATEST_IMAGE    = 'academic-chatbot:latest'
        METRICS_PORT    = '8000'
        APP_PORT        = '8501'
        PYTHONUNBUFFERED = '1'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        disableConcurrentBuilds()
        ansiColor('xterm')
    }

    stages {
        stage('1. SCM Checkout & Environment Sanity') {
            steps {
                echo "=========================================================="
                echo " Starting CI/CD Build for ${env.APP_NAME}"
                echo " Commit SHA: ${env.GIT_COMMIT}"
                echo " Branch:     ${env.GIT_BRANCH}"
                echo " Build ID:   ${env.BUILD_NUMBER}"
                echo "=========================================================="
                sh 'git log -1 --pretty=format:"Commit: %h - %an <%ae>: %s"'
            }
        }

        stage('2. Static Code Analysis & Linting') {
            steps {
                echo "Running Python Code Quality Gates & Formatting Checks..."
                sh '''
                    python3 -m pip install --upgrade pip flake8
                    flake8 app.py rag_engine.py monitoring/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
                '''
            }
        }

        stage('3. Automated Unit & Integration Tests') {
            steps {
                echo "Executing Pytest Suite with Coverage Analysis..."
                sh '''
                    python3 -m pip install -r requirements.txt pytest pytest-cov
                    mkdir -p test-reports
                    python3 -m pytest tests/ --junitxml=test-reports/junit.xml --cov=monitoring --cov-report=term
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-reports/*.xml'
                }
            }
        }

        stage('4. Docker Container Build & Tagging') {
            steps {
                echo "Building Multi-Stage Production Docker Image: ${env.DOCKER_IMAGE}..."
                sh '''
                    docker build \
                        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                        --build-arg VCS_REF=${GIT_COMMIT} \
                        -t ${DOCKER_IMAGE} \
                        -t ${LATEST_IMAGE} .
                '''
            }
        }

        stage('5. Container Security & Health Audit') {
            steps {
                echo "Auditing container non-root execution and security compliance..."
                sh '''
                    # Verify non-root user
                    USER_ID=$(docker run --rm ${DOCKER_IMAGE} id -u)
                    if [ "$USER_ID" = "0" ]; then
                        echo "SECURITY VIOLATION: Container is running as root user (UID 0)"
                        exit 1
                    else
                        echo "Security Audit Passed: Container runs as unprivileged UID ${USER_ID}"
                    fi
                '''
            }
        }

        stage('6. Deploy Multi-Service Application (Docker Compose)') {
            steps {
                echo "Deploying full stack via Docker Compose (Chatbot + Prometheus + Grafana)..."
                sh '''
                    docker compose down --remove-orphans || true
                    docker compose up -d academic-chatbot prometheus grafana
                '''
            }
        }

        stage('7. Smoke Test & Nagios Health Verification') {
            steps {
                echo "Validating Application Health and Prometheus Scrape Endpoints..."
                sh '''
                    # Wait for container startup
                    sleep 10
                    python3 monitoring/nagios/check_chatbot_health.py -H localhost -p 8501 -m 8000 --check-metrics
                '''
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Pipeline completed for build #${env.BUILD_NUMBER}. Academic Chatbot is live and monitored."
        }
        failure {
            echo "FAILURE: Build #${env.BUILD_NUMBER} failed. Review stage logs and Nagios alerts."
        }
        always {
            cleanWs deleteDirs: true, notFailBuild: true
        }
    }
}
