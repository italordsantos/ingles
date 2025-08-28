#!/usr/bin/env python3
"""
📝 SISTEMA DE LOGGING
Configuração e gerenciamento de logs do sistema
"""

import sys
from pathlib import Path
from loguru import logger

def setup_logger(log_level: str = "INFO", log_file: str = None) -> None:
    """Configura o sistema de logging"""
    
    # Remover handlers padrão
    logger.remove()
    
    # Configurar formato padrão
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Handler para console
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
    
    # Handler para arquivo de erro
    error_log_path = Path("logs/errors.log")
    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        error_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Handler para arquivo de debug
    debug_log_path = Path("logs/debug.log")
    debug_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        debug_log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="20 MB",
        retention="3 days",
        compression="zip"
    )
    
    logger.info("Sistema de logging configurado com sucesso")

def get_logger(name: str = None):
    """Obtém logger configurado"""
    if name:
        return logger.bind(name=name)
    return logger

def log_function_call(func_name: str, args: tuple = None, kwargs: dict = None):
    """Decorator para log de chamadas de função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Chamando função: {func_name}")
            if args:
                logger.debug(f"Argumentos posicionais: {args}")
            if kwargs:
                logger.debug(f"Argumentos nomeados: {kwargs}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Função {func_name} executada com sucesso")
                return result
            except Exception as e:
                logger.error(f"Erro na função {func_name}: {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_execution_time(func_name: str):
    """Decorator para log de tempo de execução"""
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"Iniciando execução da função: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Função {func_name} executada em {execution_time:.2f} segundos")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Função {func_name} falhou após {execution_time:.2f} segundos: {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_memory_usage(func_name: str):
    """Decorator para log de uso de memória"""
    import psutil
    import os
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            logger.debug(f"Memória antes de {func_name}: {memory_before:.2f} MB")
            
            try:
                result = func(*args, **kwargs)
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_diff = memory_after - memory_before
                
                logger.info(f"Memória após {func_name}: {memory_after:.2f} MB (diferença: {memory_diff:+.2f} MB)")
                return result
            except Exception as e:
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_diff = memory_after - memory_before
                
                logger.error(f"Função {func_name} falhou. Memória: {memory_after:.2f} MB (diferença: {memory_diff:+.2f} MB)")
                raise
        
        return wrapper
    return decorator

def log_file_operations(operation: str):
    """Decorator para log de operações de arquivo"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Iniciando {operation}: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"{operation} concluído com sucesso: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Erro na {operation}: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_database_operations(operation: str):
    """Decorator para log de operações de banco de dados"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Iniciando operação de banco: {operation} - {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"Operação de banco concluída: {operation} - {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Erro na operação de banco {operation}: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_validation_results(validation_type: str):
    """Decorator para log de resultados de validação"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Iniciando validação: {validation_type} - {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, dict):
                    if result.get('is_valid', False):
                        logger.info(f"Validação {validation_type} bem-sucedida: {func.__name__}")
                    else:
                        issues_count = len(result.get('issues', []))
                        logger.warning(f"Validação {validation_type} com {issues_count} problemas: {func.__name__}")
                else:
                    logger.info(f"Validação {validation_type} concluída: {func.__name__}")
                
                return result
            except Exception as e:
                logger.error(f"Erro na validação {validation_type}: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_export_results(export_format: str):
    """Decorator para log de resultados de exportação"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Iniciando exportação: {export_format} - {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, dict) and result.get('success', False):
                    logger.info(f"Exportação {export_format} bem-sucedida: {func.__name__}")
                else:
                    logger.warning(f"Exportação {export_format} com problemas: {func.__name__}")
                
                return result
            except Exception as e:
                logger.error(f"Erro na exportação {export_format}: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_performance_metrics(metric_name: str):
    """Decorator para log de métricas de performance"""
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"Iniciando medição de {metric_name}: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log com diferentes níveis baseado no tempo
                if execution_time < 1.0:
                    logger.debug(f"{metric_name}: {execution_time:.3f}s - {func.__name__}")
                elif execution_time < 5.0:
                    logger.info(f"{metric_name}: {execution_time:.3f}s - {func.__name__}")
                else:
                    logger.warning(f"{metric_name}: {execution_time:.3f}s (lento) - {func.__name__}")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Erro em {metric_name} após {execution_time:.3f}s: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_data_processing(category: str, item_count: int = None):
    """Decorator para log de processamento de dados"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if item_count:
                logger.info(f"Iniciando processamento de {category}: {item_count} itens - {func.__name__}")
            else:
                logger.debug(f"Iniciando processamento de {category}: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, dict):
                    processed_count = len(result) if result else 0
                    logger.info(f"Processamento de {category} concluído: {processed_count} itens processados")
                else:
                    logger.info(f"Processamento de {category} concluído: {func.__name__}")
                
                return result
            except Exception as e:
                logger.error(f"Erro no processamento de {category}: {func.__name__} - {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_error_with_context(error: Exception, context: str = "", additional_info: dict = None):
    """Log de erro com contexto adicional"""
    error_msg = f"ERRO: {str(error)}"
    if context:
        error_msg += f" | Contexto: {context}"
    
    if additional_info:
        error_msg += f" | Info adicional: {additional_info}"
    
    logger.error(error_msg)
    
    # Log detalhado para debug
    logger.debug(f"Detalhes do erro: {type(error).__name__}")
    logger.debug(f"Arquivo: {error.__traceback__.tb_frame.f_code.co_filename}")
    logger.debug(f"Linha: {error.__traceback__.tb_lineno}")
    logger.debug(f"Função: {error.__traceback__.tb_frame.f_code.co_name}")

def log_success_with_context(success_msg: str, context: str = "", additional_info: dict = None):
    """Log de sucesso com contexto adicional"""
    success_log = f"SUCESSO: {success_msg}"
    if context:
        success_log += f" | Contexto: {context}"
    
    if additional_info:
        success_log += f" | Info adicional: {additional_info}"
    
    logger.info(success_log)

def log_warning_with_context(warning_msg: str, context: str = "", additional_info: dict = None):
    """Log de aviso com contexto adicional"""
    warning_log = f"AVISO: {warning_msg}"
    if context:
        warning_log += f" | Contexto: {context}"
    
    if additional_info:
        warning_log += f" | Info adicional: {additional_info}"
    
    logger.warning(warning_log)
