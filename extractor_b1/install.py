#!/usr/bin/env python3
"""
🔧 INSTALADOR RÁPIDO DO EXTRACTOR B1
Script para instalação e configuração inicial do sistema
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_directories():
    """Cria a estrutura de diretórios necessária"""
    print("📁 Criando estrutura de diretórios...")
    
    directories = [
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
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ Estrutura de diretórios criada!")

def test_installation():
    """Testa se a instalação foi bem-sucedida"""
    print("🧪 Testando instalação...")
    
    try:
        # Testar importação dos módulos principais
        from scripts.extractor import DocumentExtractor
        from scripts.processor import DataProcessor
        from utils.config import Config
        
        print("✅ Importações funcionando corretamente!")
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def main():
    """Função principal de instalação"""
    print("🚀 INSTALADOR DO EXTRACTOR B1")
    print("=" * 50)
    
    # 1. Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação das dependências")
        return False
    
    # 2. Criar diretórios
    create_directories()
    
    # 3. Testar instalação
    if not test_installation():
        print("❌ Falha no teste de instalação")
        return False
    
    print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print("\n📝 PRÓXIMOS PASSOS:")
    print("   1. Coloque seus materiais PDF/DOCX em materials/B1/")
    print("   2. Execute: python main.py --level B1")
    print("   3. Ou teste com: python example_usage.py")
    print("\n📚 Para mais informações, consulte o README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
