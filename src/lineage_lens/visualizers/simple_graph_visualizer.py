"""
Simple, reliable graph visualizer using basic HTML/CSS/JS
Fallback when Cytoscape.js fails to load
"""

import json
from typing import Dict, List, Any
import streamlit.components.v1 as components
from ..models.lineage_models import LineageGraph, TableType
import math


class SimpleGraphVisualizer:
    """Simple, reliable graph visualizer using basic web technologies"""
    
    def __init__(self):
        # Airflow-inspired color scheme
        self.color_map = {
            TableType.SOURCE: '#017CEE',      # Airflow blue for sources
            TableType.INTERMEDIATE: '#8E44AD', # Purple for intermediate processing
            TableType.TARGET: '#E67E22'       # Orange for final outputs
        }
    
    def render_in_streamlit(self, lineage_graph: LineageGraph, height: int = 600):
        """Render graph visualization in Streamlit using basic HTML/SVG"""
        
        # Calculate positions using a simple force-directed layout
        positions = self._calculate_positions(lineage_graph)
        
        # Create HTML with SVG visualization
        html_content = self._create_svg_visualization(lineage_graph, positions, height)
        
        # Render in Streamlit
        components.html(html_content, height=height + 50)
        
        # Return statistics
        stats = self._calculate_stats(lineage_graph)
        return stats
    
    def _calculate_positions(self, lineage_graph: LineageGraph) -> Dict[str, Dict[str, float]]:
        """Calculate node positions using Airflow DAG-style hierarchical layout"""
        positions = {}
        tables = list(lineage_graph.tables.items())
        
        if not tables:
            return positions
        
        # Build dependency levels for true hierarchical layout
        levels = self._build_dependency_levels(lineage_graph)
        
        # Layout parameters - optimized to prevent AxiosError 400
        width = 1000   # Conservative width to reduce SVG payload
        height = 700   # Conservative height to avoid 400 errors  
        level_height = height / (len(levels) + 1)
        min_level_height = 120  # Compact spacing to reduce payload size
        level_height = max(level_height, min_level_height)
        
        # Position nodes level by level (like Airflow DAG)
        for level_idx, level_tables in enumerate(levels):
            y_position = level_height * (level_idx + 1)
            
            # Calculate spacing for this level
            if len(level_tables) == 1:
                # Single node - center it
                positions[level_tables[0]] = {
                    'x': width / 2,
                    'y': y_position
                }
            else:
                # Multiple nodes - distribute evenly with ultra-generous spacing
                total_width = width * 0.85  # Use 85% of width for more margins
                margin = width * 0.075  # 7.5% margin on each side for breathing room
                
                if len(level_tables) <= 2:  # Only 2 nodes per row for maximum spacing
                    # Standard horizontal distribution with maximum spacing
                    node_spacing = total_width / (len(level_tables) + 1)
                    for i, table in enumerate(level_tables):
                        positions[table] = {
                            'x': margin + node_spacing * (i + 1),
                            'y': y_position
                        }
                else:
                    # For many nodes, use compact rows to prevent 400 errors
                    per_row = 3  # Balanced number for readability vs size
                    row_count = (len(level_tables) + per_row - 1) // per_row
                    row_height = level_height * 0.5 / row_count  # Maximum space between rows
                    
                    for i, table in enumerate(level_tables):
                        row = i // per_row
                        col = i % per_row
                        nodes_in_row = min(per_row, len(level_tables) - row * per_row)
                        
                        # Balanced spacing to prevent large SVG payloads
                        row_spacing = max(250, total_width / (nodes_in_row + 1))  # Balanced 250px spacing
                        positions[table] = {
                            'x': margin + row_spacing * (col + 1),
                            'y': y_position - (level_height * 0.3) + (row * row_height)
                        }
        
        return positions
    
    def _build_dependency_levels(self, lineage_graph: LineageGraph) -> List[List[str]]:
        """Build hierarchical levels based on dependencies (like Airflow DAG levels)"""
        levels = []
        processed = set()
        remaining_tables = set(lineage_graph.tables.keys())
        
        while remaining_tables:
            current_level = []
            
            # Find tables with no unprocessed dependencies
            for table_name in list(remaining_tables):
                table = lineage_graph.tables[table_name]
                dependencies_satisfied = all(
                    dep in processed or dep not in lineage_graph.tables
                    for dep in table.upstream_tables
                )
                
                if dependencies_satisfied:
                    current_level.append(table_name)
            
            # If no progress can be made, add remaining tables to avoid infinite loop
            if not current_level:
                current_level = list(remaining_tables)
            
            # Sort tables in level for consistent positioning
            current_level.sort()
            levels.append(current_level)
            
            # Mark these tables as processed
            for table in current_level:
                processed.add(table)
                remaining_tables.discard(table)
        
        return levels
    
    def _calculate_node_width(self, table_name: str) -> int:
        """Calculate dynamic node width based on text length"""
        min_width = 120
        char_width = 8  # Approximate width per character
        calculated_width = max(min_width, len(table_name) * char_width + 20)  # +20 for padding
        return min(calculated_width, 250)  # Max width of 250px
    
    def _create_svg_visualization(self, lineage_graph: LineageGraph, positions: Dict, height: int) -> str:
        """Create SVG-based visualization"""
        
        width = 1000  # Match the layout width
        svg_height = height - 50  # Less reduction to use more space
        
        # Start HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Lineage Lens - Simple Graph</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .controls {{
                    margin-bottom: 15px;
                    text-align: center;
                }}
                .control-btn {{
                    background: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    margin: 0 5px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 12px;
                }}
                .control-btn:hover {{
                    background: #2980b9;
                }}
                .stats {{
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 15px;
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                }}
                .stat-item {{
                    text-align: center;
                    margin: 5px;
                }}
                .stat-number {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .stat-label {{
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .legend {{
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-bottom: 15px;
                    flex-wrap: wrap;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    font-size: 12px;
                }}
                .legend-color {{
                    width: 16px;
                    height: 16px;
                    border-radius: 3px;
                    margin-right: 6px;
                }}
                .node {{
                    cursor: pointer;
                    transition: all 0.3s ease;
                }}
                .node {{
                    position: relative;
                    z-index: 10;
                }}
                .node:hover {{
                    filter: brightness(1.1);
                    transform: scale(1.05);
                    z-index: 20;
                }}
                .edge {{
                    transition: all 0.3s ease;
                    z-index: 1;
                }}
                .edge:hover {{
                    stroke: #495057 !important;
                    stroke-width: 2.4 !important;
                    opacity: 0.9 !important;
                    cursor: pointer;
                    z-index: 5;
                }}
                /* Ensure SVG elements are properly layered */
                svg {{
                    overflow: visible;
                }}
                svg g.node {{
                    z-index: 10;
                }}
                svg path, svg line {{
                    z-index: 1;
                }}
                .tooltip {{
                    position: absolute;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    pointer-events: none;
                    z-index: 1000;
                    display: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h3 style="text-align: center; margin: 0 0 15px 0; color: #2c3e50;">📊 Data Lineage Graph</h3>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {self.color_map[TableType.SOURCE]};"></div>
                        <span>Source Tables</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {self.color_map[TableType.INTERMEDIATE]};"></div>
                        <span>Intermediate Tables</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {self.color_map[TableType.TARGET]};"></div>
                        <span>Target Tables</span>
                    </div>
                </div>
                
                <div class="controls">
                    <button class="control-btn" onclick="resetView()">🔄 Reset View</button>
                    <button class="control-btn" onclick="fitToView()">📏 Fit to View</button>
                    <button class="control-btn" onclick="exportData()">💾 Export Data</button>
                </div>
                
                <svg id="graph" width="100%" height="{svg_height}" viewBox="0 0 {width} {svg_height}" style="border: 1px solid #e1e5e9; border-radius: 8px; background: #f8f9fa; max-width: 100%;">
                    <!-- Edges (drawn first, but with proper z-index) -->
        """
        
        # Add edges with improved arrow positioning
        for table_name, table in lineage_graph.tables.items():
            if table_name in positions:
                target_pos = positions[table_name]
                for upstream in table.upstream_tables:
                    if upstream in positions:
                        source_pos = positions[upstream]
                        
                        # Calculate connection points on node edges (Airflow-style)
                        # Use dynamic node widths
                        source_node_width = self._calculate_node_width(upstream) // 2
                        target_node_width = self._calculate_node_width(table_name) // 2
                        node_height = 20  # half height
                        
                        # Calculate angle to determine best connection points
                        dx = target_pos['x'] - source_pos['x']
                        dy = target_pos['y'] - source_pos['y']
                        
                        # Source connection point (bottom of source node)
                        if abs(dx) < source_node_width:  # Directly above/below
                            source_x = source_pos['x']
                            source_y = source_pos['y'] + node_height
                        else:  # Side connection
                            source_x = source_pos['x'] + (source_node_width if dx > 0 else -source_node_width)
                            source_y = source_pos['y']
                        
                        # Target connection point (top of target node)
                        if abs(dx) < target_node_width:  # Directly above/below
                            target_x = target_pos['x']
                            target_y = target_pos['y'] - node_height
                        else:  # Side connection
                            target_x = target_pos['x'] + (-target_node_width if dx > 0 else target_node_width)
                            target_y = target_pos['y']
                        
                        # Use curved paths for better visual flow and avoid overlapping nodes
                        avg_node_width = (source_node_width + target_node_width) / 2
                        if abs(dx) > avg_node_width * 1.5:  # Use curved path for longer distances
                            # Calculate control points for smooth curve that avoids nodes
                            mid_x = (source_x + target_x) / 2
                            mid_y = (source_y + target_y) / 2
                            control_offset = min(60, abs(dy) / 2.5)
                            
                            # Adjust curve to avoid going through intermediate nodes
                            if dy > 0:  # Downward flow
                                curve_y = mid_y - control_offset
                            else:  # Upward flow (rare)
                                curve_y = mid_y + control_offset
                            
                            html += f"""
                    <path d="M {source_x},{source_y} Q {mid_x},{curve_y} {target_x},{target_y}" 
                          stroke="#6c757d" stroke-width="2" class="edge" fill="none"
                          marker-end="url(#arrowhead)" opacity="0.8" style="z-index: 1;"/>
                            """
                        else:  # Use straight line for short distances
                            html += f"""
                    <line x1="{source_x}" y1="{source_y}" 
                          x2="{target_x}" y2="{target_y}" 
                          stroke="#6c757d" stroke-width="2" class="edge"
                          marker-end="url(#arrowhead)" opacity="0.8" style="z-index: 1;"/>
                            """
        
        # Add Airflow-style definitions (shadows, gradients, arrows)
        html += """
                    <defs>
                        <!-- Drop shadow filter for nodes -->
                        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                            <feDropShadow dx="2" dy="3" stdDeviation="3" flood-color="#00000040"/>
                        </filter>
                        
                        <!-- Professional arrow marker -->
                        <marker id="arrowhead" markerWidth="8" markerHeight="6" 
                                refX="7" refY="3" orient="auto" markerUnits="strokeWidth">
                            <polygon points="0 0, 8 3, 0 6" fill="#6c757d" stroke="none"/>
                        </marker>
                        
                        <!-- Gradient for edges -->
                        <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#6c757d;stop-opacity:0.7" />
                            <stop offset="100%" style="stop-color:#495057;stop-opacity:0.8" />
                        </linearGradient>
                    </defs>
                    
                    <!-- Nodes -->
        """
        
        # Add nodes
        for table_name, table in lineage_graph.tables.items():
            if table_name in positions:
                pos = positions[table_name]
                color = self.color_map[table.table_type]
                
                # Create display name (full name, no truncation)
                display_name = table_name
                
                # Create tooltip text
                tooltip_text = f"Table: {table_name}\\nType: {table.table_type.value.title()}"
                if table.upstream_tables:
                    tooltip_text += f"\\nUpstream: {', '.join(table.upstream_tables)}"
                if table.downstream_tables:
                    tooltip_text += f"\\nDownstream: {', '.join(table.downstream_tables)}"
                
                # Use the helper function for dynamic node width
                node_width = self._calculate_node_width(display_name)
                node_height = 40
                
                html += f"""
                    <g class="node" data-tooltip="{tooltip_text}" 
                       onmouseover="showTooltip(event, this)" onmouseout="hideTooltip()" style="z-index: 10;">
                        <!-- Airflow-style rounded rectangle with proper layering -->
                        <rect x="{pos['x'] - node_width//2}" y="{pos['y'] - node_height//2}" 
                              width="{node_width}" height="{node_height}" 
                              rx="12" ry="12" fill="{color}" 
                              stroke="#ffffff" stroke-width="3"
                              filter="url(#shadow)" style="z-index: 10;"/>
                        <!-- Text with better styling -->
                        <text x="{pos['x']}" y="{pos['y'] + 4}" text-anchor="middle" 
                              fill="white" font-size="12" font-weight="600" 
                              font-family="Arial, sans-serif" style="z-index: 11;">{display_name}</text>
                    </g>
                """
        
        # Close SVG and add JavaScript
        stats = self._calculate_stats(lineage_graph)
        html += f"""
                </svg>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">{stats['total_tables']}</div>
                        <div class="stat-label">Total Tables</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats['source_tables']}</div>
                        <div class="stat-label">Source Tables</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats['intermediate_tables']}</div>
                        <div class="stat-label">Intermediate</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats['target_tables']}</div>
                        <div class="stat-label">Target Tables</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{stats['total_relationships']}</div>
                        <div class="stat-label">Relationships</div>
                    </div>
                </div>
            </div>
            
            <div id="tooltip" class="tooltip"></div>
            
            <script>
                function showTooltip(event, element) {{
                    const tooltip = document.getElementById('tooltip');
                    const text = element.getAttribute('data-tooltip');
                    tooltip.innerHTML = text.replace(/\\\\n/g, '<br>');
                    tooltip.style.display = 'block';
                    tooltip.style.left = (event.pageX + 10) + 'px';
                    tooltip.style.top = (event.pageY - 10) + 'px';
                }}
                
                function hideTooltip() {{
                    document.getElementById('tooltip').style.display = 'none';
                }}
                
                function resetView() {{
                    const svg = document.getElementById('graph');
                    svg.setAttribute('viewBox', '0 0 {width} {svg_height}');
                }}
                
                function fitToView() {{
                    // Calculate the bounding box of all nodes
                    const svg = document.getElementById('graph');
                    const nodes = document.querySelectorAll('.node rect');
                    
                    if (nodes.length === 0) return;
                    
                    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                    
                    nodes.forEach(node => {{
                        const x = parseFloat(node.getAttribute('x'));
                        const y = parseFloat(node.getAttribute('y'));
                        const width = parseFloat(node.getAttribute('width'));
                        const height = parseFloat(node.getAttribute('height'));
                        
                        minX = Math.min(minX, x);
                        minY = Math.min(minY, y);
                        maxX = Math.max(maxX, x + width);
                        maxY = Math.max(maxY, y + height);
                    }});
                    
                    // Add padding
                    const padding = 50;
                    minX -= padding;
                    minY -= padding;
                    maxX += padding;
                    maxY += padding;
                    
                    const contentWidth = maxX - minX;
                    const contentHeight = maxY - minY;
                    
                    // Update viewBox to fit content
                    svg.setAttribute('viewBox', `${{minX}} ${{minY}} ${{contentWidth}} ${{contentHeight}}`);
                }}
                
                function exportData() {{
                    const data = {json.dumps({
                        'tables': {name: {
                            'type': table.table_type.value,
                            'upstream': list(table.upstream_tables),
                            'downstream': list(table.downstream_tables)
                        } for name, table in lineage_graph.tables.items()},
                        'stats': stats
                    })};
                    
                    const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'lineage_data.json';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }}
                
                // Add some basic interactivity and auto-fit on load
                document.addEventListener('DOMContentLoaded', function() {{
                    // Auto-fit the view after a short delay to ensure everything is rendered
                    setTimeout(fitToView, 100);
                }});
                
                document.querySelectorAll('.node').forEach(node => {{
                    node.addEventListener('click', function() {{
                        // Highlight connected nodes
                        const tableName = this.querySelector('text').textContent;
                        console.log('Clicked table:', tableName);
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return html
    
    def _calculate_stats(self, lineage_graph: LineageGraph) -> Dict[str, int]:
        """Calculate graph statistics"""
        total_tables = len(lineage_graph.tables)
        source_tables = sum(1 for t in lineage_graph.tables.values() if t.table_type == TableType.SOURCE)
        target_tables = sum(1 for t in lineage_graph.tables.values() if t.table_type == TableType.TARGET)
        intermediate_tables = total_tables - source_tables - target_tables
        
        total_relationships = sum(len(t.upstream_tables) for t in lineage_graph.tables.values())
        
        return {
            'total_tables': total_tables,
            'source_tables': source_tables,
            'intermediate_tables': intermediate_tables,
            'target_tables': target_tables,
            'total_relationships': total_relationships
        }
