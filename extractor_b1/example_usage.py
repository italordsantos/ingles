#!/usr/bin/env python3
"""
📚 EXEMPLO DE USO DO EXTRACTOR B1
Demonstra como usar o sistema de extração e processamento
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from scripts.extractor import DocumentExtractor
from scripts.processor import DataProcessor
from scripts.validator import DataValidator
from scripts.exporter import DataExporter
from utils.config import Config
from utils.logger import setup_logger

def main():
    """Exemplo de uso completo do sistema"""
    
    print("🚀 EXTRACTOR B1 - EXEMPLO DE USO")
    print("=" * 50)
    
    # 1. Configurar logging
    setup_logger()
    
    # 2. Carregar configurações
    config = Config("config/settings.yaml")
    
    # 3. Exemplo com nível B1
    level = "B1"
    print(f"\n📁 Processando nível: {level}")
    
    # 4. Extrair documentos
    print("\n🔍 ETAPA 1: EXTRAÇÃO DE DOCUMENTOS")
    print("-" * 40)
    
    extractor = DocumentExtractor(config, level)
    
    # Verificar se há materiais para processar
    materials_path = Path(f"materials/{level}")
    if not materials_path.exists():
        print(f"❌ Pasta de materiais não encontrada: {materials_path}")
        print("📝 Crie a pasta e adicione seus PDFs/DOCXs")
        return
    
    # Listar materiais disponíveis
    materials = list(materials_path.glob("*"))
    print(f"📚 Materiais encontrados: {len(materials)}")
    for material in materials:
        print(f"   - {material.name}")
    
    # Extrair conteúdo
    raw_data = extractor.extract_all()
    print(f"✅ Extração concluída: {len(raw_data)} documentos processados")
    
    # 5. Processar e estruturar dados
    print("\n🔧 ETAPA 2: PROCESSAMENTO E ESTRUTURAÇÃO")
    print("-" * 40)
    
    processor = DataProcessor(config, level)
    processed_data = processor.process_all(raw_data)
    
    # Mostrar resumo dos dados processados
    for category, data in processed_data.items():
        if data:
            print(f"   📊 {category}: {len(data)} itens")
    
    # 6. Validar dados
    print("\n✅ ETAPA 3: VALIDAÇÃO DE DADOS")
    print("-" * 40)
    
    validator = DataValidator(config, level)
    validation_results = validator.validate_all(processed_data)
    
    # Mostrar resultados da validação
    for category, result in validation_results.items():
        status = "✅" if result['is_valid'] else "❌"
        quality = result.get('quality_score', 0)
        print(f"   {status} {category}: {quality:.1f}/100")
    
    # 7. Exportar dados
    print("\n📤 ETAPA 4: EXPORTAÇÃO DE DADOS")
    print("-" * 40)
    
    exporter = DataExporter(config, level)
    export_results = exporter.export_all(processed_data, "all")
    
    # Mostrar resultados da exportação
    for format_type, result in export_results.items():
        if result.get('success'):
            print(f"   ✅ {format_type.upper()}: {result.get('filename', 'N/A')}")
        else:
            print(f"   ❌ {format_type.upper()}: {result.get('error', 'Erro desconhecido')}")
    
    # 8. Resumo final
    print("\n🎉 PROCESSAMENTO CONCLUÍDO!")
    print("=" * 50)
    
    total_items = sum(len(data) for data in processed_data.values() if data)
    print(f"📊 Total de itens processados: {total_items}")
    
    # Mostrar localização dos arquivos de saída
    output_paths = {
        "Raw Extraction": f"output/raw_extraction/{level}/",
        "Processed Data": f"output/processed_data/{level}/",
        "Database Ready": f"output/database_ready/{level}/",
        "Reports": f"output/reports/{level}/"
    }
    
    print("\n📁 ARQUIVOS DE SAÍDA:")
    for description, path in output_paths.items():
        if Path(path).exists():
            print(f"   📂 {description}: {path}")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Verifique os arquivos de saída")
    print("   2. Use os dados JSON/SQL na sua plataforma")
    print("   3. Verifique os relatórios de validação")
    print("   4. Execute novamente para novos materiais")

def create_sample_materials():
    """Cria estrutura de pastas e materiais de exemplo"""
    
    print("\n📁 CRIANDO ESTRUTURA DE EXEMPLO")
    print("-" * 40)
    
    # Criar estrutura de pastas
    folders = [
        "materials/A1",
        "materials/A2", 
        "materials/B1",
        "materials/B2",
        "materials/C1",
        "materials/C2",
        "output/raw_extraction",
        "output/processed_data",
        "output/database_ready",
        "output/reports",
        "logs"
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Criada pasta: {folder}")
    
    # Criar arquivo de exemplo B1
    sample_file = Path("materials/B1/sample_vocabulary.txt")
    sample_content = """VOCABULARY B1 - SAMPLE

Family and Relationships:
mother - a female parent
father - a male parent
sister - a female sibling
brother - a male sibling
grandmother - mother of your parent
grandfather - father of your parent

Food and Drinks:
restaurant - a place where you can eat
kitchen - room where food is prepared
breakfast - first meal of the day
lunch - meal eaten in the middle of the day
dinner - main meal of the day
coffee - hot drink made from coffee beans
tea - hot drink made from tea leaves

Jobs and Professions:
teacher - someone who teaches
doctor - medical professional
engineer - designs and builds things
manager - person in charge of others
employee - person who works for a company
"""
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"   ✅ Criado arquivo de exemplo: {sample_file}")
    
    print("\n📝 ARQUIVO DE EXEMPLO CRIADO!")
    print("   Agora você pode executar o sistema com:")
    print("   python example_usage.py")

if __name__ == "__main__":
    # Verificar se há materiais para processar
    if not any(Path("materials").glob("*/*")):
        print("📁 Nenhum material encontrado. Criando estrutura de exemplo...")
        create_sample_materials()
        print("\n" + "="*50)
    
    # Executar exemplo
    main()
