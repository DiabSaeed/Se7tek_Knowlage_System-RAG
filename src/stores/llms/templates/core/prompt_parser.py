import yaml
from typing import Dict, Any
from jinja2 import Template
from pathlib import Path

class PromptParser:
    
    def __init__(self, locale: str = "en"):
        base_dir = Path(__file__).resolve().parent.parent
        template_path = base_dir/ "locales"  / f"{locale}" / "rag_prompts.yaml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found at: {template_path}")
        with open(template_path, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)
        if not isinstance(content, dict):
                raise ValueError(f"Failed to load valid YAML from {template_path}. File might be empty.")
                
        self.template_content: Dict[str, Any] = content
    
    def build_rag_prompt(self, query:str, context_chunks: list, tone: str = "professional") -> list:
        
        system_prompt = Template(self.template_content['system_prompt'])
        user_prompt = Template(self.template_content['user_prompt'])
        
        system_message = system_prompt.render(tone=tone)
        user_message = user_prompt.render(user_query=query, context_chunks=context_chunks)
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
