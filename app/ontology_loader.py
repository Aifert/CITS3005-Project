from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty


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
    onto = get_ontology("http://www.ifixit.com/ontology#")

    with onto:
        # Define classes
        class Procedure(Thing):
            pass

        class Item(Thing):
            pass

        class Part(Thing):
            pass

        class Tool(Thing):
            pass

        class Step(Thing):
            pass

        class Image(Thing):
            pass

        # Define object properties
        class hasProcedure(ObjectProperty):
            domain = [Item]
            range = [Procedure]

        class hasStep(ObjectProperty):
            domain = [Procedure]
            range = [Step]

        class usesPart(ObjectProperty):
            domain = [Step]
            range = [Part]

        class usesTool(ObjectProperty):
            domain = [Step]
            range = [Tool]

        class hasImage(ObjectProperty):
            domain = [Step]
            range = [Image]

        # Define data properties
        class title(DataProperty):
            domain = [Procedure]
            range = [str]

        class stepOrder(DataProperty):
            domain = [Step]
            range = [int]

        class stepText(DataProperty):
            domain = [Step]
            range = [str]

        class imageUrl(DataProperty):
            domain = [Image]
            range = [str]

    return onto
