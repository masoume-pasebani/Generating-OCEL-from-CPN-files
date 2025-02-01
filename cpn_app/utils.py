import networkx as nx
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
from io import BytesIO
import itertools


def parse_cpn(file_path):
    """
    Parses the XML CPN file to extract places, transitions, arcs, and net names.
    """
    places = {}
    transitions = {}
    arcs = []
    net_names = {}  # Dictionary to store net names for each transition/place
    net_name_per_sheet = {}  # Mapping between net sheet ID and net name

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract the Petri nets and their names
        for binder in root.findall(".//cpnbinder"):
            for sheet in binder.findall(".//cpnsheet"):
                sheet_id = sheet.get("id")

                # Find the name of the net
                net_name_element = sheet.find(".//name")
                net_name = net_name_element.text.strip() if net_name_element is not None else f"Net {sheet_id}"

                # Store net name for each sheet
                net_name_per_sheet[sheet_id] = net_name

        # Extract transitions: Assuming transitions are under cpnsheet elements with zorder position value "0"
        for binder in root.findall(".//cpnbinder"):
            for sheet in binder.findall(".//cpnsheet"):
                zorder = sheet.find(".//zorder/position")
                if zorder is not None and zorder.get('value') == "0":
                    trans_id = sheet.get("id")
                    # Each sheet with zorder value "0" can be treated as a transition
                    transitions[trans_id] = net_name_per_sheet.get(trans_id, f"Transition {trans_id}")

        # Example arcs: Placeholder for arcs
        for place in net_name_per_sheet:
            for trans in transitions:
                arcs.append((place, trans))  # Dummy arcs for demonstration

    except ET.ParseError as e:
        print(f"Error parsing the XML file: {e}")
    except Exception as e:
        print(f"Error processing the file: {e}")

    return net_name_per_sheet, transitions, arcs, net_name_per_sheet


def generate_ocel(places, transitions, arcs, output_file):
    """
    Generates an Object-Centric Event Log (OCEL) from the parsed CPN data and saves it to a CSV file.
    """
    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["case_id", "activity", "timestamp", "objects"])
        writer.writeheader()

        # Generate the event log
        case_id = 1  # Initialize a case ID
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Generate a current timestamp

        for arc in arcs:
            place, transition = arc
            # Generate a random object involved (for now, map places to objects)
            objects = [place]
            activity = transitions.get(transition, "Unknown Activity")
            
            # Create a row for the event log
            event = {
                "case_id": f"case_{case_id}",
                "activity": activity,
                "timestamp": timestamp,
                "objects": ";".join(objects)  # List of objects involved
            }

            # Write the event to the CSV file
            writer.writerow(event)

            case_id += 1  # Increment the case_id for the next event

    print(f"OCEL saved to {output_file}")
import json

def visualize_cpn(places, transitions, arcs, net_names):
    """
    Visualizes the CPN using NetworkX and Matplotlib, and displays the net names instead of IDs.
    """
    # Initialize a directed graph
    graph = nx.DiGraph()

    # Add places and transitions as nodes
    for place_id, net_name in places.items():
        graph.add_node(place_id, label=net_name, type='place')  # 'type' helps in identifying node type

    for trans_id, trans_name in transitions.items():
        graph.add_node(trans_id, label=trans_name, type='transition')

    # Add arcs as edges
    graph.add_edges_from(arcs)

    # Use spring layout for node positioning
    pos = nx.spring_layout(graph, seed=42)

    # Separate places and transitions for different styles
    place_nodes = [node for node, data in graph.nodes(data=True) if data['type'] == 'place']
    transition_nodes = [node for node, data in graph.nodes(data=True) if data['type'] == 'transition']

    # Draw places as circles (lightblue)
    nx.draw_networkx_nodes(graph, pos, nodelist=place_nodes, node_color='lightblue', node_shape='o', node_size=2000)

    # Draw transitions as squares (lightgreen)
    nx.draw_networkx_nodes(graph, pos, nodelist=transition_nodes, node_color='lightgreen', node_shape='s', node_size=1500)

    # Draw edges (arcs) with arrows
    nx.draw_networkx_edges(graph, pos, edgelist=arcs, arrowstyle='->', arrowsize=15, edge_color='gray')

    # Draw labels for both places and transitions
    labels = nx.get_node_attributes(graph, 'label')
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=10, font_weight='bold')

    # Display the plot
    plt.title("Colored Petri Net (CPN) Visualization")
    plt.axis('off')  # Turn off axes for a cleaner look
    plt.show()


def draw_cpn(places, transitions, arcs, net_names):
    """
    Visualizes the CPN using NetworkX and Matplotlib, and displays the net names instead of IDs.
    """
    graph = nx.DiGraph()

    # Add places and transitions as nodes with their corresponding net names as labels
    for place_id, net_name in places.items():
        graph.add_node(place_id, label=net_name, type='place', shape='circle')

    for trans_id, trans_name in transitions.items():
        graph.add_node(trans_id, label=trans_name, type='transition', shape='circle')  # Change to 'circle'

    # Add arcs as edges (you will need to adjust this for your specific arc parsing)
    graph.add_edges_from(arcs)

    # Layout for positioning nodes
    pos = nx.spring_layout(graph, seed=42)

    # Set node colors for places (lightblue for places)
    node_colors = ['lightblue' if data['type'] == 'place' else 'lightblue' for node, data in graph.nodes(data=True)]

    # Set node shapes
    places_nodes = [node for node, data in graph.nodes(data=True) if data['type'] == 'place']
    transitions_nodes = [node for node, data in graph.nodes(data=True) if data['type'] == 'transition']

    # Generate a list of unique colors for the transitions
    transition_colors = itertools.cycle([
        'lightblue', 'lightgreen', 'lightcoral', 'lightpink', 'lightseagreen', 'lightsalmon', 'lightsteelblue'
    ])

    # Draw places (circles) with lightblue
    nx.draw_networkx_nodes(graph, pos, nodelist=places_nodes, node_color='lightblue', node_shape='o', node_size=2000)

    # Draw transitions (also circles, now) with different colors
    transition_color_map = {trans_id: next(transition_colors) for trans_id in transitions_nodes}
    nx.draw_networkx_nodes(graph, pos, nodelist=transitions_nodes,
                           node_color=[transition_color_map[node] for node in transitions_nodes],
                           node_shape='o', node_size=2000)

    # Draw edges (arcs) with arrows
    nx.draw_networkx_edges(graph, pos, edgelist=arcs, arrowstyle='->', arrowsize=15, edge_color='gray')

    # Draw node labels
    nx.draw_networkx_labels(graph, pos, labels=nx.get_node_attributes(graph, 'label'), font_size=10, font_weight='bold')

    # Display the plot
    plt.title("Colored Petri Net (CPN) Visualization")
    plt.axis('off')  # Hide axes for a cleaner look
    plt.show()