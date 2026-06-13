from .BaseController import BaseController
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

logger = logging.getLogger()

class ChunckingController(BaseController):
    def __init__(self, chunk_size: int = 1000, recursive_chars: int = 200):
        super().__init__()
        self.headers_to_split_on = [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ]
        self.mark_down_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap = recursive_chars
        )
    def chunk_splitter(self, langchain_docs: list[Document]):
        final_chunks = []
        
        for doc in langchain_docs:
            try:
                header_splits = self.mark_down_splitter.split_text(doc.page_content)
                for split in header_splits:
                    combined_metadata = doc.metadata.copy()
                    combined_metadata.update(split.metadata)
                    sub_chunks = self.text_splitter.split_text(split.page_content)
                    for chunk_text in sub_chunks:
                        final_chunks.append(
                            Document(
                                page_content=chunk_text,
                                metadata=combined_metadata.copy()
                            )
                        )
            except Exception as e:
                logger.error(f"Failed to chunk document from source {doc.metadata.get('source')}: {e}")
                
        return final_chunks