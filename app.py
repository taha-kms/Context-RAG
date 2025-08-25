# app.py
from webapp import create_app

app = create_app()

if __name__ == "__main__":
    # Local dev run: python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
