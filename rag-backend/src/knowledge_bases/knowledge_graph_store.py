import json
import os

import networkx as nx
import matplotlib.pyplot as plt

from models.enums import InformationTier
from util.config_loader import load_config
from models.activity import Activity

config = load_config()

class KnowledgeGraphStore:
    def __init__(self):
        os.makedirs(config["paths"]["knowledge_graph"], exist_ok=True)
        self.title_graph = nx.MultiDiGraph()
        self.title_graph_path = f"{config['paths']['knowledge_graph']}/title_graph.json"
        self.title_desc_graph = nx.MultiDiGraph()
        self.title_desc_graph_path = f"{config['paths']['knowledge_graph']}/title_desc_graph.json"

    # property graph
    def build_graphs(self, data: list[Activity]):
        # build graphs with skills and locations as separate nodes
        for activity in data:
            self.title_graph.add_node(activity.id, type="Activity",
                                      text=activity.text_variations.get(InformationTier.TITLE_ONLY),
                                      embedding="",  # create embeddings if wanted
                                      startTime=activity.metadata.starting_date,
                                      endTime=activity.metadata.end_date)

            self.title_desc_graph.add_node(activity.id, type="Activity",
                                      text=activity.text_variations.get(InformationTier.TITLE_DESC),
                                      embedding="",  # create embeddings if wanted
                                      startTime=activity.metadata.starting_date,
                                      endTime=activity.metadata.end_date)

            for skill in activity.soft_skills:
                skill_id = self.__get_or_create_skill_node(self.title_graph, skill)
                self.title_graph.add_edge(activity.id, skill_id, "REQUIRES_SKILL")
                skill_id = self.__get_or_create_skill_node(self.title_desc_graph, skill)
                self.title_desc_graph.add_edge(activity.id, skill_id, "REQUIRES_SKILL")

            loc_id = self.__get_or_create_loc_node(self.title_graph, activity.metadata.location)
            self.title_graph.add_edge(activity.id, loc_id, "LOCATED_IN")
            loc_id = self.__get_or_create_loc_node(self.title_desc_graph, activity.metadata.location)
            self.title_desc_graph.add_edge(activity.id, loc_id, "LOCATED_IN")

        self.__save_graph_to_json(self.title_graph, self.title_graph_path)
        self.__save_graph_to_json(self.title_desc_graph, self.title_desc_graph_path)


    def __get_or_create_skill_node(self, graph: nx.MultiDiGraph, skill: str) -> str:
        skill_id = f"skl_{skill.lower().strip().replace(' ', '_')}"
        if not graph.has_node(skill_id):
            graph.add_node(skill_id, type="Skill", name=skill)
        return skill_id

    def __get_or_create_loc_node(self, graph: nx.MultiDiGraph, loc: str) -> str:
        loc_id = f"loc_{loc.lower().strip().replace(' ', '_')}"
        if not graph.has_node(loc_id):
            graph.add_node(loc_id, type="Location", name=loc)
        return loc_id

    def __save_graph_to_json(self, graph, path):
        json_graph = nx.node_link_data(graph)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(json_graph, f, ensure_ascii=False, indent=4)

    def load_graphs(self):
        if not os.path.exists(self.title_graph_path):
            raise FileNotFoundError(f"File not found: {self.title_graph_path}")
        if not os.path.exists(self.title_desc_graph_path):
            raise FileNotFoundError(f"File not found: {self.title_desc_graph_path}")

        with open(self.title_graph_path, "r") as f:
            self.title_graph = nx.node_link_graph(json.load(f), edges="links", create_using=nx.MultiDiGraph)

        with open(self.title_desc_graph_path, "r") as f:
            self.title_desc_graph = nx.node_link_graph(json.load(f), edges="links", create_using=nx.MultiDiGraph)


    # ai generated
    def plot_graph(self, graph):
        title = "Graph Visualization"
        plt.figure(figsize=(12, 8))
        plt.title(title, fontsize=14, fontweight='bold')

        # 1. Layout berechnen (spring-layout sorgt für eine organische Verteilung)
        pos = nx.spring_layout(graph, k=0.5, seed=42)

        # 2. Knoten nach Typen farblich trennen
        color_map = []
        labels = {}

        for node, data in graph.nodes(data=True):
            node_type = data.get("type", "Unknown")

            if node_type == "Activity":
                color_map.append("#3498db")  # Blau für Stellenanzeigen
                # Kürzen des Titels/Textes für die Beschriftung, damit es lesbar bleibt
                labels[node] = data.get("text", node)[:15] + "..."

            elif node_type == "Location":
                color_map.append("#e74c3c")  # Rot für Standorte
                labels[node] = data.get("name", node)

            elif node_type == "Skill":
                color_map.append("#2ecc71")  # Grün für Soft Skills
                labels[node] = data.get("name", node)

            else:
                color_map.append("#95a5a6")  # Grau für Unbekanntes
                labels[node] = node

        # 3. Kanten-Beschriftungen sammeln (z.B. "LOCATED_IN", "REQUIRES")
        edge_labels = {
            (u, v): data.get("relationship", "")
            for u, v, data in graph.edges(data=True)
        }

        # 4. Graphen zeichnen
        # Knoten zeichnen
        nx.draw_networkx_nodes(graph, pos, node_color=color_map, node_size=800, alpha=0.9)

        # Kanten zeichnen
        nx.draw_networkx_edges(graph, pos, arrowstyle="->", arrowsize=15, edge_color="#bdc3c7", width=1.5)

        # Beschriftungen der Knoten zeichnen
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=9, font_weight="bold")

        # Beschriftungen der Kanten zeichnen (optional, kann bei großen Graphen unübersichtlich werden)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=7, font_color="#7f8c8d")

        # 5. Legende manuell hinzufügen
        # (Erstellt kleine Dummy-Punkte für die Legende rechts unten)
        plt.scatter([], [], c="#3498db", label="Offering (Stelle)")
        plt.scatter([], [], c="#e74c3c", label="Location (Ort)")
        plt.scatter([], [], c="#2ecc71", label="Soft Skill")
        plt.legend(loc="lower right", scatterpoints=1, frameon=True)

        plt.axis("off")  # Achsen ausblenden
        plt.tight_layout()
        plt.show()