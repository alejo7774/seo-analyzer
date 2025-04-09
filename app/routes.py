# app/routes.py

from flask import Blueprint, render_template, request
from app.analyzer import analyze_seo

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['url']
        result = analyze_seo(url)
    return render_template('index.html', result=result)
