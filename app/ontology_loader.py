from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty, sync_reasoner_pellet
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import os
import logging


logging.basicConfig(level=logging.INFO)


def load_ontology(file_path):
    """
    Load the iFixit ontology from the given file path.
    """
    try:
        onto = get_ontology(file_path).load()
        return onto
    except Exception as e:
        return None


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


def demonstrate_reasoning(onto, kg):
    if onto is None:
        logging.error("Cannot demonstrate reasoning: Ontology is None")
        return None, {}

    with onto:
        try:
            # Ensure all necessary classes and properties exist
            if "Procedure" not in onto.classes():
                class Procedure(Thing):
                    namespace = onto

            if "Step" not in onto.classes():
                class Step(Thing):
                    namespace = onto

            if "CautionProcedure" not in onto.classes():
                class CautionProcedure(Procedure):
                    namespace = onto

            if "hasStep" not in onto.object_properties():
                class hasStep(ObjectProperty):
                    namespace = onto
                    domain = [onto.Procedure]
                    range = [onto.Step]

            if "stepText" not in onto.data_properties():
                class stepText(DataProperty):
                    namespace = onto
                    domain = [onto.Step]
                    range = [str]

            # Create instances from the knowledge graph
            for proc in kg.graph.subjects(RDF.type, URIRef(str(onto.Procedure.iri))):
                procedure = onto.Procedure(str(proc).split('#')[-1])
                for step in kg.graph.objects(proc, URIRef(str(onto.hasStep.iri))):
                    step_instance = onto.Step(str(step).split('#')[-1])
                    procedure.hasStep.append(step_instance)
                    for text in kg.graph.objects(step, URIRef(str(onto.stepText.iri))):
                        step_instance.stepText.append(str(text))

            # Simple rule: If a step contains "careful", the procedure is a CautionProcedure
            for proc in onto.Procedure.instances():
                for step in proc.hasStep:
                    if step.stepText and any("careful" in text.lower() for text in step.stepText):
                        proc.is_a.append(onto.CautionProcedure)
                        break

            # Collect reasoning results
            reasoning_results = {
                "CautionProcedures": [instance.name for instance in onto.CautionProcedure.instances()],
                "AllProcedures": [instance.name for instance in onto.Procedure.instances()],
                "StepsWithCaution": [
                    (step.name, step.stepText[0])
                    for proc in onto.Procedure.instances()
                    for step in proc.hasStep
                    if step.stepText and any("careful" in text.lower() for text in step.stepText)
                ]
            }
            logging.info("Reasoning completed successfully")
            return onto, reasoning_results
        except Exception as e:
            logging.error(f"Error during reasoning: {str(e)}")
            return onto, {}
