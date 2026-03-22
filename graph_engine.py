from streamlit_agraph import agraph, Node, Edge, Config


def build_knowledge_graph(graph_data, candidate_name, target_role):
    nodes = []
    edges = []

    # --- 1. CORE ENTITY NODES ---
    # User Node (Center, Image Avatar)
    nodes.append(Node(id="User", label=candidate_name, size=55, color="#6C63FF",
                      shape="circularImage", image="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                      title="You"))

    # Target Role Node (The Goal)
    nodes.append(Node(id="Target", label=target_role, size=45, color="#ECC94B",
                      shape="star", title="Your Target Role"))
    edges.append(Edge(source="User", target="Target", label="Applying for", color="#ECC94B", dashes=True))

    # --- 2. CATEGORY NODES ---
    nodes.append(Node(id="MatchedSkills", label="✅ Acquired Skills", size=35, color="#38B2AC", shape="dot"))
    nodes.append(Node(id="MissingSkills", label="⚠️ Missing Skills", size=35, color="#E53E3E", shape="dot"))
    nodes.append(Node(id="Experience", label="💼 Experience", size=35, color="#3182CE", shape="dot"))
    nodes.append(Node(id="Education", label="🎓 Education", size=35, color="#DD6B20", shape="dot"))

    # Connect Categories (Notice Missing Skills connects to the TARGET, not the User)
    edges.append(Edge(source="User", target="MatchedSkills", color="#38B2AC", label="has"))
    edges.append(Edge(source="Target", target="MissingSkills", color="#E53E3E", label="requires"))
    edges.append(Edge(source="User", target="Experience", color="#3182CE"))
    edges.append(Edge(source="User", target="Education", color="#DD6B20"))

    # --- 3. POPULATING DATA ---
    # Matched Skills (Green Boxes)
    for skill in graph_data.get("matched_skills", [])[:10]:
        nodes.append(Node(id=f"match_{skill}", label=skill, size=20, color="#81E6D9", shape="box",
                          title=f"Verified Skill: {skill}"))
        edges.append(Edge(source="MatchedSkills", target=f"match_{skill}", color="#81E6D9"))

    # Missing Skills (Red Dashed Boxes)
    for skill in graph_data.get("missing_skills", [])[:7]:
        nodes.append(
            Node(id=f"miss_{skill}", label=skill, size=20, color="#FEB2B2", shape="box", title=f"Gap to fill: {skill}"))
        edges.append(Edge(source="MissingSkills", target=f"miss_{skill}", color="#FEB2B2", dashes=True))

    # Experience (Nested: Category -> Job Title -> Company)
    for i, exp in enumerate(graph_data.get("experience", [])[:4]):
        title = exp.get("title", "Role")
        org = exp.get("organization", "Company")
        exp_id, org_id = f"exp_{i}", f"org_{i}"

        nodes.append(Node(id=exp_id, label=title, size=25, color="#63B3ED", shape="ellipse", title=title))
        nodes.append(Node(id=org_id, label=org, size=20, color="#A0AEC0", shape="box", title=org))

        edges.append(Edge(source="Experience", target=exp_id, color="#63B3ED"))
        edges.append(Edge(source=exp_id, target=org_id, color="#A0AEC0", label="at"))

    # Education (Nested: Category -> Degree -> Institution)
    for i, edu in enumerate(graph_data.get("education", [])[:3]):
        deg = edu.get("degree", "Degree")
        inst = edu.get("institution", "Institution")
        edu_id, inst_id = f"edu_{i}", f"inst_{i}"

        nodes.append(Node(id=edu_id, label=deg, size=25, color="#F6AD55", shape="ellipse", title=deg))
        nodes.append(Node(id=inst_id, label=inst, size=20, color="#A0AEC0", shape="box", title=inst))

        edges.append(Edge(source="Education", target=edu_id, color="#F6AD55"))
        edges.append(Edge(source=edu_id, target=inst_id, color="#A0AEC0", label="from"))

    # --- 4. ADVANCED VIS.JS PHYSICS ---
    config = Config(
        width="100%",
        height=750,
        directed=True,  # Shows arrows
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
        interaction={
            "hover": True,
            "navigationButtons": True,  # Adds Zoom in/out/pan UI buttons
            "zoomView": True
        },
        kwargs={
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -12000,  # Massive repulsion prevents ANY clumping
                    "centralGravity": 0.3,
                    "springLength": 200,
                    "springConstant": 0.04,
                    "damping": 0.09,
                    "avoidOverlap": 1.0
                }
            },
            "edges": {
                "smooth": {
                    "type": "continuous",
                    "forceDirection": "none"
                }
            }
        }
    )

    return agraph(nodes=nodes, edges=edges, config=config)