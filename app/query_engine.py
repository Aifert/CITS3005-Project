from rdflib import Graph

class QueryEngine:
    def __init__(self, graph):
        self.graph = graph

    def find_procedures_with_more_than_n_steps(self, n):
        query = f"""
        SELECT ?procedure (COUNT(?step) as ?stepCount)
        WHERE {{
            ?procedure a :Procedure ;
                       :has_step ?step .
        }}
        GROUP BY ?procedure
        HAVING (?stepCount > {n})
        """
        return self.graph.query(query)

    def find_items_with_more_than_n_procedures(self, n):
        query = f"""
        SELECT ?item (COUNT(?procedure) as ?procedureCount)
        WHERE {{
            ?item a :Item ;
                  :has_procedure ?procedure .
        }}
        GROUP BY ?item
        HAVING (?procedureCount > {n})
        """
        return self.graph.query(query)

    # Add more query methods as needed
