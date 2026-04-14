from app import app

if __name__ == '__main__':
    print("Starting application on http://127.0.0.1:5004/")
    print("Press Ctrl+C to stop")
    app.run(host='127.0.0.1', port=5004, debug=True)
