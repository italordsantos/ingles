# 🚀 EXTRACTOR B1 - PROCESSADOR DE MATERIAIS CAMBRIDGE

## 📁 **ESTRUTURA DO PROJETO**

```
extractor_b1/
├── 📁 materials/                    # Materiais para processamento
│   ├── 📁 A1/                      # Materiais nível A1
│   ├── 📁 A2/                      # Materiais nível A2
│   ├── 📁 B1/                      # Materiais nível B1 (PRINCIPAL)
│   ├── 📁 B2/                      # Materiais nível B2
│   ├── 📁 C1/                      # Materiais nível C1
│   └── 📁 C2/                      # Materiais nível C2
├── 📁 output/                       # Resultados do processamento
│   ├── 📁 raw_extraction/          # Extração bruta dos documentos
│   ├── 📁 processed_data/          # Dados processados e estruturados
│   ├── 📁 database_ready/          # Dados prontos para importação
│   └── 📁 reports/                 # Relatórios de processamento
├── 📁 config/                       # Configurações do sistema
├── 📁 scripts/                      # Scripts de processamento
├── 📁 utils/                        # Utilitários e helpers
└── 📁 tests/                        # Testes automatizados
```

## 🎯 **COMO USAR**

### **1. Preparar Materiais**
- Coloque os PDFs/DOCXs em `materials/B1/` (ou nível desejado)
- Suporta: PDF, DOCX, PPTX, XLSX, HTML, TXT, imagens

### **2. Executar Pipeline**
```bash
# Processar apenas B1
python main.py --level B1

# Processar todos os níveis
python main.py --level ALL

# Processar com validação
python main.py --level B1 --validate
```

### **3. Resultados**
- **Raw**: Conteúdo extraído bruto
- **Processed**: Dados estruturados por categoria
- **Database**: SQL/JSON prontos para importação
- **Reports**: Estatísticas e validação

## 🔧 **INSTALAÇÃO**

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações
```

## 📊 **FORMATOS DE SAÍDA**

### **Vocabulário B1**
```json
{
  "word": "accomplish",
  "phonetic": "/əˈkʌm.plɪʃ/",
  "part_of_speech": "verb",
  "definition_en": "to succeed in doing something",
  "definition_pt": "realizar, conseguir",
  "level": "B1",
  "category": "achievement",
  "examples": ["She accomplished her goal"]
}
```

### **Gramática B1**
```json
{
  "rule_name": "Present Perfect",
  "category": "tenses",
  "level": "B1",
  "description": "Use for past actions with present relevance",
  "examples": ["I have been to Paris", "She has finished her work"],
  "exercises": [...]
}
```

## 🚀 **PRÓXIMOS PASSOS**

1. **Colocar materiais** na pasta do nível desejado
2. **Executar pipeline** de extração
3. **Validar dados** extraídos
4. **Importar no banco** da plataforma
5. **Testar funcionalidades** com dados reais

## 📝 **SUPORTE**

- **Níveis**: A1, A2, B1, B2, C1, C2
- **Formatos**: PDF, DOCX, PPTX, XLSX, HTML, TXT, PNG, JPG
- **Idiomas**: Inglês (principal), Português (traduções)
- **Certificações**: Cambridge, IELTS, TOEFL, etc.
