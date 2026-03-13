import os
import json
import networkx as nx

class CitationGraphBuilder:
    def __init__(self):
        self.embeddings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
        self.graph_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'graph', 'citation_graph.json')
        
    def build_frontend_graph(self):
        """
        Loads the citation graph and paper metadata, returning a JSON-friendly 
        nodes/edges structure for React Flow.
        """
        nodes_res = []
        edges_res = []
        
        try:
            with open(self.graph_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
        except Exception as e:
            print(f"Graph loader error: {e}")
            return {"nodes": [], "edges": []}
            
        try:
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                embedded_data = json.load(f)
        except Exception as e:
            embedded_data = []
            
        # Map IDs to titles/clusters
        metadata_map = {}
        for paper in embedded_data:
            pid = paper.get("id")
            if pid:
                metadata_map[pid] = {
                    "title": paper.get("title", ""),
                    "topic_cluster": "Unclustered"  # We could re-cluster or compute it live, but leaving simple for now
                }
                
        # We need the nodes actually existing in the graph
        links = graph_data.get("links", [])
        
        added_nodes = set()
        
        # We will parse the D3 formatted links into React Flow formatted elements
        for i, link in enumerate(links):
            source = str(link.get("source"))
            target = str(link.get("target"))
            
            edges_res.append({
                "id": f"e-{source}-{target}-{i}",
                "source": source,
                "target": target,
                "type": "smoothstep"
            })
            
            for node_id in [source, target]:
                if node_id not in added_nodes:
                    added_nodes.add(node_id)
                    title = metadata_map.get(node_id, {}).get("title", f"Paper {node_id}")
                    
                    nodes_res.append({
                        "id": node_id,
                        "data": {
                            "label": title[:30] + "..." if len(title) > 30 else title,
                            "full_title": title
                        },
                        "position": {"x": 0, "y": 0} # Let UI engine layout forces handle this
                    })
                    
        return {
            "nodes": nodes_res,
            "edges": edges_res
        }
