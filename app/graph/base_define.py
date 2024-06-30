from helper.base_define import dump
from enum import Enum

class Shape(Enum):
    diamond = 'diamond'
    predicate = 'predicate'
    entity = 'entity'

class NodeAttr(Enum):
    headnoun = 'headnoun'
    range = 'range'
    negative = 'negative'
    negative_node = 'negative_node'  

class Connection:
    def __init__(self, node, name, attr = None):
        self.node = node  
        self.name = name  
        self.attr = attr
        self.ref = {}

    def __repr__(self):
        return f"<Connection(node={self.node}, name={self.name})>"

class Node:
    def __init__(self, shape, name, id, ref: dict = {}):
        self.id = id  
        self.shape = shape
        self.name = name
        self.ref = ref
        self.connections = []

    def connect(self, other_node, connection_name = '', attr_name = None):
        
        self.connections.append(Connection(other_node, connection_name, attr_name))

    def __repr__(self):
        return f"< Node(id = {self.id}, shape = {self.shape}, name = {self.name}) >" 
        

class Graph:
    def __init__(self):
        self.nodes = []

    def append(self, node: Node):
        self.nodes.append(node)

        return

    def insert(self, shape, name, id, ref: dict = {}):
        """插入一個新節點到圖中"""
        if self.search_by_shape_and_name(shape, name) == None:
            newNode = Node(shape, name, id, ref)
            self.nodes.append(newNode)
            return newNode

        return None

    def search_connections(self, shape_from, shape_to, two_way = True):
        """搜尋所有指定形狀連接的節點對，包括雙向連接"""
        connections = []
        for node in self.nodes:
            if node.shape == shape_from:
                for connection in node.connections:
                    if connection.node.shape == shape_to:
                        connections.append((node, connection.node))

            elif node.shape == shape_to and two_way:  
                for connection in node.connections:
                    if connection.node.shape == shape_from:
                        connections.append((connection.node, node))  

        return connections

    def search_by_name(self, name):
        lists = []

        for node in self.nodes:
            if node.name == name:
                lists.append(node)

        return lists

    def search_by_shape(self, shape):
        lists = []

        for node in self.nodes:
            if node.shape == shape:
                lists.append(node)

        return lists

    def search_by_shape_to_another_shape_and_name(self, shape_from, shape_to, goal_node_name, not_node_list = []):
        for node in self.nodes:
            if node.shape == shape_from and node.name not in not_node_list:
                for connection in node.connections:
                    if connection.node.shape == shape_to and connection.node.name == goal_node_name:
                        return node

        return None

    def search_by_shape_to_another_shape_and_name_lists(self, shape_from, shape_to, goal_node_name):
        lists = []

        for node in self.nodes:
            if node.shape == shape_from:
                for connection in node.connections:
                    if connection.node.shape == shape_to and connection.node.name == goal_node_name:
                        lists.append(node)

        return lists

    def search_by_shape_and_name_to_another_shape(self, shape_from, from_node_name, shape_to):
        for node in self.nodes:
            if node.shape == shape_from and node.name == from_node_name:
                for connection in node.connections:
                    if connection.node.shape == shape_to:
                        return node

        return None

    def search_by_shape_and_name(self, shape, name):
        for node in self.nodes:
            if  node.shape == shape and node.name == name:
                return node

        return None

    def search_by_shape_and_like_name(self, shape, name):
        for node in self.nodes:
            if  node.shape == shape and name in node.name:
                return node

        return None

    def search_connection_by_name(self, connectionName):
        lists = []

        """根據連線名稱搜尋連線"""
        for node in self.nodes:
            for connection in node.connections:
                if connection.name == connectionName:
                    lists.append((node, connection.node))

        return lists
