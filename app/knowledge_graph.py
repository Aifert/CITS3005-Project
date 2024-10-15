import json
from urllib.parse import quote
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import RDFS, XSD


class KnowledgeGraph:
    def __init__(self):
        self.graph = Graph()
        self.ifixit = Namespace("http://www.ifixit.com/ontology#")
        self.graph.bind("ifixit", self.ifixit)

    def load_data(self, file_path):
        """
        Load data from a JSON file and populate the knowledge graph.
        """
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    self._process_item(data)
                except json.JSONDecodeError as e:
                    print(f"Error loading JSON data: {e}")

    def _process_item(self, item_data):
        """
        Process an individual item and add its procedures, steps, parts, and tools
        into the knowledge graph.
        """

        # Create a URI for the item (using the 'Title')
        encoded_title = quote(item_data['Title'].replace(' ', '_'))
        item_uri = URIRef(self.ifixit[encoded_title])
        self.graph.add((item_uri, RDF.type, self.ifixit.Item))
        self.graph.add((item_uri, self.ifixit.title, Literal(item_data['Title'])))

        # Process the procedure
        encoded_procedure = quote(f"{item_data['Title'].replace(' ', '_')}_Procedure")
        procedure_uri = URIRef(self.ifixit[encoded_procedure])
        self.graph.add((procedure_uri, RDF.type, self.ifixit.Procedure))
        self.graph.add((item_uri, self.ifixit.hasProcedure, procedure_uri))

        # Process the toolbox (tools used in the item)
        toolbox_tools = [tool['Name'] for tool in item_data.get('Toolbox', [])]
        self._add_tools(procedure_uri, toolbox_tools)

        # Process steps for the procedure
        self._add_steps(procedure_uri, item_data['Steps'])

        # Ensure that all tools used in steps are part of the procedure's toolbox
        for step in item_data['Steps']:
            step_tools = step.get('Tools_extracted', [])
            for tool in step_tools:
                if tool != "NA" and tool not in toolbox_tools:
                    toolbox_tools.append(tool)
                    self._add_tools(procedure_uri, [tool])

        # Add difficulty level and estimated time for the procedure
        self.graph.add((procedure_uri, self.ifixit.difficultyLevel, Literal(item_data.get('Difficulty', 'Medium'))))
        self.graph.add((procedure_uri, self.ifixit.estimatedTime, Literal(item_data.get('Time_Required', 'PT1H'), datatype=XSD.duration)))

        # Add sub-procedure relationships
        for sub_procedure_id in item_data.get('SubProcedures', []):
            sub_procedure = URIRef(self.ifixit[f"Procedure_{sub_procedure_id}"])
            self.graph.add((procedure_uri, self.ifixit.hasSubProcedure, sub_procedure))

        # Add part requirements
        for part in item_data.get('RequiredParts', []):
            part_uri = URIRef(self.ifixit[f"Part_{part['Name'].replace(' ', '_')}"])
            self.graph.add((procedure_uri, self.ifixit.requiresPart, part_uri))

    def _add_steps(self, procedure_uri, steps):
        """
        Add the steps of a procedure to the knowledge graph.
        """
        for step_data in steps:
            encoded_step = quote(f"{procedure_uri}/step_{step_data['Order']}")
            step_uri = URIRef(encoded_step)
            self.graph.add((step_uri, RDF.type, self.ifixit.Step))
            self.graph.add((step_uri, self.ifixit.stepOrder, Literal(step_data['Order'], datatype=XSD.integer)))
            self.graph.add((step_uri, self.ifixit.stepText, Literal(step_data['Text_raw'])))
            self.graph.add((procedure_uri, self.ifixit.hasStep, step_uri))

            # Handle parts mentioned in the step
            self._add_parts(step_uri, step_data.get('Word_level_parts_clean', []))

            # Handle tools extracted from the step
            self._add_tools(step_uri, step_data.get('Tools_extracted', []))

            # Handle images associated with the step
            self._add_images(step_uri, step_data.get('Images', []))

    def _add_parts(self, step_uri, parts):
        """
        Add the parts used in a step to the knowledge graph.
        """
        for part in parts:
            if part:
                encoded_part = quote(part.replace(' ', '_'))
                part_uri = URIRef(self.ifixit[encoded_part])
                self.graph.add((part_uri, RDF.type, self.ifixit.Part))
                self.graph.add((step_uri, self.ifixit.usesPart, part_uri))

    def _add_tools(self, procedure_or_step_uri, tools):
        """
        Add the tools used in a procedure or step to the knowledge graph.
        """
        for tool in tools:
            if tool != "NA":  # Handle missing or non-applicable tools
                encoded_tool = quote(tool.replace(' ', '_'))
                tool_uri = URIRef(self.ifixit[encoded_tool])
                self.graph.add((tool_uri, RDF.type, self.ifixit.Tool))
                self.graph.add((procedure_or_step_uri, self.ifixit.usesTool, tool_uri))

    def _add_images(self, step_uri, images):
        """
        Add the images associated with a step to the knowledge graph.
        """
        for image in images:
            encoded_image = quote(f"image_{hash(image)}")
            image_uri = URIRef(self.ifixit[encoded_image])
            self.graph.add((image_uri, RDF.type, self.ifixit.Image))
            self.graph.add((image_uri, self.ifixit.imageUrl, Literal(image, datatype=XSD.anyURI)))
            self.graph.add((step_uri, self.ifixit.hasImage, image_uri))

    def execute_query(self, query):
        """
        Execute a SPARQL query on the knowledge graph.
        """
        results = self.graph.query(query)
        return results
