#!/usr/bin/env python3
"""
🚀 EXTRACTOR B1 - PIPELINE PRINCIPAL DE EXTRAÇÃO
Processa materiais Cambridge e extrai dados estruturados para a plataforma
"""

import click
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from scripts.extractor import DocumentExtractor
from scripts.processor import DataProcessor
from scripts.validator import DataValidator
from scripts.exporter import DataExporter
from utils.config import Config
from utils.logger import setup_logger

console = Console()
logger = setup_logger()

@click.command()
@click.option('--level', '-l', 
              type=click.Choice(['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'ALL']),
              default='B1', 
              help='Nível de certificação para processar')
@click.option('--validate', '-v', 
              is_flag=True, 
              help='Executar validação dos dados extraídos')
@click.option('--export', '-e', 
              type=click.Choice(['json', 'sql', 'csv', 'all']),
              default='all', 
              help='Formato de exportação')
@click.option('--config', '-c', 
              default='config/settings.yaml', 
              help='Arquivo de configuração')
def main(level, validate, export, config):
    """🚀 EXTRACTOR B1 - Pipeline de Extração de Materiais Cambridge"""
    
    console.print(Panel.fit(
        "[bold blue]🚀 EXTRACTOR B1[/bold blue]\n"
        "[dim]Pipeline de Extração de Materiais Cambridge[/dim]",
        border_style="blue"
    ))
    
    try:
        # Carregar configurações
        config_obj = Config(config)
        console.print(f"✅ Configurações carregadas de: [blue]{config}[/blue]")
        
        # Determinar níveis para processar
        levels_to_process = [level] if level != 'ALL' else ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        for current_level in levels_to_process:
            console.print(f"\n[bold green]🎯 PROCESSANDO NÍVEL: {current_level}[/bold green]")
            
            # ETAPA 1: EXTRAÇÃO BRUTA
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Extraindo documentos...", total=None)
                
                extractor = DocumentExtractor(config_obj, current_level)
                raw_data = extractor.extract_all()
                
                progress.update(task, description=f"✅ Extração concluída: {len(raw_data)} documentos")
            
            # ETAPA 2: PROCESSAMENTO E ESTRUTURAÇÃO
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processando e estruturando dados...", total=None)
                
                processor = DataProcessor(config_obj, current_level)
                processed_data = processor.process_all(raw_data)
                
                progress.update(task, description=f"✅ Processamento concluído: {len(processed_data)} categorias")
            
            # ETAPA 3: VALIDAÇÃO (OPCIONAL)
            if validate:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Validando dados...", total=None)
                    
                    validator = DataValidator(config_obj, current_level)
                    validation_results = validator.validate_all(processed_data)
                    
                    progress.update(task, description="✅ Validação concluída")
                
                # Mostrar resultados da validação
                show_validation_results(validation_results, console)
            
            # ETAPA 4: EXPORTAÇÃO
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Exportando dados...", total=None)
                
                exporter = DataExporter(config_obj, current_level)
                export_results = exporter.export_all(processed_data, export)
                
                progress.update(task, description="✅ Exportação concluída")
            
            # Mostrar resumo dos resultados
            show_export_summary(export_results, current_level, console)
        
        console.print("\n[bold green]🎉 PIPELINE CONCLUÍDO COM SUCESSO![/bold green]")
        console.print("📁 Verifique as pastas de output para os resultados")
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {str(e)}")
        console.print(f"\n[bold red]❌ ERRO NO PIPELINE:[/bold red] {str(e)}")
        sys.exit(1)

def show_validation_results(results, console):
    """Mostra resultados da validação"""
    table = Table(title="📊 Resultados da Validação")
    table.add_column("Categoria", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Itens", style="yellow")
    table.add_column("Problemas", style="red")
    
    for category, result in results.items():
        status = "✅" if result['is_valid'] else "❌"
        problems = len(result.get('issues', []))
        table.add_row(
            category,
            status,
            str(result.get('item_count', 0)),
            str(problems)
        )
    
    console.print(table)

def show_export_summary(results, level, console):
    """Mostra resumo da exportação"""
    table = Table(title=f"📤 Resumo da Exportação - Nível {level}")
    table.add_column("Formato", style="cyan")
    table.add_column("Arquivo", style="blue")
    table.add_column("Tamanho", style="yellow")
    table.add_column("Status", style="green")
    
    for format_type, result in results.items():
        status = "✅" if result['success'] else "❌"
        table.add_row(
            format_type.upper(),
            result.get('filename', 'N/A'),
            result.get('size', 'N/A'),
            status
        )
    
    console.print(table)

if __name__ == "__main__":
    main()
