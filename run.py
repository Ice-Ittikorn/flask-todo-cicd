from app import create_app
from flask_cors import CORS

app = create_app()

CORS(app, origins=["https://ice-ittikorn.github.io"], supports_credentials=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)