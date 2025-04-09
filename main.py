# main.py

from flask import Flask
from app.routes import seo_bp

app = Flask(__name__)
app.register_blueprint(seo_bp)


if __name__ == '__main__':
    app.run(debug=True)
