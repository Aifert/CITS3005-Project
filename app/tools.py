from app import query_engine


def generate_queries():
    queries_dict = dict()
    # for i in query_engine's methods:
    for method in dir(query_engine):
        if callable(getattr(query_engine, method)) and not method.startswith("__"):
            queries_dict[method] = getattr(query_engine, method)

    return queries_dict


queries = generate_queries()
