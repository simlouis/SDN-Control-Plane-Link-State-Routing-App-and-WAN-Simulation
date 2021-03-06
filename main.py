import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import sys

port_list = []
graph = []
file_to_send = "routing_table.json"

host = str(sys.argv[1])
endpoint = str(sys.argv[2])

connected = False


def connect():
    global connected
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    data = None

    try:
        data = session.get("http://{}:2222/get_topology/{}".format(host, endpoint)).json()
    except Exception as e:
        print("Connection failed")
        print(e)
        exit()

    try:
        data["connected"]
        connected = True
        compute_optimal(data)
    except KeyError as e:
        print(data)


def compute_optimal(data):
    high_num_vertices = 0

    # Get max number of vertices
    for i in data.values():
        for j in i:
            edge = j
            try:
                source_node = int(edge[0])
            except Exception as e:
                source_node = high_num_vertices
            if source_node > high_num_vertices:
                high_num_vertices = source_node

    high_num_vertices += 3

    for i in range(high_num_vertices):
        lis = []
        graph.append(lis)

    # Differentiate between source node, destination node, and out port
    for i in data.values():
        for node in i:
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
                    if source_ip == "169.254.20.158":
                        source_ip_int = high_num_vertices
                    elif source_ip == "169.254.173.130":
                        source_ip_int = high_num_vertices - 1
                    elif source_ip == "169.254.240.121":
                        source_ip_int = high_num_vertices - 2

                source_ip_tuple = (str(source_ip), source_ip_int - 1)

            if isinstance(node[1], int):
                dest_ip = node[1]
                dest_ip_tuple = (str(dest_ip), dest_ip - 1)

            elif isinstance(node[1], str):
                dest_ip = node[1]
                dest_ip_int = 0
                try:
                    dest_ip_int = int(dest_ip)
                except Exception as e:
                    if dest_ip == "169.254.20.158":
                        dest_ip_int = high_num_vertices
                    elif dest_ip == "169.254.173.130":
                        dest_ip_int = high_num_vertices - 1
                    elif dest_ip == "169.254.240.121":
                        dest_ip_int = high_num_vertices - 2

                dest_ip_tuple = (str(dest_ip), dest_ip_int - 1)

            port_list.append((source_ip_tuple[0], source_ip_tuple[1], dest_ip_tuple[0], dest_ip_tuple[1], out_port_int))
            add_edge(graph, source_ip_tuple[1], dest_ip_tuple[1])

        host1 = 0
        host2 = 0
        host3 = 0

        for i in port_list:
            if i[0] == "169.254.20.158":
                host1 = i[1]
            if i[0] == "169.254.173.130":
                host2 = i[1]
            if i[0] == "169.254.240.121":
                host3 = i[1]

        routing_table = [shortest_distance(graph, host1, host2, high_num_vertices, port_list),
                         shortest_distance(graph, host1, host3, high_num_vertices, port_list),
                         shortest_distance(graph, host2, host1, high_num_vertices, port_list),
                         shortest_distance(graph, host2, host3, high_num_vertices, port_list),
                         shortest_distance(graph, host3, host1, high_num_vertices, port_list),
                         shortest_distance(graph, host3, host2, high_num_vertices, port_list)]

        flattened_table = []
        for i in routing_table:
            for j in i:
                flattened_table.append(j)

        json_data = {"table_entries" : flattened_table}

        with open(file_to_send, 'w') as file:
            json.dump(json_data, file)


def add_edge(graph, src, dest):
    graph[src].append(dest)
    graph[dest].append(src)


# Algorithm taken from geekforgeeks shortest unweighted path
def shortest_distance(graph, src, dest, vertices, ports):
    pred = [None] * vertices
    dist = [None] * vertices

    routing_tuples = []

    src_string = ""
    for i in ports:
        if i[1] == src:
            src_string = i[0]

    dest_string = ""
    for i in ports:
        if i[1] == dest:
            dest_string = i[0]

    if not BFS(graph, src, dest, vertices, pred, dist):
        print("There is no path from {} to {}".format(src, dest))

    path = []
    crawl = dest
    path.append(crawl)

    while pred[crawl] != -1:
        path.append(pred[crawl])
        crawl = pred[crawl]

    for port in ports:
        if port[1] == path[len(path) - 1] and port[3] == path[len(path) - 2]:
            if port[4] == -1:
                print("Shortest path from {} to {} goes out port: ".format(src_string, dest_string))
                for i in ports:
                    if i[1] == path[len(path) - 2] and i[3] == path[len(path) - 3]:
                        out_port = str(i[4])
                        print(out_port)
            else:
                out_port = str(port[4])
                print("Shortest path from {} to {} goes out port: {}".format(src_string, dest_string, out_port))

    print("Shortest path length is : {} \n".format(str(dist[dest])), end='')

    for i in range(len(path) - 1, -1, -1):
        print("{}".format(path[i] + 1), end=' ')
    print("\n")

    for i in range(len(path) - 2):
        for j in ports:
            if path[i + 1] == j[1] and path[i] == j[3]:
                if j[4] != -1:
                    routing_tuples.append({"switch_id": int(j[0]), "dst_ip": dest_string, "out_port": j[4]})

    return routing_tuples


# Algorithm taken from geeksforgeeks BFS
def BFS(graph, src, dest, vertices, pred, dist):
    queue = []

    visited = [False for i in range(vertices)]

    for i in range(vertices):
        dist[i] = 10000
        pred[i] = -1

    visited[src] = True
    dist[src] = 0
    queue.append(src)

    while len(queue) != 0:
        u = queue[0]
        queue.pop(0)
        for i in range(len(graph[u])):
            if visited[graph[u][i]] == False:
                visited[graph[u][i]] = True
                dist[graph[u][i]] = dist[u] + 1
                pred[graph[u][i]] = u
                queue.append(graph[u][i])

                if graph[u][i] == dest:
                    return True

    return False


def send_table():
    global connected
    if connected:
        with open(file_to_send, 'r') as file:
            send = json.load(file)
            results = requests.post("http://{}:2222/set_tables/{}".format(host, endpoint), json=send)
            print(results.json())


connect()
send_table()

