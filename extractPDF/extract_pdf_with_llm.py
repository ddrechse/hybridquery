#!/usr/bin/env python3
"""
PDF to Oracle Property Graph Extractor (LLM-Enhanced)

This script uses:
1. Docling - To parse the PDF structure (text and layout)
2. Ollama (LLM) - To semantically extract treatments, conditions, and relationships
3. GraphDataBuilder - To save Oracle-compatible CSV files

Usage:
    python extract_pdf_with_llm.py path/to/paper.pdf --model llama3.1

Author: Oracle GraphRAG POC (Updated for LLM)
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Optional, List

# Check imports
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("WARNING: Docling not installed. Install with: pip install docling")

try:
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
    from pydantic import ValidationError
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("WARNING: LangChain/Ollama packages not installed. Install with: pip install langchain langchain-ollama pydantic")

from graph_schema import ExtractionResult

try:
    from oracle_loader import OracleGraphLoader
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

class PDFToGraphExtractorLLM:
    """Main extractor class using LLM"""

    def __init__(self, 
                 model_name: str = "llama3.1", 
                 output_dir: str = 'output', 
                 base_url: str = "http://localhost:11434",
                 db_config: Optional[Dict] = None):
        
        self.output_dir = output_dir
        self.db_config = db_config
        self.use_db = db_config is not None
        self.model_name = model_name
        self.base_url = base_url

        if self.use_db:
            if not ORACLE_AVAILABLE:
                raise RuntimeError("Oracle Loader could not be imported. Check oracledb dependency.")
            print(f"🔄 Using Direct Database Loader (User: {self.db_config['user']})")
            self.loader = OracleGraphLoader(
                user=self.db_config['user'],
                password=self.db_config['password'],
                dsn=self.db_config['dsn']
            )
        else:
            raise ValueError("❌ Database configuration is required. usage: --db-user <user> --db-pass <pass> --db-dsn <dsn>")
        
        if DOCLING_AVAILABLE:
            self.doc_converter = DocumentConverter()
        
        if LANGCHAIN_AVAILABLE:
            print(f"🤖 Initializing Ollama with model: {model_name}...")
            # Initialize Structured Output LLM
            llm = ChatOllama(model=model_name, base_url=base_url, temperature=0, format="json")
            self.llm = llm

    def parse_pdf_with_docling(self, pdf_path: Path) -> Dict:
        """Parse PDF using Docling (Same as original)"""
        if not DOCLING_AVAILABLE:
            raise RuntimeError("Docling is not installed.")

        # ... (rest of method same as before) ...
        print(f"📄 Parsing PDF with Docling: {pdf_path.name}")
        result = self.doc_converter.convert(str(pdf_path))
        doc = result.document
        
        # Extract title
        markdown = doc.export_to_markdown()
        lines = markdown.split('\n')
        title = "Untitled Document"
        for line in lines[:20]:
            if line.strip().startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        return {
            'title': title,
            'text': markdown,
            'filename': pdf_path.name
        }

    def extract_with_llm(self, text: str) -> ExtractionResult:
        """Use LLM to extract entities from text"""
        # ... (same extraction logic) ...
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain dependencies missing.")

        print("🔍 Sending text to LLM for extraction (this may take a minute)...")
        
        from langchain_core.output_parsers import PydanticOutputParser
        
        parser = PydanticOutputParser(pydantic_object=ExtractionResult)

        processed_text = text[:12000] 
        if len(text) > 12000:
            print("   ⚠️ Text truncated to first 12000 chars to fit context window.")

        CANONICAL_TREATMENTS = [
            "Metformin", "GLP-1 Agonists", "SGLT2 Inhibitors", "DPP-4 Inhibitors", 
            "Insulin Therapy", "Basal Insulin", "Sulfonylureas", "Semaglutide", 
            "Liraglutide", "Empagliflozin", "Dapagliflozin", "Canagliflozin", 
            "Sitagliptin", "Linagliptin"
        ]

        CANONICAL_CONDITIONS = ["Type 2 Diabetes", "Type 1 Diabetes"]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert medical researcher building a Knowledge Graph."),
            ("system", "Extract all pharmaceutical treatments, medical conditions, and their treatments relationships from the text.\n{format_instructions}"),
            ("system", "IMPORTANT: Normalize extracted treatment names to match this canonical list if possible: " + ", ".join(CANONICAL_TREATMENTS) + ". If a treatment is not in the list, use its most common generic name."),
            ("system", "IMPORTANT: Normalize extracted condition names to these exact values: " + ", ".join(CANONICAL_CONDITIONS) + ". Map 'Type 2 Diabetes mellitus' or 'T2DM' to 'Type 2 Diabetes'."),
            ("system", "Ignore general lifestyle advice unless it's a specific protocol. Focus on drugs and diseases."),
            ("human", "Analyze this text and extract the graph data:\n\n{text}")
        ])

        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "text": processed_text,
                "format_instructions": parser.get_format_instructions()
            })
            
            print(f"   ✓ LLM extraction successful")
            return result
        except Exception as e:
            print(f"   ❌ LLM Extraction failed: {e}")
            return ExtractionResult()

    def convert_to_builder_format(self, llm_result: ExtractionResult) -> Dict:
        """Convert Pydantic result to format expected by loader"""
        
        treatments = set()
        conditions = set()
        relationships = []

        # Process Treatments
        for t in llm_result.treatments:
            treatments.add(t.name)
            
        # Process Conditions
        for c in llm_result.conditions:
            conditions.add(c.name)
            
        # Process Relationships
        for r in llm_result.relationships:
            treatments.add(r.treatment_name)
            conditions.add(r.condition_name)
            
            if r.relationship_type == "TREATS":
                relationships.append((r.treatment_name, r.condition_name))
        
        return {
            'treatments': treatments,
            'conditions': conditions,
            'relationships': relationships
        }

    def process_pdf(self, pdf_path: str, publication_date: Optional[str] = None):
        """Main pipeline"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ Error: File not found {pdf_path}")
            sys.exit(1)

        # 1. Parse
        parsed = self.parse_pdf_with_docling(pdf_path)
        
        # 2. Extract (LLM)
        llm_result = self.extract_with_llm(parsed['text'])
        
        # 3. Convert
        entities = self.convert_to_builder_format(llm_result)
        
        print(f"   ► Found {len(entities['treatments'])} treatments")
        print(f"   ► Found {len(entities['conditions'])} conditions")
        print(f"   ► Found {len(entities['relationships'])} relationships")

        # 4. Load (DB or CSV)
        # 4. Load (DB)
        if self.use_db:
            print(f"🚀 Inserting directly into Oracle Database...")
            
            self.loader.build_graph_from_entities(
                paper_filename=parsed['filename'],
                paper_title=parsed['title'],
                treatments=entities['treatments'],
                conditions=entities['conditions'],
                relationships=entities['relationships'],
                publication_date=publication_date
            )
            
            # 5. Save/Commit
            self.loader.close() # Commits transaction
            print("\n✅ Database Insert Complete!")

def main():
    parser = argparse.ArgumentParser(description='LLM-based PDF to Graph Extractor')
    parser.add_argument('pdf_file', help='Path to PDF file')
    parser.add_argument('--model', default='llama3.1', help='Ollama model name (default: llama3.1)')
    parser.add_argument('--date', default=None, help='Publication date (YYYY-MM-DD)')
    parser.add_argument('--output', default='output', help='Output directory (only used if not using DB)')
    
    # DB Arguments
    parser.add_argument('--db-user', help='Oracle DB User', default=None)
    parser.add_argument('--db-pass', help='Oracle DB Password', default=None)
    parser.add_argument('--db-dsn', help='Oracle DB DSN (e.g. localhost:1521/FREEPDB1)', default=None)
    
    args = parser.parse_args()
    
    db_config = None
    if args.db_user and args.db_pass and args.db_dsn:
        db_config = {
            'user': args.db_user,
            'password': args.db_pass,
            'dsn': args.db_dsn
        }
    
    extractor = PDFToGraphExtractorLLM(
        model_name=args.model, 
        output_dir=args.output,
        db_config=db_config
    )
    extractor.process_pdf(args.pdf_file, publication_date=args.date)

if __name__ == '__main__':
    main()
