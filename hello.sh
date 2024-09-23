pipeline {
    agent any
    stages {
        stage('Hello') {
            steps {
                script {
                    echo "Hello, Jenkins!"
                }
            }
        }
    }
}
