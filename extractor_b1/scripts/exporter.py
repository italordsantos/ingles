#!/usr/bin/env python3
"""
📤 EXPORTADOR DE DADOS - MULTIPLOS FORMATOS
Exporta dados processados em JSON, SQL, CSV e outros formatos
"""

import json
import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

class DataExporter:
    """Exporta dados processados em múltiplos formatos"""
    
    def __init__(self, config, level: str):
        self.config = config
        self.level = level
        self.output_path = Path(f"output/database_ready/{level}")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exportador inicializado para nível {level}")
    
    def export_all(self, processed_data: Dict[str, Any], export_format: str) -> Dict[str, Any]:
        """Exporta todos os dados no formato especificado"""
        export_results = {}
        
        if export_format in ['json', 'all']:
            export_results['json'] = self.export_to_json(processed_data)
        
        if export_format in ['sql', 'all']:
            export_results['sql'] = self.export_to_sql(processed_data)
        
        if export_format in ['csv', 'all']:
            export_results['csv'] = self.export_to_csv(processed_data)
        
        if export_format in ['postgresql', 'all']:
            export_results['postgresql'] = self.export_to_postgresql(processed_data)
        
        # Salvar resumo da exportação
        self.save_export_summary(export_results)
        
        return export_results
    
    def export_to_json(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta dados para JSON estruturado"""
        try:
            # Exportar cada categoria separadamente
            for category, data in processed_data.items():
                if data:
                    category_file = self.output_path / f"{category}.json"
                    with open(category_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Exportar arquivo consolidado
            consolidated_file = self.output_path / "all_data.json"
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Exportar schema para importação
            schema_file = self.output_path / "import_schema.json"
            schema = self.generate_import_schema(processed_data)
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exportação JSON concluída: {consolidated_file}")
            
            return {
                'success': True,
                'filename': str(consolidated_file),
                'size': consolidated_file.stat().st_size,
                'files_created': len([k for k, v in processed_data.items() if v]) + 2
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na exportação JSON: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_sql(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta dados para SQL (SQLite)"""
        try:
            db_file = self.output_path / f"{self.level}_data.db"
            
            # Criar banco SQLite
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Criar tabelas
            self.create_sqlite_tables(cursor)
            
            # Inserir dados
            for category, data in processed_data.items():
                if data:
                    self.insert_category_data(cursor, category, data)
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Exportação SQL concluída: {db_file}")
            
            return {
                'success': True,
                'filename': str(db_file),
                'size': db_file.stat().st_size,
                'tables_created': len([k for k, v in processed_data.items() if v])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na exportação SQL: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_csv(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta dados para CSV"""
        try:
            files_created = 0
            
            for category, data in processed_data.items():
                if data:
                    csv_file = self.output_path / f"{category}.csv"
                    self.export_category_to_csv(category, data, csv_file)
                    files_created += 1
            
            logger.info(f"✅ Exportação CSV concluída: {files_created} arquivos")
            
            return {
                'success': True,
                'filename': f"{files_created} arquivos CSV",
                'size': 'N/A',
                'files_created': files_created
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na exportação CSV: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_postgresql(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta dados para PostgreSQL (scripts SQL)"""
        try:
            # Gerar scripts SQL para PostgreSQL
            sql_file = self.output_path / f"{self.level}_postgresql.sql"
            
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(f"-- =====================================================\n")
                f.write(f"-- SCRIPT POSTGRESQL PARA NÍVEL {self.level}\n")
                f.write(f"-- =====================================================\n\n")
                
                # Scripts de criação de tabelas
                f.write(self.generate_postgresql_tables())
                f.write("\n")
                
                # Scripts de inserção de dados
                for category, data in processed_data.items():
                    if data:
                        f.write(self.generate_postgresql_inserts(category, data))
                        f.write("\n")
            
            logger.info(f"✅ Exportação PostgreSQL concluída: {sql_file}")
            
            return {
                'success': True,
                'filename': str(sql_file),
                'size': sql_file.stat().st_size,
                'tables_created': len([k for k, v in processed_data.items() if v])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na exportação PostgreSQL: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_sqlite_tables(self, cursor):
        """Cria tabelas no SQLite"""
        # Tabela de vocabulário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                definition_en TEXT NOT NULL,
                definition_pt TEXT,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                examples TEXT,
                phonetic TEXT,
                part_of_speech TEXT,
                is_phrasal_verb BOOLEAN,
                source_document TEXT,
                context TEXT
            )
        ''')
        
        # Tabela de gramática
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grammar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                category TEXT NOT NULL,
                level TEXT NOT NULL,
                description TEXT,
                examples TEXT,
                rules TEXT,
                exercises TEXT,
                source_document TEXT,
                context TEXT
            )
        ''')
        
        # Tabela de materiais de leitura
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reading_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                word_count INTEGER,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT,
                source_document TEXT,
                questions TEXT
            )
        ''')
        
        # Tabela de materiais de listening
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listening_materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT,
                source_document TEXT,
                questions TEXT
            )
        ''')
        
        # Tabela de prompts de escrita
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS writing_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                prompt TEXT NOT NULL,
                type TEXT,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                word_limit TEXT,
                source_document TEXT,
                suggestions TEXT
            )
        ''')
        
        # Tabela de tópicos de speaking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speaking_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                type TEXT,
                level TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT,
                source_document TEXT,
                questions TEXT
            )
        ''')
    
    def insert_category_data(self, cursor, category: str, data: Dict[str, Any]):
        """Insere dados de uma categoria no SQLite"""
        if category == 'vocabulary':
            for word_id, word_data in data.items():
                cursor.execute('''
                    INSERT INTO vocabulary (
                        word, definition_en, definition_pt, level, category,
                        examples, phonetic, part_of_speech, is_phrasal_verb,
                        source_document, context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    word_data.get('word', ''),
                    word_data.get('definition_en', ''),
                    word_data.get('definition_pt', ''),
                    word_data.get('level', ''),
                    word_data.get('category', ''),
                    json.dumps(word_data.get('examples', [])),
                    word_data.get('phonetic', ''),
                    word_data.get('part_of_speech', ''),
                    word_data.get('is_phrasal_verb', False),
                    word_data.get('source_document', ''),
                    word_data.get('context', '')
                ))
        
        elif category == 'grammar':
            for rule_id, rule_data in data.items():
                cursor.execute('''
                    INSERT INTO grammar (
                        rule_name, category, level, description, examples,
                        rules, exercises, source_document, context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule_data.get('rule_name', ''),
                    rule_data.get('category', ''),
                    rule_data.get('level', ''),
                    rule_data.get('description', ''),
                    json.dumps(rule_data.get('examples', [])),
                    json.dumps(rule_data.get('rules', [])),
                    json.dumps(rule_data.get('exercises', [])),
                    rule_data.get('source_document', ''),
                    rule_data.get('context', '')
                ))
        
        elif category == 'reading_materials':
            for text_id, text_data in data.items():
                cursor.execute('''
                    INSERT INTO reading_materials (
                        title, content, word_count, level, category,
                        difficulty, source_document, questions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    text_data.get('title', ''),
                    text_data.get('content', ''),
                    text_data.get('word_count', 0),
                    text_data.get('level', ''),
                    text_data.get('category', ''),
                    text_data.get('difficulty', ''),
                    text_data.get('source_document', ''),
                    json.dumps(text_data.get('questions', []))
                ))
        
        elif category == 'listening_materials':
            for dialogue_id, dialogue_data in data.items():
                cursor.execute('''
                    INSERT INTO listening_materials (
                        title, content, type, level, category,
                        difficulty, source_document, questions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dialogue_data.get('title', ''),
                    dialogue_data.get('content', ''),
                    dialogue_data.get('type', ''),
                    dialogue_data.get('level', ''),
                    dialogue_data.get('category', ''),
                    dialogue_data.get('difficulty', ''),
                    dialogue_data.get('source_document', ''),
                    json.dumps(dialogue_data.get('questions', []))
                ))
        
        elif category == 'writing_prompts':
            for prompt_id, prompt_data in data.items():
                cursor.execute('''
                    INSERT INTO writing_prompts (
                        title, prompt, type, level, category,
                        word_limit, source_document, suggestions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prompt_data.get('title', ''),
                    prompt_data.get('prompt', ''),
                    prompt_data.get('type', ''),
                    prompt_data.get('level', ''),
                    prompt_data.get('category', ''),
                    prompt_data.get('word_limit', ''),
                    prompt_data.get('source_document', ''),
                    json.dumps(prompt_data.get('suggestions', []))
                ))
        
        elif category == 'speaking_topics':
            for topic_id, topic_data in data.items():
                cursor.execute('''
                    INSERT INTO speaking_topics (
                        title, topic, type, level, category,
                        difficulty, source_document, questions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    topic_data.get('title', ''),
                    topic_data.get('topic', ''),
                    topic_data.get('type', ''),
                    topic_data.get('level', ''),
                    topic_data.get('category', ''),
                    topic_data.get('difficulty', ''),
                    topic_data.get('source_document', ''),
                    json.dumps(topic_data.get('questions', []))
                ))
    
    def export_category_to_csv(self, category: str, data: Dict[str, Any], csv_file: Path):
        """Exporta uma categoria para CSV"""
        if not data:
            return
        
        # Determinar campos baseado na categoria
        if category == 'vocabulary':
            fieldnames = ['word', 'definition_en', 'definition_pt', 'level', 'category', 
                         'phonetic', 'part_of_speech', 'is_phrasal_verb', 'source_document']
        elif category == 'grammar':
            fieldnames = ['rule_name', 'category', 'level', 'description', 'source_document']
        elif category == 'reading_materials':
            fieldnames = ['title', 'word_count', 'level', 'category', 'difficulty', 'source_document']
        elif category == 'listening_materials':
            fieldnames = ['title', 'type', 'level', 'category', 'difficulty', 'source_document']
        elif category == 'writing_prompts':
            fieldnames = ['title', 'type', 'level', 'category', 'word_limit', 'source_document']
        elif category == 'speaking_topics':
            fieldnames = ['title', 'type', 'level', 'category', 'difficulty', 'source_document']
        else:
            fieldnames = list(next(iter(data.values())).keys())
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item_id, item_data in data.items():
                # Preparar linha para CSV
                row = {}
                for field in fieldnames:
                    value = item_data.get(field, '')
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False)
                    row[field] = str(value) if value is not None else ''
                
                writer.writerow(row)
    
    def generate_postgresql_tables(self) -> str:
        """Gera scripts de criação de tabelas PostgreSQL"""
        return '''
-- Criação das tabelas para nível B1
CREATE TABLE IF NOT EXISTS vocabulary (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    definition_en TEXT NOT NULL,
    definition_pt TEXT,
    level VARCHAR(2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    examples JSONB,
    phonetic VARCHAR(100),
    part_of_speech VARCHAR(20),
    is_phrasal_verb BOOLEAN DEFAULT FALSE,
    source_document VARCHAR(255),
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS grammar (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    level VARCHAR(2) NOT NULL,
    description TEXT,
    examples JSONB,
    rules JSONB,
    exercises JSONB,
    source_document VARCHAR(255),
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reading_materials (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER,
    level VARCHAR(2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20),
    source_document VARCHAR(255),
    questions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS listening_materials (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50),
    level VARCHAR(2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20),
    source_document VARCHAR(255),
    questions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS writing_prompts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    prompt TEXT NOT NULL,
    type VARCHAR(50),
    level VARCHAR(2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    word_limit VARCHAR(50),
    source_document VARCHAR(255),
    suggestions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS speaking_topics (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    topic TEXT NOT NULL,
    type VARCHAR(50),
    level VARCHAR(2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20),
    source_document VARCHAR(255),
    questions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para otimização
CREATE INDEX IF NOT EXISTS idx_vocabulary_word ON vocabulary(word);
CREATE INDEX IF NOT EXISTS idx_vocabulary_level ON vocabulary(level);
CREATE INDEX IF NOT EXISTS idx_vocabulary_category ON vocabulary(category);
CREATE INDEX IF NOT EXISTS idx_grammar_level ON grammar(level);
CREATE INDEX IF NOT EXISTS idx_grammar_category ON grammar(category);
'''
    
    def generate_postgresql_inserts(self, category: str, data: Dict[str, Any]) -> str:
        """Gera scripts de inserção PostgreSQL"""
        if not data:
            return ""
        
        sql = f"\n-- Inserção de dados para {category}\n"
        
        if category == 'vocabulary':
            for word_id, word_data in data.items():
                sql += f"INSERT INTO vocabulary (word, definition_en, definition_pt, level, category, examples, phonetic, part_of_speech, is_phrasal_verb, source_document, context) VALUES (\n"
                sql += f"    '{word_data.get('word', '').replace(\"'\", \"''\")}',\n"
                sql += f"    '{word_data.get('definition_en', '').replace(\"'\", \"''\")}',\n"
                sql += f"    '{word_data.get('definition_pt', '').replace(\"'\", \"''\")}',\n"
                sql += f"    '{word_data.get('level', '')}',\n"
                sql += f"    '{word_data.get('category', '')}',\n"
                sql += f"    '{json.dumps(word_data.get('examples', []))}',\n"
                sql += f"    '{word_data.get('phonetic', '')}',\n"
                sql += f"    '{word_data.get('part_of_speech', '')}',\n"
                sql += f"    {str(word_data.get('is_phrasal_verb', False)).lower()},\n"
                sql += f"    '{word_data.get('source_document', '')}',\n"
                sql += f"    '{word_data.get('context', '').replace(\"'\", \"''\")}'\n"
                sql += f");\n\n"
        
        # Adicionar outras categorias conforme necessário
        return sql
    
    def generate_import_schema(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera schema para importação na plataforma"""
        schema = {
            "version": "1.0",
            "level": self.level,
            "export_date": str(Path().cwd()),
            "categories": {},
            "import_instructions": {
                "database": "Use o script SQL gerado para criar as tabelas",
                "api": "Use os arquivos JSON para importar via API",
                "validation": "Verifique os relatórios de validação antes da importação"
            }
        }
        
        for category, data in processed_data.items():
            if data:
                schema["categories"][category] = {
                    "item_count": len(data),
                    "sample_item": next(iter(data.values())),
                    "fields": list(next(iter(data.values())).keys())
                }
        
        return schema
    
    def save_export_summary(self, export_results: Dict[str, Any]):
        """Salva resumo da exportação"""
        summary = {
            "level": self.level,
            "export_date": str(Path().cwd()),
            "formats_exported": list(export_results.keys()),
            "results": export_results
        }
        
        summary_file = self.output_path / "export_summary.json"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Resumo da exportação salvo em: {summary_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resumo: {str(e)}")
