// Define an empty map for storing remote SSH connection parameters
def remote = [:]

pipeline {

    agent any

    environment {
        server_name = credentials('wp_name')
        server_host = credentials('wp_host')
        ssh_key = credentials('wp_devops')
    }

    stages {
        stage('Ssh to connect bigelow server') {
            steps {
                script {
                    // Set up remote SSH connection parameters
                    remote.allowAnyHosts = true
                    remote.identityFile = ssh_key
                    remote.user = ssh_key_USR
                    remote.name = server_name
                    remote.host = server_host
                    
                }
            }
        }
        stage('Download latest release and create enviroment') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        cd /var/www/waterpoints_mcp/lswms_mcp
                        git checkout main
                        git pull origin main
                    """
                }
            }
        }
        stage('activate enviroment and install requirements') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        cd /var/www/waterpoints_mcp/lswms_mcp
                        uv sync --no-dev
                    """
                }
            }
        }
        stage('Init api') {
            steps {
                script {
                    sshCommand remote: remote, command: """
                        cd /var/www/waterpoints_mcp/lswms_mcp
                        fuser -k 5004/tcp || true
                        source .venv/bin/activate
                        nohup uv run lswms-mcp ./mcp.log 2>&1 < /dev/null &
                    """
                }
            }
        }       
    }
    
    post {
        failure {
            script {
                echo 'fail'
            }
        }

        success {
            script {
                echo 'everything went very well, MCP in production'
            }
        }
    }
 
}
