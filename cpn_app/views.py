from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import UploadedCPNFile, GeneratedOCEL
from .forms import UploadCPNForm
import os
import xml.etree.ElementTree as ET
import csv
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from .utils import draw_cpn
import random
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from .forms import *
from django.contrib.auth import authenticate, login, logout 
from .decorators import auth_user_should_not_access
import matplotlib.pyplot as plt
import networkx as nx
import itertools




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def welcome(request):
    return render(request, 'cpn_app/Welcome.html')
User = get_user_model()


@login_required
def index(request):
    """
    Render the user's upload form and display their uploaded files.
    """
    if request.method == 'POST':
        form = UploadCPNForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the file and associate it with the logged-in user
            cpn_file = form.save(commit=False)
            cpn_file.user = request.user  # Assign the current user
            cpn_file.save()
            return redirect('cpn_app:index')
    else:
        form = UploadCPNForm()

    # Fetch files uploaded by the logged-in user
    uploaded_files = UploadedCPNFile.objects.filter(user=request.user)

    return render(request, 'cpn_app/index.html', {'form': form, 'uploaded_files': uploaded_files})



def Login(request):
    form = SignUpForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)


        if not user:
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'cpn_app/Login.html')

        login(request, user)
        return redirect('cpn_app:index')  # Redirect to index page

    return render(request, 'cpn_app/Login.html', {'form': form})


def Register(request):
    form = SignUpForm()

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if len(password1) < 6:
            messages.error(request, 'Password should be at least 6 characters for greater security')
            return redirect('cpn_app:register')

        if password1 != password2:
            messages.error(request, 'Password Mismatch! Your Passwords Do Not Match')
            return redirect('cpn_app:register')

        if not username:
            messages.error(request, 'Username is required!')
            return redirect('cpn_app:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is taken! Choose another one')
            return redirect('cpn_app:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is taken! Choose another one')
            return redirect('cpn_app:register')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email)
        user.set_password(password1)
        user.save()

        login(request, user)  # Automatically log the user in after registration
        messages.success(request, 'Successful SignUp!')
        return redirect('cpn_app:index')  # Redirect to index page after registration

    return render(request, 'cpn_app/Register.html', {'form': form})



def Logout(request):
    
    logout(request)
    messages.success(request, 'Successfully Logged Out!')

    return redirect(reverse('cpn_app:login'))


def parse_cpn(file_path):
    """
    Parses the CPN file for places, transitions, arcs, and net names.
    """
    places = {}
    transitions = {}
    arcs = []
    net_names = {}  # New dictionary to store net names

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Parse places
        for place in root.findall(".//place"):
            place_id = place.get("id")
            places[place_id] = place.find("text").text if place.find("text") is not None else place_id

        # Parse transitions
        for transition in root.findall(".//trans"):
            trans_id = transition.get("id")
            transitions[trans_id] = transition.find("text").text if transition.find("text") is not None else trans_id

        # Parse arcs
        for arc in root.findall(".//arc"):
            place_end = arc.find("placeend").get("idref")
            trans_end = arc.find("transend").get("idref")
            arcs.append((place_end, trans_end))

        # Parse nets (example logic, adapt to your CPN file structure)
        for net in root.findall(".//net"):
            net_id = net.get("id")
            net_name = net.find("text").text if net.find("text") is not None else net_id
            net_names[net_id] = net_name

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")

    return places, transitions, arcs, net_names



def draw_cpn(places, transitions, arcs, net_names, file_id):
    """
    Visualizes the CPN using NetworkX and Matplotlib, and saves it as an image file.
    """
    graph = nx.DiGraph()

    # Add places and transitions as nodes with their corresponding net names as labels
    for place_id, net_name in places.items():
        graph.add_node(place_id, label=net_name, type='place', shape='circle')

    for trans_id, trans_name in transitions.items():
        graph.add_node(trans_id, label=trans_name, type='transition', shape='circle')

    # Add arcs as edges
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

    # Save the plot as an image in the media folder
    image_path = os.path.join(settings.MEDIA_ROOT, 'visualizations', f"cpn_{file_id}.png")
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    plt.title("Colored Petri Net (CPN) Visualization")
    plt.axis('off')  # Hide axes for a cleaner look
    plt.savefig(image_path)  # Save as PNG image
    plt.close()  # Close the plot to free up memory

    return os.path.join(settings.MEDIA_URL, 'visualizations', f"cpn_{file_id}.png")

from django.shortcuts import render
from django.http import JsonResponse



def visualize_cpn(request, file_id):
    """
    Visualizes the parsed CPN as a graph using the draw_cpn function.
    """
    uploaded_file = UploadedCPNFile.objects.get(pk=file_id)
    cpn_file_path = uploaded_file.file.path

    # Parse the CPN
    places, transitions, arcs, net_names = parse_cpn(cpn_file_path)

    # Generate the visualization and save it as an image
    image_url = draw_cpn(places, transitions, arcs, net_names, file_id)

    return render(request, 'cpn_app/visualize_cpn.html', {'file_id':file_id,'image_url': image_url})




def draw_cpn_model(places, transitions, arcs, tokens, net_names):
    """
    Visualizes the entire Colored Petri Net (CPN) model, including tokens and relationships.
    """
    import matplotlib.pyplot as plt
    import networkx as nx

    # Create a directed graph
    graph = nx.DiGraph()

    # Add places and transitions as nodes with labels
    for place_id, net_name in places.items():
        graph.add_node(place_id, label=net_name, type='place', shape='circle', color='lightblue')

    for trans_id, trans_name in transitions.items():
        graph.add_node(trans_id, label=trans_name, type='transition', shape='square', color='lightgreen')

    # Add arcs as edges with token flow
    graph.add_edges_from(arcs)

    # Generate a list of unique colors for transitions
    transition_colors = itertools.cycle([
        'lightcoral', 'lightpink', 'lightseagreen', 'lightsalmon', 'lightsteelblue'
    ])

    # Set positions using spring layout for better visualization
    pos = nx.spring_layout(graph, seed=42)

    # Define node colors and shapes
    node_colors = []
    node_shapes = {}
    for node, data in graph.nodes(data=True):
        if data["type"] == "place":
            node_colors.append("lightblue")
            node_shapes[node] = "o"  # Circle for places
        elif data["type"] == "transition":
            node_colors.append("lightgreen")
            node_shapes[node] = "s"  # Square for transitions

    # Draw places and transitions separately for shape distinction
    places_nodes = [node for node, data in graph.nodes(data=True) if data["type"] == "place"]
    transitions_nodes = [node for node, data in graph.nodes(data=True) if data["type"] == "transition"]

    # Draw places
    nx.draw_networkx_nodes(
        graph, pos, nodelist=places_nodes, node_color="lightblue", node_shape="o", node_size=2000
    )

    # Draw transitions
    nx.draw_networkx_nodes(
        graph, pos, nodelist=transitions_nodes, node_color="lightgreen", node_shape="s", node_size=1500
    )

    # Draw edges with labels for token flow
    edge_labels = {}
    for arc in arcs:
        place, transition = arc
        if (place, transition) in tokens:
            edge_labels[(place, transition)] = f"{tokens[(place, transition)]} tokens"

    nx.draw_networkx_edges(graph, pos, edgelist=arcs, arrowstyle="->", arrowsize=15, edge_color="gray")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=10)

    # Draw labels
    labels = nx.get_node_attributes(graph, 'label')
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=10, font_weight="bold")

    # Show the plot
    plt.title("Colored Petri Net (CPN) Model Visualization")
    plt.axis("off")
    plt.show()

def draw_cpn2(places, transitions, arcs, net_names):
    """
    Visualizes the CPN using NetworkX and Matplotlib, and displays the net names instead of IDs.
    """
    graph = nx.DiGraph()

    # Add places and transitions as nodes with their corresponding net names as labels
    for place_id, net_name in places.items():
        graph.add_node(place_id, label=net_name, type='place', shape='circle')

    for trans_id, trans_name in transitions.items():
        graph.add_node(trans_id, label=trans_name, type='transition', shape='circle')  # Change to 'circle'

    # Add arcs as edges
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

    plt.title("Colored Petri Net (CPN) Visualization")
    plt.axis('off')  # Hide axes for a cleaner look
    plt.show()



def visualize_cpn2(request, file_id):
    """
    Visualizes the parsed CPN as a graph using draw_cpn2 function and returns the result as an image.
    """
    uploaded_file = UploadedCPNFile.objects.get(pk=file_id)
    cpn_file_path = uploaded_file.file.path

    # Parse the CPN
    places, transitions, arcs, net_names = parse_cpn(cpn_file_path)

    graph_output_path = f"media/cpn_graphs/graph_{file_id}.png"
    os.makedirs(os.path.dirname(graph_output_path), exist_ok=True)

    # Create and save the graph
    plt.figure(figsize=(10, 8))
    draw_cpn2(places, transitions, arcs, net_names)  
    plt.show()
    
    graph_output_path = f"media/cpn_graphs/graph_{file_id}.png"
    os.makedirs(os.path.dirname(graph_output_path), exist_ok=True)
    plt.savefig(graph_output_path, dpi=300)
    plt.close()  

    graph_url = f"/{graph_output_path}"
    return JsonResponse({"status": "success", "graph_url": graph_url})




def get_cpn_graph_data(request, file_id):
    """
    API endpoint to get CPN graph data (places, transitions, arcs).
    """
    uploaded_file = UploadedCPNFile.objects.get(pk=file_id)
    cpn_file_path = uploaded_file.file.path

    # Parse the CPN file
    places, transitions, arcs, _ = parse_cpn(cpn_file_path)

    # Prepare data for the client
    nodes = [
        {"data": {"id": place_id, "label": label, "type": "place"}}
        for place_id, label in places.items()
    ] + [
        {"data": {"id": trans_id, "label": label, "type": "transition"}}
        for trans_id, label in transitions.items()
    ]

    edges = [
        {"data": {"source": source, "target": target}}
        for source, target in arcs
    ]

    return JsonResponse({"nodes": nodes, "edges": edges})



import os
import csv
import random
from datetime import datetime, timedelta
from lxml import etree
from django.shortcuts import render
from .models import UploadedCPNFile, GeneratedOCEL
from django.http import JsonResponse
from django.conf import settings

import pm4py
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_cpn2(file_path):
    """
    Parses the CPN file for places, transitions, arcs, and net names.
    """
    places = {}
    transitions = {}
    arcs = []
    net_names = {}  #

    try:
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Parse places
        for place in root.findall(".//place"):
            place_id = place.get("id")
            places[place_id] = place.find("text").text if place.find("text") is not None else place_id

        # Parse transitions
        for transition in root.findall(".//trans"):
            trans_id = transition.get("id")
            transitions[trans_id] = transition.find("text").text if transition.find("text") is not None else trans_id

        # Parse arcs
        for arc in root.findall(".//arc"):
            place_end = arc.find("placeend").get("idref")
            trans_end = arc.find("transend").get("idref")
            arcs.append((place_end, trans_end))

        # Parse nets (example logic, adapt to your CPN file structure)
        for net in root.findall(".//net"):
            net_id = net.get("id")
            net_name = net.find("text").text if net.find("text") is not None else net_id
            net_names[net_id] = net_name

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")

    return places, transitions, arcs, net_names

def determine_activity_duration(activity_name):
    """
    Determines the duration of the activity based on its type.
    """
    if "Start" in activity_name:
        return random.randint(60, 300)  # Short duration for start activities
    elif "End" in activity_name:
        return random.randint(180, 600)  # Slightly longer for end activities
    elif "Process" in activity_name or "Execute" in activity_name:
        return random.randint(600, 1800)  # Longer for process activities
    elif "Review" in activity_name:
        return random.randint(300, 900)  # Medium duration for review activities
    else:
        return random.randint(300, 1200)  # Default duration for unspecified activities

import os
import csv
import random
from datetime import datetime, timedelta
from lxml import etree
from django.shortcuts import render
from .models import UploadedCPNFile, GeneratedOCEL
from django.http import JsonResponse
from django.conf import settings

# Importing pm4py for process mining analysis
import pm4py
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_cpn2(file_path):
    """
    Parses the CPN file for places, transitions, arcs, and net names.
    """
    places = {}
    transitions = {}
    arcs = []
    net_names = {}  #

    try:
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Parse places
        for place in root.findall(".//place"):
            place_id = place.get("id")
            places[place_id] = place.find("text").text if place.find("text") is not None else place_id

        # Parse transitions
        for transition in root.findall(".//trans"):
            trans_id = transition.get("id")
            transitions[trans_id] = transition.find("text").text if transition.find("text") is not None else trans_id

        # Parse arcs
        for arc in root.findall(".//arc"):
            place_end = arc.find("placeend").get("idref")
            trans_end = arc.find("transend").get("idref")
            arcs.append((place_end, trans_end))

        # Parse nets (example logic, adapt to your CPN file structure)
        for net in root.findall(".//net"):
            net_id = net.get("id")
            net_name = net.find("text").text if net.find("text") is not None else net_id
            net_names[net_id] = net_name

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")

    return places, transitions, arcs, net_names

def determine_activity_duration(activity_name):
    """
    Determines the duration of the activity based on its type.
    """
    if "Start" in activity_name:
        return random.randint(60, 300)  # Short duration for start activities
    elif "End" in activity_name:
        return random.randint(180, 600)  # Slightly longer for end activities
    elif "Process" in activity_name or "Execute" in activity_name:
        return random.randint(600, 1800)  # Longer for process activities
    elif "Review" in activity_name:
        return random.randint(300, 900)  # Medium duration for review activities
    else:
        return random.randint(300, 1200)  # Default duration for unspecified activities

from django.shortcuts import render
from django.http import JsonResponse
import os
import csv
import json
from datetime import datetime, timedelta
from .models import UploadedCPNFile, GeneratedOCEL
from django.conf import settings

def generate_ocel2(request, file_id):
    """
    Generate OCEL from the uploaded file and save as CSV and JSON.
    """
    uploaded_file = UploadedCPNFile.objects.get(pk=file_id)
    cpn_file_path = uploaded_file.file.path

    # Parse the CPN
    places, transitions, arcs, _ = parse_cpn2(cpn_file_path)

    if not arcs:
        return JsonResponse({"status": "error", "message": "No arcs found in the CPN file!"})

    # Initialize timestamps for the cases
    base_time = datetime.now()
    case_start_times = {}
    case_end_times = {}

    events = []
    case_id = 1
    previous_end_time = base_time

    for arc in arcs:
        place, transition = arc
        activity = transitions.get(transition, "Unknown Activity")

        objects_for_event = []

        if place and place in places:
            place_name = places[place]
            if place_name:
                objects_for_event.append(place_name)

        if transition and transition in transitions:
            transition_name = transitions[transition]
            if transition_name:
                objects_for_event.append(transition_name)

        event_data = {
            "case_id": f"case_{case_id}",
            "activity": activity,
            "started_at": previous_end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "finished_at": (previous_end_time + timedelta(seconds=determine_activity_duration(activity))).strftime('%Y-%m-%d %H:%M:%S'),
            "duration_seconds": determine_activity_duration(activity),
            "objects": objects_for_event
        }

        events.append(event_data)

        previous_end_time = previous_end_time + timedelta(seconds=determine_activity_duration(activity))
        case_id += 1

    # Generate OCEL CSV file
    output_csv = os.path.join(settings.BASE_DIR, 'media', 'ocel_files', f"ocel_{file_id}.csv")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    with open(output_csv, mode='w', newline='') as file:
        fieldnames = ["case_id", "activity", "started_at", "finished_at", "duration_seconds", "objects"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for event_data in events:
            writer.writerow(event_data)

    # Save the events as JSON to a file
    output_json = os.path.join(settings.BASE_DIR, 'media', 'ocel_files', f"ocel_{file_id}.json")
    with open(output_json, 'w') as json_file:
        json.dump({"status": "success", "data": events}, json_file, indent=4)

    # Create a record in the database for the generated OCEL file
    GeneratedOCEL.objects.create(cpn_file=uploaded_file, generated_file=output_csv)

    # Build the URLs for the generated files
    generated_csv_url = os.path.join(settings.MEDIA_URL, 'ocel_files', f"ocel_{file_id}.csv")
    generated_json_url = os.path.join(settings.MEDIA_URL, 'ocel_files', f"ocel_{file_id}.json")

    return render(request, 'cpn_app/generate_ocel.html', {
        'generated_csv_url': generated_csv_url,
        'generated_json_url': generated_json_url
    })
