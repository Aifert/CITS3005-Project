from flask import render_template, request, jsonify
from app import app, query_engine
from .tools import queries


@app.route('/')
def index():
    return render_template('search_form.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    print(query)
    try:
        raw_results = queries[query]()
    except KeyError:
        raw_results = query_engine.execute_query(query)

    results = []

    for row in raw_results:
        uri_ref = row[0]
        results.append(str(uri_ref))

    return render_template('results.html', results=results, query=query)

@app.route('/reasoning_results')
def show_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results)
