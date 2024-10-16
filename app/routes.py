from flask import render_template, request, jsonify
from app import app, query_engine
from .tools import queries
from app.graph_generator import generate_query_graph
from app import kg


@app.route('/')
def index():
    return render_template('search_form.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    print(query)
    try:
        raw_results = queries[query]()
    except Exception:
        try:
            query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX ifixit: <http://www.ifixit.com/ontology#>
            {query}"""
            raw_results = query_engine.execute_query(query)
        except Exception:
            return render_template('search_form.html')

    results = []

    for row in raw_results:
        uri_ref = row[0]
        results.append(str(uri_ref))
    # Generate the graph for these specific results
    generate_query_graph(kg, results)

    return render_template('results.html', results=results, query=query)

@app.route('/careful_reasoning_results')
def show_careful_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results, result_type="CautionProcedures", subtype="StepsWithCaution", text_to_highlight="careful")


@app.route('/long_reasoning_results')
def show_long_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results, result_type="LongProcedures", subtype="ProceduresWithStepCount", text_to_highlight="")


@app.route('/complex_reasoning_results')
def show_complex_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results, result_type="ComplexProcedures", subtype="", text_to_highlight="")


@app.route('/all_reasoning_results')
def show_all_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results, result_type="AllProcedures", subtype=None, text_to_highlight="")


@app.route('/step_count_reasoning_results')
def show_step_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results, result_type="ProceduresWithStepCount", subtype=None, text_to_highlight="")


@app.route('/tool_count_reasoning_results')
def show_tool_reasoning_results():
    results = app.config['REASONING_RESULTS']
    return render_template('reasoning_results.html', results=results, result_type="ProceduresWithToolCount", subtype=None, text_to_highlight="")


@app.route('/knowledge_graph')
def show_knowledge_graph():
    return render_template('knowledge_graph.html')

@app.route('/query_graph')
def show_query_graph():
    return render_template('query_graph.html')
