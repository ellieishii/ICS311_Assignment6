import matplotlib.pyplot as plt
import networkx as nx
import random

# Initialize the graph (adjacency list)
graph = {
    'user1': [('viewed', 'post1'), ('commented', 'post2')],
    'user2': [('viewed', 'post1')],
    'user3': [('commented', 'post2')],
    'post1': [('authored', 'user1')],
    'post2': [('authored', 'user1')]
}

# Dummy data for posts (views and comments for each post)
posts = {
    'post1': {'views': ['user1', 'user2'], 'comments': ['user2']},
    'post2': {'views': ['user1', 'user3'], 'comments': ['user1', 'user3']}
}

# PageRank algorithm
def pagerank(graph, alpha=0.85, max_iter=100):
    pr = {node: 1.0 for node in graph}  # Initialize page ranks
    for _ in range(max_iter):
        new_pr = {}
        for node in graph:
            # For each node, calculate its new rank based on neighbors
            new_pr[node] = (1 - alpha) + alpha * sum(pr[neighbor] / len(graph[neighbor]) for neighbor in graph[node])
        pr = new_pr
    return pr

# Calculate the importance of posts based on views, comments, or a blend of both
def calculate_importance(posts, criterion='views'):
    importance = {}
    for post_id, post_data in posts.items():
        if criterion == 'views':
            importance[post_id] = len(post_data['views'])
        elif criterion == 'comments':
            importance[post_id] = len(post_data['comments'])
        else:  # Blended criterion (views + comments)
            importance[post_id] = len(post_data['views']) + len(post_data['comments'])
    return importance

# Create the graph using NetworkX (convert adjacency list into a graph)
G = nx.Graph()
for user_id, neighbors in graph.items():
    for rel_type, post_id in neighbors:
        if post_id not in graph:
            graph[post_id] = []  # Create post if it doesn't exist
        G.add_edge(user_id, post_id, relationship=rel_type)

# Compute the PageRank values for nodes
pr = pagerank(graph)

# Choose a criterion for importance (views, comments, or a blend)
criterion = 'views'  # You can change this to 'comments' or 'blend'
post_importance = calculate_importance(posts, criterion)

# Visualize the graph
node_colors = ['red' if pr[node] > 1.0 else 'blue' for node in G]
node_sizes = [100 * pr[node] for node in G]  # Scale node size based on PageRank

# Highlight important posts based on chosen criteria
post_threshold = 1  # Threshold for post importance (can be adjusted)
important_nodes = [node for node in G if node in posts and post_importance.get(node, 0) > post_threshold]
node_colors = [ 'green' if node in important_nodes else color for node, color in zip(G.nodes, node_colors)]
node_sizes = [ 150 if node in important_nodes else size for node, size in zip(G.nodes, node_sizes)]

# Layout the graph (spring layout is used for better spacing of nodes)
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=node_sizes, font_size=8)
plt.title(f"Social Media Network Graph - Importance by {criterion.capitalize()}")
plt.show()
