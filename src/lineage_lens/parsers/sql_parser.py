"""
SQL parsing module for extracting lineage information from SQL queries
"""

import re
import sqlparse
from typing import List, Set, Dict, Optional
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, Name
import sqlparse.tokens as tokens

from ..models.lineage_models import TableLineage, ColumnLineage, TableType, LineageGraph


class SQLLineageParser:
    """Parse SQL queries to extract table and column lineage"""
    
    def __init__(self):
        self.table_patterns = {
            'from': re.compile(r'\bFROM\s+([^\s,\(\)]+)', re.IGNORECASE),
            'join': re.compile(r'\bJOIN\s+([^\s,\(\)]+)', re.IGNORECASE),
            'insert': re.compile(r'\bINSERT\s+INTO\s+([^\s,\(\)]+)', re.IGNORECASE),
            'create': re.compile(r'\bCREATE\s+(?:TABLE\s+)?([^\s,\(\)]+)', re.IGNORECASE),
            'update': re.compile(r'\bUPDATE\s+([^\s,\(\)]+)', re.IGNORECASE)
        }
    
    def parse_sql_file(self, sql_content: str) -> LineageGraph:
        """Parse SQL content and return lineage graph"""
        lineage_graph = LineageGraph()
        statements = sqlparse.split(sql_content)
        
        for statement in statements:
            if statement.strip():
                table_info = self._parse_statement(statement)
                if table_info:
                    lineage_graph.add_table(table_info)
        
        self._build_relationships(lineage_graph)
        self._classify_table_types(lineage_graph)
        return lineage_graph
    
    def _parse_statement(self, sql_statement: str) -> Optional[TableLineage]:
        """Parse a single SQL statement"""
        parsed = sqlparse.parse(sql_statement)[0]
        statement_type = self._get_statement_type(parsed)
        
        if statement_type in ['CREATE', 'INSERT']:
            return self._parse_ddl_dml(sql_statement, statement_type)
        
        return None
    
    def _get_statement_type(self, parsed: Statement) -> str:
        """Determine the type of SQL statement"""
        first_token = None
        for token in parsed.flatten():
            # Check for keywords including DDL and DML tokens
            if (token.ttype in (Keyword, tokens.Keyword.DDL, tokens.Keyword.DML) and 
                token.value.upper() in ['SELECT', 'CREATE', 'INSERT', 'UPDATE']):
                first_token = token.value.upper()
                break
        return first_token or 'UNKNOWN'
    
    def _parse_ddl_dml(self, sql_statement: str, statement_type: str) -> Optional[TableLineage]:
        """Parse DDL/DML statements to extract table lineage"""
        target_table = self._extract_target_table(sql_statement, statement_type)
        source_tables = self._extract_source_tables(sql_statement)
        
        if not target_table:
            return None
        
        # Initial classification - will be refined later
        table_type = TableType.SOURCE if not source_tables else TableType.INTERMEDIATE
        
        return TableLineage(
            table_name=target_table,
            table_type=table_type,
            upstream_tables=source_tables,
            sql_query=sql_statement.strip()
        )
    
    def _extract_target_table(self, sql_statement: str, statement_type: str) -> Optional[str]:
        """Extract target table from SQL statement"""
        if statement_type == 'CREATE':
            match = self.table_patterns['create'].search(sql_statement)
        elif statement_type == 'INSERT':
            match = self.table_patterns['insert'].search(sql_statement)
        else:
            return None
        
        return self._clean_table_name(match.group(1)) if match else None
    
    def _extract_source_tables(self, sql_statement: str) -> Set[str]:
        """Extract source tables from SQL statement"""
        source_tables = set()
        
        # Find FROM clauses
        from_matches = self.table_patterns['from'].findall(sql_statement)
        for table in from_matches:
            source_tables.add(self._clean_table_name(table))
        
        # Find JOIN clauses
        join_matches = self.table_patterns['join'].findall(sql_statement)
        for table in join_matches:
            source_tables.add(self._clean_table_name(table))
        
        return source_tables
    
    def _clean_table_name(self, table_name: str) -> str:
        """Clean and normalize table name"""
        # Remove quotes, brackets, semicolons, and schema prefixes for simplification
        cleaned = table_name.strip().strip('"`[];')
        if '.' in cleaned:
            cleaned = cleaned.split('.')[-1]  # Take only table name, ignore schema
        return cleaned
    
    def _build_relationships(self, lineage_graph: LineageGraph) -> None:
        """Build downstream relationships in the lineage graph"""
        for table_name, table in lineage_graph.tables.items():
            for upstream_table in table.upstream_tables:
                if upstream_table in lineage_graph.tables:
                    lineage_graph.tables[upstream_table].downstream_tables.add(table_name)
    
    def _classify_table_types(self, lineage_graph: LineageGraph) -> None:
        """Classify tables as source, intermediate, or target based on relationships"""
        for table_name, table in lineage_graph.tables.items():
            has_upstream = bool(table.upstream_tables)
            has_downstream = bool(table.downstream_tables)
            
            if not has_upstream and not has_downstream:
                # No relationships - could be source or standalone
                table.table_type = TableType.SOURCE
            elif not has_upstream and has_downstream:
                # Only downstream dependencies - this is a source table
                table.table_type = TableType.SOURCE
            elif has_upstream and not has_downstream:
                # Only upstream dependencies - this is a target table
                table.table_type = TableType.TARGET
            else:
                # Both upstream and downstream - this is an intermediate table
                table.table_type = TableType.INTERMEDIATE
    
    def extract_column_lineage(self, sql_statement: str) -> List[ColumnLineage]:
        """Extract column-level lineage (simplified implementation)"""
        # This is a basic implementation - would need more sophisticated parsing for production
        columns = []
        
        # Extract SELECT columns
        select_pattern = re.compile(r'SELECT\s+(.*?)\s+FROM', re.IGNORECASE | re.DOTALL)
        match = select_pattern.search(sql_statement)
        
        if match:
            select_clause = match.group(1)
            column_specs = [col.strip() for col in select_clause.split(',')]
            
            for col_spec in column_specs:
                if ' AS ' in col_spec.upper():
                    parts = col_spec.upper().split(' AS ')
                    column_name = parts[1].strip()
                    source_expr = parts[0].strip()
                else:
                    column_name = col_spec.split('.')[-1].strip()
                    source_expr = col_spec
                
                # Extract source columns from expression (simplified)
                source_columns = self._extract_source_columns(source_expr)
                
                columns.append(ColumnLineage(
                    column_name=column_name,
                    source_columns=source_columns,
                    transformation_type="direct" if len(source_columns) == 1 else "computed"
                ))
        
        return columns
    
    def _extract_source_columns(self, expression: str) -> List[str]:
        """Extract source column names from an expression"""
        # Simple pattern to find column references
        column_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')
        potential_columns = column_pattern.findall(expression)
        
        # Filter out SQL keywords and functions
        sql_keywords = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'AS', 'AND', 'OR', 'NOT', 
                       'SUM', 'COUNT', 'AVG', 'MAX', 'MIN', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'}
        
        return [col for col in potential_columns if col.upper() not in sql_keywords]
