from owlready2 import *

def load_ontology(file_path):
    """
    Load the iFixit ontology from the given file path.
    """
    onto = get_ontology(file_path).load()
    return onto

def create_ontology():
    """
    Create the iFixit ontology structure.
    """
    onto = get_ontology("http://example.org/ifixit-ontology.owl")

    with onto:
        # Define classes
        class Item(Thing):
            pass

        class Procedure(Thing):
            pass

        class Tool(Thing):
            pass

        class Step(Thing):
            pass

        # Define object properties
        class has_part(ObjectProperty):
            domain = [Item]
            range = [Item]

        class has_procedure(ObjectProperty):
            domain = [Item]
            range = [Procedure]

        class has_step(ObjectProperty):
            domain = [Procedure]
            range = [Step]

        class uses_tool(ObjectProperty):
            domain = [Step]
            range = [Tool]

    return onto

# Add more functions as needed
