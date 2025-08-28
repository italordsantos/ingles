#!/usr/bin/env python3
"""
✅ VALIDADOR DE DADOS - VERIFICAÇÃO DE QUALIDADE
Valida dados processados e identifica problemas
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from loguru import logger

class DataValidator:
    """Valida dados processados para garantir qualidade"""
    
    def __init__(self, config, level: str):
        self.config = config
        self.level = level
        self.output_path = Path(f"output/reports/{level}")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Critérios de validação
        self.validation_rules = {
            'vocabulary': {
                'required_fields': ['word', 'definition_en', 'level', 'category'],
                'word_min_length': 2,
                'definition_min_length': 10,
                'valid_categories': ['family', 'food', 'jobs', 'weather', 'transport', 'house', 'general']
            },
            'grammar': {
                'required_fields': ['rule_name', 'category', 'level', 'description'],
                'rule_name_min_length': 5,
                'description_min_length': 20,
                'valid_categories': ['tenses', 'conditionals', 'modals', 'prepositions', 'general']
            },
            'reading_materials': {
                'required_fields': ['title', 'content', 'level', 'category'],
                'content_min_length': 50,
                'valid_categories': ['reading_comprehension']
            },
            'listening_materials': {
                'required_fields': ['title', 'content', 'level', 'category'],
                'content_min_length': 30,
                'valid_categories': ['listening_comprehension']
            },
            'writing_prompts': {
                'required_fields': ['title', 'prompt', 'level', 'category'],
                'prompt_min_length': 20,
                'valid_categories': ['writing_practice']
            },
            'speaking_topics': {
                'required_fields': ['title', 'topic', 'level', 'category'],
                'topic_min_length': 20,
                'valid_categories': ['speaking_practice']
            }
        }
        
        logger.info(f"Validador inicializado para nível {level}")
    
    def validate_all(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida todos os dados processados"""
        validation_results = {}
        
        for category, data in processed_data.items():
            if data and category in self.validation_rules:
                logger.info(f"Validando categoria: {category}")
                validation_results[category] = self.validate_category(category, data)
            elif data:
                logger.warning(f"Categoria {category} não tem regras de validação definidas")
                validation_results[category] = {
                    'is_valid': True,
                    'item_count': len(data),
                    'issues': [],
                    'warnings': ['Sem regras de validação definidas']
                }
        
        # Salvar relatório de validação
        self.save_validation_report(validation_results)
        
        return validation_results
    
    def validate_category(self, category: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma categoria específica"""
        rules = self.validation_rules[category]
        issues = []
        warnings = []
        valid_items = 0
        
        for item_id, item_data in data.items():
            item_issues = self.validate_item(category, item_data, rules)
            if item_issues:
                issues.append({
                    'item_id': item_id,
                    'issues': item_issues
                })
            else:
                valid_items += 1
        
        # Verificar critérios gerais da categoria
        category_issues = self.validate_category_general(category, data, rules)
        issues.extend(category_issues)
        
        # Determinar se a categoria é válida
        is_valid = len(issues) == 0 and valid_items > 0
        
        return {
            'is_valid': is_valid,
            'item_count': len(data),
            'valid_items': valid_items,
            'invalid_items': len(issues),
            'issues': issues,
            'warnings': warnings,
            'quality_score': self.calculate_quality_score(valid_items, len(data), len(issues))
        }
    
    def validate_item(self, category: str, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Valida um item individual"""
        issues = []
        
        # Verificar campos obrigatórios
        for field in rules['required_fields']:
            if field not in item_data or not item_data[field]:
                issues.append(f"Campo obrigatório ausente ou vazio: {field}")
        
        # Validações específicas por categoria
        if category == 'vocabulary':
            issues.extend(self.validate_vocabulary_item(item_data, rules))
        elif category == 'grammar':
            issues.extend(self.validate_grammar_item(item_data, rules))
        elif category == 'reading_materials':
            issues.extend(self.validate_reading_item(item_data, rules))
        elif category == 'listening_materials':
            issues.extend(self.validate_listening_item(item_data, rules))
        elif category == 'writing_prompts':
            issues.extend(self.validate_writing_item(item_data, rules))
        elif category == 'speaking_topics':
            issues.extend(self.validate_speaking_item(item_data, rules))
        
        return issues
    
    def validate_vocabulary_item(self, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Validações específicas para vocabulário"""
        issues = []
        
        # Verificar comprimento da palavra
        word = item_data.get('word', '')
        if len(word) < rules['word_min_length']:
            issues.append(f"Palavra muito curta: '{word}' (mínimo {rules['word_min_length']} caracteres)")
        
        # Verificar comprimento da definição
        definition = item_data.get('definition_en', '')
        if len(definition) < rules['definition_min_length']:
            issues.append(f"Definição muito curta: '{definition[:50]}...' (mínimo {rules['definition_min_length']} caracteres)")
        
        # Verificar categoria válida
        category = item_data.get('category', '')
        if category not in rules['valid_categories']:
            issues.append(f"Categoria inválida: '{category}' (válidas: {', '.join(rules['valid_categories'])})")
        
        # Verificar se é phrasal verb
        if item_data.get('is_phrasal_verb', False) and ' ' not in word:
            issues.append(f"Marcado como phrasal verb mas não contém espaço: '{word}'")
        
        return issues
    
    def validate_grammar_item(self, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Validações específicas para gramática"""
        issues = []
        
        # Verificar comprimento do nome da regra
        rule_name = item_data.get('rule_name', '')
        if len(rule_name) < rules['rule_name_min_length']:
            issues.append(f"Nome da regra muito curto: '{rule_name}' (mínimo {rules['rule_name_min_length']} caracteres)")
        
        # Verificar comprimento da descrição
        description = item_data.get('description', '')
        if len(description) < rules['description_min_length']:
            issues.append(f"Descrição muito curta: '{description[:50]}...' (mínimo {rules['description_min_length']} caracteres)")
        
        # Verificar categoria válida
        category = item_data.get('category', '')
        if category not in rules['valid_categories']:
            issues.append(f"Categoria inválida: '{category}' (válidas: {', '.join(rules['valid_categories'])})")
        
        # Verificar se tem exemplos
        examples = item_data.get('examples', [])
        if not examples:
            issues.append("Sem exemplos de uso")
        
        return issues
    
    def validate_reading_item(self, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Validações específicas para materiais de leitura"""
        issues = []
        
        # Verificar comprimento do conteúdo
        content = item_data.get('content', '')
        if len(content) < rules['content_min_length']:
            issues.append(f"Conteúdo muito curto: {len(content)} caracteres (mínimo {rules['content_min_length']})")
        
        # Verificar se tem perguntas
        questions = item_data.get('questions', [])
        if not questions:
            issues.append("Sem perguntas de compreensão")
        
        return issues
    
    def validate_listening_item(self, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Validações específicas para materiais de listening"""
        issues = []
        
        # Verificar comprimento do conteúdo
        content = item_data.get('content', '')
        if len(content) < rules['content_min_length']:
            issues.append(f"Conteúdo muito curto: {len(content)} caracteres (mínimo {rules['content_min_length']})")
        
        # Verificar se parece um diálogo
        if item_data.get('type') == 'dialogue' and content.count('"') < 4:
            issues.append("Marcado como diálogo mas não contém aspas suficientes")
        
        return issues
    
    def validate_writing_item(self, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Validações específicas para prompts de escrita"""
        issues = []
        
        # Verificar comprimento do prompt
        prompt = item_data.get('prompt', '')
        if len(prompt) < rules['prompt_min_length']:
            issues.append(f"Prompt muito curto: {len(prompt)} caracteres (mínimo {rules['prompt_min_length']})")
        
        # Verificar se tem sugestões
        suggestions = item_data.get('suggestions', [])
        if not suggestions:
            issues.append("Sem sugestões de escrita")
        
        return issues
    
    def validate_speaking_item(self, item_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
        """Validações específicas para tópicos de speaking"""
        issues = []
        
        # Verificar comprimento do tópico
        topic = item_data.get('topic', '')
        if len(topic) < rules['topic_min_length']:
            issues.append(f"Tópico muito curto: {len(topic)} caracteres (mínimo {rules['topic_min_length']})")
        
        # Verificar se tem perguntas
        questions = item_data.get('questions', [])
        if not questions:
            issues.append("Sem perguntas para discussão")
        
        return issues
    
    def validate_category_general(self, category: str, data: Dict[str, Any], rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validações gerais da categoria"""
        issues = []
        
        # Verificar se há dados suficientes
        if len(data) < 5:
            issues.append({
                'item_id': 'category_general',
                'issues': [f"Poucos itens na categoria: {len(data)} (recomendado: pelo menos 5)"]
            })
        
        # Verificar duplicatas
        if category == 'vocabulary':
            words = [item.get('word', '').lower() for item in data.values()]
            duplicates = [word for word in set(words) if words.count(word) > 1]
            if duplicates:
                issues.append({
                    'item_id': 'category_general',
                    'issues': [f"Palavras duplicadas encontradas: {', '.join(duplicates[:5])}"]
                })
        
        return issues
    
    def calculate_quality_score(self, valid_items: int, total_items: int, total_issues: int) -> float:
        """Calcula pontuação de qualidade (0-100)"""
        if total_items == 0:
            return 0.0
        
        # Base: porcentagem de itens válidos
        base_score = (valid_items / total_items) * 100
        
        # Penalidade por problemas
        issue_penalty = min(total_issues * 5, 30)  # Máximo 30 pontos de penalidade
        
        final_score = max(base_score - issue_penalty, 0.0)
        return round(final_score, 1)
    
    def save_validation_report(self, validation_results: Dict[str, Any]):
        """Salva relatório de validação"""
        # Relatório detalhado
        report_file = self.output_path / "validation_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Relatório de validação salvo em: {report_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {str(e)}")
        
        # Resumo executivo
        summary = {
            "level": self.level,
            "total_categories": len(validation_results),
            "valid_categories": len([r for r in validation_results.values() if r['is_valid']]),
            "total_items": sum(r['item_count'] for r in validation_results.values()),
            "total_issues": sum(len(r['issues']) for r in validation_results.values()),
            "overall_quality_score": self.calculate_overall_quality(validation_results),
            "category_scores": {
                category: result['quality_score'] 
                for category, result in validation_results.items()
            }
        }
        
        summary_file = self.output_path / "validation_summary.json"
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Resumo de validação salvo em: {summary_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resumo: {str(e)}")
    
    def calculate_overall_quality(self, validation_results: Dict[str, Any]) -> float:
        """Calcula pontuação geral de qualidade"""
        if not validation_results:
            return 0.0
        
        total_score = sum(result['quality_score'] for result in validation_results.values())
        return round(total_score / len(validation_results), 1)
