#!/usr/bin/env python3
"""
🔧 PROCESSADOR DE DADOS - ESTRUTURAÇÃO PARA B1
Processa dados extraídos e os organiza em categorias estruturadas
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

class DataProcessor:
    """Processa dados extraídos e os estrutura para a plataforma"""
    
    def __init__(self, config, level: str):
        self.config = config
        self.level = level
        self.output_path = Path(f"output/processed_data/{level}")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Padrões para identificação de conteúdo
        self.vocabulary_patterns = {
            'word_definition': r'(\b\w+\b)\s*[-–—]\s*(.+)',
            'phrasal_verb': r'(\b\w+\s+\w+\b)\s*[-–—]\s*(.+)',
            'example_sentence': r'["""]([^"""]+)["""]',
            'phonetic': r'/([^/]+)/',
            'part_of_speech': r'\b(noun|verb|adjective|adverb|preposition|conjunction|pronoun)\b'
        }
        
        self.grammar_patterns = {
            'rule_name': r'([A-Z][^:]+):',
            'example': r'["""]([^"""]+)["""]',
            'explanation': r'([^.!?]+[.!?])',
            'structure': r'(\w+\s+\w+\s+\w+)'
        }
        
        logger.info(f"Processador inicializado para nível {level}")
    
    def process_all(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa todos os dados extraídos"""
        processed_data = {
            "vocabulary": {},
            "grammar": {},
            "exercises": {},
            "reading_materials": {},
            "listening_materials": {},
            "writing_prompts": {},
            "speaking_topics": {}
        }
        
        for filename, document_data in raw_data.items():
            if document_data.get('status') == 'success':
                try:
                    logger.info(f"Processando documento: {filename}")
                    document_processed = self.process_document(filename, document_data)
                    
                    # Mesclar dados processados
                    for category, data in document_processed.items():
                        if data:
                            if category not in processed_data:
                                processed_data[category] = {}
                            processed_data[category].update(data)
                
                except Exception as e:
                    logger.error(f"Erro ao processar {filename}: {str(e)}")
        
        # Salvar dados processados
        self.save_processed_data(processed_data)
        
        return processed_data
    
    def process_document(self, filename: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um documento específico"""
        processed = {}
        
        # Identificar tipo de documento baseado no nome
        if 'vocabulary' in filename.lower() or 'vocab' in filename.lower():
            processed['vocabulary'] = self.extract_vocabulary(document_data)
        elif 'grammar' in filename.lower() or 'gram' in filename.lower():
            processed['grammar'] = self.extract_grammar(document_data)
        elif 'reading' in filename.lower():
            processed['reading_materials'] = self.extract_reading_materials(document_data)
        elif 'listening' in filename.lower():
            processed['listening_materials'] = self.extract_listening_materials(document_data)
        elif 'writing' in filename.lower():
            processed['writing_prompts'] = self.extract_writing_prompts(document_data)
        elif 'speaking' in filename.lower():
            processed['speaking_topics'] = self.extract_speaking_topics(document_data)
        else:
            # Tentar identificar automaticamente
            processed.update(self.auto_identify_content(document_data))
        
        return processed
    
    def extract_vocabulary(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai vocabulário do documento"""
        vocabulary = {}
        content = document_data.get('content', {})
        full_text = content.get('full_text', '')
        
        # Processar parágrafos para encontrar vocabulário
        for paragraph in content.get('paragraphs', []):
            # Procurar por padrões de palavra-definição
            matches = re.findall(self.vocabulary_patterns['word_definition'], paragraph)
            for word, definition in matches:
                if len(word) > 2:  # Filtrar palavras muito curtas
                    vocabulary[word.lower()] = {
                        "word": word.strip(),
                        "definition_en": definition.strip(),
                        "definition_pt": "",  # Será preenchido posteriormente
                        "level": self.level,
                        "category": self.identify_vocabulary_category(word, definition),
                        "examples": self.extract_examples(paragraph),
                        "phonetic": self.extract_phonetic(paragraph),
                        "part_of_speech": self.extract_part_of_speech(paragraph),
                        "is_phrasal_verb": ' ' in word,
                        "source_document": document_data.get('filename', ''),
                        "context": paragraph[:200] + "..." if len(paragraph) > 200 else paragraph
                    }
        
        # Processar tabelas para vocabulário estruturado
        for table in document_data.get('tables', []):
            table_vocab = self.process_vocabulary_table(table)
            vocabulary.update(table_vocab)
        
        logger.info(f"✅ Vocabulário extraído: {len(vocabulary)} palavras")
        return vocabulary
    
    def extract_grammar(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai regras gramaticais do documento"""
        grammar = {}
        content = document_data.get('content', {})
        full_text = content.get('full_text', '')
        
        # Processar por seções
        sections = self.split_into_sections(full_text)
        
        for section_name, section_content in sections.items():
            if section_name and len(section_name) > 3:
                grammar[section_name] = {
                    "rule_name": section_name.strip(),
                    "category": self.identify_grammar_category(section_name),
                    "level": self.level,
                    "description": self.extract_grammar_description(section_content),
                    "examples": self.extract_grammar_examples(section_content),
                    "rules": self.extract_grammar_rules(section_content),
                    "exercises": self.extract_grammar_exercises(section_content),
                    "source_document": document_data.get('filename', ''),
                    "context": section_content[:300] + "..." if len(section_content) > 300 else section_content
                }
        
        logger.info(f"✅ Gramática extraída: {len(grammar)} regras")
        return grammar
    
    def extract_reading_materials(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai materiais de leitura"""
        reading = {}
        content = document_data.get('content', {})
        
        # Identificar textos de leitura
        paragraphs = content.get('paragraphs', [])
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 100:  # Textos longos são candidatos a leitura
                reading[f"text_{i+1}"] = {
                    "title": f"Reading Text {i+1}",
                    "content": paragraph,
                    "word_count": len(paragraph.split()),
                    "level": self.level,
                    "category": "reading_comprehension",
                    "difficulty": self.assess_reading_difficulty(paragraph),
                    "source_document": document_data.get('filename', ''),
                    "questions": self.generate_reading_questions(paragraph)
                }
        
        return reading
    
    def extract_listening_materials(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai materiais de listening"""
        listening = {}
        content = document_data.get('content', {})
        
        # Identificar diálogos e conversas
        paragraphs = content.get('paragraphs', [])
        for i, paragraph in enumerate(paragraphs):
            if self.is_dialogue(paragraph):
                listening[f"dialogue_{i+1}"] = {
                    "title": f"Listening Dialogue {i+1}",
                    "content": paragraph,
                    "type": "dialogue",
                    "level": self.level,
                    "category": "listening_comprehension",
                    "difficulty": self.assess_listening_difficulty(paragraph),
                    "source_document": document_data.get('filename', ''),
                    "questions": self.generate_listening_questions(paragraph)
                }
        
        return listening
    
    def extract_writing_prompts(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai prompts de escrita"""
        writing = {}
        content = document_data.get('content', {})
        
        # Identificar tópicos de escrita
        paragraphs = content.get('paragraphs', [])
        for i, paragraph in enumerate(paragraphs):
            if self.is_writing_prompt(paragraph):
                writing[f"prompt_{i+1}"] = {
                    "title": f"Writing Prompt {i+1}",
                    "prompt": paragraph,
                    "type": "writing_task",
                    "level": self.level,
                    "category": "writing_practice",
                    "word_limit": self.extract_word_limit(paragraph),
                    "source_document": document_data.get('filename', ''),
                    "suggestions": self.generate_writing_suggestions(paragraph)
                }
        
        return writing
    
    def extract_speaking_topics(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai tópicos de speaking"""
        speaking = {}
        content = document_data.get('content', {})
        
        # Identificar tópicos de conversa
        paragraphs = content.get('paragraphs', [])
        for i, paragraph in enumerate(paragraphs):
            if self.is_speaking_topic(paragraph):
                speaking[f"topic_{i+1}"] = {
                    "title": f"Speaking Topic {i+1}",
                    "topic": paragraph,
                    "type": "conversation_topic",
                    "level": self.level,
                    "category": "speaking_practice",
                    "difficulty": self.assess_speaking_difficulty(paragraph),
                    "source_document": document_data.get('filename', ''),
                    "questions": self.generate_speaking_questions(paragraph)
                }
        
        return speaking
    
    def auto_identify_content(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica automaticamente o tipo de conteúdo"""
        content = document_data.get('content', {})
        full_text = content.get('full_text', '').lower()
        
        identified = {}
        
        # Identificar por palavras-chave
        if any(word in full_text for word in ['vocabulary', 'word', 'phrase', 'meaning']):
            identified['vocabulary'] = self.extract_vocabulary(document_data)
        
        if any(word in full_text for word in ['grammar', 'rule', 'tense', 'verb']):
            identified['grammar'] = self.extract_grammar(document_data)
        
        if any(word in full_text for word in ['read', 'text', 'passage', 'article']):
            identified['reading_materials'] = self.extract_reading_materials(document_data)
        
        return identified
    
    # Métodos auxiliares
    def identify_vocabulary_category(self, word: str, definition: str) -> str:
        """Identifica categoria do vocabulário"""
        definition_lower = definition.lower()
        
        categories = {
            'family': ['family', 'mother', 'father', 'sister', 'brother'],
            'food': ['food', 'eat', 'drink', 'cook', 'restaurant'],
            'jobs': ['job', 'work', 'career', 'profession', 'employee'],
            'weather': ['weather', 'climate', 'temperature', 'rain', 'sun'],
            'transport': ['transport', 'car', 'bus', 'train', 'airplane'],
            'house': ['house', 'home', 'room', 'furniture', 'kitchen']
        }
        
        for category, keywords in categories.items():
            if any(keyword in definition_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def identify_grammar_category(self, rule_name: str) -> str:
        """Identifica categoria da regra gramatical"""
        rule_lower = rule_name.lower()
        
        if any(word in rule_lower for word in ['tense', 'present', 'past', 'future']):
            return 'tenses'
        elif any(word in rule_lower for word in ['conditional', 'if']):
            return 'conditionals'
        elif any(word in rule_lower for word in ['modal', 'can', 'must', 'should']):
            return 'modals'
        elif any(word in rule_lower for word in ['preposition', 'in', 'on', 'at']):
            return 'prepositions'
        else:
            return 'general'
    
    def extract_examples(self, text: str) -> List[str]:
        """Extrai exemplos de uso"""
        examples = re.findall(self.vocabulary_patterns['example_sentence'], text)
        return [ex.strip() for ex in examples if len(ex.strip()) > 10]
    
    def extract_phonetic(self, text: str) -> str:
        """Extrai transcrição fonética"""
        phonetic = re.search(self.vocabulary_patterns['phonetic'], text)
        return phonetic.group(1) if phonetic else ""
    
    def extract_part_of_speech(self, text: str) -> str:
        """Extrai classe gramatical"""
        pos = re.search(self.vocabulary_patterns['part_of_speech'], text)
        return pos.group(1) if pos else "unknown"
    
    def split_into_sections(self, text: str) -> Dict[str, str]:
        """Divide texto em seções"""
        sections = {}
        current_section = ""
        current_content = ""
        
        lines = text.split('\n')
        for line in lines:
            if re.match(r'^[A-Z][^:]*:', line):  # Nova seção
                if current_section:
                    sections[current_section] = current_content.strip()
                current_section = line.strip()
                current_content = ""
            else:
                current_content += line + "\n"
        
        if current_section:
            sections[current_section] = current_content.strip()
        
        return sections
    
    def process_vocabulary_table(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Processa tabela de vocabulário"""
        vocabulary = {}
        
        if not table.get('rows'):
            return vocabulary
        
        # Assumir primeira linha como cabeçalho
        headers = table['rows'][0] if table['rows'] else []
        
        for row in table['rows'][1:]:  # Pular cabeçalho
            if len(row) >= 2:
                word = row[0].strip()
                definition = row[1].strip()
                
                if word and definition and len(word) > 2:
                    vocabulary[word.lower()] = {
                        "word": word,
                        "definition_en": definition,
                        "definition_pt": "",
                        "level": self.level,
                        "category": self.identify_vocabulary_category(word, definition),
                        "examples": [],
                        "phonetic": "",
                        "part_of_speech": "unknown",
                        "is_phrasal_verb": ' ' in word,
                        "source_document": "table_extraction",
                        "context": f"From table: {word} - {definition}"
                    }
        
        return vocabulary
    
    def save_processed_data(self, processed_data: Dict[str, Any]):
        """Salva dados processados"""
        for category, data in processed_data.items():
            if data:
                output_file = self.output_path / f"{category}.json"
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                    logger.info(f"✅ {category} salvo em: {output_file}")
                except Exception as e:
                    logger.error(f"❌ Erro ao salvar {category}: {str(e)}")
        
        # Salvar resumo geral
        summary = {
            "level": self.level,
            "total_categories": len([k for k, v in processed_data.items() if v]),
            "vocabulary_count": len(processed_data.get('vocabulary', {})),
            "grammar_count": len(processed_data.get('grammar', {})),
            "reading_count": len(processed_data.get('reading_materials', {})),
            "listening_count": len(processed_data.get('listening_materials', {})),
            "writing_count": len(processed_data.get('writing_prompts', {})),
            "speaking_count": len(processed_data.get('speaking_topics', {}))
        }
        
        summary_file = self.output_path / "processing_summary.json"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Resumo do processamento salvo em: {summary_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resumo: {str(e)}")
    
    # Métodos de avaliação de dificuldade
    def assess_reading_difficulty(self, text: str) -> str:
        """Avalia dificuldade do texto de leitura"""
        word_count = len(text.split())
        avg_word_length = sum(len(word) for word in text.split()) / word_count if word_count > 0 else 0
        
        if word_count < 100 or avg_word_length < 4.5:
            return "easy"
        elif word_count < 300 or avg_word_length < 5.5:
            return "medium"
        else:
            return "hard"
    
    def assess_listening_difficulty(self, text: str) -> str:
        """Avalia dificuldade do material de listening"""
        return self.assess_reading_difficulty(text)  # Mesma lógica por enquanto
    
    def assess_speaking_difficulty(self, text: str) -> str:
        """Avalia dificuldade do tópico de speaking"""
        return "medium"  # Padrão para speaking
    
    # Métodos de identificação de tipo
    def is_dialogue(self, text: str) -> bool:
        """Identifica se é um diálogo"""
        return '"' in text and text.count('"') >= 4
    
    def is_writing_prompt(self, text: str) -> bool:
        """Identifica se é um prompt de escrita"""
        prompt_keywords = ['write', 'describe', 'explain', 'discuss', 'compare']
        return any(keyword in text.lower() for keyword in prompt_keywords)
    
    def is_speaking_topic(self, text: str) -> bool:
        """Identifica se é um tópico de speaking"""
        speaking_keywords = ['talk about', 'discuss', 'describe', 'opinion', 'experience']
        return any(keyword in text.lower() for keyword in speaking_keywords)
    
    # Métodos de geração de conteúdo
    def extract_word_limit(self, text: str) -> str:
        """Extrai limite de palavras do prompt"""
        word_limit_match = re.search(r'(\d+)\s*words?', text.lower())
        return word_limit_match.group(1) + " words" if word_limit_match else "100 words"
    
    def generate_reading_questions(self, text: str) -> List[Dict[str, str]]:
        """Gera perguntas de compreensão"""
        # Implementação básica - pode ser expandida
        return [
            {"question": "What is the main topic of this text?", "type": "main_idea"},
            {"question": "What are the key points mentioned?", "type": "key_points"}
        ]
    
    def generate_listening_questions(self, text: str) -> List[Dict[str, str]]:
        """Gera perguntas de listening"""
        return [
            {"question": "What is the conversation about?", "type": "topic"},
            {"question": "What are the speakers discussing?", "type": "discussion"}
        ]
    
    def generate_speaking_questions(self, text: str) -> List[Dict[str, str]]:
        """Gera perguntas para speaking"""
        return [
            {"question": "What is your opinion on this topic?", "type": "opinion"},
            {"question": "Can you share a related experience?", "type": "experience"}
        ]
    
    def generate_writing_suggestions(self, text: str) -> List[str]:
        """Gera sugestões para escrita"""
        return [
            "Use clear topic sentences",
            "Include supporting details",
            "Use appropriate vocabulary",
            "Check grammar and spelling"
        ]
