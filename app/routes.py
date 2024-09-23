from flask import render_template, request
from app import app, query_engine

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = query_engine.execute_query(query)
    return render_template('results.html', results=results)
