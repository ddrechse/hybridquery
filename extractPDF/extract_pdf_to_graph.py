#!/usr/bin/env python3
"""
PDF to Oracle Property Graph Extractor

This script uses Docling to parse a medical research PDF and extracts:
- Paper metadata (title, filename, date)
- Treatments mentioned in the paper
- Medical conditions discussed
- Relationships (MENTIONS, TREATS)

Output: CSV files ready for Oracle Property Graph import

Usage:
    python extract_pdf_to_graph.py path/to/paper.pdf

Author: Oracle GraphRAG POC
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Optional

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("WARNING: Docling not installed. Install with: pip install docling")

from entity_patterns import MedicalEntityExtractor
from graph_builder import GraphDataBuilder


class PDFToGraphExtractor:
    """Main extractor class"""

    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.entity_extractor = MedicalEntityExtractor()
        self.graph_builder = GraphDataBuilder(output_dir=output_dir)

        if DOCLING_AVAILABLE:
            self.doc_converter = DocumentConverter()
        else:
            self.doc_converter = None

    def parse_pdf_with_docling(self, pdf_path: Path) -> Dict:
        """
        Parse PDF using Docling

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with 'title', 'text', 'sections'
        """
        if not DOCLING_AVAILABLE:
            raise RuntimeError("Docling is not installed. Install with: pip install docling")

        print(f"📄 Parsing PDF with Docling: {pdf_path.name}")

        # Convert PDF
        result = self.doc_converter.convert(str(pdf_path))
        doc = result.document

        # Extract title (first heading or filename)
        title = self._extract_title(doc)

        # Export full text
        text_content = doc.export_to_markdown()

        # Extract sections (if available)
        sections = self._extract_sections(text_content)

        print(f"   ✓ Extracted {len(text_content)} characters")
        print(f"   ✓ Found {len(sections)} sections")

        return {
            'title': title,
            'text': text_content,
            'sections': sections,
            'filename': pdf_path.name
        }

    def _extract_title(self, doc) -> str:
        """Extract document title from Docling document"""
        # Try to get title from document structure
        markdown = doc.export_to_markdown()
        lines = markdown.split('\n')

        # Look for first heading (# or **)
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if line.startswith('# '):
                return line.replace('# ', '').strip()
            if line.startswith('**') and line.endswith('**'):
                return line.replace('**', '').strip()

        return "Untitled Document"

    def _extract_sections(self, markdown_text: str) -> Dict[str, str]:
        """Extract document sections from markdown"""
        sections = {}
        current_section = None
        current_content = []

        for line in markdown_text.split('\n'):
            # Check for section headers
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content)

                # Start new section
                current_section = line.replace('## ', '').replace('*', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def extract_entities_from_text(self, text: str) -> Dict:
        """
        Extract medical entities from text

        Args:
            text: Document text content

        Returns:
            Dictionary with 'treatments', 'conditions', 'relationships'
        """
        print("🔍 Extracting entities...")

        entities = self.entity_extractor.extract_all_entities(text)

        print(f"   ✓ Found {len(entities['treatments'])} unique treatments")
        print(f"   ✓ Found {len(entities['conditions'])} unique conditions")
        print(f"   ✓ Found {len(entities['relationships'])} treatment-condition relationships")

        return entities

    def build_graph_data(
        self,
        pdf_filename: str,
        title: str,
        entities: Dict,
        publication_date: Optional[str] = None
    ):
        """
        Build graph data from extracted entities

        Args:
            pdf_filename: PDF filename
            title: Paper title
            entities: Extracted entities dict
            publication_date: Publication date (YYYY-MM-DD)
        """
        print("🔨 Building graph data...")

        self.graph_builder.build_graph_from_entities(
            paper_filename=pdf_filename,
            paper_title=title,
            treatments=entities['treatments'],
            conditions=entities['conditions'],
            relationships=entities['relationships'],
            publication_date=publication_date
        )

        summary = self.graph_builder.get_summary()
        print(f"   ✓ Created {summary['papers']} paper node")
        print(f"   ✓ Created {summary['treatments']} treatment nodes")
        print(f"   ✓ Created {summary['conditions']} condition nodes")
        print(f"   ✓ Created {summary['mentions_edges']} MENTIONS edges")
        print(f"   ✓ Created {summary['treats_edges']} TREATS edges")

    def save_graph_csv_files(self):
        """Save graph data as CSV files"""
        print("💾 Saving CSV files...")
        self.graph_builder.save_csv_files()

    def process_pdf(self, pdf_path: str, publication_date: Optional[str] = None):
        """
        Main processing pipeline

        Args:
            pdf_path: Path to PDF file
            publication_date: Optional publication date (YYYY-MM-DD)
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            print(f"❌ Error: PDF file not found: {pdf_path}")
            sys.exit(1)

        print("=" * 70)
        print("PDF TO ORACLE PROPERTY GRAPH EXTRACTOR")
        print("=" * 70)
        print()

        # Step 1: Parse PDF
        parsed_doc = self.parse_pdf_with_docling(pdf_path)
        print()

        # Step 2: Extract entities
        entities = self.extract_entities_from_text(parsed_doc['text'])
        print()

        # Step 3: Build graph data
        self.build_graph_data(
            pdf_filename=parsed_doc['filename'],
            title=parsed_doc['title'],
            entities=entities,
            publication_date=publication_date
        )
        print()

        # Step 4: Save CSV files
        self.save_graph_csv_files()
        print()

        print("=" * 70)
        print("✅ EXTRACTION COMPLETE!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Review CSV files in output/ directory")
        print("2. Load into Oracle using SQL scripts")
        print("3. Run hybrid queries!")
        print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Extract medical research PDF to Oracle Property Graph format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s paper.pdf
  %(prog)s ../sample-data/diabetes_treatment_study.pdf
  %(prog)s paper.pdf --date 2023-01-15
  %(prog)s paper.pdf --output my_output_dir

Output:
  Creates CSV files in output/ directory:
    - papers_nodes.csv
    - treatments_nodes.csv
    - conditions_nodes.csv
    - mentions_edges.csv
    - treats_edges.csv
        """
    )

    parser.add_argument(
        'pdf_file',
        help='Path to PDF file to process'
    )

    parser.add_argument(
        '--date',
        help='Publication date (YYYY-MM-DD format)',
        default=None
    )

    parser.add_argument(
        '--output',
        help='Output directory for CSV files (default: output)',
        default='output'
    )

    args = parser.parse_args()

    # Create extractor
    extractor = PDFToGraphExtractor(output_dir=args.output)

    # Process PDF
    try:
        extractor.process_pdf(args.pdf_file, publication_date=args.date)
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
