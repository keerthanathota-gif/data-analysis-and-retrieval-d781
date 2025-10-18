"""
LLM Service for CFR Agentic AI Application
Uses Google FLAN-T5-base for generating justifications, summaries, and cluster names
FLAN-T5 is instruction-tuned and excellent for summarization and explanations
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import List, Dict, Any
import re

class LLMService:
    def __init__(self, model_name: str = "google/flan-t5-base"):
        """
        Initialize LLM service with FLAN-T5-base
        
        Args:
            model_name: HuggingFace model name (default: flan-t5-base for quality)
        """
        print(f"Loading LLM model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        print(f"LLM model (FLAN-T5-base) loaded on {self.device}")
    
    def generate_text(self, prompt: str, max_length: int = 256) -> str:
        """
        Generate text using FLAN-T5
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            
        Returns:
            Generated text
        """
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                temperature=0.7,
                do_sample=False  # Use beam search for better quality
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text.strip()
    
    def generate_parity_justification(self, item_type: str, item_name: str, 
                                     check_result: bool, details: Dict) -> str:
        """
        Generate LLM justification for parity check
        
        Args:
            item_type: Type of item (chapter/subchapter/section)
            item_name: Name of the item
            check_result: Whether parity check passed
            details: Details about the parity check
            
        Returns:
            LLM-generated justification
        """
        status = "passed" if check_result else "failed"
        
        if item_type == "chapter":
            count = details.get('subchapter_count', 0)
            prompt = f"Explain why a chapter with {count} subchapters {status} the parity check. What does this indicate about its structure?"
        elif item_type == "subchapter":
            count = details.get('part_count', 0)
            prompt = f"Explain why a subchapter with {count} parts {status} the parity check. What does this mean for content organization?"
        elif item_type == "section":
            length = details.get('text_length', 0)
            prompt = f"Explain why a section with {length} characters of text {status} the parity check. What does this indicate?"
        else:
            prompt = f"Explain the parity check result for this {item_type}."
        
        response = self.generate_text(prompt, max_length=128)
        
        # Fallback if generation is poor
        if len(response) < 10:
            if check_result:
                response = f"The {item_type} passed parity check, indicating proper structure and content organization."
            else:
                response = f"The {item_type} failed parity check, suggesting structural issues or missing content."
        
        return response
    
    def generate_redundancy_justification(self, item1_name: str, item2_name: str,
                                         similarity_score: float, is_redundant: bool,
                                         overlap_content: str = None) -> str:
        """
        Generate LLM justification for redundancy check
        
        Args:
            item1_name: Name of first item
            item2_name: Name of second item
            similarity_score: Similarity score (0-1)
            is_redundant: Whether items are redundant
            overlap_content: Overlapping content sample
            
        Returns:
            LLM-generated justification
        """
        percent = int(similarity_score * 100)
        
        # Truncate names if too long
        name1 = item1_name[:60] if len(item1_name) > 60 else item1_name
        name2 = item2_name[:60] if len(item2_name) > 60 else item2_name
        
        if is_redundant:
            prompt = f"Two regulatory items '{name1}' and '{name2}' have {percent}% similarity. Explain why they are redundant and suggest if they should be consolidated."
        else:
            prompt = f"Two regulatory items '{name1}' and '{name2}' have {percent}% similarity but are not redundant. Explain why they should remain separate."
        
        response = self.generate_text(prompt, max_length=150)
        
        # Fallback if generation is poor
        if len(response) < 10:
            if is_redundant:
                response = f"These items show {percent}% similarity, indicating significant redundancy. Consider consolidating them to reduce duplication."
            else:
                response = f"While {percent}% similar, these items serve distinct purposes and should remain separate."
        
        return response
    
    def generate_overlap_explanation(self, item1_name: str, item2_name: str,
                                    similarity_score: float) -> str:
        """
        Generate explanation for overlapping content
        
        Args:
            item1_name: Name of first item
            item2_name: Name of second item
            similarity_score: Similarity score
            
        Returns:
            Explanation of overlap
        """
        percent = int(similarity_score * 100)
        
        # Truncate names if too long
        name1 = item1_name[:50] if len(item1_name) > 50 else item1_name
        name2 = item2_name[:50] if len(item2_name) > 50 else item2_name
        
        prompt = f"Explain what content overlaps between regulatory items '{name1}' and '{name2}' which have {percent}% similarity. What themes or topics do they share?"
        
        response = self.generate_text(prompt, max_length=128)
        
        # Fallback if generation is poor
        if len(response) < 10:
            response = f"These items share {percent}% similarity, likely overlapping in regulatory requirements, compliance standards, or policy guidelines."
        
        return response
    
    def generate_cluster_summary(self, cluster_items: List[Dict[str, Any]], 
                                cluster_type: str) -> str:
        """
        Generate summary for a cluster based on actual content
        
        Args:
            cluster_items: List of items in the cluster with text content
            cluster_type: Type of cluster (chapter/subchapter/section)
            
        Returns:
            LLM-generated cluster summary
        """
        # Collect actual text content from cluster items
        text_samples = []
        subjects = []
        
        for item in cluster_items[:5]:  # Analyze first 5 items for summary
            # Get subject/name
            if cluster_type == 'section':
                subject = item.get('subject', '') or item.get('section_number', '')
            else:
                subject = item.get('name', '')
            
            if subject:
                subjects.append(subject)
            
            # Get text content
            text = item.get('text', '')
            if text:
                # Sample first 200 characters of text
                text_samples.append(text[:200])
        
        # If we have text content, use it for better summary
        if text_samples:
            combined_text = " ".join(text_samples)
            # Truncate to prevent token limit
            combined_text = combined_text[:800]
            
            prompt = f"Summarize the common regulatory theme and purpose of this cluster of {len(cluster_items)} {cluster_type}s. Content sample: {combined_text}"
            
            response = self.generate_text(prompt, max_length=150)
        elif subjects:
            # Fallback to subjects if no text
            subjects_text = ", ".join(subjects[:3])
            prompt = f"Summarize the common theme of this cluster containing {len(cluster_items)} {cluster_type}s: {subjects_text}"
            response = self.generate_text(prompt, max_length=128)
        else:
            # Final fallback
            return f"This cluster contains {len(cluster_items)} {cluster_type}s with related regulatory content."
        
        # Validate response quality
        if len(response) < 15:
            response = f"This cluster groups {len(cluster_items)} {cluster_type}s covering similar regulatory requirements and compliance standards."
        
        return response
    
    def generate_cluster_name(self, cluster_items: List[Dict[str, Any]],
                             cluster_type: str, summary: str = None) -> str:
        """
        Generate a descriptive name for a cluster based on content
        
        Args:
            cluster_items: List of items in the cluster
            cluster_type: Type of cluster
            summary: Optional cluster summary
            
        Returns:
            Suggested cluster name (short)
        """
        # Use summary if available for better naming
        if summary and len(summary) > 20:
            prompt = f"Generate a short descriptive name (3-6 words) for this cluster: {summary[:200]}"
            name = self.generate_text(prompt, max_length=20)
            
            # Clean up the name
            name = re.sub(r'["\']', '', name)
            name = name.strip('.,;')
            
            # Validate and return if good
            if len(name) > 5 and len(name) < 60:
                return name
        
        # Fallback: extract from subjects/names
        subjects = []
        for item in cluster_items[:5]:
            if cluster_type == 'section':
                subject = item.get('subject', '')
            else:
                subject = item.get('name', '')
            
            if subject and len(subject) < 80:
                subjects.append(subject)
        
        if subjects:
            subjects_text = "; ".join(subjects[:3])
            prompt = f"Generate a concise name (4-6 words) for a cluster of {cluster_type}s including: {subjects_text}"
            name = self.generate_text(prompt, max_length=20)
            
            # Clean up
            name = re.sub(r'["\']', '', name)
            name = name.strip('.,;')
            
            if len(name) > 5 and len(name) < 60:
                return name
        
        # Final fallback
        return f"{cluster_type.capitalize()} Group {len(cluster_items)} Items"
    
    def generate_section_summary(self, section_text: str, section_subject: str) -> str:
        """
        Generate a brief summary of a section
        
        Args:
            section_text: Full section text
            section_subject: Section subject/title
            
        Returns:
            Brief summary
        """
        # Truncate text if too long
        text_sample = section_text[:500] if section_text else ""
        
        prompt = f"Summarize this regulation section titled '{section_subject}': {text_sample}"
        
        return self.generate_text(prompt, max_length=150)


# Global instance
llm_service = None

def get_llm_service():
    """Get or create LLM service instance (lazy loading)"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service
