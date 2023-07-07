# Importing all the libraries and packages that will be used

import copy
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import pyproj
import requests
import shutil
import os

from geopy import distance
from shapely.geometry import Point


# Auxiliary classes and functions

class Agora:

    def __init__ (self, year, month, day, hour, minute, second=0):
        """
        Initializes a time-like object with the specified date and time.

        :param year (int): Year.
        :param month (int): Month.
        :param day (int): Day.
        :param hour (int): Hour.
        :param minute (int): Minute.
        :param second (int): Second (default: 0).
        """

        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __repr__( self):
        """
        Returns a string representation of the time in the format
        'YYYYMMDDHHMM'.
        """

        return f"{self.year:04d}{self.month:02d}{self.day:02d}{self.hour:02d}{self.minute:02d}"

    def step (self, integer):
        """
        Adds a specified number of seconds ('integer') to the current time.

        :param integer (int): Number of seconds to add.
        """

        total_seconds = self.second + integer

        # Update the seconds, minutes, and hours accordingly
        self.second = total_seconds % 60
        total_minutes = (total_seconds - self.second) // 60 + self.minute

        self.minute = total_minutes % 60
        total_hours = (total_minutes - self.minute) // 60 + self.hour

        self.hour = total_hours % 24

        # Update the day if necessary
        self.day += (total_hours - self.hour) // 24

    def get_flooding_points (self, url='https://github.com/liviatomas/floods_saopaulo/raw/main/1_input/e_Floods_2019.xlsx'):
        """
        Returns a list of flooding points at the current time.

        :param url (str): URL of the Excel file containing flooding data
            (default: 'https://github.com/liviatomas/floods_saopaulo/raw/main/1_input/e_Floods_2019.xlsx')

        :return flooding_points (list): List of flooding points. Each point is
            represented as a tuple (x, y) of coordinates.
        """

        # Formatting the date and time
        date = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
        start_time = f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"

        # Downloading the Excel file containing flooding data
        flood_df = pd.read_excel(url)

        # Filtering the data based on the current time
        my_floods = flood_df.loc[(flood_df['DATE'] == date) & (flood_df['START_T'] < start_time) & (flood_df['END_T'] > start_time)]

        # Extracting the coordinates
        flooding_points = my_floods[['X', 'Y']].values.tolist()

        # Converting coordinates
        flooding_points = [convert_coordinates(x, y) for x, y in flooding_points]

        return flooding_points


class Grafo:

    def __init__ (self, lat0, latoo, lon0, lonoo):
        """
        Initializes a graph object with latitude and longitude boundaries.
        Downloads and processes the graph data from OpenStreetMap within the
        specified boundaries.

        :param lat0 (float): Minimum latitude boundary.
        :param latoo (float): Maximum latitude boundary.
        :param lon0 (float): Minimum longitude boundary.
        :param lonoo (float): Maximum longitude boundary.
        """

        self.lat0 = lat0
        self.latoo = latoo
        self.lon0 = lon0
        self.lonoo = lonoo

        # Download and process the graph data within the specified boundaries
        self.graph = ox.graph_from_bbox(lat0, latoo, lon0, lonoo, network_type='drive')
        self.graph = ox.add_edge_speeds(self.graph)
        self.graph = ox.add_edge_travel_times(self.graph)
        self.graph = ox.distance.add_edge_lengths(self.graph)

    def get_nearest_node (self, lat, lon):
        """
        Finds the nearest node in the graph to the given latitude and
        longitude coordinates.

        :param lat (float): Latitude coordinate.
        :param lon (float): Longitude coordinate.

        :return node (int): Nearest node ID.
        """

        # Project the graph to enable us to use the nearest_nodes method
        graph_proj = ox.project_graph(self.graph)

        # Project the coordinates of the given point
        coords = [(lon, lat)]
        point = ox.projection.project_geometry(Point(coords))[0]
        x, y = point.x, point.y

        # Find the nearest node
        node = ox.distance.nearest_nodes(graph_proj, x, y, return_dist=False)

        return node

    def crop (self, initial_point, final_point):
        """
        Crops the graph based on the fastest path between two given nodes.

        :param initial_point (int): ID of the initial node.
        :param final_point (int): ID of the final node.

        :return cropped_graph (networkx.MultiDiGraph): Cropped graph
            containing only the nodes and edges around the fastest path.
        """

        # Find the fastest path between the initial and final nodes
        gmaps_path = nx.astar_path(self.graph, initial_point, final_point, weight='travel_time')

        # Retrieve latitude and longitude coordinates of the nodes along the
        # fastest path (aka Google Maps route)
        lats = [self.graph.nodes[node]['y'] for node in gmaps_path]
        lons = [self.graph.nodes[node]['x'] for node in gmaps_path]

        # Determine a tight bounding box around the path
        lat_min = min(lats)
        lat_max = max(lats)
        lon_min = min(lons)
        lon_max = max(lons)

        # Adjust the bounding box to ensure it contains the graph properly and
        # falls within the initial boundaries
        bbox_lat_min = max(self.lat0, lat_min - (lat_max - lat_min))
        bbox_lat_max = min(self.latoo, lat_max + (lat_max - lat_min))
        bbox_lon_min = max(self.lon0, lon_min - (lon_max - lon_min))
        bbox_lon_max = min(self.lonoo, lon_max + (lon_max - lon_min))

        # Crop the graph based on the adjusted bounding box
        self.graph = ox.truncate.truncate_graph_bbox(self.graph, bbox_lat_max, bbox_lat_min, bbox_lon_max, bbox_lon_min)

        return self.graph

    def reset (self):
        """
        Resets the graph to its original state, downloading and processing
        the graph data again.

        :return graph (networkx.MultiDiGraph): Reset graph.
        """

        self.graph = ox.graph_from_bbox(lat0, latoo, lon0, lonoo, network_type='drive')
        self.graph = ox.add_edge_speeds(self.graph)
        self.graph = ox.add_edge_travel_times(self.graph)
        self.graph = ox.distance.add_edge_lengths(self.graph)

        return self.graph

    def find_edge_by_nodes (self, node1, node2):
        """
        Finds an edge in the graph that links node1 to node2.

        :param node1 (int): Starting node ID.
        :param node2 (int): Ending node ID.

        :return None or edges[0] (None or tuple): Edge that links node1 to
            node2.
        """

        # Gather all the edges of the graph that start at node1 and end at node2,
        # or start at node2 and end at node1
        e1 = [e for e in self.graph.edges if e[0] == node1 and e[1] == node2]
        e2 = [e for e in self.graph.edges if e[0] == node2 and e[1] == node1]
        edges = [*e1, *e2]

        # If no edges were found, then print a message and return None.
        if len(edges) == 0:
            print(f"There are no edges linking {node1} to {node2} in graph.")
            return None

        # Otherwise, return the first edge that was found.
        else:
            return edges[0]


class Radar:

    def __init__ (self, lat0, lon0, dlat, dlon):
        """
        Initializes a radar object with latitude and longitude information.
        This class represents the radar that provides the information on
        precipitation.

        :param lat0 (float): Minimum latitude boundary.
        :param lon0 (float): Minimum longitude boundary.
        :param dlat (float): Spacing in the latitude grid.
        :param dlon (float): Spacing in the longitude grid.
        """

        self.lat0 = lat0
        self.lon0 = lon0
        self.dlat = dlat
        self.dlon = dlon

        self.source = "https://raw.githubusercontent.com/RPvMM-2023-S1/Rain-and-flood-informed-vehicle-routing-problem/main/radar_data/R13537439_"

    def rain_by_time (self, agora):
        """
        Reads rainfall data (mm) from a text file and returns it as a matrix.

        :param agora (Agora): An instance of the Agora class that represents
            the time.

        :return A (list or None): Matrix of rainfall data. Each element
            represents the rainfall in millimeters at a specific location. If
            the data is not available, returns None.
        """

        filename = self.source + repr(agora) + ".txt"
        radar_id = self.source.split("/")[-1]
        local_filename = os.path.join('radar_cache', radar_id + repr(agora) + ".txt")

        # Check if the 'radar_cache' folder exists and create it if necessary
        if not os.path.isdir('radar_cache'):
            os.mkdir('radar_cache')

        # Check if the local file already exists
        if os.path.isfile(local_filename):
            # If the file exists, open it and read the data
            with open(local_filename, 'r') as file:
                    data = file.readlines()
        else:
            try:
                # If the file doesn't exist locally, try to download it
                response = requests.get(filename)

                # Check if the download was successful (status code 200)
                if response.status_code == 200:
                    # Extract the text data from the response and split it
                    # into lines
                    data = response.text.splitlines()

                    # Save the downloaded data to the local file
                    with open(local_filename, 'w') as file:
                            file.write('\n'.join(data))
                else:
                    # If the file doesn't exist on the server, print an error
                    # message
                    print(f"File {filename} does not exist.")
                    data = None

            except FileNotFoundError:
                # If there was an error with file handling, print an error
                # message
                print(f"File {filename} does not exist.")
                data = None

        # Data processing to create matrix A
        if data:
            # Create a matrix A by splitting each line and converting entries
            # to integers.  If the entry is "-99", it is replaced with 0.
            A = [[0 if entry == "-99" else int(entry) for entry in line.split()] for line in data]
        else:
            A = None

        # Print the resulting matrix A
        return A

    def rain_at_edge (self, graph, edge, agora):
        """
        Reads the rain data from a matrix and returns the maximum rainfall in
        a given edge of a given graph.

        :param graph (networkx.Graph): Graph object.
        :param edge (tuple): Edge in the graph.
        :param agora (Agora): An instance of the Agora class that represents
            the time.

        :return (int): Maximum rainfall on the edge.
        """

        # Gather the coordinates of several points along the edge
        if 'geometry' in graph.edges[edge]:
            lonlats = list(graph.edges[edge]['geometry'].coords)
        else:
            lonlats = []

        initial = edge[0]
        lon, lat = graph.nodes[initial]['x'], graph.nodes[initial]['y']
        lonlats.append((lon, lat))

        final = edge[1]
        lon, lat = graph.nodes[final]['x'], graph.nodes[final]['y']
        lonlats.append((lon, lat))

        # List the rows and columns of the points of the edge
        rowcols = [(int((lat - self.lat0) / self.dlat), int((lon - self.lon0) / self.dlon)) for lon, lat in lonlats]

        # List the mms of rain in the points of the edge
        matrix = self.rain_by_time(agora)
        rainfall = [matrix[row][col] for row, col in rowcols]

        return max(rainfall)


# Extra auxiliary functions

def convert_coordinates (longitude, latitude):
    """
    Converts coordinates from EPSG 4326 system to UTM 23S system.

    :param longitude (float): Longitude coordinate.
    :param latitude (float): Latitude coordinate.

    :return (tuple): Converted coordinates in UTM 23S system.
    """

    utm23s = pyproj.CRS.from_string('+proj=utm +zone=23 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
    epsg4326 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(utm23s, epsg4326)

    return transformer.transform(longitude, latitude)


def oracle (grafo, path, initial_point, tyme):
    """
    Predicts the node and crossed edges after a given time in a given path.

    :param grafo (Grafo): An instance of the Grafo class in which the path is
        contained.
    :param path (list): A list of edges that representa a path in the grafo.
    :param initial_point (int): ID of the initial point in the path.
    :param tyme (int): Time in seconds.

    :return next_node, crossed_edges (tuple): Next node after the given
        time and a list of edges crossed on the way.
    """

    # Find the initial point within the path
    initial_indices = [i for i in range(len(path)) if path[i] == initial_point]

    # If the initial point is not in the path, return the initial point and
    # an empty list:
    if len(initial_indices) == 0:
        print(f"The node {initial_point} is not in {path}.")
        return initial_point, []

    # Otherwise, if the initial point is in the path, that is, if
    # initial_indices != []:
    else:
        n = initial_indices[0]
        next_node = initial_point
        crossed_edges = []

        # While there is: time left to cross the path and points in the path
        # to be crossed
        while tyme > 0 and n < len(path)-1:
            current_node = path[n]
            next_node = path[n+1]

            # Find the edge in the graph
            e = grafo.find_edge_by_nodes(current_node, next_node)
            crossed_edges.append(e)

            # Update the time left
            tyme -= grafo.graph.edges[e]['travel_time']

            # Update the index for the next step
            n += 1

        return next_node, crossed_edges


def is_flooded (graph, edge, flooded_points):
    """
    Checks if a given edge of a graph is within 200 meters of a reported
    flooded point.

    :param graph (networkx.Graph): Graph object.
    :param edge (tuple): Edge in the graph.
    :param flooded_points (list): List of flooded points.

    :return tf (bool): True if edge is near a flooded point, False otherwise.
    """

    # Gather the coordinates of several points along the edge
    if 'geometry' in graph.edges[edge]:
        lonlats = list(graph.edges[edge]['geometry'].coords)
    else:
        lonlats = []

    initial = edge[0]
    lon, lat = graph.nodes[initial]['x'], graph.nodes[initial]['y']
    lonlats.append((lon, lat))

    final = edge[1]
    lon, lat = graph.nodes[final]['x'], graph.nodes[final]['y']
    lonlats.append((lon, lat))

    # List of (latitudes, longitudes) of the points of the edge
    latlons = [(y, x) for x, y in lonlats]

    # Determine whether any of the points of the edge are closer to 200 meters
    # of any of the flooded points (tf = True) or not (tf = False)
    tf = False
    for p in latlons:
        for q in flooded_points:
            if distance.great_circle(p, q).meters < 200:
                tf = True
                break

    return tf



class Experiment:

    def __init__ (self, origin, destination, agora, grafo, radar):
        """
        Initializes an experiment object with the given parameters.

        :param origin (tuple): The coordinates of the start location.
        :param destination (tuple): The coordinates of the end location.
        :param agora: An instace of the Agora class that represents the
            initial time (time of departure of the vehicle).
        :param grafo: An instace of the Grafo class that represents the road
            network.
        :param radar: An instance of the Radar class that represents the
            radar that will provide information on precipitation.
        """

        self.origin = grafo.get_nearest_node(*origin)
        self.destination = grafo.get_nearest_node(*destination)
        self.agora = agora
        self.grafo = grafo
        self.radar = radar

    def experiment (self, weight):
        """
        Calculates the path that minimizes a certain function (weight).

        :param weight (function): The weight function used to calculate the
            weights of edges in the graph.

        :return edge_rains (dict): A dictionary containing the edges of the
            optimal path and their corresponding rainfall values (at the time
            of travel).
        """

        # Parameters
        start = copy.deepcopy(self.origin)
        time = copy.deepcopy(self.agora)
        graph = self.grafo.crop(self.origin, self.destination)

        # Dicionary where we will save infomation about the path
        edge_rains = {}

        # Main loop
        while start != self.destination:

            # Update: list of fooded points, matrix with rain info and weigths
            flooding_points = time.get_flooding_points()

            if self.radar.rain_by_time(time):
                A = self.radar.rain_by_time(time)
                rains = {e: self.radar.rain_at_edge(graph, e, time) for e in graph.edges}
                weights = {e: weight(graph, e, flooding_points, rains) for e in graph.edges}
                nx.set_edge_attributes(graph, weights, 'weight')
            else:
                rains = {e: 0 for e in graph.edges}

            # Calculate the path with the least rain
            shortest_path = nx.astar_path(graph, start, self.destination, weight='weight')

            # Add 10 minutes to the current time for the next iteration
            time.step(600)

            # Predict where the start of the next iteration will be
            start, subpath = oracle(self.grafo, shortest_path, shortest_path[0], 600)

            # Save the information of the edges that will be crossed
            for e in subpath:
                edge_rains[e] = rains[e]

        return edge_rains

    def analysis (self, dictionary):
        """
        Prints the results of the output of an experiment.

        :param dictionary (dict): A dictionary containing the edges of a path
            and their corresponding rainfall values (output of an experiment).

        :return (tuple): A tuple containing the total length, total time, and
            rainfall per second along the path.
        """

        # Lists the edges of the path
        edge_path = list(dictionary.keys())

        # Prints the total length of the path
        edge_lengths = [self.grafo.graph.edges[e]['length'] for e in edge_path]
        total_length = sum(edge_lengths) / 1000
        print(f"The total distance traveled was {total_length:.3f} km.")

        # Prints the total duration of the path
        edge_times = [self.grafo.graph.edges[e]['travel_time'] for e in edge_path]
        total_time = sum(edge_times)
        print(f"The travel time was {total_time // 60:.0f} minutes and {total_time % 60:.0f} seconds.")

        # Prints the amount of rain along the path
        edge_rain_per_sec = [dictionary[e] * self.grafo.graph.edges[e]['travel_time'] for e in edge_path]
        rain_per_sec = sum(edge_rain_per_sec)
        print(f"The rainfall along the path was: {rain_per_sec:.03f} mm.")

        return total_length, total_time, rain_per_sec
