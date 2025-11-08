"""
Professional Cytoscape.js Graph Visualizer for Data Lineage
"""

import json
from typing import Dict, List, Any
import streamlit.components.v1 as components
from ..models.lineage_models import LineageGraph, TableType


class CytoscapeGraphVisualizer:
    """Professional graph visualizer using Cytoscape.js"""
    
    def __init__(self):
        self.color_map = {
            TableType.SOURCE: '#27AE60',      # Professional Green
            TableType.INTERMEDIATE: '#3498DB',  # Professional Blue  
            TableType.TARGET: '#E74C3C'       # Professional Red
        }
        
        self.node_styles = {
            TableType.SOURCE: {
                'shape': 'roundrectangle',
                'background-color': '#27AE60',
                'border-width': '3px',
                'border-color': '#229954',
                'width': '100px',
                'height': '60px'
            },
            TableType.INTERMEDIATE: {
                'shape': 'roundrectangle', 
                'background-color': '#3498DB',
                'border-width': '3px',
                'border-color': '#2E86AB',
                'width': '100px',
                'height': '60px'
            },
            TableType.TARGET: {
                'shape': 'roundrectangle',
                'background-color': '#E74C3C', 
                'border-width': '3px',
                'border-color': '#C0392B',
                'width': '100px',
                'height': '60px'
            }
        }
    
    def create_cytoscape_visualization(self, lineage_graph: LineageGraph, layout_algorithm: str = "dagre") -> str:
        """Create professional Cytoscape.js visualization"""
        
        # Convert lineage graph to Cytoscape format
        elements = self._convert_to_cytoscape_elements(lineage_graph)
        
        # Generate the complete HTML with Cytoscape.js
        html_content = self._generate_cytoscape_html(elements, layout_algorithm)
        
        return html_content
    
    def _convert_to_cytoscape_elements(self, lineage_graph: LineageGraph) -> List[Dict]:
        """Convert LineageGraph to Cytoscape.js elements format"""
        elements = []
        
        # Add nodes
        for table_name, table_info in lineage_graph.tables.items():
            # Create abbreviated display name
            display_name = self._create_display_name(table_name)
            
            # Create tooltip with detailed info
            tooltip = self._create_tooltip(table_name, table_info)
            
            node_element = {
                'data': {
                    'id': table_name,
                    'label': display_name,
                    'type': table_info.table_type.value,
                    'tooltip': tooltip,
                    'full_name': table_name,
                    'column_count': len(table_info.columns) if table_info.columns else 0,
                    'upstream_count': len(table_info.upstream_tables),
                    'downstream_count': len(table_info.downstream_tables)
                }
            }
            elements.append(node_element)
        
        # Add edges
        for table_name, table_info in lineage_graph.tables.items():
            for upstream_table in table_info.upstream_tables:
                edge_element = {
                    'data': {
                        'id': f"{upstream_table}-{table_name}",
                        'source': upstream_table,
                        'target': table_name
                    }
                }
                elements.append(edge_element)
        
        return elements
    
    def _create_display_name(self, table_name: str) -> str:
        """Create readable display name for nodes"""
        if len(table_name) <= 15:
            return table_name
            
        # Handle common prefixes
        if table_name.startswith('raw_'):
            abbreviated = table_name[4:]
        elif table_name.startswith('staging_'):
            abbreviated = 'stg_' + table_name[8:]
        elif table_name.startswith('dim_'):
            abbreviated = 'dim_' + table_name[4:]
        elif table_name.startswith('fact_'):
            abbreviated = 'fact_' + table_name[5:]
        else:
            abbreviated = table_name
            
        # If still too long, truncate with ellipsis
        if len(abbreviated) > 15:
            abbreviated = abbreviated[:12] + '...'
            
        return abbreviated
    
    def _create_tooltip(self, table_name: str, table_info) -> str:
        """Create detailed tooltip content"""
        tooltip_parts = [
            f"Table: {table_name}",
            f"Type: {table_info.table_type.value.title()}",
            f"Columns: {len(table_info.columns) if table_info.columns else 0}",
            f"Upstream: {len(table_info.upstream_tables)}",
            f"Downstream: {len(table_info.downstream_tables)}"
        ]
        
        if table_info.columns and len(table_info.columns) > 0:
            column_names = [col.column_name for col in table_info.columns[:5]]
            if len(table_info.columns) > 5:
                column_names.append(f"... and {len(table_info.columns) - 5} more")
            tooltip_parts.append(f"Sample Columns: {', '.join(column_names)}")
        
        return "\\n".join(tooltip_parts)
    
    def _generate_cytoscape_html(self, elements: List[Dict], layout_algorithm: str) -> str:
        """Generate complete HTML with Cytoscape.js visualization"""
        
        elements_json = json.dumps(elements, indent=2)
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Lineage Lens - Professional Data Lineage</title>
    
    <!-- Cytoscape.js -->
    <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
    <script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
    <script src="https://unpkg.com/cytoscape-cola@2.5.1/cytoscape-cola.js"></script>
    <script src="https://unpkg.com/cytoscape-euler@1.2.2/cytoscape-euler.js"></script>
    
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        
        #cy {{
            width: 100%;
            height: 600px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            background: white;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }}
        
        .controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 999;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .control-btn {{
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .layout-btn {{
            background: #3498db;
            color: white;
        }}
        
        .layout-btn:hover {{
            background: #2980b9;
            transform: translateY(-1px);
        }}
        
        .action-btn {{
            background: #27ae60;
            color: white;
        }}
        
        .action-btn:hover {{
            background: #229954;
            transform: translateY(-1px);
        }}
        
        .info-panel {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 999;
            background: white;
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            min-width: 200px;
            font-size: 12px;
        }}
        
        .legend {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            z-index: 999;
            background: white;
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 4px 0;
            font-size: 12px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 11px;
            pointer-events: none;
            z-index: 1000;
            max-width: 250px;
            white-space: pre-line;
        }}
    </style>
</head>
<body>
    <div class="controls">
        <button class="control-btn layout-btn" onclick="changeLayout('dagre')">Hierarchical</button>
        <button class="control-btn layout-btn" onclick="changeLayout('cola')">Force</button>
        <button class="control-btn layout-btn" onclick="changeLayout('circle')">Circular</button>
        <button class="control-btn layout-btn" onclick="changeLayout('grid')">Grid</button>
        <button class="control-btn action-btn" onclick="fitGraph()">Fit View</button>
        <button class="control-btn action-btn" onclick="centerGraph()">Center</button>
        <button class="control-btn action-btn" onclick="resetZoom()">Reset Zoom</button>
    </div>
    
    <div class="info-panel">
        <h4 style="margin: 0 0 8px 0; color: #2c3e50;">Graph Statistics</h4>
        <div id="stats">Loading...</div>
    </div>
    
    <div class="legend">
        <h4 style="margin: 0 0 8px 0; color: #2c3e50;">Table Types</h4>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #27AE60;"></div>
            <span>Source Tables</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #3498DB;"></div>
            <span>Intermediate Tables</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #E74C3C;"></div>
            <span>Target Tables</span>
        </div>
    </div>
    
    <div id="cy"></div>
    <div id="tooltip" class="tooltip" style="display: none;"></div>
    
    <script>
        var cy = cytoscape({{
            container: document.getElementById('cy'),
            
            elements: {elements_json},
            
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'background-color': function(ele) {{
                            const type = ele.data('type');
                            const colors = {{
                                'source': '#27AE60',
                                'intermediate': '#3498DB', 
                                'target': '#E74C3C'
                            }};
                            return colors[type] || '#95a5a6';
                        }},
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '11px',
                        'font-weight': 'bold',
                        'color': 'white',
                        'text-outline-width': 2,
                        'text-outline-color': function(ele) {{
                            const type = ele.data('type');
                            const colors = {{
                                'source': '#229954',
                                'intermediate': '#2E86AB',
                                'target': '#C0392B'
                            }};
                            return colors[type] || '#7f8c8d';
                        }},
                        'width': '100px',
                        'height': '50px',
                        'shape': 'roundrectangle',
                        'border-width': '3px',
                        'border-color': function(ele) {{
                            const type = ele.data('type');
                            const colors = {{
                                'source': '#229954',
                                'intermediate': '#2E86AB',
                                'target': '#C0392B'
                            }};
                            return colors[type] || '#7f8c8d';
                        }},
                        'transition-property': 'background-color, border-color, transform',
                        'transition-duration': '0.3s'
                    }}
                }},
                {{
                    selector: 'node:hover',
                    style: {{
                        'transform': 'scale(1.1)',
                        'border-width': '4px',
                        'z-index': 999
                    }}
                }},
                {{
                    selector: 'node:selected',
                    style: {{
                        'border-width': '5px',
                        'border-color': '#FFD700',
                        'transform': 'scale(1.15)',
                        'z-index': 999
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 3,
                        'line-color': '#7f8c8d',
                        'target-arrow-color': '#7f8c8d',
                        'target-arrow-shape': 'triangle',
                        'target-arrow-size': '8px',
                        'curve-style': 'bezier',
                        'source-endpoint': 'outside-to-node',
                        'target-endpoint': 'outside-to-node',
                        'transition-property': 'line-color, target-arrow-color, width',
                        'transition-duration': '0.3s'
                    }}
                }},
                {{
                    selector: 'edge:hover',
                    style: {{
                        'width': 4,
                        'line-color': '#2c3e50',
                        'target-arrow-color': '#2c3e50'
                    }}
                }},
                {{
                    selector: 'edge:selected',
                    style: {{
                        'width': 5,
                        'line-color': '#FFD700',
                        'target-arrow-color': '#FFD700'
                    }}
                }}
            ],
            
            layout: {{
                name: '{layout_algorithm}',
                rankDir: 'TB',
                spacingFactor: 1.5,
                nodeDimensionsIncludeLabels: true,
                animate: true,
                animationDuration: 1000,
                fit: true,
                padding: 30
            }},
            
            // Interaction options
            wheelSensitivity: 0.2,
            minZoom: 0.3,
            maxZoom: 3.0
        }});
        
        // Add interactivity
        var tooltip = document.getElementById('tooltip');
        
        // Node hover events
        cy.on('mouseover', 'node', function(evt) {{
            var node = evt.target;
            tooltip.innerHTML = node.data('tooltip');
            tooltip.style.display = 'block';
        }});
        
        cy.on('mouseout', 'node', function(evt) {{
            tooltip.style.display = 'none';
        }});
        
        cy.on('mousemove', function(evt) {{
            tooltip.style.left = (evt.originalEvent.clientX + 10) + 'px';
            tooltip.style.top = (evt.originalEvent.clientY - 10) + 'px';
        }});
        
        // Node click events
        cy.on('tap', 'node', function(evt) {{
            var node = evt.target;
            var data = node.data();
            
            // Highlight connected nodes
            var connectedEdges = node.connectedEdges();
            var connectedNodes = connectedEdges.connectedNodes();
            
            cy.elements().removeClass('highlighted').addClass('dimmed');
            node.removeClass('dimmed').addClass('highlighted');
            connectedNodes.removeClass('dimmed').addClass('highlighted');
            connectedEdges.removeClass('dimmed').addClass('highlighted');
            
            // Show detailed info
            alert(`Table Details:\\n\\nName: ${{data.full_name}}\\nType: ${{data.type.toUpperCase()}}\\nColumns: ${{data.column_count}}\\nUpstream Dependencies: ${{data.upstream_count}}\\nDownstream Dependencies: ${{data.downstream_count}}`);
        }});
        
        // Click on background to reset highlighting
        cy.on('tap', function(evt) {{
            if (evt.target === cy) {{
                cy.elements().removeClass('highlighted dimmed');
            }}
        }});
        
        // Layout functions
        function changeLayout(layoutName) {{
            var layoutOptions = {{
                'dagre': {{
                    name: 'dagre',
                    rankDir: 'TB',
                    spacingFactor: 1.5,
                    nodeDimensionsIncludeLabels: true
                }},
                'cola': {{
                    name: 'cola',
                    animate: true,
                    refresh: 1,
                    maxSimulationTime: 4000,
                    ungrabifyWhileSimulating: false,
                    fit: true,
                    padding: 30,
                    nodeDimensionsIncludeLabels: true
                }},
                'circle': {{
                    name: 'circle',
                    fit: true,
                    padding: 30,
                    spacingFactor: 1.5
                }},
                'grid': {{
                    name: 'grid',
                    fit: true,
                    padding: 30,
                    spacingFactor: 1.5
                }}
            }};
            
            cy.layout(layoutOptions[layoutName] || layoutOptions['dagre']).run();
        }}
        
        function fitGraph() {{
            cy.fit(null, 50);
        }}
        
        function centerGraph() {{
            cy.center();
        }}
        
        function resetZoom() {{
            cy.zoom(1);
            cy.center();
        }}
        
        // Update statistics
        function updateStats() {{
            var nodes = cy.nodes();
            var edges = cy.edges();
            var sourceNodes = nodes.filter('[type = "source"]');
            var intermediateNodes = nodes.filter('[type = "intermediate"]');
            var targetNodes = nodes.filter('[type = "target"]');
            
            document.getElementById('stats').innerHTML = `
                <div><strong>Total Tables:</strong> ${{nodes.length}}</div>
                <div><strong>Relationships:</strong> ${{edges.length}}</div>
                <div><strong>Source Tables:</strong> ${{sourceNodes.length}}</div>
                <div><strong>Intermediate:</strong> ${{intermediateNodes.length}}</div>
                <div><strong>Target Tables:</strong> ${{targetNodes.length}}</div>
            `;
        }}
        
        // Initialize stats
        cy.ready(function() {{
            updateStats();
        }});
        
        // Add CSS for highlighting
        cy.style()
            .selector('.highlighted')
            .style({{
                'opacity': 1,
                'z-index': 999
            }})
            .selector('.dimmed')
            .style({{
                'opacity': 0.3
            }})
            .update();
    </script>
</body>
</html>
        """
        
        return html_template
    
    def render_in_streamlit(self, lineage_graph: LineageGraph, layout_algorithm: str = "dagre", height: int = 650):
        """Render the Cytoscape visualization in Streamlit"""
        html_content = self.create_cytoscape_visualization(lineage_graph, layout_algorithm)
        components.html(html_content, height=height, scrolling=False)
        
        # Return some statistics for display
        stats = {
            'total_tables': len(lineage_graph.tables),
            'source_tables': len(lineage_graph.source_tables),
            'intermediate_tables': len([t for t in lineage_graph.tables.values() 
                                       if t.table_type == TableType.INTERMEDIATE]),
            'target_tables': len(lineage_graph.target_tables),
            'total_relationships': sum(len(table.upstream_tables) 
                                     for table in lineage_graph.tables.values())
        }
        
        return stats
