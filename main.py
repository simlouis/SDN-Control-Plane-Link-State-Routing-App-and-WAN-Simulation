import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import socket

router1 = "169.254.20.158"
router2 = "169.254.173.130"
router3 = "169.254.240.121"


def connect():
    # cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # host = input("Please enter host name")
    host = "www.goatgoose.com"
    # port = 2222
    #
    # try:
    #     cl.connect((host, port))
    # except Exception as e:
    #     print(e)
    #
    # print("Connected to {} on port {}".format(host, port))

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    endpoint = input("Please enter an endpoint")
    data = None

    try:
        test = session.get("http://{}:2222/get_topology/{}".format(host, endpoint))
        data = test.json()
    except Exception as e:
        print(e)

    if data is not None:
        compute_optimal(data)


def compute_optimal(data):
    # print(data)
    # src = router1
    # dest = router2

    nodes = []

    for i in data.values():
        for j in i:
            if j[0] not in nodes:
                nodes.append(j[0])

    print(nodes)

    # dykstras algorithm to compute forwarding tables

    pass


def send_tables():

    # send new forwarding tables to network with requests POST

    pass

connect()

