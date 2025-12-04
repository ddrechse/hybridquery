#!/usr/bin/env python3
"""
Entity Patterns for Medical Research Paper Extraction

This module contains regex patterns and logic for extracting:
- Treatments (medications, therapies)
- Conditions (diseases, diagnoses)
- Relationships (MENTIONS, TREATS)

Author: Oracle GraphRAG POC
"""

import re
from typing import List, Tuple, Set
from dataclasses import dataclass


@dataclass
class EntityMention:
    """Represents a mention of an entity in text"""
    entity_type: str  # 'treatment' or 'condition'
    entity_name: str
    start_pos: int
    end_pos: int
    context: str  # Surrounding text


class MedicalEntityExtractor:
    """Extract medical entities and relationships from text"""

    def __init__(self):
        # Known treatments to look for
        self.known_treatments = [
            'Metformin',
            'GLP-1 Agonists',
            'GLP-1 agonists',
            'GLP-1 receptor agonists',
            'SGLT2 Inhibitors',
            'SGLT2 inhibitors',
            'DPP-4 Inhibitors',
            'DPP-4 inhibitors',
            'Insulin Therapy',
            'Insulin therapy',
            'Basal Insulin',
            'Basal insulin',
            'Sulfonylureas',
            'Liraglutide',
            'Semaglutide',
            'Empagliflozin',
            'Dapagliflozin',
            'Canagliflozin',
            'Sitagliptin',
            'Linagliptin',
        ]

        # Known conditions
        self.known_conditions = [
            'Type 1 Diabetes',
            'Type 2 Diabetes',
            'Diabetes mellitus',
            'Diabetes',
        ]

        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for entity extraction"""

        # Pattern for finding treatments
        treatment_names = '|'.join(re.escape(t) for t in self.known_treatments)
        self.treatment_pattern = re.compile(
            rf'\b({treatment_names})\b',
            re.IGNORECASE
        )

        # Pattern for finding conditions
        condition_names = '|'.join(re.escape(c) for c in self.known_conditions)
        self.condition_pattern = re.compile(
            rf'\b({condition_names})\b',
            re.IGNORECASE
        )

        # Patterns for treatment-condition relationships
        # These find phrases like "GLP-1 agonists treat Type 2 Diabetes"
        self.treats_patterns = [
            # "Treatment treats/treating/treat Condition"
            re.compile(
                rf'\b({treatment_names})\s+(?:treat|treats|treating|for)\s+({condition_names})\b',
                re.IGNORECASE
            ),
            # "Treatment for Condition"
            re.compile(
                rf'\b({treatment_names})\s+for\s+({condition_names})\b',
                re.IGNORECASE
            ),
            # "Condition treatment with Treatment"
            re.compile(
                rf'\b({condition_names})\s+treatment\s+with\s+({treatment_names})\b',
                re.IGNORECASE
            ),
        ]

    def extract_treatments(self, text: str) -> Set[str]:
        """
        Extract all treatment mentions from text

        Args:
            text: Document text

        Returns:
            Set of unique treatment names
        """
        treatments = set()

        for match in self.treatment_pattern.finditer(text):
            treatment = match.group(1)
            # Normalize to title case
            normalized = self._normalize_treatment_name(treatment)
            treatments.add(normalized)

        return treatments

    def extract_conditions(self, text: str) -> Set[str]:
        """
        Extract all condition mentions from text

        Args:
            text: Document text

        Returns:
            Set of unique condition names
        """
        conditions = set()

        for match in self.condition_pattern.finditer(text):
            condition = match.group(1)
            # Normalize to standard names
            normalized = self._normalize_condition_name(condition)
            conditions.add(normalized)

        return conditions

    def extract_treats_relationships(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract treatment-treats-condition relationships

        Args:
            text: Document text

        Returns:
            List of (treatment, condition) tuples
        """
        relationships = []

        for pattern in self.treats_patterns:
            for match in pattern.finditer(text):
                groups = match.groups()

                # Identify which group is treatment vs condition
                if len(groups) == 2:
                    # Check first group
                    if any(t.lower() in groups[0].lower() for t in self.known_treatments):
                        treatment = groups[0]
                        condition = groups[1]
                    else:
                        treatment = groups[1]
                        condition = groups[0]

                    # Normalize names
                    treatment = self._normalize_treatment_name(treatment)
                    condition = self._normalize_condition_name(condition)

                    relationships.append((treatment, condition))

        return relationships

    def _normalize_treatment_name(self, name: str) -> str:
        """Normalize treatment name to standard form"""
        name_lower = name.lower()

        # Map variations to standard names
        mappings = {
            'glp-1 agonist': 'GLP-1 Agonists',
            'glp-1 receptor agonist': 'GLP-1 Agonists',
            'sglt2 inhibitor': 'SGLT2 Inhibitors',
            'dpp-4 inhibitor': 'DPP-4 Inhibitors',
            'insulin therapy': 'Insulin Therapy',
            'basal insulin': 'Basal Insulin',
            'sulfonylurea': 'Sulfonylureas',
        }

        for pattern, standard in mappings.items():
            if pattern in name_lower:
                return standard

        # Default: title case
        return name.title()

    def _normalize_condition_name(self, name: str) -> str:
        """Normalize condition name to standard form"""
        name_lower = name.lower()

        if 'type 1' in name_lower:
            return 'Type 1 Diabetes'
        elif 'type 2' in name_lower:
            return 'Type 2 Diabetes'
        elif 'diabetes' in name_lower:
            return 'Type 2 Diabetes'  # Default assumption

        return name.title()

    def extract_all_entities(self, text: str) -> dict:
        """
        Extract all entities and relationships from text

        Args:
            text: Document text

        Returns:
            Dictionary with 'treatments', 'conditions', and 'relationships'
        """
        return {
            'treatments': self.extract_treatments(text),
            'conditions': self.extract_conditions(text),
            'relationships': self.extract_treats_relationships(text)
        }


def extract_from_sections(sections: dict) -> dict:
    """
    Extract entities from structured document sections

    Args:
        sections: Dictionary of section_name -> text_content

    Returns:
        Dictionary with extracted entities
    """
    extractor = MedicalEntityExtractor()

    # Combine all text
    all_text = '\n'.join(sections.values())

    # Extract entities
    entities = extractor.extract_all_entities(all_text)

    # Add section-specific context if needed
    entities['sections_analyzed'] = list(sections.keys())

    return entities


if __name__ == '__main__':
    # Test with sample text
    sample_text = """
    GLP-1 agonists are highly effective treatments for Type 2 Diabetes.
    SGLT2 inhibitors effectively treat Type 2 Diabetes through renal glucose excretion.
    DPP-4 inhibitors provide moderate glycemic control for Type 2 Diabetes.
    Insulin Therapy is essential for Type 1 Diabetes management.
    Basal insulin treats Type 2 Diabetes when oral agents are insufficient.
    """

    extractor = MedicalEntityExtractor()
    results = extractor.extract_all_entities(sample_text)

    print("Treatments found:")
    for t in sorted(results['treatments']):
        print(f"  - {t}")

    print("\nConditions found:")
    for c in sorted(results['conditions']):
        print(f"  - {c}")

    print("\nRelationships found:")
    for treatment, condition in results['relationships']:
        print(f"  - {treatment} → TREATS → {condition}")
