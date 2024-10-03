from rdflib import Graph


class QueryEngine:
    def __init__(self, graph):
        self.graph = graph
        self.prefix = "PREFIX ifixit: <http://www.ifixit.com/ontology#>"

    def execute_query(self, query_to_execute):
        query = f"""
        {self.prefix}
        {query_to_execute}
        """
        return self.graph.query(query)

    def find_procedures_with_more_than_6_steps(self):
        query = f"""
        {self.prefix}
        SELECT ?item ?procedure (COUNT(?step) as ?stepCount)
            WHERE {{
                ?item rdf:type ifixit:Item .
                ?item ifixit:hasProcedure ?procedure .
                ?procedure ifixit:hasStep ?step .
            }}
            GROUP BY ?item ?procedure
            HAVING (COUNT(?step) > 6)
            ORDER BY DESC(?stepCount)
            """
        return self.graph.query(query)


    def find_items_with_more_than_10_procedures(self):
        query = f"""
        {self.prefix}
        SELECT ?item (COUNT(?procedure) as ?procedureCount)
            WHERE {{
                ?item rdf:type ifixit:Item .
                ?item ifixit:hasProcedure ?procedure .
            }}
            GROUP BY ?item
            HAVING (COUNT(?procedure) > 10)
            ORDER BY DESC(?procedureCount)
        """
        return self.execute_query(query)

    def find_procedures_with_unused_tools(self):
        query = f"""
        {self.prefix}
        SELECT DISTINCT ?procedure
        WHERE {{
            ?procedure rdf:type ifixit:Procedure .
            FILTER NOT EXISTS {{
                ?procedure ifixit:usesTool ?tool .
            }}
        }}
        """
        return self.execute_query(query)

    def flag_potential_hazards(self):
        query = f"""
        {self.prefix}
        SELECT ?procedure ?step ?stepText
        WHERE {{
            ?procedure rdf:type ifixit:Procedure .
            ?procedure ifixit:hasStep ?step .
            ?step ifixit:stepText ?stepText .
            FILTER (REGEX(?stepText, "careful|dangerous|carefully", "i"))
        }}
        """
        return self.execute_query(query)

    def find_all_triples(self):
        query = f"""
        {self.prefix}
        SELECT ?s ?p ?o
        WHERE {{
            ?s ?p ?o .
        }}
        """
        return self.graph.query(query)
    # Add more query methods as needed
