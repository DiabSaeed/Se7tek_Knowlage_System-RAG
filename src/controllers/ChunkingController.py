from .BaseController import BaseController
from langchain_core.documents import Document
import re
import logging

logger = logging.getLogger()

class ChunckingController(BaseController):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def _is_table_row(self, text: str) -> bool:
        """Check if text is a table row extracted by LlamaParse"""
        return bool(re.search(r'Study/Author:\s*\w+', text))
    
    def _extract_study_name(self, text: str) -> str:
        """Extract study name for grouping"""
        match = re.search(r'Study/Author:\s*([^,]+)', text)
        return match.group(1).strip() if match else ""
    
    def _group_by_table(self, text: str) -> list[str]:
        """Group table rows together, keep prose separate"""
        lines = text.split('\n')
        groups = []
        current_table = []
        current_prose = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if self._is_table_row(line):
                # If we were building prose, save it
                if current_prose:
                    groups.append('\n'.join(current_prose))
                    current_prose = []
                current_table.append(line)
            else:
                # If we were building table, save it as one chunk
                if current_table:
                    groups.append('\n'.join(current_table))
                    current_table = []
                current_prose.append(line)
        
        # Don't forget leftovers
        if current_table:
            groups.append('\n'.join(current_table))
        if current_prose:
            groups.append('\n'.join(current_prose))
            
        return groups
    
    def _split_table_rows(self, table_text: str, max_rows: int = 10) -> list[str]:
        """Split large tables into chunks of rows"""
        rows = [r.strip() for r in table_text.split('\n') if r.strip()]
        
        if len(rows) <= max_rows:
            return ['\n'.join(rows)]
        
        chunks = []
        for i in range(0, len(rows), max_rows):
            chunk_rows = rows[i:i + max_rows]
            # Add overlap: include last 2 rows from previous chunk
            if i > 0 and len(rows) > 0:
                overlap_rows = rows[max(0, i-2):i]
                chunk_rows = overlap_rows + chunk_rows
            chunks.append('\n'.join(chunk_rows))
            
        return chunks
    
    def chunk_splitter(self, langchain_docs: list[Document]) -> list[Document]:
        final_chunks = []
        
        for doc in langchain_docs:
            try:
                # Group by tables vs prose
                groups = self._group_by_table(doc.page_content)
                
                for group in groups:
                    if self._is_table_row(group.split('\n')[0]):
                        # Table group - split by rows
                        table_chunks = self._split_table_rows(group, max_rows=8)
                        for chunk in table_chunks:
                            final_chunks.append(Document(
                                page_content=chunk,
                                metadata={
                                    **doc.metadata,
                                    "chunk_type": "table",
                                    "contains_table": True
                                }
                            ))
                    else:
                        # Prose - use simple splitting
                        if len(group) > self.chunk_size:
                            # Simple sentence-based splitting for prose
                            sentences = re.split(r'(?<=[.!?])\s+', group)
                            current_chunk = []
                            current_len = 0
                            
                            for sent in sentences:
                                if current_len + len(sent) > self.chunk_size and current_chunk:
                                    final_chunks.append(Document(
                                        page_content=' '.join(current_chunk),
                                        metadata={
                                            **doc.metadata,
                                            "chunk_type": "prose"
                                        }
                                    ))
                                    # Keep overlap
                                    overlap_sents = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                                    current_chunk = overlap_sents + [sent]
                                    current_len = sum(len(s) for s in current_chunk)
                                else:
                                    current_chunk.append(sent)
                                    current_len += len(sent)
                            
                            if current_chunk:
                                final_chunks.append(Document(
                                    page_content=' '.join(current_chunk),
                                    metadata={
                                        **doc.metadata,
                                        "chunk_type": "prose"
                                    }
                                ))
                        else:
                            final_chunks.append(Document(
                                page_content=group,
                                metadata={
                                    **doc.metadata,
                                    "chunk_type": "prose"
                                }
                            ))
                            
            except Exception as e:
                logger.error(f"Failed to chunk document: {e}")
                
        return final_chunks