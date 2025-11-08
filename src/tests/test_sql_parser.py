"""
Tests for SQL parser functionality
"""

import pytest
from lineage_lens.parsers.sql_parser import SQLLineageParser
from lineage_lens.models.lineage_models import TableType


class TestSQLLineageParser:
    """Test cases for SQL lineage parser"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = SQLLineageParser()
    
    def test_simple_create_table(self):
        """Test parsing simple CREATE TABLE statement"""
        sql = """
        CREATE TABLE customer_summary AS
        SELECT customer_id, name, email
        FROM raw_customers
        WHERE status = 'active';
        """
        
        lineage_graph = self.parser.parse_sql_file(sql)
        
        assert len(lineage_graph.tables) == 1
        assert 'customer_summary' in lineage_graph.tables
        
        table = lineage_graph.tables['customer_summary']
        assert table.table_type == TableType.TARGET
        assert 'raw_customers' in table.upstream_tables
    
    def test_complex_join_query(self):
        """Test parsing query with multiple joins"""
        sql = """
        CREATE TABLE sales_report AS
        SELECT 
            o.order_id,
            c.customer_name,
            p.product_name,
            SUM(oi.quantity * oi.price) as total_value
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY o.order_id, c.customer_name, p.product_name;
        """
        
        lineage_graph = self.parser.parse_sql_file(sql)
        
        table = lineage_graph.tables['sales_report']
        expected_sources = {'orders', 'customers', 'order_items', 'products'}
        assert table.upstream_tables == expected_sources
    
    def test_multiple_statements(self):
        """Test parsing multiple SQL statements"""
        sql = """
        CREATE TABLE staging_customers AS
        SELECT * FROM raw_customers;
        
        CREATE TABLE customer_metrics AS
        SELECT customer_id, COUNT(*) as order_count
        FROM staging_customers sc
        JOIN orders o ON sc.customer_id = o.customer_id
        GROUP BY customer_id;
        """
        
        lineage_graph = self.parser.parse_sql_file(sql)
        
        assert len(lineage_graph.tables) == 2
        assert 'staging_customers' in lineage_graph.tables
        assert 'customer_metrics' in lineage_graph.tables
        
        # Check relationships
        staging_table = lineage_graph.tables['staging_customers']
        metrics_table = lineage_graph.tables['customer_metrics']
        
        assert 'raw_customers' in staging_table.upstream_tables
        assert 'staging_customers' in metrics_table.upstream_tables
        assert 'orders' in metrics_table.upstream_tables
