from graphviz import Digraph
import os
import re
# 添加graphviz的环境变量
ori_path = os.environ["PATH"]
if re.search("Graphviz", ori_path, re.I) == None:
    gra_path = os.getcwd() + "\\Graphviz-11.0.0-win64\\bin" 
    os.environ["PATH"] = ori_path + ";" + gra_path  


class Node:
    num = 0
    def __init__(self, name:str, val=0):
        self.index = str(Node.num)
        if val == "cut":
            self.val = val
        else:
            self.val = str(val)
        self.name = name    # max, min, chance, eval, cut
        self.childen = []
        Node.num += 1

    def add_child(self, child, action_edge:str):
        self.childen.append(( child, action_edge ))
    
    def set_val(self, val:int):
        self.val = str(val)
        

def draw_tree(root):
    tree_graph = Digraph(name="Expectiminimax-Tree", format="png", engine="fdp")
    tree_graph.graph_attr['dpi'] = '150'


    def dfs(node):

        if node.name == "max":
            node_shape = "triangle"
            node_color = "#75FA8D"

        elif node.name == "min":
            node_shape = "invtriangle"
            node_color = "#F09B59"

        elif node.name == "cut":
            node_shape = "star"
            node_color = "#D12D20"

        elif node.name == "eval":
            node_shape = "box"
            node_color = "#73FBFD"
        else:
            node_shape = "circle"
            node_color = "#F2F051"
        
        tree_graph.attr('node', shape=node_shape, color=node_color)
        tree_graph.node(name=node.index, style='filled', label=node.val)

        for child,edge_val in node.childen:
            dfs(child)
            tree_graph.edge(node.index, child.index, edge_val, fontname="SimHei")

    dfs(root)
    tree_graph.view()



