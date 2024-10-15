from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty, sync_reasoner_pellet
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import os
import logging
import types


logging.basicConfig(level=logging.INFO)


def load_ontology(file_path):
    """
    Load the iFixit ontology from the given file path.
    """
    try:
        onto = get_ontology(file_path).load()
        return onto
    except Exception:
        logging.exception("Failed to load ontology")
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
            classes_to_check = ["Procedure", "Step", "CautionProcedure", "LongProcedure", "ComplexProcedure", "Tool"]
            for class_name in classes_to_check:
                if class_name not in onto.classes():
                    logging.info(f"Creating class: {class_name}")
                    types.new_class(class_name, (Thing,))

            properties_to_check = [
                ("hasStep", ObjectProperty, onto.Procedure, onto.Step),
                ("stepText", DataProperty, onto.Step, str),
                ("usesTool", ObjectProperty, onto.Step, onto.Tool)
            ]
            for prop_name, prop_type, domain, range_ in properties_to_check:
                if prop_name not in onto.properties():
                    logging.info(f"Creating property: {prop_name}")
                    new_prop = types.new_class(prop_name, (prop_type,))
                    new_prop.domain = [domain]
                    new_prop.range = [range_]

            # Create instances from the knowledge graph
            for proc in kg.graph.subjects(RDF.type, URIRef(str(onto.Procedure.iri))):
                proc_name = str(proc).split('#')[-1]
                logging.info(f"Processing procedure: {proc_name}")
                procedure = onto.Procedure(proc_name)
                for step in kg.graph.objects(proc, URIRef(str(onto.hasStep.iri))):
                    step_name = str(step).split('#')[-1]
                    logging.info(f"Processing step: {step_name}")
                    step_instance = onto.Step(step_name)
                    procedure.hasStep.append(step_instance)
                    for text in kg.graph.objects(step, URIRef(str(onto.stepText.iri))):
                        step_instance.stepText.append(str(text))
                    for tool in kg.graph.objects(step, URIRef(str(onto.usesTool.iri))):
                        tool_name = str(tool).split('#')[-1]
                        logging.info(f"Processing tool: {tool_name}")
                        tool_instance = onto.Tool(tool_name)
                        step_instance.usesTool.append(tool_instance)

            # Apply reasoning rules
            for proc in onto.Procedure.instances():
                logging.info(f"Applying rules to procedure: {proc.name}")

                # Rule 1: CautionProcedure
                for step in proc.hasStep:
                    if step.stepText and any("careful" in text.lower() for text in step.stepText):
                        proc.is_a.append(onto.CautionProcedure)
                        logging.info(f"Procedure {proc.name} classified as CautionProcedure")
                        break

                # Rule 2: LongProcedure
                if len(proc.hasStep) > 10:
                    proc.is_a.append(onto.LongProcedure)
                    logging.info(f"Procedure {proc.name} classified as LongProcedure")

                # Rule 3: ComplexProcedure
                tools = set()
                for step in proc.hasStep:
                    tools.update(step.usesTool)
                if len(tools) > 5:
                    proc.is_a.append(onto.ComplexProcedure)
                    logging.info(f"Procedure {proc.name} classified as ComplexProcedure")

            # Collect reasoning results
            reasoning_results = {
                "CautionProcedures": [instance.name for instance in onto.CautionProcedure.instances()],
                "LongProcedures": [instance.name for instance in onto.LongProcedure.instances()],
                "ComplexProcedures": [instance.name for instance in onto.ComplexProcedure.instances()],
                "AllProcedures": [instance.name for instance in onto.Procedure.instances()],
                "StepsWithCaution": [
                    (step.name, step.stepText[0])
                    for proc in onto.Procedure.instances()
                    for step in proc.hasStep
                    if step.stepText and any("careful" in text.lower() for text in step.stepText)
                ],
                "ProceduresWithStepCount": [
                    (proc.name, len(proc.hasStep))
                    for proc in onto.Procedure.instances()
                ],
                "ProceduresWithToolCount": [
                    (proc.name, len(set(tool for step in proc.hasStep for tool in step.usesTool)))
                    for proc in onto.Procedure.instances()
                ]
            }
            logging.info("Reasoning completed successfully")
            return onto, reasoning_results
        except Exception as e:
            logging.exception(f"Error during reasoning: {str(e)}")
            return onto, {}
