"""
Citation and source tracker for managing research sources and citations.
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional
from .base import BaseComponent

class BaseCitationTracker(BaseComponent):
    """Interface for citation and source tracking."""
    
    def register_source(self, source_data):
        """
        Register a new information source.
        
        Parameters:
            source_data: Dict containing source metadata (type, url, author, etc.)
            
        Returns:
            source_id: Unique identifier for the registered source
        """
        raise NotImplementedError
    
    def cite_source(self, source_id, content_fragment, context=None):
        """
        Create a citation for a specific content fragment.
        
        Parameters:
            source_id: ID of the source being cited
            content_fragment: The specific text/data being cited
            context: Optional context information (page numbers, etc.)
            
        Returns:
            citation_id: Unique identifier for this citation
        """
        raise NotImplementedError
    
    def get_citation(self, citation_id, format_style=None):
        """
        Get a formatted citation by ID.
        
        Parameters:
            citation_id: ID of the citation
            format_style: Optional citation style (APA, MLA, Chicago, etc.)
            
        Returns:
            Formatted citation string
        """
        raise NotImplementedError
    
    def get_bibliography(self, citation_ids=None, format_style=None):
        """
        Generate a bibliography from citations.
        
        Parameters:
            citation_ids: Optional list of citation IDs to include
            format_style: Optional citation style
            
        Returns:
            Formatted bibliography
        """
        raise NotImplementedError
    
    def assess_source_quality(self, source_id, criteria=None):
        """
        Assess the quality and reliability of a source.
        
        Parameters:
            source_id: ID of the source to assess
            criteria: Optional specific criteria to assess
            
        Returns:
            Dict with quality assessment scores
        """
        raise NotImplementedError
    
    def get_source_provenance(self, content_fragment):
        """
        Find the source of a specific content fragment.
        
        Parameters:
            content_fragment: Text fragment to trace
            
        Returns:
            List of possible source matches with confidence scores
        """
        raise NotImplementedError
    
    def export_citations(self, format_type, citation_ids=None):
        """
        Export citations to various formats (BibTeX, RIS, etc.).
        
        Parameters:
            format_type: Export format type
            citation_ids: Optional specific citations to export
            
        Returns:
            Formatted export data
        """
        raise NotImplementedError


class DefaultCitationTracker(BaseCitationTracker):
    """Default implementation of the citation and source tracker."""
    
    def __init__(self, config=None):
        """Initialize the citation tracker."""
        super().__init__(config)
        self.sources = {}
        self.citations = {}
        self.citation_formats = {
            "apa": self._format_apa,
            "mla": self._format_mla,
            "chicago": self._format_chicago
        }
    
    def register_source(self, source_data):
        """Register a new information source."""
        if not source_data:
            return None
        
        # Generate a unique ID
        source_id = str(uuid.uuid4())
        
        # Add timestamp
        source_data["registered_at"] = time.time()
        
        # Store source
        self.sources[source_id] = source_data
        
        return source_id
    
    def cite_source(self, source_id, content_fragment, context=None):
        """Create a citation for a specific content fragment."""
        if source_id not in self.sources:
            return None
        
        # Generate a unique ID
        citation_id = str(uuid.uuid4())
        
        # Create citation record
        citation = {
            "id": citation_id,
            "source_id": source_id,
            "content_fragment": content_fragment,
            "context": context or {},
            "created_at": time.time()
        }
        
        # Store citation
        self.citations[citation_id] = citation
        
        return citation_id
    
    def get_citation(self, citation_id, format_style=None):
        """Get a formatted citation by ID."""
        if citation_id not in self.citations:
            return None
        
        citation = self.citations[citation_id]
        source_id = citation["source_id"]
        
        if source_id not in self.sources:
            return None
        
        source = self.sources[source_id]
        
        # Default to APA style if not specified
        format_style = format_style or "apa"
        
        # Use the appropriate formatter
        formatter = self.citation_formats.get(format_style.lower(), self._format_apa)
        return formatter(source, citation)
    
    def get_bibliography(self, citation_ids=None, format_style=None):
        """Generate a bibliography from citations."""
        # Default to all citations if not specified
        if citation_ids is None:
            citation_ids = list(self.citations.keys())
        
        # Default to APA style if not specified
        format_style = format_style or "apa"
        
        # Get unique sources
        source_ids = set()
        for citation_id in citation_ids:
            if citation_id in self.citations:
                source_ids.add(self.citations[citation_id]["source_id"])
        
        # Generate bibliography entries
        entries = []
        for source_id in source_ids:
            if source_id in self.sources:
                source = self.sources[source_id]
                
                # Use the appropriate formatter
                formatter = self.citation_formats.get(format_style.lower(), self._format_apa)
                entry = formatter(source, None)  # No specific citation for bibliography
                entries.append(entry)
        
        # Sort entries alphabetically
        entries.sort()
        
        return entries
    
    def assess_source_quality(self, source_id, criteria=None):
        """Assess the quality and reliability of a source."""
        if source_id not in self.sources:
            return None
        
        source = self.sources[source_id]
        
        # Default criteria
        default_criteria = {
            "relevance": True,
            "credibility": True,
            "timeliness": True
        }
        
        # Use provided criteria or defaults
        criteria = criteria or default_criteria
        
        # Simple scoring (this would be more sophisticated in a real implementation)
        scores = {}
        
        if "relevance" in criteria:
            # Placeholder for relevance scoring
            scores["relevance"] = 0.8  # Default high score
        
        if "credibility" in criteria:
            # Assess credibility based on source type
            source_type = source.get("type", "").lower()
            if source_type in ["academic", "journal", "government"]:
                scores["credibility"] = 0.9
            elif source_type in ["news", "blog"]:
                scores["credibility"] = 0.7
            elif source_type in ["social_media"]:
                scores["credibility"] = 0.4
            else:
                scores["credibility"] = 0.6
        
        if "timeliness" in criteria:
            # Assess timeliness based on publication date
            if "published_date" in source:
                try:
                    # Calculate age in days
                    current_time = time.time()
                    pub_time = time.mktime(time.strptime(source["published_date"], "%Y-%m-%d"))
                    age_days = (current_time - pub_time) / (60 * 60 * 24)
                    
                    # Score based on age
                    if age_days < 30:  # Less than a month
                        scores["timeliness"] = 0.9
                    elif age_days < 365:  # Less than a year
                        scores["timeliness"] = 0.7
                    else:
                        scores["timeliness"] = 0.5
                except:
                    scores["timeliness"] = 0.6  # Default if date parsing fails
            else:
                scores["timeliness"] = 0.6  # Default if no date
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores) if scores else 0
        
        return {
            "source_id": source_id,
            "scores": scores,
            "overall_score": overall_score
        }
    
    def get_source_provenance(self, content_fragment):
        """Find the source of a specific content fragment."""
        if not content_fragment:
            return []
        
        matches = []
        
        # Simple string matching (a real implementation would use more sophisticated techniques)
        for citation_id, citation in self.citations.items():
            cited_text = citation.get("content_fragment", "")
            
            if not cited_text:
                continue
            
            # Check if the fragment is contained in the citation
            if content_fragment in cited_text:
                source_id = citation["source_id"]
                
                if source_id in self.sources:
                    matches.append({
                        "citation_id": citation_id,
                        "source_id": source_id,
                        "confidence": 1.0,  # Perfect match
                        "source_data": self.sources[source_id]
                    })
            
            # Check for partial matches
            elif len(content_fragment) > 10:  # Only for substantial fragments
                # Simple similarity measure (not ideal)
                similarity = self._text_similarity(content_fragment, cited_text)
                
                if similarity > 0.7:  # Arbitrary threshold
                    source_id = citation["source_id"]
                    
                    if source_id in self.sources:
                        matches.append({
                            "citation_id": citation_id,
                            "source_id": source_id,
                            "confidence": similarity,
                            "source_data": self.sources[source_id]
                        })
        
        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        return matches
    
    def export_citations(self, format_type, citation_ids=None):
        """Export citations to various formats."""
        # Default to all citations if not specified
        if citation_ids is None:
            citation_ids = list(self.citations.keys())
        
        if format_type.lower() == "bibtex":
            return self._export_bibtex(citation_ids)
        elif format_type.lower() == "ris":
            return self._export_ris(citation_ids)
        else:
            return None
    
    def _format_apa(self, source, citation=None):
        """Format a citation in APA style."""
        # Extract source data
        source_type = source.get("type", "website").lower()
        
        if source_type == "journal" or source_type == "article":
            # Journal article format
            authors = source.get("authors", [])
            year = source.get("year", "n.d.")
            title = source.get("title", "Untitled")
            journal = source.get("journal", "Unknown Journal")
            volume = source.get("volume", "")
            issue = source.get("issue", "")
            pages = source.get("pages", "")
            url = source.get("url", "")
            
            # Format authors
            author_text = self._format_authors(authors)
            
            # Basic format: Author(s). (Year). Title. Journal, Volume(Issue), Pages. URL
            citation_text = f"{author_text} ({year}). {title}. "
            
            if journal:
                citation_text += f"{journal}"
                
                if volume:
                    citation_text += f", {volume}"
                    
                    if issue:
                        citation_text += f"({issue})"
                
                if pages:
                    citation_text += f", {pages}"
                
                citation_text += "."
            
            if url:
                citation_text += f" Retrieved from {url}"
            
            return citation_text
            
        elif source_type == "book":
            # Book format
            authors = source.get("authors", [])
            year = source.get("year", "n.d.")
            title = source.get("title", "Untitled")
            publisher = source.get("publisher", "")
            location = source.get("location", "")
            
            # Format authors
            author_text = self._format_authors(authors)
            
            # Basic format: Author(s). (Year). Title. Location: Publisher.
            citation_text = f"{author_text} ({year}). {title}. "
            
            if location and publisher:
                citation_text += f"{location}: {publisher}."
            elif publisher:
                citation_text += f"{publisher}."
            
            return citation_text
            
        else:
            # Website/generic format
            authors = source.get("authors", [])
            year = source.get("year", "n.d.")
            title = source.get("title", "Untitled")
            site_name = source.get("site_name", "")
            url = source.get("url", "")
            accessed_date = source.get("accessed_date", "")
            
            # Format authors
            author_text = self._format_authors(authors)
            
            # Basic format: Author(s). (Year). Title. Site Name. URL
            citation_text = f"{author_text} ({year}). {title}. "
            
            if site_name:
                citation_text += f"{site_name}. "
            
            if url:
                citation_text += f"Retrieved from {url}"
                
                if accessed_date:
                    citation_text += f" on {accessed_date}"
            
            return citation_text
    
    def _format_mla(self, source, citation=None):
        """Format a citation in MLA style."""
        # Extract source data
        source_type = source.get("type", "website").lower()
        
        if source_type == "journal" or source_type == "article":
            # Journal article format
            authors = source.get("authors", [])
            title = source.get("title", "Untitled")
            journal = source.get("journal", "Unknown Journal")
            volume = source.get("volume", "")
            issue = source.get("issue", "")
            year = source.get("year", "n.d.")
            pages = source.get("pages", "")
            url = source.get("url", "")
            
            # Format authors
            author_text = self._format_authors_mla(authors)
            
            # Basic format: Author(s). "Title." Journal, vol. Volume, no. Issue, Year, pp. Pages. URL.
            citation_text = f"{author_text}. \"{title}.\" {journal}"
            
            if volume:
                citation_text += f", vol. {volume}"
            
            if issue:
                citation_text += f", no. {issue}"
            
            if year:
                citation_text += f", {year}"
            
            if pages:
                citation_text += f", pp. {pages}"
            
            citation_text += "."
            
            if url:
                citation_text += f" {url}."
            
            return citation_text
            
        elif source_type == "book":
            # Book format
            authors = source.get("authors", [])
            title = source.get("title", "Untitled")
            publisher = source.get("publisher", "")
            year = source.get("year", "n.d.")
            
            # Format authors
            author_text = self._format_authors_mla(authors)
            
            # Basic format: Author(s). Title. Publisher, Year.
            citation_text = f"{author_text}. {title}. "
            
            if publisher:
                citation_text += f"{publisher}"
                
                if year:
                    citation_text += f", {year}"
                
                citation_text += "."
            
            return citation_text
            
        else:
            # Website/generic format
            authors = source.get("authors", [])
            title = source.get("title", "Untitled")
            site_name = source.get("site_name", "")
            publisher = source.get("publisher", "")
            date = source.get("date", source.get("year", "n.d."))
            url = source.get("url", "")
            accessed_date = source.get("accessed_date", "")
            
            # Format authors
            author_text = self._format_authors_mla(authors)
            
            # Basic format: Author(s). "Title." Site Name, Publisher, Date, URL. Accessed Date.
            citation_text = f"{author_text}. \"{title}.\" "
            
            if site_name:
                citation_text += f"{site_name}"
                
                if publisher:
                    citation_text += f", {publisher}"
                
                if date:
                    citation_text += f", {date}"
                
                citation_text += ", "
            
            if url:
                citation_text += f"{url}."
                
                if accessed_date:
                    citation_text += f" Accessed {accessed_date}."
            
            return citation_text
    
    def _format_chicago(self, source, citation=None):
        """Format a citation in Chicago style."""
        # Extract source data
        source_type = source.get("type", "website").lower()
        
        if source_type == "journal" or source_type == "article":
            # Journal article format
            authors = source.get("authors", [])
            title = source.get("title", "Untitled")
            journal = source.get("journal", "Unknown Journal")
            volume = source.get("volume", "")
            issue = source.get("issue", "")
            year = source.get("year", "n.d.")
            pages = source.get("pages", "")
            
            # Format authors
            author_text = self._format_authors(authors)
            
            # Basic format: Author(s). "Title." Journal Volume, no. Issue (Year): Pages.
            citation_text = f"{author_text}. \"{title}.\" {journal}"
            
            if volume:
                citation_text += f" {volume}"
                
                if issue:
                    citation_text += f", no. {issue}"
            
            if year:
                citation_text += f" ({year})"
            
            if pages:
                citation_text += f": {pages}"
            
            citation_text += "."
            
            return citation_text
            
        elif source_type == "book":
            # Book format
            authors = source.get("authors", [])
            title = source.get("title", "Untitled")
            publisher = source.get("publisher", "")
            location = source.get("location", "")
            year = source.get("year", "n.d.")
            
            # Format authors
            author_text = self._format_authors(authors)
            
            # Basic format: Author(s). Title. Location: Publisher, Year.
            citation_text = f"{author_text}. {title}. "
            
            if location and publisher:
                citation_text += f"{location}: {publisher}"
            elif publisher:
                citation_text += f"{publisher}"
            
            if year:
                citation_text += f", {year}"
            
            citation_text += "."
            
            return citation_text
            
        else:
            # Website/generic format
            authors = source.get("authors", [])
            title = source.get("title", "Untitled")
            site_name = source.get("site_name", "")
            publisher = source.get("publisher", "")
            date = source.get("date", "")
            url = source.get("url", "")
            accessed_date = source.get("accessed_date", "")
            
            # Format authors
            author_text = self._format_authors(authors)
            
            # Basic format: Author(s). "Title." Site Name. Publisher, Date. URL.
            citation_text = f"{author_text}. \"{title}.\" "
            
            if site_name:
                citation_text += f"{site_name}. "
            
            if publisher:
                citation_text += f"{publisher}"
                
                if date:
                    citation_text += f", {date}"
                
                citation_text += ". "
            
            if url:
                citation_text += f"{url}."
                
                if accessed_date:
                    citation_text += f" Accessed {accessed_date}."
            
            return citation_text
    
    def _format_authors(self, authors):
        """Format author names for citations."""
        if not authors:
            return "Unknown"
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _format_authors_mla(self, authors):
        """Format author names for MLA citations."""
        if not authors:
            return "Unknown"
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    def _export_bibtex(self, citation_ids):
        """Export citations to BibTeX format."""
        bibtex_entries = []
        
        for citation_id in citation_ids:
            if citation_id not in self.citations:
                continue
            
            citation = self.citations[citation_id]
            source_id = citation["source_id"]
            
            if source_id not in self.sources:
                continue
            
            source = self.sources[source_id]
            source_type = source.get("type", "misc").lower()
            
            # Map source type to BibTeX entry type
            entry_type = {
                "journal": "article",
                "article": "article",
                "book": "book",
                "website": "misc",
                "conference": "inproceedings"
            }.get(source_type, "misc")
            
            # Generate a key for the entry
            first_author = source.get("authors", ["Unknown"])[0].split()[-1]  # Last name
            year = source.get("year", "nd")
            key = f"{first_author}{year}"
            
            # Start the entry
            entry = f"@{entry_type}{{{key},\n"
            
            # Add fields
            if "authors" in source:
                authors = " and ".join(source["authors"])
                entry += f"  author = {{{authors}}},\n"
            
            if "title" in source:
                entry += f"  title = {{{source['title']}}},\n"
            
            if entry_type == "article":
                if "journal" in source:
                    entry += f"  journal = {{{source['journal']}}},\n"
                
                if "volume" in source:
                    entry += f"  volume = {{{source['volume']}}},\n"
                
                if "issue" in source:
                    entry += f"  number = {{{source['issue']}}},\n"
                
                if "pages" in source:
                    entry += f"  pages = {{{source['pages']}}},\n"
            
            if entry_type == "book":
                if "publisher" in source:
                    entry += f"  publisher = {{{source['publisher']}}},\n"
                
                if "location" in source:
                    entry += f"  address = {{{source['location']}}},\n"
            
            if "year" in source:
                entry += f"  year = {{{source['year']}}},\n"
            
            if "url" in source:
                entry += f"  url = {{{source['url']}}},\n"
            
            # Close the entry
            entry += "}\n"
            
            bibtex_entries.append(entry)
        
        return "\n".join(bibtex_entries)
    
    def _export_ris(self, citation_ids):
        """Export citations to RIS format."""
        ris_entries = []
        
        for citation_id in citation_ids:
            if citation_id not in self.citations:
                continue
            
            citation = self.citations[citation_id]
            source_id = citation["source_id"]
            
            if source_id not in self.sources:
                continue
            
            source = self.sources[source_id]
            source_type = source.get("type", "misc").lower()
            
            # Map source type to RIS type
            ris_type = {
                "journal": "JOUR",
                "article": "JOUR",
                "book": "BOOK",
                "website": "ELEC",
                "conference": "CONF"
            }.get(source_type, "GEN")
            
            # Start the entry
            entry = [f"TY  - {ris_type}"]
            
            # Add fields
            for author in source.get("authors", []):
                entry.append(f"AU  - {author}")
            
            if "title" in source:
                entry.append(f"TI  - {source['title']}")
            
            if ris_type == "JOUR":
                if "journal" in source:
                    entry.append(f"JO  - {source['journal']}")
                
                if "volume" in source:
                    entry.append(f"VL  - {source['volume']}")
                
                if "issue" in source:
                    entry.append(f"IS  - {source['issue']}")
                
                if "pages" in source:
                    entry.append(f"SP  - {source['pages']}")
            
            if ris_type == "BOOK":
                if "publisher" in source:
                    entry.append(f"PB  - {source['publisher']}")
                
                if "location" in source:
                    entry.append(f"CY  - {source['location']}")
            
            if "year" in source:
                entry.append(f"PY  - {source['year']}")
            
            if "url" in source:
                entry.append(f"UR  - {source['url']}")
            
            # End the entry
            entry.append("ER  - ")
            
            ris_entries.append("\n".join(entry))
        
        return "\n\n".join(ris_entries)
    
    def _text_similarity(self, text1, text2):
        """
        Calculate a simple similarity score between two texts.
        
        This is a very basic implementation using word overlap.
        A real implementation would use more sophisticated measures.
        """
        # Tokenize into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
