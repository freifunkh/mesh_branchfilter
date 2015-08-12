#!/usr/bin/python3
import os
import json
import urllib.request

from config import *

try:
    nodes_request = urllib.request.Request(nodes_json_url)
    nodes_json_response = urllib.request.urlopen(nodes_request)
    graph_request = urllib.request.Request(graph_json_url)
    graph_json_response = urllib.request.urlopen(graph_request)
except urllib.error.URLError:
    print("URL Error occured")

nodes_data = json.loads(nodes_json_response.read().decode())
graph_data = json.loads(graph_json_response.read().decode())

# modify nodes_data
nodes_buffer = {}
nodes_buffer['timestamp'] = nodes_data['timestamp']
nodes_buffer['version'] = nodes_data['version']
nodes_buffer['nodes'] = {}

# interesting macs:
interesting_nodes = []

# append each node
for mac in nodes_data['nodes']:
    node = nodes_data['nodes'][mac]
    try:
        # TODO check wether the neccesity of the following if is a bugs result
        if node['nodeinfo']['system'] != []:
            if node['nodeinfo']['system']['site_code'] in site_codes:
                interesting_nodes.append(node['nodeinfo']['network']['mac'])
                nodes_buffer['nodes'][mac] = node
    except KeyError:
        pass

shortened_interesting = []

for each in interesting_nodes:
    shortened_interesting.append(each.replace(":", ""))

# modify graph.json

graph_buffer = {}
graph_buffer['version'] = graph_data["version"]
graph_buffer['batadv'] = {}
graph_buffer['batadv']['directed'] = graph_data['batadv']['directed']
graph_buffer['batadv']['graph'] = graph_data['batadv']['graph']
graph_buffer['batadv']['nodes'] = []
graph_buffer['batadv']['links'] = []
graph_buffer['batadv']['multigraph'] = graph_data['batadv']['multigraph']

translate = []
for node in graph_data['batadv']['nodes']:
    try:
        if node['node_id'] in shortened_interesting:
            graph_buffer['batadv']['nodes'].append(node)
            translate.append(graph_data['batadv']['nodes'].index(node))
    except KeyError:
        # print("KeyError")
        pass

for link in graph_data['batadv']['links']:
    try:
        if link['source'] in translate and link['target'] in translate:
            link['source'] = translate.index(link['source'])
            link['target'] = translate.index(link['target'])
            graph_buffer['batadv']['links'].append(link)
    except KeyError:
        pass

# store the jsons
with open('nodes.json', 'w') as outfile:
    json.dump(nodes_buffer, outfile)
with open('graph.json', 'w') as graph_file:
    json.dump(graph_buffer, graph_file)

# print where the script has been executed and where the json files are
print(os.getcwd())
