"""
Graph visualization module for lineage data using NetworkX and Plotly
"""

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Optional
import math

from ..models.lineage_models import LineageGraph, TableType


class LineageGraphVisualizer:
    """Create interactive visualizations of data lineage graphs"""
    
    def __init__(self):
        self.color_map = {
            TableType.SOURCE: '#27AE60',      # Modern Green
            TableType.INTERMEDIATE: '#3498DB',  # Modern Blue  
            TableType.TARGET: '#E74C3C'       # Modern Red
        }
        
        self.node_size_map = {
            TableType.SOURCE: 60,
            TableType.INTERMEDIATE: 60,
            TableType.TARGET: 60
        }
    
    def create_networkx_graph(self, lineage_graph: LineageGraph) -> nx.DiGraph:
        """Convert LineageGraph to NetworkX directed graph"""
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for table_name, table_info in lineage_graph.tables.items():
            G.add_node(
                table_name,
                table_type=table_info.table_type.value,
                color=self.color_map[table_info.table_type],
                size=self.node_size_map[table_info.table_type],
                columns=len(table_info.columns),
                schema=table_info.schema_name or "default"
            )
        
        # Add edges
        for table_name, table_info in lineage_graph.tables.items():
            for upstream_table in table_info.upstream_tables:
                if upstream_table in lineage_graph.tables:
                    G.add_edge(upstream_table, table_name)
        
        return G
    
    def create_plotly_visualization(self, lineage_graph: LineageGraph, 
                                  layout_algorithm: str = "spring") -> go.Figure:
        """Create interactive Plotly visualization of lineage graph"""
        G = self.create_networkx_graph(lineage_graph)
        
        if not G.nodes():
            return self._create_empty_plot()
        
        # Calculate layout
        pos = self._calculate_layout(G, layout_algorithm)
        
        # Extract node information
        node_trace = self._create_node_trace(G, pos)
        edge_trace = self._create_edge_trace(G, pos)
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=self._create_layout()
        )
        
        return fig
    
    def _calculate_layout(self, G: nx.DiGraph, algorithm: str) -> Dict[str, Tuple[float, float]]:
        """Calculate node positions using various layout algorithms"""
        if algorithm == "hierarchical":
            return self._hierarchical_layout(G)
        elif algorithm == "circular":
            return nx.circular_layout(G)
        elif algorithm == "kamada_kawai":
            return nx.kamada_kawai_layout(G) if len(G.nodes()) > 1 else nx.spring_layout(G)
        else:  # default spring layout with systematic positioning
            # Use a more systematic spring layout
            pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
            
            # Try to make it more hierarchical by adjusting y-coordinates
            if len(G.nodes()) > 1:
                # Group nodes by their role (source, intermediate, target)
                source_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
                target_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
                intermediate_nodes = [n for n in G.nodes() if n not in source_nodes and n not in target_nodes]
                
                # Adjust y-coordinates to create layers
                for node in source_nodes:
                    if node in pos:
                        pos[node] = (pos[node][0], pos[node][1] + 0.5)
                
                for node in target_nodes:
                    if node in pos:
                        pos[node] = (pos[node][0], pos[node][1] - 0.5)
            
            return pos
    
    def _hierarchical_layout(self, G: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Create systematic hierarchical layout like professional pipeline diagrams"""
        try:
            # Identify layers based on longest path from sources
            source_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
            if not source_nodes:
                return nx.spring_layout(G)
            
            # BFS to assign layers (top-down approach)
            layer_assignments = {}
            for source in source_nodes:
                layer_assignments[source] = 0
            
            queue = source_nodes.copy()
            while queue:
                current = queue.pop(0)
                current_layer = layer_assignments[current]
                
                for successor in G.successors(current):
                    new_layer = current_layer + 1
                    if successor not in layer_assignments or layer_assignments[successor] < new_layer:
                        layer_assignments[successor] = new_layer
                        if successor not in queue:
                            queue.append(successor)
            
            # Group nodes by layer
            layers = {}
            max_layer = max(layer_assignments.values()) if layer_assignments else 0
            
            for node, layer in layer_assignments.items():
                if layer not in layers:
                    layers[layer] = []
                layers[layer].append(node)
            
            # Create systematic positions
            pos = {}
            layer_height = 2.0  # Increased vertical spacing between layers
            
            for layer_num in range(max_layer + 1):
                if layer_num in layers:
                    nodes_in_layer = layers[layer_num]
                    num_nodes = len(nodes_in_layer)
                    
                    # Calculate horizontal positions for even spacing
                    if num_nodes == 1:
                        x_positions = [0]
                    else:
                        # Spread nodes evenly across horizontal space with more spacing
                        width = min(4.0, num_nodes * 0.8)  # Dynamic width based on number of nodes
                        spacing = width / max(1, num_nodes - 1) if num_nodes > 1 else 0
                        start_x = -width / 2
                        x_positions = [start_x + i * spacing for i in range(num_nodes)]
                    
                    # Assign positions
                    for i, node in enumerate(sorted(nodes_in_layer)):
                        x_pos = x_positions[i]
                        y_pos = max_layer - layer_num  # Top-down (sources at top)
                        pos[node] = (x_pos, y_pos * layer_height)
            
            return pos
            
        except Exception:
            return nx.spring_layout(G)
    
    def _create_display_text(self, table_name: str) -> str:
        """Create readable display text for nodes"""
        # Split long table names and create multi-line text
        if len(table_name) > 12:
            # Common prefixes to abbreviate
            if table_name.startswith('raw_'):
                abbreviated = table_name[4:]  # Remove 'raw_' prefix
            elif table_name.startswith('staging_'):
                abbreviated = 'stg_' + table_name[8:]  # Replace 'staging_' with 'stg_'
            else:
                abbreviated = table_name
            
            # If still too long, split into lines
            if len(abbreviated) > 12:
                words = abbreviated.replace('_', ' ').split()
                if len(words) > 1:
                    mid = len(words) // 2
                    line1 = ' '.join(words[:mid])
                    line2 = ' '.join(words[mid:])
                    return f"{line1}<br>{line2}"
                else:
                    # Single long word, split at underscore or middle
                    if '_' in abbreviated:
                        parts = abbreviated.split('_', 1)
                        return f"{parts[0]}<br>{parts[1]}"
                    else:
                        mid = len(abbreviated) // 2
                        return f"{abbreviated[:mid]}<br>{abbreviated[mid:]}"
            return abbreviated
        return table_name
    
    def _create_node_trace(self, G: nx.DiGraph, pos: Dict) -> go.Scatter:
        """Create node trace for Plotly"""
        node_x, node_y = [], []
        node_text, node_color, node_size = [], [], []
        hover_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_info = G.nodes[node]
            
            # Create more readable node text
            display_text = self._create_display_text(node)
            node_text.append(display_text)
            node_color.append(node_info['color'])
            node_size.append(node_info['size'])
            
            # Create hover text
            hover_info = f"""
            <b>{node}</b><br>
            Type: {node_info['table_type']}<br>
            Schema: {node_info['schema']}<br>
            Columns: {node_info['columns']}<br>
            Connections: {G.degree(node)}
            """
            hover_text.append(hover_info)
        
        return go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            textfont=dict(size=9, color="white", family="Arial Bold"),
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_text,
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color="#ffffff"),
                opacity=0.95,
                symbol="square",  # Rectangular nodes
                sizemode="area"  # Better sizing for rectangles
            ),
            name="Tables"
        )
    
    def _create_edge_trace(self, G: nx.DiGraph, pos: Dict) -> go.Scatter:
        """Create edge trace for Plotly"""
        edge_x, edge_y = [], []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        return go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2.5, color='#7f8c8d', dash='solid'),
            hoverinfo='none',
            mode='lines',
            name="Dependencies",
            opacity=0.7
        )
    
    def _create_layout(self) -> go.Layout:
        """Create Plotly layout configuration"""
        return go.Layout(
            title=dict(
                text="📊 Data Lineage Flow",
                x=0.5,
                font=dict(size=24, family="Arial Black", color="#2c3e50")
            ),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=60, l=20, r=20, t=60),
            height=600,
            width=None,
            annotations=[
                dict(
                    text="🟢 Source Tables  🔵 Intermediate Tables  🔴 Target Tables",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.08,
                    xanchor='center', yanchor='top',
                    font=dict(size=14, family="Arial", color="#34495e")
                )
            ],
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-3, 3]  # Wider range for better node spacing
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False,
                range=[-2, 8]  # Taller range for hierarchical layout
            ),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='#ffffff',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            )
        )
    
    def _create_empty_plot(self) -> go.Figure:
        """Create empty plot when no data is available"""
        fig = go.Figure()
        fig.add_annotation(
            text="No lineage data available.<br>Please upload SQL files to analyze.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def create_summary_stats(self, lineage_graph: LineageGraph) -> Dict:
        """Create summary statistics for the lineage graph"""
        G = self.create_networkx_graph(lineage_graph)
        
        stats = {
            "total_tables": len(lineage_graph.tables),
            "source_tables": len(lineage_graph.source_tables),
            "target_tables": len(lineage_graph.target_tables),
            "intermediate_tables": len(lineage_graph.tables) - len(lineage_graph.source_tables) - len(lineage_graph.target_tables),
            "total_connections": G.number_of_edges(),
            "max_depth": 0,
            "complexity_score": 0
        }
        
        if G.nodes():
            try:
                # Calculate maximum depth
                source_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
                if source_nodes:
                    max_depth = 0
                    for source in source_nodes:
                        try:
                            paths = nx.single_source_shortest_path_length(G, source)
                            max_depth = max(max_depth, max(paths.values()) if paths else 0)
                        except Exception:
                            pass
                    stats["max_depth"] = max_depth
                
                # Calculate complexity score (simple heuristic)
                stats["complexity_score"] = min(100, (stats["total_connections"] * 10) + (stats["max_depth"] * 5))
                
            except Exception:
                pass
        
        return stats
