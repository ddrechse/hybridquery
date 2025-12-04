#!/usr/bin/env python3
"""
Process medical documents using Docling to extract structured content
for Oracle GraphRAG hybrid query demo.

This script uses Docling to parse PDF and Excel files, extracting:
- Document metadata
- Structured text content
- Tables and data
- Hierarchical structure

Author: Oracle GraphRAG POC
"""

import os
import sys
from pathlib import Path
import json
import pandas as pd

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("ERROR: Docling not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


class MedicalDocumentProcessor:
    """Process medical documents using Docling"""

    def __init__(self, data_dir="../sample-data", output_dir="./output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.converter = DocumentConverter()

    def process_pdf(self, pdf_path):
        """
        Process PDF document using Docling

        Args:
            pdf_path: Path to PDF file

        Returns:
            DoclingDocument object with structured content
        """
        print(f"Processing PDF: {pdf_path}")

        # Convert document
        result = self.converter.convert(str(pdf_path))
        doc = result.document

        # Extract metadata
        metadata = {
            'filename': pdf_path.name,
            'title': self._extract_title(doc),
            'text_content': doc.export_to_markdown(),
            'structure': self._extract_structure(doc)
        }

        # Save processed document
        output_file = self.output_dir / f"{pdf_path.stem}_processed.json"
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  → Saved to: {output_file}")
        return metadata

    def process_excel(self, excel_path):
        """
        Process Excel file using Docling

        Args:
            excel_path: Path to Excel file

        Returns:
            Structured data from Excel
        """
        print(f"Processing Excel: {excel_path}")

        # For Excel, we can use pandas as Docling also supports it
        # In real implementation, Docling would handle this
        df = pd.read_csv(excel_path)  # Our sample is actually CSV format

        data = {
            'filename': excel_path.name,
            'columns': df.columns.tolist(),
            'rows': df.to_dict('records'),
            'row_count': len(df)
        }

        # Save processed data
        output_file = self.output_dir / f"{excel_path.stem}_processed.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"  → Saved to: {output_file}")
        return data

    def _extract_title(self, doc):
        """Extract document title from Docling document"""
        # Docling provides hierarchical structure
        # Look for title in document metadata or first heading
        markdown = doc.export_to_markdown()
        lines = markdown.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        return "Untitled Document"

    def _extract_structure(self, doc):
        """Extract document structure (sections, headings)"""
        # Docling preserves document structure
        structure = {
            'sections': [],
            'tables': []
        }

        markdown = doc.export_to_markdown()
        current_section = None

        for line in markdown.split('\n'):
            if line.startswith('===== ') and line.endswith(' ====='):
                # Section heading
                section_name = line.replace('=====', '').strip()
                current_section = {'name': section_name, 'content': []}
                structure['sections'].append(current_section)
            elif current_section:
                current_section['content'].append(line)

        return structure

    def process_all(self):
        """Process all documents in the sample-data directory"""
        print("=" * 60)
        print("DOCLING DOCUMENT PROCESSOR")
        print("=" * 60)

        results = {
            'pdf_documents': [],
            'excel_documents': []
        }

        # Process PDF files
        for pdf_file in self.data_dir.glob("*.pdf"):
            metadata = self.process_pdf(pdf_file)
            results['pdf_documents'].append(metadata)

        # Process Excel/CSV files
        for data_file in self.data_dir.glob("*.xlsx"):
            metadata = self.process_excel(data_file)
            results['excel_documents'].append(metadata)

        # Also check for CSV files
        for csv_file in self.data_dir.glob("treatment_outcomes.*"):
            if csv_file.suffix in ['.csv', '.xlsx']:
                metadata = self.process_excel(csv_file)
                results['excel_documents'].append(metadata)

        # Save summary
        summary_file = self.output_dir / "processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("=" * 60)
        print(f"Processing complete! Summary saved to: {summary_file}")
        print(f"  PDF documents processed: {len(results['pdf_documents'])}")
        print(f"  Excel documents processed: {len(results['excel_documents'])}")
        print("=" * 60)

        return results


def main():
    """Main entry point"""
    processor = MedicalDocumentProcessor()
    results = processor.process_all()

    print("\nNext step: Run extract_entities.py to extract graph entities")


if __name__ == "__main__":
    main()
