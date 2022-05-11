import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import socket

router1 = "169.254.20.158"
router2 = "169.254.173.130"
router3 = "169.254.240.121"

port_list = []
graph = [[]]


def connect():
    host = "www.goatgoose.com"

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    endpoint = input("Please enter an endpoint")
    data = None

    try:
        data = session.get("http://{}:2222/get_topology/{}".format(host, endpoint)).json()
    except Exception as e:
        print(e)

    if data is not None:
        compute_optimal(data)


def compute_optimal(data):
    high_num_vertices = 0
    src_node = 0
    dest_node = 0

    for i in data.values():
        for j in i:
            edge = j
            source_node = 0

            try:
                source_node = int(edge[0])
            except Exception as e:
                source_node = high_num_vertices
            if source_node > high_num_vertices:
                high_num_vertices = source_node

    high_num_vertices += 3

    # for i in range(high_num_vertices):
    #     graph.append()

    for i in data.values():
        for node in i:
            # source_ip_tuple = ()
            # dest_ip_tuple = ()
            out_port_int = int(node[2])

            if isinstance(node[0], int):
                source_ip = node[0]
                source_ip_tuple = (str(source_ip), source_ip - 1)
            else:
                source_ip = str(node[0])
                source_ip_int = 0
                try:
                    source_ip = int(source_ip)
                except Exception as e:
                    if source_ip == router1:
                        source_ip_int = high_num_vertices
                    elif source_ip == router2:
                        source_ip_int = high_num_vertices - 1
                    elif source_ip == router3:
                        source_ip_int = high_num_vertices - 2

                source_ip_tuple = (str(source_ip), source_ip_int - 1)
                source_node = source_ip_tuple[1]

            if isinstance(node[1], int):
                dest_ip = node[1]
                dest_ip_tuple = (str(dest_ip), dest_ip - 1)

            elif isinstance(node[1], str):
                dest_ip = node[1]
                dest_ip_int = 0
                try:
                    dest_ip_int = int(dest_ip)
                except Exception as e:
                    if dest_ip == router1:
                        dest_ip_int = high_num_vertices
                    elif dest_ip == router2:
                        dest_ip_int = high_num_vertices - 1
                    elif dest_ip == router3:
                        dest_ip_int = high_num_vertices - 2

                dest_ip_tuple = (str(dest_ip), dest_ip_int - 1)
                dest_node = dest_ip_tuple[1]

            port_list.append((source_ip_tuple[0], source_ip_tuple[1], dest_ip_tuple[0], dest_ip_tuple[1], out_port_int))
            add_edge(graph, source_ip_tuple[1], dest_ip_tuple[1])


def add_edge(graph, src, dest):
    graph[src].append(dest)
    graph[dest].append(src)

def send_tables():

    # send new forwarding tables to network with requests POST

    pass

connect()

