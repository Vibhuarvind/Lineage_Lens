"""
Pydantic models for data lineage representation
"""

from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field
from enum import Enum


class TableType(str, Enum):
    SOURCE = "source"
    INTERMEDIATE = "intermediate" 
    TARGET = "target"


class ColumnLineage(BaseModel):
    """Represents column-level lineage information"""
    column_name: str = Field(..., description="Name of the column")
    source_columns: List[str] = Field(default_factory=list, description="Source columns this column depends on")
    transformation_type: Optional[str] = Field(None, description="Type of transformation applied")
    

class TableLineage(BaseModel):
    """Represents table-level lineage information"""
    table_name: str = Field(..., description="Name of the table")
    schema_name: Optional[str] = Field(None, description="Schema/database name")
    table_type: TableType = Field(..., description="Type of table in the lineage")
    upstream_tables: Set[str] = Field(default_factory=set, description="Tables this table depends on")
    downstream_tables: Set[str] = Field(default_factory=set, description="Tables that depend on this table")
    columns: List[ColumnLineage] = Field(default_factory=list, description="Column lineage information")
    sql_query: Optional[str] = Field(None, description="SQL query that creates this table")


class LineageGraph(BaseModel):
    """Complete lineage graph representation"""
    tables: Dict[str, TableLineage] = Field(default_factory=dict, description="All tables in the lineage")
    source_tables: Set[str] = Field(default_factory=set, description="Source tables with no upstream dependencies")
    target_tables: Set[str] = Field(default_factory=set, description="Target tables with no downstream dependencies")
    
    def add_table(self, table: TableLineage) -> None:
        """Add a table to the lineage graph"""
        self.tables[table.table_name] = table
        
        if table.table_type == TableType.SOURCE:
            self.source_tables.add(table.table_name)
        elif table.table_type == TableType.TARGET:
            self.target_tables.add(table.table_name)
    
    def get_upstream_tables(self, table_name: str) -> Set[str]:
        """Get all upstream tables for a given table"""
        if table_name not in self.tables:
            return set()
        return self.tables[table_name].upstream_tables
    
    def get_downstream_tables(self, table_name: str) -> Set[str]:
        """Get all downstream tables for a given table"""
        if table_name not in self.tables:
            return set()
        return self.tables[table_name].downstream_tables


class LineageQuery(BaseModel):
    """User query for lineage information"""
    query_text: str = Field(..., description="Natural language query about lineage")
    table_focus: Optional[str] = Field(None, description="Specific table to focus the query on")
    query_type: Optional[str] = Field(None, description="Type of query (upstream, downstream, explanation)")


class LineageExplanation(BaseModel):
    """LLM-generated explanation of lineage"""
    explanation: str = Field(..., description="Human-readable explanation of the lineage")
    affected_tables: List[str] = Field(default_factory=list, description="Tables mentioned in the explanation")
    confidence_score: Optional[float] = Field(None, description="Confidence score of the explanation")
