from typing import Dict, List, Any, Optional, Set
import logging
from collections import deque
import threading

class Graph:
    """A graph implementation supporting both directed and undirected graphs."""
    
    def __init__(self, directed: bool = False, max_vertices: Optional[int] = 10000):
        """
        Initialize the graph.
        
        Args:
            directed: Whether the graph is directed
            max_vertices: Maximum number of vertices allowed (None for unlimited)
        """
        self.graph: Dict[Any, List[Any]] = {}
        self.directed = directed
        self.max_vertices = max_vertices
        self._lock = threading.Lock()  # Thread safety
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Track graph properties
        self.vertex_count = 0
        self.edge_count = 0

    def _validate_vertex(self, vertex: Any) -> None:
        """Validate vertex data."""
        if vertex is None:
            raise ValueError("Vertex cannot be None")
        if not isinstance(vertex, (str, int, float)):
            raise TypeError("Vertex must be a string, integer, or float")
        
    def add_vertex(self, vertex: Any) -> bool:
        """Add a vertex to the graph if it doesn't exist."""
        try:
            self._validate_vertex(vertex)
            
            with self._lock:
                if self.max_vertices and self.vertex_count >= self.max_vertices:
                    raise ValueError(f"Maximum vertex limit ({self.max_vertices}) reached")
                
                if vertex not in self.graph:
                    self.graph[vertex] = []
                    self.vertex_count += 1
                    self.logger.debug(f"Added vertex: {vertex}")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding vertex: {str(e)}")
            raise

    def add_edge(self, src: Any, dest: Any) -> None:
        """Add an edge between two vertices."""
        try:
            self._validate_vertex(src)
            self._validate_vertex(dest)
            
            with self._lock:
                # Add vertices if they don't exist
                if src not in self.graph:
                    self.add_vertex(src)
                if dest not in self.graph:
                    self.add_vertex(dest)
                
                # Avoid duplicate edges
                if dest not in self.graph[src]:
                    self.graph[src].append(dest)
                    self.edge_count += 1
                    
                    if not self.directed and src != dest:  # Handle self-loops
                        if src not in self.graph[dest]:
                            self.graph[dest].append(src)
                
                self.logger.debug(f"Added edge: {src} -> {dest}")
                
        except Exception as e:
            self.logger.error(f"Error adding edge: {str(e)}")
            raise

    def remove_edge(self, src: Any, dest: Any) -> bool:
        """Remove an edge between two vertices."""
        try:
            with self._lock:
                if src in self.graph and dest in self.graph[src]:
                    self.graph[src].remove(dest)
                    self.edge_count -= 1
                    
                    if not self.directed and src != dest:
                        if dest in self.graph and src in self.graph[dest]:
                            self.graph[dest].remove(src)
                    
                    self.logger.debug(f"Removed edge: {src} -> {dest}")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing edge: {str(e)}")
            raise

    def remove_vertex(self, vertex: Any) -> bool:
        """Remove a vertex and all its edges."""
        try:
            with self._lock:
                if vertex in self.graph:
                    # Count edges to be removed
                    edges_count = len(self.graph[vertex])
                    
                    # Remove edges pointing to this vertex
                    for adj in list(self.graph):
                        if vertex in self.graph[adj]:
                            self.graph[adj].remove(vertex)
                            self.edge_count -= 1
                    
                    # Remove the vertex
                    del self.graph[vertex]
                    self.vertex_count -= 1
                    self.edge_count -= edges_count
                    
                    self.logger.debug(f"Removed vertex: {vertex}")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing vertex: {str(e)}")
            raise

    def get_adjacent_vertices(self, vertex: Any) -> List[Any]:
        """Get all vertices adjacent to the given vertex."""
        try:
            return self.graph.get(vertex, []).copy()  # Return a copy for safety
        except Exception as e:
            self.logger.error(f"Error getting adjacent vertices: {str(e)}")
            raise

    def has_path(self, start: Any, end: Any) -> bool:
        """Check if there's a path between start and end vertices using BFS."""
        if start not in self.graph or end not in self.graph:
            return False
            
        visited = set()
        queue = deque([start])
        
        while queue:
            vertex = queue.popleft()
            if vertex == end:
                return True
            
            if vertex not in visited:
                visited.add(vertex)
                queue.extend(v for v in self.graph[vertex] if v not in visited)
                
        return False

    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        return {
            "vertices": self.vertex_count,
            "edges": self.edge_count,
            "is_directed": self.directed
        }

    def __str__(self) -> str:
        """String representation of the graph."""
        return str(self.graph)
    
# Example usage with new features
try:
    # Create a graph with maximum 100 vertices
    g = Graph(directed=True, max_vertices=100)
    
    # Add vertices and edges
    g.add_vertex('A')
    g.add_vertex('B')
    g.add_edge('A', 'B')
    g.add_edge('B', 'C')  # Will automatically add vertex C
    
    # Check path existence
    print(g.has_path('A', 'C'))  # True
    
    # Get graph statistics
    print(g.get_stats())
    
except Exception as e:
    logging.error(f"Error in graph operations: {str(e)}")