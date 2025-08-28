#!/usr/bin/env python3
"""
📄 EXTRACTOR DE DOCUMENTOS - USANDO DOCLING
Extrai conteúdo bruto de PDFs, DOCXs e outros formatos
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

try:
    from docling import DocumentConverter
    from docling.document import DoclingDocument
except ImportError:
    logger.error("Docling não encontrado. Instale com: pip install docling")
    raise

class DocumentExtractor:
    """Extrator de documentos usando Docling"""
    
    def __init__(self, config, level: str):
        self.config = config
        self.level = level
        self.materials_path = Path(f"materials/{level}")
        self.output_path = Path(f"output/raw_extraction/{level}")
        self.supported_formats = ['.pdf', '.docx', '.pptx', '.xlsx', '.html', '.txt']
        
        # Criar diretórios se não existirem
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar Docling
        self.converter = DocumentConverter()
        
        logger.info(f"Extractor inicializado para nível {level}")
        logger.info(f"Pasta de materiais: {self.materials_path}")
        logger.info(f"Pasta de saída: {self.output_path}")
    
    def extract_all(self) -> Dict[str, Any]:
        """Extrai todos os documentos do nível especificado"""
        if not self.materials_path.exists():
            logger.warning(f"Pasta de materiais não encontrada: {self.materials_path}")
            return {}
        
        documents = {}
        files_found = list(self.materials_path.glob("*"))
        
        logger.info(f"Encontrados {len(files_found)} arquivos em {self.materials_path}")
        
        for file_path in files_found:
            if file_path.suffix.lower() in self.supported_formats:
                try:
                    logger.info(f"Processando: {file_path.name}")
                    extracted_data = self.extract_document(file_path)
                    documents[file_path.name] = extracted_data
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path.name}: {str(e)}")
                    documents[file_path.name] = {
                        "error": str(e),
                        "status": "failed"
                    }
            else:
                logger.warning(f"Formato não suportado: {file_path.name}")
        
        # Salvar extração bruta
        self.save_raw_extraction(documents)
        
        return documents
    
    def extract_document(self, file_path: Path) -> Dict[str, Any]:
        """Extrai um documento específico"""
        try:
            # Converter documento usando Docling
            doc: DoclingDocument = self.converter.convert(str(file_path))
            
            # Extrair diferentes tipos de conteúdo
            extracted_data = {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix.lower(),
                "status": "success",
                "metadata": self.extract_metadata(doc),
                "content": self.extract_content(doc),
                "tables": self.extract_tables(doc),
                "images": self.extract_images(doc),
                "structure": self.extract_structure(doc)
            }
            
            logger.info(f"✅ Documento extraído com sucesso: {file_path.name}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Erro na extração de {file_path.name}: {str(e)}")
            raise
    
    def extract_metadata(self, doc: DoclingDocument) -> Dict[str, Any]:
        """Extrai metadados do documento"""
        try:
            return {
                "title": getattr(doc, 'title', None),
                "author": getattr(doc, 'author', None),
                "language": getattr(doc, 'language', None),
                "page_count": len(doc.pages) if hasattr(doc, 'pages') else None,
                "creation_date": getattr(doc, 'creation_date', None),
                "modification_date": getattr(doc, 'modification_date', None)
            }
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados: {str(e)}")
            return {}
    
    def extract_content(self, doc: DoclingDocument) -> Dict[str, Any]:
        """Extrai conteúdo textual do documento"""
        try:
            content = {
                "full_text": "",
                "pages": [],
                "paragraphs": [],
                "sentences": []
            }
            
            if hasattr(doc, 'pages'):
                for i, page in enumerate(doc.pages):
                    page_text = ""
                    if hasattr(page, 'text'):
                        page_text = page.text
                    elif hasattr(page, 'content'):
                        page_text = str(page.content)
                    
                    content["pages"].append({
                        "page_number": i + 1,
                        "text": page_text,
                        "word_count": len(page_text.split()) if page_text else 0
                    })
                    content["full_text"] += page_text + "\n"
            
            # Dividir em parágrafos e frases
            if content["full_text"]:
                content["paragraphs"] = [p.strip() for p in content["full_text"].split('\n\n') if p.strip()]
                content["sentences"] = [s.strip() for s in content["full_text"].replace('\n', ' ').split('.') if s.strip()]
            
            return content
            
        except Exception as e:
            logger.warning(f"Erro ao extrair conteúdo: {str(e)}")
            return {"error": str(e)}
    
    def extract_tables(self, doc: DoclingDocument) -> List[Dict[str, Any]]:
        """Extrai tabelas do documento"""
        try:
            tables = []
            if hasattr(doc, 'tables'):
                for i, table in enumerate(doc.tables):
                    table_data = {
                        "table_number": i + 1,
                        "rows": [],
                        "columns": [],
                        "data": []
                    }
                    
                    if hasattr(table, 'rows'):
                        for row in table.rows:
                            row_data = []
                            for cell in row.cells:
                                cell_text = getattr(cell, 'text', str(cell))
                                row_data.append(cell_text)
                            table_data["rows"].append(row_data)
                            table_data["data"].append(row_data)
                    
                    if table_data["rows"]:
                        table_data["columns"] = len(table_data["rows"][0]) if table_data["rows"] else 0
                        tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.warning(f"Erro ao extrair tabelas: {str(e)}")
            return []
    
    def extract_images(self, doc: DoclingDocument) -> List[Dict[str, Any]]:
        """Extrai informações sobre imagens"""
        try:
            images = []
            if hasattr(doc, 'images'):
                for i, image in enumerate(doc.images):
                    image_info = {
                        "image_number": i + 1,
                        "type": getattr(image, 'type', 'unknown'),
                        "size": getattr(image, 'size', None),
                        "caption": getattr(image, 'caption', None),
                        "alt_text": getattr(image, 'alt_text', None)
                    }
                    images.append(image_info)
            
            return images
            
        except Exception as e:
            logger.warning(f"Erro ao extrair imagens: {str(e)}")
            return []
    
    def extract_structure(self, doc: DoclingDocument) -> Dict[str, Any]:
        """Extrai estrutura hierárquica do documento"""
        try:
            structure = {
                "headings": [],
                "sections": [],
                "lists": [],
                "footnotes": []
            }
            
            # Extrair cabeçalhos se disponível
            if hasattr(doc, 'headings'):
                for heading in doc.headings:
                    heading_info = {
                        "text": getattr(heading, 'text', str(heading)),
                        "level": getattr(heading, 'level', 1),
                        "page": getattr(heading, 'page', None)
                    }
                    structure["headings"].append(heading_info)
            
            # Extrair listas se disponível
            if hasattr(doc, 'lists'):
                for lst in doc.lists:
                    list_info = {
                        "type": getattr(lst, 'type', 'unordered'),
                        "items": []
                    }
                    
                    if hasattr(lst, 'items'):
                        for item in lst.items:
                            item_text = getattr(item, 'text', str(item))
                            list_info["items"].append(item_text)
                    
                    structure["lists"].append(list_info)
            
            return structure
            
        except Exception as e:
            logger.warning(f"Erro ao extrair estrutura: {str(e)}")
            return {}
    
    def save_raw_extraction(self, documents: Dict[str, Any]):
        """Salva a extração bruta em arquivo JSON"""
        output_file = self.output_path / "raw_extraction.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Extração bruta salva em: {output_file}")
            
            # Salvar também um resumo
            summary = {
                "level": self.level,
                "total_documents": len(documents),
                "successful_extractions": len([d for d in documents.values() if d.get('status') == 'success']),
                "failed_extractions": len([d for d in documents.values() if d.get('status') == 'failed']),
                "file_types": list(set([d.get('file_type', 'unknown') for d in documents.values()])),
                "total_pages": sum([len(d.get('content', {}).get('pages', [])) for d in documents.values() if d.get('status') == 'success']),
                "total_words": sum([d.get('content', {}).get('full_text', '').count(' ') for d in documents.values() if d.get('status') == 'success'])
            }
            
            summary_file = self.output_path / "extraction_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Resumo da extração salvo em: {summary_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar extração bruta: {str(e)}")
            raise
