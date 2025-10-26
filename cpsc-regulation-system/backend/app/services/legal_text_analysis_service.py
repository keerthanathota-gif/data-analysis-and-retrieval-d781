"""
Legal Text Analysis Service for CPSC Regulation System
Provides detailed legal analysis of regulation pairs including:
- Summary of relationship (parity/overlap/redundancy)
- Key common elements showing semantic similarity
- Distinct elements and differences
- Justification for similarity scores
"""

import json
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.database import Section, SectionEmbedding
from app.services.embedding_service_original import EmbeddingService
from app.services.llm_service import llm_service
import numpy as np


class LegalTextAnalysisService:
    """
    Service for detailed legal text analysis between regulation pairs
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.redundancy_threshold = 1.0   # 100% similarity - exact duplicates
        self.parity_threshold_min = 0.90  # 90% similarity - near duplicates
        self.parity_threshold_max = 1.0   # Up to 100%
        self.overlap_threshold_min = 0.80  # 80% similarity - significant overlap
        self.overlap_threshold_max = 0.90  # Up to 90%

    def analyze_regulation_pair(
        self,
        regulation_a_id: int,
        regulation_b_id: int,
        db: Session,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive legal analysis of two regulations

        Args:
            regulation_a_id: ID of first regulation
            regulation_b_id: ID of second regulation
            db: Database session
            use_llm: Whether to use LLM for enhanced analysis

        Returns:
            Detailed analysis including summary, key elements, differences, and justification
        """
        print(f"\n[Legal Analysis] Analyzing regulations {regulation_a_id} and {regulation_b_id}")

        # Fetch regulations
        reg_a = db.query(Section).filter(Section.id == regulation_a_id).first()
        reg_b = db.query(Section).filter(Section.id == regulation_b_id).first()

        if not reg_a or not reg_b:
            return {
                'error': 'One or both regulations not found',
                'regulation_a_id': regulation_a_id,
                'regulation_b_id': regulation_b_id
            }

        # Fetch embeddings
        emb_a = db.query(SectionEmbedding).filter(
            SectionEmbedding.section_id == regulation_a_id
        ).first()
        emb_b = db.query(SectionEmbedding).filter(
            SectionEmbedding.section_id == regulation_b_id
        ).first()

        if not emb_a or not emb_b:
            return {
                'error': 'Embeddings not found for one or both regulations',
                'regulation_a_id': regulation_a_id,
                'regulation_b_id': regulation_b_id
            }

        # Compute similarity scores
        similarity_scores = self._compute_similarity_scores(emb_a, emb_b)

        # Categorize relationship
        category = self._categorize_relationship(similarity_scores['overall'])

        # Basic structural analysis
        structural_analysis = self._analyze_structure(reg_a, reg_b)

        # Enhanced LLM analysis if requested
        llm_analysis = None
        if use_llm:
            try:
                llm_analysis = self._llm_enhanced_analysis(
                    reg_a, reg_b, similarity_scores, category
                )
            except Exception as e:
                print(f"[Legal Analysis] LLM analysis failed: {str(e)}")
                llm_analysis = None

        # Generate comprehensive report
        report = self._generate_analysis_report(
            reg_a, reg_b, similarity_scores, category,
            structural_analysis, llm_analysis
        )

        return report

    def _compute_similarity_scores(
        self,
        emb_a: SectionEmbedding,
        emb_b: SectionEmbedding
    ) -> Dict[str, float]:
        """
        Compute various similarity metrics
        """
        vec_a = np.array(json.loads(emb_a.embedding))
        vec_b = np.array(json.loads(emb_b.embedding))

        # Cosine similarity
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        cosine_similarity = dot_product / (norm_a * norm_b)

        # Convert to percentages
        return {
            'overall': float(cosine_similarity),
            'redundancy_score': float(cosine_similarity * 100),
            'parity_score': float(cosine_similarity * 100) if cosine_similarity >= 0.85 else 0.0,
            'overlap_score': float(cosine_similarity * 100) if cosine_similarity >= 0.70 else 0.0
        }

    def _categorize_relationship(self, similarity: float) -> Dict[str, str]:
        """
        Categorize the relationship based on similarity score
        """
        if similarity >= self.redundancy_threshold:
            return {
                'type': 'REDUNDANCY',
                'color': '#dc2626',
                'icon': '🔴',
                'description': 'Exact duplicate regulations (100% similar)',
                'recommendation': 'CONSOLIDATE: These are exact duplicates - merge immediately'
            }
        elif self.parity_threshold_min <= similarity < self.parity_threshold_max:
            return {
                'type': 'PARITY',
                'color': '#f59e0b',
                'icon': '🟠',
                'description': f'Near duplicate regulations ({similarity*100:.1f}% similar)',
                'recommendation': 'REVIEW: LLM validation to confirm semantic parity'
            }
        elif self.overlap_threshold_min <= similarity < self.parity_threshold_min:
            return {
                'type': 'OVERLAP',
                'color': '#3b82f6',
                'icon': '🔵',
                'description': 'Significant content overlap (80-90% similar)',
                'recommendation': 'CROSS-REFERENCE: Link regulations for better navigation'
            }
        else:
            return {
                'type': 'DISTINCT',
                'color': '#10b981',
                'icon': '🟢',
                'description': 'Regulations address different topics (<80% similar)',
                'recommendation': 'No action needed - regulations cover different areas'
            }

    def _analyze_structure(self, reg_a: Section, reg_b: Section) -> Dict[str, Any]:
        """
        Analyze structural similarities and differences
        """
        text_a = reg_a.text or ""
        text_b = reg_b.text or ""

        # Length comparison
        length_ratio = len(text_b) / len(text_a) if len(text_a) > 0 else 0

        # Word-level statistics
        words_a = text_a.split()
        words_b = text_b.split()
        common_words = set(words_a) & set(words_b)
        unique_to_a = set(words_a) - set(words_b)
        unique_to_b = set(words_b) - set(words_a)

        # Sentence count
        sentences_a = text_a.count('.') + text_a.count('!') + text_a.count('?')
        sentences_b = text_b.count('.') + text_b.count('!') + text_b.count('?')

        return {
            'length_comparison': {
                'regulation_a_chars': len(text_a),
                'regulation_b_chars': len(text_b),
                'length_ratio': round(length_ratio, 2),
                'difference': abs(len(text_a) - len(text_b))
            },
            'word_analysis': {
                'common_words_count': len(common_words),
                'unique_to_a_count': len(unique_to_a),
                'unique_to_b_count': len(unique_to_b),
                'total_words_a': len(words_a),
                'total_words_b': len(words_b)
            },
            'sentence_count': {
                'regulation_a': sentences_a,
                'regulation_b': sentences_b
            }
        }

    def _llm_enhanced_analysis(
        self,
        reg_a: Section,
        reg_b: Section,
        similarity_scores: Dict[str, float],
        category: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Use LLM for enhanced legal analysis
        """
        # Build category-specific guidance
        if category['type'] == 'PARITY':
            category_focus = """
You are an expert in U.S. federal regulatory document analysis.

CRITICAL TASK: Determine if these regulations are in SEMANTIC PARITY.

Semantic parity means: They describe the same rule, responsibility, or condition, even if the language differs.

Instructions:
1. Compare Regulation A and Regulation B carefully
2. Determine if they express the SAME MEANING and INTENT
3. If YES (semantic parity exists):
   - Output: {{"is_parity": true, "summary": "2-3 sentence summary of shared meaning"}}
4. If NO (not in semantic parity):
   - Output: {{"is_parity": false, "summary": ""}}

Be concise and factual. Focus on semantic equivalence, not just textual similarity."""
        elif category['type'] == 'OVERLAP':
            category_focus = """
You are an expert in U.S. federal regulatory document analysis.

CRITICAL TASK: Determine if these regulations have SEMANTIC OVERLAP.

Semantic overlap means: They share PARTIALLY SIMILAR rules, responsibilities, or conditions.

Instructions:
1. Compare Regulation A and Regulation B carefully
2. Determine if they have partial overlap in meaning/intent
3. If YES (semantic overlap exists):
   - Output: {{"is_overlap": true, "summary": "2-3 sentence summary of what overlaps and what differs"}}
4. If NO (no overlap, completely different):
   - Output: {{"is_overlap": false, "summary": ""}}

Be concise and factual. Focus on semantic overlap, not just textual similarity."""
        elif category['type'] == 'REDUNDANCY':
            category_focus = """
IMPORTANT: These regulations show REDUNDANCY (≥95% similar).
Focus your summary on:
- How these regulations are nearly IDENTICAL
- Whether consolidation would improve clarity
- Any minor differences that might justify keeping them separate
- Impact of potential duplication on compliance"""
        else:
            category_focus = """
These regulations are DISTINCT (below 70% similarity).
Focus your summary on the different regulatory areas they address."""

        prompt = f"""You are an expert in U.S. federal regulatory document analysis.

You will receive a pair of regulations (Regulation A and Regulation B).
Your task: {"Confirm if they are in SEMANTIC PARITY (express the same regulatory intent)" if category['type'] == 'PARITY' else "Identify SEMANTIC OVERLAP (share some common areas but differ in others)"}.

{"PARITY means: Both regulations express the SAME regulatory intent, rule, or requirement, even if worded differently." if category['type'] == 'PARITY' else "OVERLAP means: Regulations cover SOME of the same areas but differ in other sections."}

For this pair:
1. Evaluate based on **meaning and regulatory intent**, not textual similarity.
2. If {"semantic parity exists" if category['type'] == 'PARITY' else "semantic overlap exists"}:
   - Set "{"is_parity" if category['type'] == 'PARITY' else "is_overlap"}" = true.
   - Write a **2-line summary** that explains:
     {"- WHAT specific regulatory requirement/rule they BOTH establish (shared intent)" if category['type'] == 'PARITY' else "- WHAT areas they OVERLAP in and WHAT differs between them"}
3. If {"no parity" if category['type'] == 'PARITY' else "no overlap (completely different)"}:
   - Set "{"is_parity" if category['type'] == 'PARITY' else "is_overlap"}" = false.
   - Keep "summary" empty.

Return the result **strictly in JSON** format as follows:

{{
  "pair_id": "{reg_a.section_number} vs {reg_b.section_number}",
  "{"is_parity" if category['type'] == 'PARITY' else "is_overlap"}": true/false,
  "summary": "2-line explanation"
}}

**Example of GOOD summary:**
{"Both regulations establish that manufacturers must label hazardous products with specific warning statements. They define the same labeling requirements and enforcement mechanisms." if category['type'] == 'PARITY' else "Regulation A covers data storage, sharing, and deletion, while Regulation B covers data sharing and breach notification. They overlap in data sharing requirements but differ in storage and breach protocols."}

**Example of BAD summary:**
{"Regulations show 85% similarity and use different wording." if category['type'] == 'PARITY' else "These regulations are 75% similar and address related topics."}

---

**Regulation A:**
Section: {reg_a.section_number}
Subject: {reg_a.subject}
Text: "{reg_a.text[:1500] if reg_a.text else 'No text available'}"

**Regulation B:**
Section: {reg_b.section_number}
Subject: {reg_b.subject}
Text: "{reg_b.text[:1500] if reg_b.text else 'No text available'}"

---

Now analyze and return ONLY the JSON result with a summary that explains WHY parity exists."""

        try:
            # Call LLM service
            response = llm_service.generate_response(prompt)

            # Parse JSON response
            try:
                # Extract JSON from response (in case LLM adds extra text)
                import re
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group()
                    result = json.loads(json_str)
                else:
                    result = json.loads(response)

                # Check if parity/overlap was detected
                is_valid = result.get('is_parity', False) if category['type'] == 'PARITY' else result.get('is_overlap', False)

                if not is_valid:
                    print(f"[Legal Analysis] LLM detected no true {category['type'].lower()} - marking for deletion")
                    return {
                        'status': 'NO_PARITY_OR_OVERLAP',
                        'category_checked': category['type'],
                        'should_delete': True,
                        'pair_id': result.get('pair_id', 'unknown'),
                        'raw_response': response
                    }

                # Parity/Overlap verified - return structured format
                return {
                    'status': 'VERIFIED',
                    'pair_id': result.get('pair_id'),
                    'is_parity': result.get('is_parity') if category['type'] == 'PARITY' else None,
                    'is_overlap': result.get('is_overlap') if category['type'] == 'OVERLAP' else None,
                    'summary': result.get('summary', ''),
                    'raw_analysis': response,
                    'parsed_sections': {
                        'summary': result.get('summary', ''),
                        'common_elements': [],  # Not needed in new format
                        'distinct_elements': [],  # Not needed in new format
                        'justification': ''  # Not needed in new format
                    }
                }
            except json.JSONDecodeError as je:
                print(f"[Legal Analysis] Failed to parse JSON response: {je}")
                print(f"Response was: {response}")
                # Fall back to basic analysis
                return {
                    'status': 'PARSE_ERROR',
                    'raw_response': response,
                    'error': str(je)
                }

        except Exception as e:
            raise Exception(f"LLM analysis failed: {str(e)}")

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured sections
        """
        sections = {
            'summary': '',
            'common_elements': [],
            'distinct_elements': [],
            'justification': ''
        }

        # Simple parsing based on markdown headers
        current_section = None
        current_text = []

        for line in response.split('\n'):
            line = line.strip()

            if 'summary of relationship' in line.lower():
                current_section = 'summary'
                current_text = []
            elif 'key common' in line.lower() or 'parity elements' in line.lower():
                if current_section and current_text:
                    self._save_section(sections, current_section, current_text)
                current_section = 'common_elements'
                current_text = []
            elif 'overlap' in line.lower() or 'distinct elements' in line.lower():
                if current_section and current_text:
                    self._save_section(sections, current_section, current_text)
                current_section = 'distinct_elements'
                current_text = []
            elif 'justification' in line.lower():
                if current_section and current_text:
                    self._save_section(sections, current_section, current_text)
                current_section = 'justification'
                current_text = []
            elif line:
                current_text.append(line)

        # Save last section
        if current_section and current_text:
            self._save_section(sections, current_section, current_text)

        return sections

    def _save_section(self, sections: Dict, section_name: str, text_lines: List[str]):
        """
        Save parsed section content
        """
        content = '\n'.join(text_lines).strip()

        if section_name in ['common_elements', 'distinct_elements']:
            # Parse bullet points
            items = []
            for line in text_lines:
                if line.startswith(('-', '*', '•')) or (line and line[0].isdigit() and '. ' in line):
                    items.append(line.lstrip('-*•0123456789. ').strip())
            sections[section_name] = items if items else [content]
        else:
            sections[section_name] = content

    def _generate_analysis_report(
        self,
        reg_a: Section,
        reg_b: Section,
        similarity_scores: Dict[str, float],
        category: Dict[str, str],
        structural_analysis: Dict[str, Any],
        llm_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report in requested format
        """
        # Check if LLM detected no parity/overlap - return deletion marker
        if llm_analysis and llm_analysis.get('should_delete'):
            return {
                'status': 'DELETE',
                'reason': f"LLM verified no true {llm_analysis['category_checked']} exists",
                'regulation_a_id': reg_a.id,
                'regulation_b_id': reg_b.id,
                'category_checked': llm_analysis['category_checked'],
                'similarity_score': similarity_scores['overall']*100,
                'message': 'This comparison should be removed - no actual parity or overlap detected'
            }

        report = {
            'regulation_a': {
                'id': reg_a.id,
                'section_number': reg_a.section_number,
                'subject': reg_a.subject,
                'citation': reg_a.citation,
                'text_preview': reg_a.text[:500] if reg_a.text else "No text available",
                'text_full': reg_a.text
            },
            'regulation_b': {
                'id': reg_b.id,
                'section_number': reg_b.section_number,
                'subject': reg_b.subject,
                'citation': reg_b.citation,
                'text_preview': reg_b.text[:500] if reg_b.text else "No text available",
                'text_full': reg_b.text
            },
            'similarity_metrics': {
                'overall_similarity': f"{similarity_scores['overall']*100:.2f}%",
                'redundancy_score': f"{similarity_scores['redundancy_score']:.2f}%",
                'parity_score': f"{similarity_scores['parity_score']:.2f}%",
                'overlap_score': f"{similarity_scores['overlap_score']:.2f}%",
                'category': category['type'],
                'category_description': category['description'],
                'category_icon': category['icon'],
                'recommendation': category['recommendation']
            },
            'structural_analysis': structural_analysis
        }

        # Add LLM analysis if available and verified
        if llm_analysis and llm_analysis.get('status') == 'VERIFIED':
            report['legal_analysis'] = {
                'verification_status': 'VERIFIED',
                'summary_of_relationship': llm_analysis['parsed_sections']['summary'],
                'key_common_or_parity_elements': llm_analysis['parsed_sections']['common_elements'],
                'overlap_or_distinct_elements': llm_analysis['parsed_sections']['distinct_elements'],
                'justification_for_scores': llm_analysis['parsed_sections']['justification'],
                'full_analysis': llm_analysis['raw_analysis']
            }
        else:
            # Fallback to basic analysis
            report['legal_analysis'] = self._generate_basic_analysis(
                reg_a, reg_b, similarity_scores, category, structural_analysis
            )

        return report

    def _generate_basic_analysis(
        self,
        reg_a: Section,
        reg_b: Section,
        similarity_scores: Dict[str, float],
        category: Dict[str, str],
        structural_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate basic analysis without LLM (fallback)
        """
        similarity = similarity_scores['overall']

        if similarity >= 0.95:
            summary = f"Regulations {reg_a.section_number} and {reg_b.section_number} are nearly identical with {similarity*100:.1f}% similarity. They appear to be duplicate regulations covering the same requirements with minimal or no differences in wording or content."
        elif similarity >= 0.85:
            summary = f"Regulations {reg_a.section_number} and {reg_b.section_number} show high parity with {similarity*100:.1f}% similarity. They convey substantially the same meaning but use different wording or structure. This suggests they may address the same regulatory requirements from different perspectives."
        elif similarity >= 0.70:
            summary = f"Regulations {reg_a.section_number} and {reg_b.section_number} have moderate overlap with {similarity*100:.1f}% similarity. They share common themes or requirements but also contain distinct provisions. They likely address related but not identical aspects of consumer product safety."
        else:
            summary = f"Regulations {reg_a.section_number} and {reg_b.section_number} are largely distinct with only {similarity*100:.1f}% similarity. They address different topics or requirements within the regulatory framework."

        return {
            'summary_of_relationship': summary,
            'key_common_or_parity_elements': [
                f"Both regulations are under CFR Title 16 (Consumer Product Safety)",
                f"Share {structural_analysis['word_analysis']['common_words_count']} common words",
                f"Similar document structure with {structural_analysis['sentence_count']['regulation_a']} and {structural_analysis['sentence_count']['regulation_b']} sentences respectively"
            ],
            'overlap_or_distinct_elements': [
                f"Regulation A has {structural_analysis['word_analysis']['unique_to_a_count']} unique terms",
                f"Regulation B has {structural_analysis['word_analysis']['unique_to_b_count']} unique terms",
                f"Length difference of {structural_analysis['length_comparison']['difference']} characters"
            ],
            'justification_for_scores': f"The computed similarity score of {similarity*100:.1f}% appears reasonable based on structural analysis. The regulations share {structural_analysis['word_analysis']['common_words_count']} common words out of {structural_analysis['word_analysis']['total_words_a']} and {structural_analysis['word_analysis']['total_words_b']} total words respectively. The {category['type']} categorization is appropriate given this level of semantic overlap."
        }


# Global instance
legal_text_analysis_service = LegalTextAnalysisService()
