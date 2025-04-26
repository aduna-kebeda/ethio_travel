from waitress import serve
from ethiotravel.wsgi import application

if __name__ == '__main__':
    print("Starting server on http://0.0.0.0:8000")
    serve(application, host='0.0.0.0', port=8000) 