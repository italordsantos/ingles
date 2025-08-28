#!/usr/bin/env python3
"""
⚙️ CONFIGURAÇÃO DO SISTEMA
Gerencia configurações e parâmetros do projeto
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

class Config:
    """Gerencia configurações do sistema"""
    
    def __init__(self, config_file: str = "config/settings.yaml"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        
        # Configurações padrão
        self.defaults = {
            "extraction": {
                "supported_formats": [".pdf", ".docx", ".pptx", ".xlsx", ".html", ".txt"],
                "max_file_size_mb": 100,
                "extract_images": True,
                "extract_tables": True,
                "extract_structure": True
            },
            "processing": {
                "min_word_length": 2,
                "min_definition_length": 10,
                "min_rule_name_length": 5,
                "min_description_length": 20,
                "auto_categorize": True,
                "generate_examples": True
            },
            "validation": {
                "strict_mode": False,
                "min_quality_score": 70.0,
                "max_issues_per_item": 5,
                "require_examples": False
            },
            "export": {
                "formats": ["json", "sql", "csv", "postgresql"],
                "include_metadata": True,
                "compress_output": False,
                "backup_original": True
            },
            "logging": {
                "level": "INFO",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                "file_logging": True,
                "console_logging": True
            }
        }
        
        # Mesclar configurações
        self.config = self.merge_configs(self.defaults, self.config)
        
        logger.info(f"Configuração carregada de: {self.config_file}")
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega arquivo de configuração"""
        if not self.config_file.exists():
            logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
            logger.info("Usando configurações padrão")
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info("Configuração YAML carregada com sucesso")
            return config or {}
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            logger.info("Usando configurações padrão")
            return {}
    
    def merge_configs(self, defaults: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Mescla configurações padrão com configurações do usuário"""
        merged = defaults.copy()
        
        def deep_merge(base: Dict[str, Any], override: Dict[str, Any]):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(merged, user_config)
        return merged
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_extraction_config(self) -> Dict[str, Any]:
        """Obtém configurações de extração"""
        return self.config.get('extraction', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Obtém configurações de processamento"""
        return self.config.get('processing', {})
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Obtém configurações de validação"""
        return self.config.get('validation', {})
    
    def get_export_config(self) -> Dict[str, Any]:
        """Obtém configurações de exportação"""
        return self.config.get('export', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtém configurações de logging"""
        return self.config.get('logging', {})
    
    def is_format_supported(self, file_extension: str) -> bool:
        """Verifica se formato é suportado"""
        supported = self.get('extraction.supported_formats', [])
        return file_extension.lower() in supported
    
    def get_max_file_size(self) -> int:
        """Obtém tamanho máximo de arquivo em bytes"""
        max_mb = self.get('extraction.max_file_size_mb', 100)
        return max_mb * 1024 * 1024
    
    def should_extract_images(self) -> bool:
        """Verifica se deve extrair imagens"""
        return self.get('extraction.extract_images', True)
    
    def should_extract_tables(self) -> bool:
        """Verifica se deve extrair tabelas"""
        return self.get('extraction.extract_tables', True)
    
    def should_extract_structure(self) -> bool:
        """Verifica se deve extrair estrutura"""
        return self.get('extraction.extract_structure', True)
    
    def get_min_word_length(self) -> int:
        """Obtém comprimento mínimo de palavra"""
        return self.get('processing.min_word_length', 2)
    
    def get_min_definition_length(self) -> int:
        """Obtém comprimento mínimo de definição"""
        return self.get('processing.min_definition_length', 10)
    
    def should_auto_categorize(self) -> bool:
        """Verifica se deve categorizar automaticamente"""
        return self.get('processing.auto_categorize', True)
    
    def should_generate_examples(self) -> bool:
        """Verifica se deve gerar exemplos"""
        return self.get('processing.generate_examples', True)
    
    def is_strict_validation(self) -> bool:
        """Verifica se validação é estrita"""
        return self.get('validation.strict_mode', False)
    
    def get_min_quality_score(self) -> float:
        """Obtém pontuação mínima de qualidade"""
        return self.get('validation.min_quality_score', 70.0)
    
    def get_max_issues_per_item(self) -> int:
        """Obtém máximo de problemas por item"""
        return self.get('validation.max_issues_per_item', 5)
    
    def should_require_examples(self) -> bool:
        """Verifica se exemplos são obrigatórios"""
        return self.get('validation.require_examples', False)
    
    def get_export_formats(self) -> list:
        """Obtém formatos de exportação"""
        return self.get('export.formats', ['json', 'sql', 'csv', 'postgresql'])
    
    def should_include_metadata(self) -> bool:
        """Verifica se deve incluir metadados"""
        return self.get('export.include_metadata', True)
    
    def should_compress_output(self) -> bool:
        """Verifica se deve comprimir saída"""
        return self.get('export.compress_output', False)
    
    def should_backup_original(self) -> bool:
        """Verifica se deve fazer backup do original"""
        return self.get('export.backup_original', True)
    
    def get_log_level(self) -> str:
        """Obtém nível de logging"""
        return self.get('logging.level', 'INFO')
    
    def get_log_format(self) -> str:
        """Obtém formato de logging"""
        return self.get('logging.format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}')
    
    def should_file_log(self) -> bool:
        """Verifica se deve fazer log em arquivo"""
        return self.get('logging.file_logging', True)
    
    def should_console_log(self) -> bool:
        """Verifica se deve fazer log no console"""
        return self.get('logging.console_logging', True)
    
    def save_config(self, config_file: Optional[str] = None) -> bool:
        """Salva configuração atual"""
        if config_file is None:
            config_file = self.config_file
        
        try:
            config_file = Path(config_file)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Configuração salva em: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {str(e)}")
            return False
    
    def create_default_config(self, config_file: Optional[str] = None) -> bool:
        """Cria arquivo de configuração padrão"""
        if config_file is None:
            config_file = self.config_file
        
        try:
            config_file = Path(config_file)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.defaults, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Configuração padrão criada em: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar configuração padrão: {str(e)}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Valida configuração atual"""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Verificar configurações obrigatórias
        required_sections = ['extraction', 'processing', 'validation', 'export', 'logging']
        for section in required_sections:
            if section not in self.config:
                validation_results['issues'].append(f"Seção obrigatória ausente: {section}")
                validation_results['is_valid'] = False
        
        # Verificar valores específicos
        if self.get_max_file_size() <= 0:
            validation_results['issues'].append("Tamanho máximo de arquivo deve ser positivo")
            validation_results['is_valid'] = False
        
        if self.get_min_quality_score() < 0 or self.get_min_quality_score() > 100:
            validation_results['warnings'].append("Pontuação de qualidade deve estar entre 0 e 100")
        
        if not self.get_export_formats():
            validation_results['issues'].append("Pelo menos um formato de exportação deve ser especificado")
            validation_results['is_valid'] = False
        
        return validation_results
