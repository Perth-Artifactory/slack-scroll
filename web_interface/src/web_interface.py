from flask import Flask
import docker

app = Flask(__name__)
client = docker.from_env()

@app.route('/reset')
def reset_service():
    try:
        # Use Docker API to restart the service
        client.containers.get('slackscroll-slack-scroll-1').restart()
        return 'Service restarted successfully', 200
    except Exception as e:
        return f'Failed to restart the service: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
