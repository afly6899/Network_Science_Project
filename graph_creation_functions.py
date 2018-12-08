import time
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite

# Read in data
def read_in_multi_bipartite_graph(filename):
    graph = bipartite.edgelist.read_edgelist(filename, create_using=nx.MultiGraph,
                                     delimiter="\t", nodetype=str, comments="#",
                                     data = [("Date", str), ("% Error", float), ("Value", float),
                                            ("Threshold", float), ("Threshold Adhered To", str)])
    return graph

# 2.

def is_int(string):
# https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except
    try:
        int(string)
        return True
    except ValueError:
        return False

def get_bipartite_sets(bipartite_graph, verbose=False):
    start_time = time.time()
    sites = []
    pollutants = []
    for subgraph in nx.connected_component_subgraphs(bipartite_graph):
        group_1, group_2 = bipartite.sets(subgraph)
        
        if is_int(next(iter(group_1))): # check if the first group contains sites
            sites += group_1
            pollutants += group_2

        else:
            sites += group_2
            pollutants += group_1
    if verbose:
        print("Getting bipartite node sets:", time.time() - start_time)
        
    return sites, pollutants

# 1.
def multi_to_single_graph_bipartite(multi_graph, verbose=False):
    start_time = time.time()
    # Converting Multigraph to Graph: https://stackoverflow.com/questions/15590812/networkx-convert-multigraph-into-simple-graph-with-weighted-edges
    single_graph = nx.Graph()
    edge_counts = {}
    for u,v,e in multi_graph.edges(data=True):
        if single_graph.has_edge(u,v):
            single_graph[u][v]["Date Info"][e["Date"]] = {"Value":e["Value"], 
                                                          "% Error":e["% Error"]}
            edge_counts[(u,v)] += 1
        else:
            single_graph.add_edge(u, v, Threshold = e["Threshold"])

            nx.set_edge_attributes(single_graph, 
                                   name="Threshold Adhered To", 
                                   values={(u,v):e["Threshold Adhered To"]})

            nx.set_edge_attributes(single_graph, 
                                   name="Date Info", 
                                   values={(u,v):{e["Date"]:{"Value":e["Value"], 
                                                   "% Error":e["% Error"]}}})
            edge_counts[(u,v)] = 1
    if verbose:
        print("Creating single linked bipartite graph:", time.time() - start_time)

    
    nx.set_edge_attributes(single_graph,
                           name="Weight",
                           values=edge_counts)
    return single_graph
    
#3.
def get_projections(single_bipartite_graph, sites, pollutants, verbose=False):
    start_time = time.time()
    sites_graph = multi_to_single_graph_projection(
                            bipartite.projected_graph(single_bipartite_graph,
                                                      nodes = sites,
                                                      multigraph = True),
                            verbose)
    
    pollutants_graph = multi_to_single_graph_projection(
                            bipartite.projected_graph(single_bipartite_graph,
                                                      nodes = pollutants,
                                                      multigraph = True),
                            verbose)
    
    if verbose:
        print("Getting projections of bipartite graph:", time.time() - start_time)

    return sites_graph, pollutants_graph


def multi_to_single_graph_projection(projected_multi_graph, verbose=False):
    # We'll need the weights for these
    start_time = time.time()
    
    single_graph = nx.Graph()
    for u, v, k in projected_multi_graph.edges(keys=True):
        if single_graph.has_edge(u,v):
            single_graph[u][v]["Weight"] += 1
            #single_graph[u][v]["Connectors"].append(k)
        else:
            single_graph.add_edge(u, v, Weight = 1, Connectors = [k])
    if verbose:
        print("Creating single linked projection graph:", time.time() - start_time)
    return single_graph

# 4.
def round_to_next(x, to=10):
#https://stackoverflow.com/questions/26454649/python-round-up-to-the-nearest-ten
    if x % to == 0:
        x += 1
    return ((x + (to-1)) // to) * to
    
def get_graphs_by_year(multi_graph, time_span=10, verbose=False):
    start_time = time.time()
    
    by_year = {year:[] for year in range(1970, 2030, time_span)}
    
    for u,v,e in multi_graph.edges(data = True):
        year = round_to_next(int(e["Date"][:4]))
        if year < 1970:
          year = 1970
        by_year[year].append((u,v,e))
        
    graphs_by_year = { year:nx.MultiGraph(by_year[year]) for year in by_year }
    
    if verbose:
        print("Grouping graphs by every", to, "years:", time.time() - start_time)
   
    return graphs_by_year
    
    
#5.
def create_filenames(dir="Graphs", gtype="Bipartite", year=None):
    filename = dir + "/" + gtype
    if year:
        filename += "_Graph_{}-{}.tsv".format(year-10 if year > 1970 else "1940", year)
    else:
        filename += "_Graph_All.tsv"
    return filename

def write_graph_to_file(filename, graph, data=None, verbose=False):
    # Takes a single-linked graph
    start_time = time.time()
    nx.write_edgelist(graph, filename, delimiter="\t", data=data)
    if verbose:
        print("Writing graphs to files:")
    try:
        # add header to files
        file = open(filename, 'r')
        file_contents = file.read()
        file.close()

        file = open(filename, 'w')
        file.write("\t".join(["Node 1", "Node 2"] + data) + "\n")
        file.write(file_contents)
        file.close()
        
        if verbose:
            print("\tSucessfully wrote to file", filename)
    except Exception as e:
        if not verbose:
            print("Writing graphs to files:")
        print("\tWriting Failed for file", filename, + ":", e)
    
    if verbose:
        print(time.time() - start_time)
        
    return None
    
    
# 6. Assuming you don't want blue!
def check_colors(nodes_colors_dict):
    plt.figure(1)
    for i,color in enumerate(nodes_colors_dict.values()):
        plt.scatter(i,i, color=color+"FF")
    plt.show()
    

def add_colors_per_node(projected_graph):
    nodes_colors_dict = {}
    
    code = int("0xFF0000", 0)
    delta = (int("0xFFCC00",0) - code)//len(projected_graph.nodes)
    for node in projected_graph.nodes:
        nodes_colors_dict[node] = "#" + hex(code)[2:]
        code += delta
    
    nx.set_node_attributes(projected_graph, nodes_colors_dict, "Color")
    return nodes_colors_dict
    
def add_weights_per_node(projected_graph, single_bipartite_graph):
    weights_dict = {node:0 for node in projected_graph.nodes}
    
    for u, v in single_bipartite_graph.edges:
        if u in weights_dict:
            weights_dict[u] += 1
        else:
            weights_dict[v] += 1
    nx.set_node_attributes(projected_graph, weights_dict, "Weight")
    return weights_dict

def write_node_attributes_to_file(projected_graph, name="Pollutant", single_bipartite_graph=None):
    attributes = list(list(projected_graph.nodes(data=True))[0][1].keys())
    if "Color" not in attributes:
        add_colors_per_node(projected_graph)
        add_weights_per_node(projected_graph, single_bipartite_graph)
    
    node_info = "\t".join([name] + attributes) + "\n"
    
    for node in projected_graph.nodes:
        attrs = projected_graph.nodes[node]
        node_list += node + "\t".join(attrs[attr] for attr in attributes) + "\n"
    
    filename = "Nodes/{}_list_All.tsv".format(name)
    
    file = open(filename, 'w')
    file.write(node_list)
    file.close()
    
    
