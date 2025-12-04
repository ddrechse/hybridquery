#!/usr/bin/env python3
"""
Graph Builder for Oracle Property Graph

Converts extracted entities into Oracle-ready CSV files for:
- Papers (nodes)
- Treatments (nodes)
- Conditions (nodes)
- MENTIONS edges (Paper -> Treatment)
- TREATS edges (Treatment -> Condition)

Author: Oracle GraphRAG POC
"""

import csv
from pathlib import Path
from typing import Set, List, Tuple, Dict
from datetime import datetime


class GraphDataBuilder:
    """Build Oracle Property Graph data from extracted entities"""

    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # ID counters
        self.paper_id = 1
        self.treatment_id = 100
        self.condition_id = 200
        self.mention_edge_id = 1000
        self.treats_edge_id = 2000

        # Entity mappings (name -> node_id)
        self.treatment_map = {}
        self.condition_map = {}

        # Data storage
        self.papers = []
        self.treatments = []
        self.conditions = []
        self.mentions_edges = []
        self.treats_edges = []

    def add_paper(self, filename: str, title: str, publication_date: str = None) -> int:
        """
        Add a paper node

        Args:
            filename: PDF filename
            title: Paper title
            publication_date: Publication date (YYYY-MM-DD format)

        Returns:
            Node ID of created paper
        """
        if publication_date is None:
            publication_date = datetime.now().strftime('%Y-%m-%d')

        paper_node = {
            'node_id': self.paper_id,
            'filename': filename,
            'title': title[:500],  # Truncate to 500 chars
            'publication_date': publication_date
        }

        self.papers.append(paper_node)
        current_id = self.paper_id
        self.paper_id += 1

        return current_id

    def add_treatment(self, treatment_name: str, treatment_type: str = 'Pharmaceutical') -> int:
        """
        Add a treatment node (if not already added)

        Args:
            treatment_name: Name of treatment
            treatment_type: Type of treatment

        Returns:
            Node ID of treatment
        """
        # Check if already exists
        if treatment_name in self.treatment_map:
            return self.treatment_map[treatment_name]

        treatment_node = {
            'node_id': self.treatment_id,
            'entity_name': treatment_name,
            'treatment_type': treatment_type
        }

        self.treatments.append(treatment_node)
        self.treatment_map[treatment_name] = self.treatment_id

        current_id = self.treatment_id
        self.treatment_id += 1

        return current_id

    def add_condition(self, condition_name: str) -> int:
        """
        Add a condition node (if not already added)

        Args:
            condition_name: Name of condition

        Returns:
            Node ID of condition
        """
        # Check if already exists
        if condition_name in self.condition_map:
            return self.condition_map[condition_name]

        # Determine ICD-10 code
        icd10_code = 'E11'  # Default to Type 2
        if 'Type 1' in condition_name:
            icd10_code = 'E10'

        condition_node = {
            'node_id': self.condition_id,
            'name': condition_name,
            'icd10_code': icd10_code
        }

        self.conditions.append(condition_node)
        self.condition_map[condition_name] = self.condition_id

        current_id = self.condition_id
        self.condition_id += 1

        return current_id

    def add_mentions_edge(self, paper_id: int, treatment_id: int):
        """
        Add MENTIONS edge: Paper -> Treatment

        Args:
            paper_id: Source paper node ID
            treatment_id: Target treatment node ID
        """
        edge = {
            'edge_id': self.mention_edge_id,
            'from_node_id': paper_id,
            'to_node_id': treatment_id
        }

        self.mentions_edges.append(edge)
        self.mention_edge_id += 1

    def add_treats_edge(self, treatment_id: int, condition_id: int):
        """
        Add TREATS edge: Treatment -> Condition

        Args:
            treatment_id: Source treatment node ID
            condition_id: Target condition node ID
        """
        # Avoid duplicates
        existing = [e for e in self.treats_edges
                    if e['from_node_id'] == treatment_id
                    and e['to_node_id'] == condition_id]

        if existing:
            return  # Already exists

        edge = {
            'edge_id': self.treats_edge_id,
            'from_node_id': treatment_id,
            'to_node_id': condition_id
        }

        self.treats_edges.append(edge)
        self.treats_edge_id += 1

    def build_graph_from_entities(
        self,
        paper_filename: str,
        paper_title: str,
        treatments: Set[str],
        conditions: Set[str],
        relationships: List[Tuple[str, str]],
        publication_date: str = None
    ):
        """
        Build complete graph from extracted entities

        Args:
            paper_filename: PDF filename
            paper_title: Paper title
            treatments: Set of treatment names
            conditions: Set of condition names
            relationships: List of (treatment, condition) tuples
            publication_date: Publication date
        """
        # Add paper node
        paper_id = self.add_paper(paper_filename, paper_title, publication_date)

        # Add treatment nodes and MENTIONS edges
        for treatment in treatments:
            treatment_id = self.add_treatment(treatment)
            self.add_mentions_edge(paper_id, treatment_id)

        # Add condition nodes
        for condition in conditions:
            self.add_condition(condition)

        # Add TREATS edges from relationships
        for treatment, condition in relationships:
            if treatment in self.treatment_map and condition in self.condition_map:
                treatment_id = self.treatment_map[treatment]
                condition_id = self.condition_map[condition]
                self.add_treats_edge(treatment_id, condition_id)

    def save_csv_files(self):
        """Save all graph data as CSV files

        IMPORTANT: All CSV files use newline='' parameter to ensure Unix line endings (LF only).
        This is critical for Oracle external tables which expect LF-only line terminators.
        Without newline='', Python may write Windows-style CRLF endings on some systems,
        causing Oracle external tables to fail with "no rows selected".
        """

        # Papers nodes
        if self.papers:
            csv_path = self.output_dir / 'papers_nodes.csv'
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['node_id', 'filename', 'title', 'publication_date'])
                writer.writeheader()
                writer.writerows(self.papers)
            print(f"✓ Saved {len(self.papers)} papers to {csv_path}")

        # Treatments nodes
        if self.treatments:
            csv_path = self.output_dir / 'treatments_nodes.csv'
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['node_id', 'entity_name', 'treatment_type'])
                writer.writeheader()
                writer.writerows(self.treatments)
            print(f"✓ Saved {len(self.treatments)} treatments to {csv_path}")

        # Conditions nodes
        if self.conditions:
            csv_path = self.output_dir / 'conditions_nodes.csv'
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['node_id', 'name', 'icd10_code'])
                writer.writeheader()
                writer.writerows(self.conditions)
            print(f"✓ Saved {len(self.conditions)} conditions to {csv_path}")

        # MENTIONS edges
        if self.mentions_edges:
            csv_path = self.output_dir / 'mentions_edges.csv'
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['edge_id', 'from_node_id', 'to_node_id'])
                writer.writeheader()
                writer.writerows(self.mentions_edges)
            print(f"✓ Saved {len(self.mentions_edges)} MENTIONS edges to {csv_path}")

        # TREATS edges
        if self.treats_edges:
            csv_path = self.output_dir / 'treats_edges.csv'
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['edge_id', 'from_node_id', 'to_node_id'])
                writer.writeheader()
                writer.writerows(self.treats_edges)
            print(f"✓ Saved {len(self.treats_edges)} TREATS edges to {csv_path}")

    def get_summary(self) -> Dict[str, int]:
        """Get summary of generated graph data"""
        return {
            'papers': len(self.papers),
            'treatments': len(self.treatments),
            'conditions': len(self.conditions),
            'mentions_edges': len(self.mentions_edges),
            'treats_edges': len(self.treats_edges)
        }


if __name__ == '__main__':
    # Test graph builder
    builder = GraphDataBuilder(output_dir='test_output')

    # Add sample data
    paper_id = builder.add_paper(
        filename='test_paper.pdf',
        title='Test Medical Paper',
        publication_date='2023-01-01'
    )

    treatment1 = builder.add_treatment('GLP-1 Agonists')
    treatment2 = builder.add_treatment('SGLT2 Inhibitors')

    condition1 = builder.add_condition('Type 2 Diabetes')

    builder.add_mentions_edge(paper_id, treatment1)
    builder.add_mentions_edge(paper_id, treatment2)

    builder.add_treats_edge(treatment1, condition1)
    builder.add_treats_edge(treatment2, condition1)

    # Save files
    builder.save_csv_files()

    # Show summary
    summary = builder.get_summary()
    print(f"\nGraph Summary: {summary}")
