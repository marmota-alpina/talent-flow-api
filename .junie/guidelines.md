# Diretrizes de Desenvolvimento - Talent Flow API

Este documento serve como guia central para o desenvolvimento, configuração, teste e manutenção da API do Talent Flow. O objetivo é garantir a consistência do código, a qualidade e a facilidade de colaboração na equipa.

## 1. Configuração do Ambiente

O projeto utiliza **Poetry** para gestão de dependências e ambientes virtuais, garantindo um ambiente de desenvolvimento reprodutível.

### 1.1. Pré-requisitos
- Python 3.11+
- Poetry instalado

### 1.2. Instalação de Dependências
Após clonar o repositório, navegue até ao diretório raiz `talent-flow-api` e execute o seguinte comando para instalar todas as dependências listadas no `pyproject.toml`:
```bash
poetry install
1.3. Adicionar Novas DependênciasPara adicionar uma nova biblioteca ao projeto, utilize o comando add do Poetry. Isto garante que tanto o pyproject.toml como o poetry.lock sejam atualizados.# Exemplo para adicionar a biblioteca 'httpx' para testes assíncronos
poetry add httpx
1.4. Executar a API LocalmentePara executar o servidor de desenvolvimento local com hot-reload ativado, utilize o seguinte comando a partir do diretório raiz:poetry run uvicorn app.main:app --reload
A API estará disponível em http://127.0.0.1:8000.A documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI estará disponível em http://127.0.0.1:8000/docs.2. TestesUtilizamos Pytest como framework de testes para garantir a robustez e fiabilidade da nossa API.2.1. Configuração de TestesAs dependências de teste (como pytest e requests) devem ser adicionadas como dependências de desenvolvimento no Poetry:poetry add pytest --group dev
poetry add requests --group dev
2.2. Executar os TestesPara executar todos os testes localizados na pasta tests/, utilize o seguinte comando a partir do diretório raiz:poetry run pytest
2.3. Adicionar Novos TestesCrie um novo ficheiro dentro do diretório tests/, seguindo a convenção de nomenclatura test_*.py (ex: test_predictions.py).Dentro do ficheiro, crie funções de teste que também comecem com test_.Utilize o TestClient do FastAPI para fazer requisições à sua aplicação sem a necessidade de um servidor em execução. Isto permite testes mais rápidos e isolados.2.4. Exemplo de Teste de Unidade para o EndpointO ficheiro tests/test_api.py deve ser refatorado para usar pytest e o TestClient, como no exemplo abaixo. Este teste verifica se o endpoint /classify-resume/ responde com sucesso e se a estrutura da resposta está correta.# tests/test_api.py

from fastapi.testclient import TestClient
import sys
import os

# Adicionar o diretório da app ao path para importações diretas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app # Importa a instância da app FastAPI
from app.resume import get_random_resume # Importa a função para obter dados de teste

# Cria um cliente de teste para a nossa aplicação
client = TestClient(app)

def test_classify_resume_endpoint_success():
    """
    Testa se o endpoint /classify-resume/ retorna um status 200 OK
    e um payload válido para um currículo correto.
    """
    # 1. Obter dados de teste
    random_resume = get_random_resume()
    payload = {
        "userId": random_resume.get("userId", "test_user_pytest"),
        "summary": random_resume.get("summary"),
        "professionalExperiences": random_resume.get("professionalExperiences"),
        "academicFormations": random_resume.get("academicFormations")
    }

    # 2. Fazer a requisição para a API
    response = client.post("/classify-resume/", json=payload)

    # 3. Verificar o resultado (Asserts)
    assert response.status_code == 200
    data = response.json()
    assert "userId" in data
    assert "predictedExperienceLevel" in data
    assert "confidenceScore" in data
    assert data["userId"] == payload["userId"]
    assert data["predictedExperienceLevel"] in ["Júnior", "Pleno", "Sênior", "Especialista"]

def test_classify_resume_missing_userid():
    """
    Testa se a API retorna um erro 422 Unprocessable Entity quando
    um campo obrigatório como userId está em falta.
    """
    # Payload inválido sem userId
    payload = {
        "summary": "Resumo de teste sem userId.",
    }
    
    response = client.post("/classify-resume/", json=payload)
    
    assert response.status_code == 422
3. Diretrizes Adicionais de Desenvolvimento3.1. Qualidade de Código (Clean Code)Funções Pequenas e Focadas: Mantenha as funções com uma única responsabilidade. As funções de pré-processamento em app/main.py são um bom exemplo.Nomenclatura Clara: Use nomes de variáveis e funções que descrevam claramente o seu propósito (ex: extract_features_for_prediction).Tipagem Estática: Utilize type hints do Python em todas as assinaturas de função para melhorar a legibilidade e permitir a verificação estática. O FastAPI aproveita-se disto para validação.Modelos Pydantic: Centralize todas as estruturas de dados de entrada e saída em app/models.py. Isto serve como uma fonte única de verdade para os contratos da API.3.2. CORS (Cross-Origin Resource Sharing)Para permitir que a sua aplicação frontend (ex: talent-flow-webapp a correr em localhost:4200) comunique com a API (a correr em localhost:8000), é necessário configurar o middleware de CORS no FastAPI.Adicione o seguinte bloco ao app/main.py:# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ... outros imports

app = FastAPI(title="Talent Flow API", version="1.0")

# --- Configuração do CORS ---
origins = [
    "http://localhost",
    "http://localhost:4200", # Endereço do frontend Angular em desenvolvimento
    "[https://talent-flow-webapp.web.app](https://talent-flow-webapp.web.app)", # Endereço de produção do frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# ... resto do código da API
3.3. DocumentaçãoDocstrings: Todas as funções públicas e módulos devem ter docstrings claras explicando o seu propósito, argumentos e o que retornam.FastAPI Docs: Aproveite a documentação automática. Adicione descrições aos seus endpoints e modelos Pydantic para enriquecer a Swagger UI e a ReDoc.@app.post("/classify-resume/", response_model=ClassificationResponse, summary="Classifica o Nível de Senioridade")
def classify_resume(payload: ResumePayload):
    """
    Recebe os dados estruturados de um currículo e utiliza um modelo
    de Machine Learning para prever o nível de experiência do profissional.

    - **payload**: Corpo da requisição com os dados do currículo.
    - **Retorna**: A classificação prevista e uma pontuação de confiança.
    """
    # ... lógica
