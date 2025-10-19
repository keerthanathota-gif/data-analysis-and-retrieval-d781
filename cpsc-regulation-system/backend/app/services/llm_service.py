"""
Mock LLM Service for CFR Agentic AI Application
This is a simplified version that doesn't require ML libraries
"""

import re
from typing import List, Dict, Any

class LLMService:
    def __init__(self, model_name: str = "mock-llm"):
        """
        Initialize mock LLM service
        
        Args:
            model_name: Model name (ignored in mock)
        """
        self.model_name = model_name
        print(f"Mock LLM service initialized (no actual model loaded)")
    
    def generate_text(self, prompt: str, max_length: int = 256) -> str:
        """
        Generate mock text based on prompt patterns
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            
        Returns:
            Generated mock text
        """
        # Simple pattern-based responses
        if "explain" in prompt.lower() and "parity" in prompt.lower():
            if "passed" in prompt:
                return "The item passed parity check, indicating proper structure and balanced content distribution."
            else:
                return "The item failed parity check, suggesting potential structural issues or imbalanced content."
        
        if "redundant" in prompt.lower():
            if "are redundant" in prompt:
                return "These items show significant similarity and overlap. Consider consolidating them to reduce duplication and improve clarity."
            else:
                return "While similar in some aspects, these items serve distinct regulatory purposes and should remain separate."
        
        if "overlap" in prompt.lower():
            return "These items share common regulatory themes including compliance requirements, safety standards, and reporting procedures."
        
        if "summarize" in prompt.lower():
            return "This group contains related regulatory content focusing on compliance, safety standards, and procedural requirements."
        
        if "name" in prompt.lower() or "title" in prompt.lower():
            return "Regulatory Standards Group"
        
        # Default response
        return "This item contains regulatory information relevant to compliance and safety standards."
    
    def generate_parity_justification(self, item_type: str, item_name: str, 
                                     check_result: bool, details: Dict) -> str:
        """
        Generate mock justification for parity check
        """
        if check_result:
            if item_type == "chapter":
                count = details.get('subchapter_count', 0)
                return f"The chapter contains {count} subchapters, providing a well-structured organization of regulatory content."
            elif item_type == "subchapter":
                count = details.get('part_count', 0)
                return f"The subchapter contains {count} parts, offering detailed coverage of specific regulatory areas."
            elif item_type == "section":
                length = details.get('text_length', 0)
                return f"The section contains {length} characters, providing comprehensive regulatory guidance."
            else:
                return f"The {item_type} passed parity check with proper structure."
        else:
            if item_type == "chapter":
                return "The chapter may have insufficient subchapters for comprehensive coverage."
            elif item_type == "subchapter":
                return "The subchapter may need additional parts for complete regulatory guidance."
            elif item_type == "section":
                return "The section may require more detailed content for clarity."
            else:
                return f"The {item_type} failed parity check and may need structural improvements."
    
    def generate_redundancy_justification(self, item1_name: str, item2_name: str,
                                         similarity_score: float, is_redundant: bool,
                                         overlap_content: str = None) -> str:
        """
        Generate mock justification for redundancy check
        """
        percent = int(similarity_score * 100)
        
        if is_redundant:
            return f"These items show {percent}% similarity, indicating significant redundancy. Consider consolidating them to eliminate duplication and improve clarity."
        else:
            return f"While {percent}% similar, these items address different regulatory aspects and should remain separate for comprehensive coverage."
    
    def generate_overlap_explanation(self, item1_name: str, item2_name: str,
                                    similarity_score: float) -> str:
        """
        Generate mock explanation for overlapping content
        """
        percent = int(similarity_score * 100)
        return f"These items share {percent}% similarity, primarily in areas of compliance requirements, safety standards, and procedural guidelines."
    
    def generate_cluster_summary(self, cluster_items: List[Dict[str, Any]], 
                                cluster_type: str) -> str:
        """
        Generate mock summary for a cluster
        """
        count = len(cluster_items)
        
        # Try to extract some meaningful info from the first few items
        topics = []
        for item in cluster_items[:3]:
            if cluster_type == 'section':
                subject = item.get('subject', '')
            else:
                subject = item.get('name', '')
            
            if subject:
                # Extract key words
                words = subject.split()[:5]
                topics.extend(words)
        
        if topics:
            topic_str = " ".join(list(set(topics))[:5])
            return f"This cluster contains {count} {cluster_type}s covering {topic_str} and related regulatory requirements."
        else:
            return f"This cluster groups {count} {cluster_type}s with related regulatory content focusing on compliance and safety standards."
    
    def generate_cluster_name(self, cluster_items: List[Dict[str, Any]],
                             cluster_type: str, summary: str = None) -> str:
        """
        Generate a mock name for a cluster
        """
        # Try to extract meaningful words from items
        words = []
        for item in cluster_items[:3]:
            if cluster_type == 'section':
                subject = item.get('subject', '')
            else:
                subject = item.get('name', '')
            
            if subject:
                # Get first significant word
                for word in subject.split():
                    if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with']:
                        words.append(word.capitalize())
                        break
        
        if words:
            return f"{' '.join(words[:2])} Standards Group"
        else:
            return f"{cluster_type.capitalize()} Regulatory Group"
    
    def generate_section_summary(self, section_text: str, section_subject: str) -> str:
        """
        Generate a mock summary of a section
        """
        if section_subject:
            return f"This section on '{section_subject}' provides regulatory guidance on compliance requirements and implementation procedures."
        else:
            return "This section contains important regulatory information for compliance and safety standards."


# Global instance
llm_service = None

def get_llm_service():
    """Get or create mock LLM service instance"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service