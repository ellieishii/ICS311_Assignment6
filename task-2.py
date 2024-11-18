import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

# User and Post classes as previously discussed
class Post:
    def __init__(self, post_id, user, content, created_at):
        self.post_id = post_id
        self.user = user
        self.content = content
        self.created_at = created_at
        self.views = []  # List of users who have viewed the post
        self.comments = []  # List of Comment objects

    def add_view(self, user):
        self.views.append(user)

    def add_comment(self, comment):
        self.comments.append(comment)

    def get_view_count(self):
        return len(self.views)

    def get_comment_count(self):
        return len(self.comments)


class Comment:
    def __init__(self, comment_id, user, content, created_at):
        self.comment_id = comment_id
        self.user = user
        self.content = content
        self.created_at = created_at


class User:
    def __init__(self, username, real_name, age, gender, location):
        self.username = username
        self.real_name = real_name
        self.age = age
        self.gender = gender
        self.location = location
        self.connections = []  # List of connected users
        self.posts = []  # List of posts authored by the user
        self.comments = []  # List of comments made by the user
        self.views = []  # List of posts viewed by the user

    def add_connection(self, user):
        self.connections.append(user)

    def add_post(self, post):
        self.posts.append(post)

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_view(self, post):
        self.views.append(post)

    def get_post_count(self):
        return len(self.posts)

    def get_comment_count(self):
        return len(self.comments)

    def get_view_count(self):
        return len(self.views)

# Function to identify interesting users
def identify_interesting_users(users, min_posts=None, max_posts=None, min_comments=None, max_comments=None, gender=None):
    interesting_users = []

    for user in users.values():
        if (min_posts is not None and user.get_post_count() < min_posts) or \
           (max_posts is not None and user.get_post_count() > max_posts) or \
           (min_comments is not None and user.get_comment_count() < min_comments) or \
           (max_comments is not None and user.get_comment_count() > max_comments) or \
           (gender is not None and user.gender != gender):
            continue
        interesting_users.append(user)
    
    return interesting_users

# BFS algorithm to traverse the graph and find connected components
def bfs(graph, start_node):
    visited = set()
    queue = deque([start_node])
    visited.add(start_node)
    connected_component = []

    while queue:
        node = queue.popleft()
        connected_component.append(node)

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return connected_component

# Function to create the graph from users and posts
def create_graph(users, posts, interesting_users=None):
    G = nx.Graph()

    # Add nodes for users and assign colors based on whether they are interesting
    for user in users.values():
        color = 'red' if user in interesting_users else 'blue'
        G.add_node(user.username, type='user', color=color, label=user.real_name)  # Store real_name for label

    # Add nodes for posts and assign a default color (e.g., 'gray')
    for post in posts:
        G.add_node(post.post_id, type='post', color='gray', label=str(post.post_id))  # Assign post_id as label

    # Add edges for user connections (e.g., follows)
    for user in users.values():
        for connection in user.connections:
            G.add_edge(user.username, connection.username)

    # Add edges for user-authored posts
    for post in posts:
        G.add_edge(post.user.username, post.post_id)

    # Add edges for user views (viewed posts)
    for post in posts:
        for viewer in post.views:
            G.add_edge(viewer.username, post.post_id)

    return G

# Visualization function for the graph
def visualize_graph(G):
    pos = nx.spring_layout(G, k=0.5, iterations=50)  # Using spring layout with better node spacing
    colors = [G.nodes[node]['color'] for node in G.nodes]  # Get the color for each node

    # Labels for users and posts (user names for users, post IDs for posts)
    labels = {}
    for node in G.nodes:
        if G.nodes[node]['type'] == 'user':
            labels[node] = G.nodes[node]['label']  # User real_name as label
        elif G.nodes[node]['type'] == 'post':
            labels[node] = str(G.nodes[node]['label'])  # Post ID as label

    # Increase node size for better visibility
    plt.figure(figsize=(12, 12))
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=1000, alpha=0.7)  # Larger nodes

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.5)

    # Draw labels (both for users and posts)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_color="black", font_weight="bold")

    # Set title and remove axis
    plt.title("Social Media Network Visualization")
    plt.axis("off")
    plt.show()

# Example usage of the code
if __name__ == "__main__":
    # Creating users
    users = {
        "user1": User("user1", "Alice", 30, "F", "New York"),
        "user2": User("user2", "Bob", 25, "M", "Los Angeles"),
        "user3": User("user3", "Charlie", 35, "M", "Chicago"),
        "user4": User("user4", "David", 28, "M", "San Francisco"),
        "user5": User("user5", "Eve", 22, "F", "Miami")
    }

    # Creating posts
    posts = [
        Post(1, users["user1"], "This is post 1", "2024-01-01"),
        Post(2, users["user2"], "This is post 2", "2024-01-02"),
        Post(3, users["user3"], "This is post 3", "2024-01-03"),
        Post(4, users["user4"], "This is post 4", "2024-01-04"),
        Post(5, users["user5"], "This is post 5", "2024-01-05")
    ]

    # Adding views and comments
    posts[0].add_view(users["user2"])
    posts[0].add_comment(Comment(1, users["user2"], "Nice post!", "2024-01-01"))
    posts[2].add_view(users["user4"])
    posts[2].add_comment(Comment(2, users["user4"], "Interesting thought!", "2024-01-02"))
    posts[3].add_view(users["user1"])

    # Adding connections (e.g., following)
    users["user1"].add_connection(users["user2"])
    users["user2"].add_connection(users["user3"])
    users["user4"].add_connection(users["user5"])

    # Identifying interesting users (e.g., users with more than 1 post)
    interesting_users = identify_interesting_users(users, min_posts=1)

    # Create and visualize the graph
    G = create_graph(users, posts, interesting_users)
    visualize_graph(G)

    # Perform BFS to find connected components
    start_node = "user1"  # Starting from "user1"
    connected_component = bfs(G, start_node)
    print(f"Connected component starting from {start_node}: {connected_component}")
