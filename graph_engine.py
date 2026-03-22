from streamlit_agraph import agraph, Node, Edge, Config


def build_knowledge_graph(graph_data, candidate_name):
    nodes = []
    edges = []

    # Central Node
    nodes.append(Node(id="User", label=candidate_name, size=400, color="#6C63FF"))

    # Categories
    nodes.append(Node(id="Skills", label="Skills", size=300, color="#FF6584"))
    nodes.append(Node(id="Experience", label="Experience", size=300, color="#38B2AC"))
    nodes.append(Node(id="Education", label="Education", size=300, color="#ED8936"))

    edges.append(Edge(source="User", target="Skills"))
    edges.append(Edge(source="User", target="Experience"))
    edges.append(Edge(source="User", target="Education"))

    # Add Skills
    for skill in graph_data.get("skills", [])[:10]:  # Limit to 10 for clean UI
        nodes.append(Node(id=skill, label=skill, size=150, color="#FFB6C1"))
        edges.append(Edge(source="Skills", target=skill))

    # Add Experience
    for exp in graph_data.get("experience", [])[:3]:
        nodes.append(Node(id=exp, label=exp, size=200, color="#81E6D9"))
        edges.append(Edge(source="Experience", target=exp))

    # Add Education
    for edu in graph_data.get("education", [])[:2]:
        nodes.append(Node(id=edu, label=edu, size=200, color="#FBD38D"))
        edges.append(Edge(source="Education", target=edu))

    config = Config(width=800,
                    height=500,
                    directed=True,
                    physics=True,
                    hierarchical=False)

    return agraph(nodes=nodes, edges=edges, config=config)