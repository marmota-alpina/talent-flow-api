# Talent Flow API

[![Status dos Testes](https://github.com/marmota-alpina/talent-flow-api/actions/workflows/python-tests.yml/badge.svg)](https://github.com/marmota-alpina/talent-flow-api/actions/workflows/python-tests.yml)

API para classificação de currículos por nível de experiência.


## Requisitos

- Python 3.11+
- Poetry para gerenciamento de dependências
- scikit-learn 1.6.1 (versão específica necessária para compatibilidade com arquivos pickle)
- imbalanced-learn 0.13.0 (para lidar com conjuntos de dados desbalanceados)

## Instalação

```bash
# Instalar dependências sem instalar o projeto em si
poetry install --no-root
```

## Executando a API

```bash
poetry run uvicorn app.main:app --reload
```

A API estará disponível em http://127.0.0.1:8000, e a documentação Swagger em http://127.0.0.1:8000/docs.

## Executando Testes

```bash
poetry run pytest
```

## Solucionando Problemas Comuns

### Comando Não Encontrado: uvicorn

Se você encontrar o erro "Command not found: uvicorn" ao tentar executar a aplicação, isso significa que o uvicorn não está instalado corretamente no seu ambiente virtual Poetry. Para resolver este problema:

1. Certifique-se de que instalou as dependências com a flag `--no-root`:
   ```bash
   poetry install --no-root
   ```

2. Verifique se o uvicorn está instalado:
   ```bash
   poetry run uvicorn --version
   ```

3. Se o problema persistir, tente instalar o uvicorn diretamente:
   ```bash
   poetry run pip install uvicorn
   ```

4. Se você ainda estiver tendo problemas, pode executar o uvicorn diretamente com Python:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### Problemas de Incompatibilidade de Versões

Se você encontrar avisos de incompatibilidade de versões do scikit-learn como:

```
InconsistentVersionWarning: Trying to unpickle estimator from version 1.6.1 when using version 1.7.0
```

### Solução Automatizada

Execute o script shell fornecido para reconstruir automaticamente seu ambiente. Este script tentará vários métodos para garantir que as versões corretas sejam instaladas:

```bash
# Torne o script executável
chmod +x rebuild_env.sh

# Execute o script
./rebuild_env.sh
```

O script irá:
1. Tentar reconstruir o ambiente usando Poetry
2. Se o Poetry falhar, recorrer à instalação direta via pip
3. Verificar se as versões corretas estão instaladas
4. Fornecer comandos para executar a aplicação

### Passos Manuais

Alternativamente, você pode seguir estes passos manuais para resolver o problema:

1. Certifique-se de que o pyproject.toml tem a versão correta do scikit-learn:
   ```toml
   "scikit-learn (==1.6.1) ; python_version >= '3.11.0rc1'"
   ```

2. Atualize o arquivo poetry.lock:
   ```bash
   poetry lock
   ```

3. Reconstrua completamente o ambiente virtual:
   ```bash
   # Remova o ambiente virtual existente
   rm -rf .venv

   # Crie um novo ambiente virtual e instale as dependências
   poetry install --no-root
   ```

4. Execute a aplicação:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Método de Instalação Direta

Se você ainda estiver enfrentando problemas, pode tentar instalar o scikit-learn diretamente usando pip:

1. Torne o script de correção executável:
   ```bash
   chmod +x fix_sklearn_version.sh
   ```

2. Execute o script para instalar o scikit-learn 1.6.1:
   ```bash
   ./fix_sklearn_version.sh
   ```

   Este script irá:
   - Detectar instalações disponíveis de Python e pip
   - Tentar ativar o ambiente virtual se ele existir
   - Tentar vários métodos para instalar o scikit-learn 1.6.1
   - Verificar a instalação

3. Se o script não funcionar, você pode instalar manualmente o scikit-learn 1.6.1:
   ```bash
   # Se estiver usando o ambiente virtual do Poetry
   poetry run pip install scikit-learn==1.6.1

   # Ou se estiver usando uma instalação global do sistema
   pip install scikit-learn==1.6.1

   # Também instale o imbalanced-learn se necessário
   pip install imbalanced-learn==0.13.0
   ```

4. Execute a aplicação:
   ```bash
   # Se o Poetry estiver funcionando
   poetry run uvicorn app.main:app --reload

   # Ou se o Poetry não estiver funcionando
   python -m uvicorn app.main:app --reload
   ```
