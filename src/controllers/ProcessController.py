from .BaseController import BaseController
from .ProjectController import ProjectController
from helpers.config import Settings
from docling.document_converter import DocumentConverter
from llama_parse import LlamaParse
from langchain_core.documents import Document
import pymupdf
import tempfile
import os
import logging

logger = logging.getLogger()

class ProcessControler(BaseController):
    def __init__(self,project_id):
        super().__init__()
        self.converter = DocumentConverter()
        self.project_id = project_id
        self.project_path = ProjectController().create_project_path(project_id=project_id)
        
    def content_extraction(self, file_path):
        simple_pages = []
        complex_pages = []
        
        with pymupdf.open(file_path) as doc_pages:
            for page in range(len(doc_pages)):
                doc = doc_pages[page]
                tables = doc.find_tables()
                images = doc.get_image_info()

                if len(tables.tables) > 0 or len(images) > 0:
                    complex_pages.append(page + 1)
                else:
                    simple_pages.append(page + 1)
            return simple_pages,complex_pages
    
    def __extract_to_temp_file(self,original_file_path, pages_list):
        temp_file = tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
        with pymupdf.open(original_file_path) as original_file:
            with pymupdf.open() as temp_doc:
                for page_num in pages_list:
                    temp_doc.insert_pdf(original_file,from_page=page_num-1 , to_page=page_num-1)
                temp_doc.save(temp_file.name)
        return temp_file.name
    
    def content_transformation(self,file_path):
        simple_pages, complex_pages = self.content_extraction(file_path=file_path)
        final_docs = []
        
        if simple_pages:
            simple_pdfs = self.__extract_to_temp_file(file_path,simple_pages)
            
            try:
                docling_result = self.converter.convert(simple_pdfs)
                docling_md = docling_result.document.export_to_markdown()
                
                final_docs.append(
                    Document(
                        page_content=docling_md,
                        metadata={
                            "source":file_path,
                            "parsed_by": "docling",
                            "pages": simple_pages
                        }
                    )
                )
            finally:
                if os.path.exists(simple_pdfs):
                    os.remove(simple_pdfs)
        if complex_pages:
            target_pages_str = ",".join(str(p - 1) for p in complex_pages)
            try:
                llama_parser = LlamaParse(
                    result_type="markdown",
                    target_pages=target_pages_str,
                    api_key= Settings.LLAMA_PARSER_API_KEY
                )
                llama_result = llama_parser.load_data(file_path=file_path)
                complext_md = "\n\n".join([doc.text for doc in llama_result])
                
                final_docs.append(
                    Document(
                        page_content=complext_md,
                        metadata = {
                            "source": file_path,
                            "parsed_by": "llama_parser",
                            "pages":complex_pages
                        }
                    )
                )
            except Exception as e:
                logger.error(f"error while parsing as {e}")
                try:
                    complex_pdfs = self.__extract_to_temp_file(file_path,complex_pages)
                    docling_result = self.converter.convert(complex_pdfs)
                    docling_md = docling_result.document.export_to_markdown()
                    
                    final_docs.append(
                        Document(
                            page_content=docling_md,
                            metadata={
                                "source":file_path,
                                "parsed_by": "docling",
                                "pages": complex_pages
                            }
                        )
                    )
                finally:
                    if os.path.exists(complex_pdfs):
                        os.remove(complex_pdfs)
        return final_docs
