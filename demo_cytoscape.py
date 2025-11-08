#!/usr/bin/env python3
"""
Demo script to showcase the new Cytoscape.js visualization
"""

import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

from lineage_lens.visualizers.cytoscape_visualizer import CytoscapeGraphVisualizer
from lineage_lens.models.lineage_models import LineageGraph, TableLineage, TableType, ColumnLineage

def create_demo_lineage():
    """Create a demo lineage graph for testing"""
    
    # Create sample tables
    tables = {
        'raw_customers': TableLineage(
            table_name='raw_customers',
            table_type=TableType.SOURCE,
            columns=[
                ColumnLineage(column_name='customer_id', data_type='INT'),
                ColumnLineage(column_name='name', data_type='VARCHAR'),
                ColumnLineage(column_name='email', data_type='VARCHAR'),
                ColumnLineage(column_name='signup_date', data_type='DATE')
            ],
            upstream_tables=set(),
            downstream_tables={'staging_customers'}
        ),
        
        'raw_orders': TableLineage(
            table_name='raw_orders',
            table_type=TableType.SOURCE,
            columns=[
                ColumnLineage(column_name='order_id', data_type='INT'),
                ColumnLineage(column_name='customer_id', data_type='INT'),
                ColumnLineage(column_name='order_date', data_type='DATE'),
                ColumnLineage(column_name='total_amount', data_type='DECIMAL')
            ],
            upstream_tables=set(),
            downstream_tables={'staging_orders'}
        ),
        
        'staging_customers': TableLineage(
            table_name='staging_customers',
            table_type=TableType.INTERMEDIATE,
            columns=[
                ColumnLineage(column_name='customer_id', data_type='INT'),
                ColumnLineage(column_name='full_name', data_type='VARCHAR'),
                ColumnLineage(column_name='email_domain', data_type='VARCHAR'),
                ColumnLineage(column_name='customer_segment', data_type='VARCHAR')
            ],
            upstream_tables={'raw_customers'},
            downstream_tables={'customer_summary', 'customer_analytics'}
        ),
        
        'staging_orders': TableLineage(
            table_name='staging_orders',
            table_type=TableType.INTERMEDIATE,
            columns=[
                ColumnLineage(column_name='order_id', data_type='INT'),
                ColumnLineage(column_name='customer_id', data_type='INT'),
                ColumnLineage(column_name='order_month', data_type='VARCHAR'),
                ColumnLineage(column_name='revenue', data_type='DECIMAL')
            ],
            upstream_tables={'raw_orders'},
            downstream_tables={'customer_summary', 'revenue_analytics'}
        ),
        
        'customer_summary': TableLineage(
            table_name='customer_summary',
            table_type=TableType.TARGET,
            columns=[
                ColumnLineage(column_name='customer_id', data_type='INT'),
                ColumnLineage(column_name='total_orders', data_type='INT'),
                ColumnLineage(column_name='total_revenue', data_type='DECIMAL'),
                ColumnLineage(column_name='avg_order_value', data_type='DECIMAL')
            ],
            upstream_tables={'staging_customers', 'staging_orders'},
            downstream_tables=set()
        ),
        
        'customer_analytics': TableLineage(
            table_name='customer_analytics',
            table_type=TableType.TARGET,
            columns=[
                ColumnLineage(column_name='customer_segment', data_type='VARCHAR'),
                ColumnLineage(column_name='segment_size', data_type='INT'),
                ColumnLineage(column_name='avg_lifetime_value', data_type='DECIMAL')
            ],
            upstream_tables={'staging_customers'},
            downstream_tables=set()
        ),
        
        'revenue_analytics': TableLineage(
            table_name='revenue_analytics',
            table_type=TableType.TARGET,
            columns=[
                ColumnLineage(column_name='order_month', data_type='VARCHAR'),
                ColumnLineage(column_name='total_revenue', data_type='DECIMAL'),
                ColumnLineage(column_name='order_count', data_type='INT')
            ],
            upstream_tables={'staging_orders'},
            downstream_tables=set()
        )
    }
    
    return LineageGraph(tables=tables)

def main():
    """Generate Cytoscape demo HTML"""
    print("🎨 Generating Cytoscape.js Demo...")
    
    # Create demo data
    lineage_graph = create_demo_lineage()
    
    # Create visualizer
    visualizer = CytoscapeGraphVisualizer()
    
    # Generate HTML
    html_content = visualizer.create_cytoscape_visualization(
        lineage_graph, 
        layout_algorithm="dagre"
    )
    
    # Save to file
    output_file = current_dir / "cytoscape_demo.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Demo HTML generated: {output_file}")
    print(f"🌐 Open in browser: file://{output_file.absolute()}")
    print("\n🎯 Demo Features:")
    print("  • Professional DAG layout")
    print("  • Interactive node hover tooltips")
    print("  • Click nodes to highlight connections")
    print("  • Multiple layout algorithms")
    print("  • Zoom, pan, and fit controls")
    print("  • Color-coded table types")
    print("  • Real-time statistics")

if __name__ == "__main__":
    main()
