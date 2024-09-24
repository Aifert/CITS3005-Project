from flask import render_template, request
from app import app, query_engine

@app.route('/')
def index():
    return render_template('search_form.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    raw_results = query_engine.execute_query(query)

    results = []

    for row in raw_results:
        uri_ref = row[0]
        results.append(str(uri_ref))

    return render_template('results.html', results=results, query=query)
