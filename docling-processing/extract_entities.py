#!/usr/bin/env python3
"""
Extract graph entities and relationships from processed documents
for Oracle Property Graph creation.

This script analyzes Docling-processed documents to extract:
- Entities: Papers, Treatments, Conditions
- Relationships: MENTIONS, TREATS

The output is formatted for Oracle Property Graph node/edge tables.

Author: Oracle GraphRAG POC
"""

import json
import re
import csv
from pathlib import Path
from collections import defaultdict


class GraphEntityExtractor:
    """Extract entities and relationships for Property Graph"""

    def __init__(self, input_dir="./output", output_dir="./graph_data"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Storage for extracted entities
        self.papers = []
        self.treatments = []
        self.conditions = []
        self.mentions_edges = []
        self.treats_edges = []

        # ID counters
        self.paper_id = 1
        self.treatment_id = 1
        self.condition_id = 1
        self.edge_id = 1

        # Entity mappings
        self.treatment_map = {}
        self.condition_map = {}

    def extract_from_pdf(self, pdf_data):
        """Extract entities from processed PDF data"""
        print(f"Extracting entities from: {pdf_data['filename']}")

        # Create Paper node
        paper_node = {
            'node_id': self.paper_id,
            'filename': pdf_data['filename'],
            'title': pdf_data['title'],
            'publication_date': '2023-01-01'  # Extract from metadata if available
        }
        self.papers.append(paper_node)
        current_paper_id = self.paper_id
        self.paper_id += 1

        # Extract mentions of treatments and conditions from text
        text_content = pdf_data['text_content']

        # Find treatment mentions (pattern: "TreatmentName for ConditionName")
        # Example: "GLP-1 agonists for Type 2 Diabetes"
        treatment_patterns = [
            r'([A-Z][A-Za-z0-9\-\s]+)\s+(?:for|treat|treats|treating)\s+(Type [12] Diabetes)',
            r'(Metformin|Insulin Therapy|GLP-1 [Aa]gonists|SGLT2 [Ii]nhibitors|DPP-4 [Ii]nhibitors|Sulfonylureas|Basal Insulin)',
        ]

        conditions_found = set()
        treatments_found = set()

        # Extract treatments and conditions
        for pattern in treatment_patterns:
            matches = re.finditer(pattern, text_content)
            for match in matches:
                if len(match.groups()) == 2:
                    treatment_name = match.group(1).strip()
                    condition_name = match.group(2).strip()
                elif len(match.groups()) == 1:
                    treatment_name = match.group(1).strip()
                    condition_name = "Type 2 Diabetes"  # Default

                treatments_found.add(treatment_name)
                conditions_found.add(condition_name)

        # Create Treatment nodes
        for treatment_name in treatments_found:
            if treatment_name not in self.treatment_map:
                treatment_node = {
                    'node_id': self.treatment_id,
                    'entity_name': treatment_name,
                    'treatment_type': 'Pharmaceutical'
                }
                self.treatments.append(treatment_node)
                self.treatment_map[treatment_name] = self.treatment_id
                self.treatment_id += 1

            # Create MENTIONS edge (Paper -> Treatment)
            mentions_edge = {
                'edge_id': self.edge_id,
                'from_node_id': current_paper_id,
                'to_node_id': self.treatment_map[treatment_name]
            }
            self.mentions_edges.append(mentions_edge)
            self.edge_id += 1

        # Create Condition nodes
        for condition_name in conditions_found:
            if condition_name not in self.condition_map:
                condition_node = {
                    'node_id': self.condition_id,
                    'name': condition_name,
                    'icd10_code': 'E11' if 'Type 2' in condition_name else 'E10'
                }
                self.conditions.append(condition_node)
                self.condition_map[condition_name] = self.condition_id
                self.condition_id += 1

        # Create TREATS edges (Treatment -> Condition)
        for treatment_name in treatments_found:
            for condition_name in conditions_found:
                treats_edge = {
                    'edge_id': self.edge_id,
                    'from_node_id': self.treatment_map[treatment_name],
                    'to_node_id': self.condition_map[condition_name]
                }
                self.treats_edges.append(treats_edge)
                self.edge_id += 1

        print(f"  → Extracted {len(treatments_found)} treatments, {len(conditions_found)} conditions")

    def extract_from_excel(self, excel_data):
        """Extract entities from processed Excel data"""
        print(f"Extracting entities from: {excel_data['filename']}")

        # Excel contains treatment outcomes data
        # Add treatments that weren't in PDF
        for row in excel_data['rows']:
            treatment_name = row.get('Treatment Name', '')
            condition_name = row.get('Condition Treated', '')

            # Add treatment if new
            if treatment_name and treatment_name not in self.treatment_map:
                treatment_node = {
                    'node_id': self.treatment_id,
                    'entity_name': treatment_name,
                    'treatment_type': 'Pharmaceutical'
                }
                self.treatments.append(treatment_node)
                self.treatment_map[treatment_name] = self.treatment_id
                self.treatment_id += 1

            # Add condition if new
            if condition_name and condition_name not in self.condition_map:
                condition_node = {
                    'node_id': self.condition_id,
                    'name': condition_name,
                    'icd10_code': 'E11' if 'Type 2' in condition_name else 'E10'
                }
                self.conditions.append(condition_node)
                self.condition_map[condition_name] = self.condition_id
                self.condition_id += 1

            # Create TREATS edge if both exist
            if treatment_name and condition_name:
                treats_edge = {
                    'edge_id': self.edge_id,
                    'from_node_id': self.treatment_map[treatment_name],
                    'to_node_id': self.condition_map[condition_name]
                }
                # Avoid duplicates
                if treats_edge not in self.treats_edges:
                    self.treats_edges.append(treats_edge)
                    self.edge_id += 1

    def save_graph_data(self):
        """Save extracted entities as CSV files for Oracle import"""
        print("\nSaving graph data...")

        # Save Papers nodes
        if self.papers:
            with open(self.output_dir / 'papers_nodes.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['node_id', 'filename', 'title', 'publication_date'])
                writer.writeheader()
                writer.writerows(self.papers)
            print(f"  → Saved {len(self.papers)} papers to papers_nodes.csv")

        # Save Treatments nodes
        if self.treatments:
            with open(self.output_dir / 'treatments_nodes.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['node_id', 'entity_name', 'treatment_type'])
                writer.writeheader()
                writer.writerows(self.treatments)
            print(f"  → Saved {len(self.treatments)} treatments to treatments_nodes.csv")

        # Save Conditions nodes
        if self.conditions:
            with open(self.output_dir / 'conditions_nodes.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['node_id', 'name', 'icd10_code'])
                writer.writeheader()
                writer.writerows(self.conditions)
            print(f"  → Saved {len(self.conditions)} conditions to conditions_nodes.csv")

        # Save MENTIONS edges
        if self.mentions_edges:
            with open(self.output_dir / 'mentions_edges.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['edge_id', 'from_node_id', 'to_node_id'])
                writer.writeheader()
                writer.writerows(self.mentions_edges)
            print(f"  → Saved {len(self.mentions_edges)} MENTIONS edges to mentions_edges.csv")

        # Save TREATS edges
        if self.treats_edges:
            with open(self.output_dir / 'treats_edges.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['edge_id', 'from_node_id', 'to_node_id'])
                writer.writeheader()
                writer.writerows(self.treats_edges)
            print(f"  → Saved {len(self.treats_edges)} TREATS edges to treats_edges.csv")

    def process_all(self):
        """Process all documents and extract graph entities"""
        print("=" * 60)
        print("GRAPH ENTITY EXTRACTOR")
        print("=" * 60)

        # Load processing summary
        summary_file = self.input_dir / "processing_summary.json"
        if not summary_file.exists():
            print(f"ERROR: {summary_file} not found. Run process_documents.py first.")
            return

        with open(summary_file) as f:
            summary = json.load(f)

        # Process PDF documents
        for pdf_doc in summary['pdf_documents']:
            self.extract_from_pdf(pdf_doc)

        # Process Excel documents
        for excel_doc in summary['excel_documents']:
            self.extract_from_excel(excel_doc)

        # Save all graph data
        self.save_graph_data()

        print("=" * 60)
        print("Entity extraction complete!")
        print("\nNext step: Load data into Oracle using SQL scripts in oracle-setup/")
        print("=" * 60)


def main():
    """Main entry point"""
    extractor = GraphEntityExtractor()
    extractor.process_all()


if __name__ == "__main__":
    main()
