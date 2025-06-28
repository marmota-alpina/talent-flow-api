# Requisitos da API de Classificação - Talent Flow

## 1. Introdução

Este documento estabelece os requisitos funcionais e não-funcionais para a API de Inteligência Artificial do Talent Flow. O objetivo principal desta API é fornecer um serviço de inferência que recebe dados de um currículo e retorna uma classificação de nível de experiência profissional (senioridade) com base num modelo de Machine Learning pré-treinado.

## 2. Requisitos Funcionais (RF)

| ID | Requisito | Descrição Detalhada | Critérios de Aceitação |
| :--- | :--- | :--- | :--- |
| **RF-001** | Endpoint de Classificação de Currículo | A API deve expor um endpoint `POST /classify-resume/` para classificar a senioridade de um currículo. | 1. O endpoint deve aceitar requisições `POST`.<br>2. O corpo da requisição deve ser um JSON válido que corresponda ao modelo `ResumePayload`.<br>3. A resposta deve ser um JSON com `status 200 OK` e corresponder ao modelo `ClassificationResponse`.<br>4. Uma requisição com formato inválido deve retornar `status 422 Unprocessable Entity`. |
| **RF-002**| Carregamento do Modelo e Artefactos | Na inicialização, a API deve carregar em memória o modelo de classificação treinado e todos os objetos de pré-processamento. | 1. O ficheiro `talent_flow_classifier.pkl` deve ser carregado.<br>2. O ficheiro `talent_flow_preprocessors.pkl` deve ser carregado.<br>3. Se os ficheiros não forem encontrados, a API deve lançar um erro crítico no log e falhar ao iniciar. |
| **RF-003**| Pipeline de Inferência Consistente | A API deve aplicar a um novo currículo exatamente a mesma sequência de passos de engenharia de características e vetorização utilizada durante o treino do modelo. | 1. Extrair `totalYearsExperience`, `numberOfJobs`, `avgYearsPerJob`.<br>2. Aplicar `MinMaxScaler` às características numéricas.<br>3. Aplicar `OneHotEncoder` à característica `highestEducationLevel`.<br>4. Aplicar `MultiLabelBinarizer` às listas de `technologies` e `softSkills`.<br>5. Aplicar `TfidfVectorizer` ao campo `fullText`.<br>6. Concatenar os vetores na ordem correta antes da predição. |
| **RF-004**| Resposta da Classificação | A resposta do endpoint deve conter a classificação de senioridade em formato de texto e a pontuação de confiança da predição. | 1. O campo `predictedExperienceLevel` deve conter um dos valores: "Júnior", "Pleno", "Sênior", "Especialista".<br>2. O campo `confidenceScore` deve ser um valor `float` entre 0.0 e 1.0, representando a probabilidade da classe prevista. |

## 3. Requisitos Não-Funcionais (RNF)

| ID | Requisito | Descrição Detalhada | Critérios de Aceitação |
| :--- | :--- | :--- | :--- |
| **RNF-001**| Desempenho | A API deve ser performática, com baixa latência para não impactar a experiência do utilizador na aplicação frontend. | 1. O tempo de resposta do endpoint `/classify-resume/` deve ser, em média, inferior a 500ms para 95% das requisições (p95). |
| **RNF-002**| Segurança | A API deve implementar práticas de segurança para proteger o serviço e os dados. | 1. A API deve ter uma política de CORS (Cross-Origin Resource Sharing) que permita requisições apenas de domínios autorizados (o frontend do Talent Flow).<br>2. A validação de todos os dados de entrada através dos modelos Pydantic deve ser rigorosa. |
| **RNF-003**| Escalabilidade | A arquitetura da API deve suportar o crescimento do número de requisições sem degradação da performance. | 1. A API deve ser *stateless* (sem estado), permitindo que múltiplas instâncias possam ser executadas em paralelo num ambiente de contêineres (ex: Docker). |
| **RNF-004**| Manutenibilidade | O código-fonte deve ser limpo, bem documentado e fácil de manter e estender. | 1. Seguir as diretrizes de código definidas no `junie/guidelines.md`.<br>2. Utilizar tipagem estática do Python em todas as funções.<br>3. Todas as funções e endpoints públicos devem ter `docstrings` claras. |
| **RNF-005**| Observabilidade | A API deve fornecer logs suficientes para monitorização e depuração. | 1. Logs devem ser gerados para cada requisição recebida (nível INFO).<br>2. Erros internos durante o processamento devem gerar logs detalhados (nível ERROR). |
| **RNF-006**| Testabilidade | O código deve ser coberto por testes automatizados para garantir a sua fiabilidade. | 1. Cobertura de testes de unidade de, no mínimo, 80% para a lógica de negócio e o endpoint da API. |

---

## 4. Requisitos de Dados

* **RDT-001: Contrato de Payload de Entrada (`ResumePayload`)**
    O corpo da requisição `POST` para `/classify-resume/` deve seguir a seguinte estrutura JSON:
    ```json
    {
      "userId": "string",
      "summary": "string (opcional)",
      "professionalExperiences": [
        {
          "role": "string (opcional)",
          "isCurrent": "boolean (opcional)",
          "startDate": "string (formato ISO, opcional)",
          "endDate": "string (formato ISO, opcional)",
          "activitiesPerformed": [
            {
              "activity": "string (opcional)",
              "problemSolved": "string (opcional)",
              "technologies": ["string"],
              "appliedSoftSkills": ["string"]
            }
          ]
        }
      ],
      "academicFormations": [
        {
          "level": "string (opcional)"
        }
      ]
    }
    ```

* **RDT-002: Artefactos do Modelo de ML**
    A API depende dos seguintes ficheiros, que devem estar localizados no diretório `ml/`:
    - `talent_flow_classifier.pkl`: O objeto do modelo RandomForest treinado.
    - `talent_flow_preprocessors.pkl`: Um dicionário Python contendo todos os objetos de pré-processamento (`scaler`, `encoders`, `vectorizer`) utilizados no treino.
