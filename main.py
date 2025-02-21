from app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))  # Use PORT from environment or default to 8080
    app.run(host="0.0.0.0", port=port)
