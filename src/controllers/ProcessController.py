from .BaseController import BaseController
from DataController import DataController
from docling.document_converter import DocumentConverter
from llama_parse import LlamaParse
from langchain_core.documents import Document

class ProcessControler(BaseController):
    def __init__(self):
        super().__init__()
    def converting_file(self,file_id):
        document_converter = DocumentConverter()
        docling_result = document_converter.convert(file_id)
        
