# ==============================================================================
# Pipeline de Pré-processamento e Treinamento de Modelo de Classificação
# VERSÃO FINAL COM EXPORTAÇÃO DO MODELO E VALIDAÇÃO COM NOVO DADO
# ==============================================================================

import json
import pandas as pd
from datetime import datetime
import requests
import numpy as np
import pickle  # Biblioteca para salvar/carregar objetos Python
import os

# --- Etapa de Configuração: Conectar ao Google Drive ---
# Esta célula irá pedir autorização para aceder ao seu Google Drive.
# Os ficheiros serão salvos lá.
try:
    from google.colab import drive

    drive.mount('/content/drive')
    # Define o caminho base para salvar os ficheiros
    DRIVE_PATH = '/content/drive/MyDrive/'
    print(f"Google Drive montado com sucesso. Os ficheiros serão salvos em: {DRIVE_PATH}")
except ImportError:
    # Se não estiver no Colab, salva na pasta local
    DRIVE_PATH = './'
    print("Ambiente não é o Google Colab. Os ficheiros serão salvos na pasta local.")

# Bibliotecas do Scikit-learn
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Biblioteca para balanceamento de dados
# AVISO: É necessário instalar a biblioteca imbalanced-learn
# No Google Colab ou Jupyter, execute em uma célula: !pip install imbalanced-learn
from imblearn.over_sampling import SMOTE

# Bibliotecas para visualização
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. Carregamento dos Dados via URL ---
DATASET_URL = "https://raw.githubusercontent.com/marmota-alpina/talent-flow-webapp/main/docs/examples/dataset.json"

try:
    response = requests.get(DATASET_URL)
    response.raise_for_status()  # Lança um erro para status HTTP 4xx/5xx
    resumes_data = response.json()
    print(f"Dataset com {len(resumes_data)} currículos carregado com sucesso da URL!")
except requests.exceptions.RequestException as e:
    print(f"Erro ao carregar o dataset da URL: {e}")
    resumes_data = []


# --- 2. Funções de Processamento para DataFrame Simplificado ---

def get_total_years_experience(experiences):
    """Calcula os anos totais de experiência, lidando com diferentes formatos de data."""
    total_days = 0
    today = datetime.now()
    if not experiences: return 0
    for exp in experiences:
        try:
            start_str = exp.get('startDate')
            end_str = exp.get('endDate')

            # Tenta múltiplos formatos de data
            start_date = None
            for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d'):
                try:
                    start_date = datetime.strptime(start_str, fmt)
                    break
                except (ValueError, TypeError):
                    continue

            if start_date is None: continue

            end_date = today
            if not exp.get('isCurrent', False) and end_str:
                for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d'):
                    try:
                        end_date = datetime.strptime(end_str, fmt)
                        break
                    except (ValueError, TypeError):
                        continue

            total_days += (end_date - start_date).days
        except Exception:
            continue  # Ignora a experiência se houver erro na data
    return round(total_days / 365.25, 1)


def get_highest_education_level(formations):
    """Obtém o maior nível de educação da lista de formações."""
    if not formations: return "Nenhum"
    level_order = {"Técnico": 1, "Graduação": 2, "Especialização": 3, "MBA": 3, "Pós-graduação": 3, "Mestrado": 4,
                   "Doutorado": 5, "Nenhum": 0}
    highest = max(formations, key=lambda x: level_order.get(x.get('level', 'Nenhum'), 0), default=None)
    return highest['level'] if highest else "Nenhum"


def extract_simplified_features(data):
    """Processa a lista de JSONs brutos e a transforma em um DataFrame do Pandas com features simplificadas."""
    processed_data = []
    for resume in data:
        all_techs, all_skills = set(), set()
        full_text_parts = [resume.get('summary', '')]
        experiences = resume.get('professionalExperiences', [])

        for exp in experiences:
            full_text_parts.append(exp.get('role', ''))
            for activity in exp.get('activitiesPerformed', []):
                full_text_parts.extend([activity.get('activity', ''), activity.get('problemSolved', '')])
                if isinstance(activity.get('technologies'), list): all_techs.update(activity.get('technologies', []))
                if isinstance(activity.get('appliedSoftSkills'), list): all_skills.update(
                    activity.get('appliedSoftSkills', []))

        num_jobs = len(experiences)
        total_years = get_total_years_experience(experiences)
        avg_years_per_job = total_years / num_jobs if num_jobs > 0 else 0

        processed_data.append({
            'userId': resume.get('userId'), 'experienceLevel': resume.get('experienceLevel'),
            'totalYearsExperience': total_years, 'numberOfJobs': num_jobs,
            'avgYearsPerJob': round(avg_years_per_job, 1),
            'highestEducationLevel': get_highest_education_level(resume.get('academicFormations', [])),
            'allTechnologies': list(all_techs), 'allSoftSkills': list(all_skills),
            'fullText': " ".join(filter(None, full_text_parts))
        })
    return pd.DataFrame(processed_data)


# --- 3. Execução e Engenharia de Características ---
if resumes_data:
    df_simplified = extract_simplified_features(resumes_data)

    print("\n" + "=" * 50)
    print("PASSO 1: DATAFRAME SIMPLIFICADO")
    print("=" * 50)
    print(df_simplified[['userId', 'experienceLevel', 'totalYearsExperience', 'numberOfJobs', 'avgYearsPerJob']].head())

    # Mapeamento e Alvo (y)
    level_mapping = {'Júnior': 0, 'Pleno': 1, 'Sênior': 2, 'Especialista': 3}
    df_simplified = df_simplified.dropna(subset=['experienceLevel'])  # Remove linhas sem o alvo
    y_target = df_simplified['experienceLevel'].map(level_mapping)

    # Pré-processadores
    scaler = MinMaxScaler()
    one_hot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    mlb_tech = MultiLabelBinarizer()
    mlb_skills = MultiLabelBinarizer()
    tfidf_vectorizer = TfidfVectorizer(max_features=200,
                                       stop_words=['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um'])

    # Fit e Transform dos dados completos (antes do split)
    numerical_features_to_scale = ['totalYearsExperience', 'numberOfJobs', 'avgYearsPerJob']
    numerical_features = scaler.fit_transform(df_simplified[numerical_features_to_scale])
    education_features = one_hot_encoder.fit_transform(df_simplified[['highestEducationLevel']])
    tech_features = mlb_tech.fit_transform(df_simplified['allTechnologies'])
    skills_features = mlb_skills.fit_transform(df_simplified['allSoftSkills'])
    text_features = tfidf_vectorizer.fit_transform(df_simplified['fullText']).toarray()

    X_final_features = np.concatenate(
        [numerical_features, education_features, tech_features, skills_features, text_features], axis=1)

    print("\n" + "=" * 50)
    print("PASSO 2: VETOR DE CARACTERÍSTICAS FINAL (PARA O MODELO)")
    print("=" * 50)
    print(f"Dimensões da Matriz de Features (X): {X_final_features.shape}")

    # --- 4. Treinamento do Modelo com SMOTE ---
    X_train, X_test, y_train, y_test = train_test_split(
        X_final_features, y_target, test_size=0.3, random_state=42, stratify=y_target
    )

    min_class_count = y_train.value_counts().min()
    k_neighbors = min(5, min_class_count - 1) if min_class_count > 1 else 1

    smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train_resampled, y_train_resampled)

    y_pred = model.predict(X_test)
    print("\n" + "=" * 50)
    print("CLASSIFICAÇÃO DO MODELO FINAL")
    print("=" * 50)
    class_names = list(level_mapping.keys())
    print(classification_report(y_test, y_pred, zero_division=0, target_names=class_names))

    # --- 5. Exportar Modelo e Pré-processadores ---
    print("\n" + "=" * 50)
    print("PASSO 3: EXPORTANDO OS ARTEFATOS DO MODELO")
    print("=" * 50)

    model_path = os.path.join(DRIVE_PATH, 'talent_flow_classifier.pkl')
    preprocessors_path = os.path.join(DRIVE_PATH, 'talent_flow_preprocessors.pkl')

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Modelo salvo em '{model_path}'")

    artifacts = {
        'scaler': scaler,
        'one_hot_encoder': one_hot_encoder,
        'mlb_tech': mlb_tech,
        'mlb_skills': mlb_skills,
        'tfidf_vectorizer': tfidf_vectorizer,
        'level_mapping': level_mapping,
        'numerical_features_order': numerical_features_to_scale
    }

    with open(preprocessors_path, 'wb') as f:
        pickle.dump(artifacts, f)
    print(f"Pré-processadores salvos em '{preprocessors_path}'")

    # --- 6. Demonstração de Como Usar o Modelo em Produção ---
    print("\n" + "=" * 50)
    print("PASSO 4: DEMONSTRAÇÃO DE PREDIÇÃO COM NOVO DADO")
    print("=" * 50)


    # Função que simula o pipeline de predição
    def predict_experience_level(new_resume_json):
        # Carregar modelo e pré-processadores
        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)
        with open(preprocessors_path, 'rb') as f:
            loaded_artifacts = pickle.load(f)

        df_new = extract_simplified_features([new_resume_json])

        # Aplicar as mesmas transformações (usando os objetos carregados)
        num_feat = loaded_artifacts['scaler'].transform(df_new[loaded_artifacts['numerical_features_order']])
        edu_feat = loaded_artifacts['one_hot_encoder'].transform(df_new[['highestEducationLevel']])
        tech_feat = loaded_artifacts['mlb_tech'].transform(df_new['allTechnologies'])
        skill_feat = loaded_artifacts['mlb_skills'].transform(df_new['allSoftSkills'])
        text_feat = loaded_artifacts['tfidf_vectorizer'].transform(df_new['fullText']).toarray()

        final_features = np.concatenate([num_feat, edu_feat, tech_feat, skill_feat, text_feat], axis=1)

        prediction_encoded = loaded_model.predict(final_features)[0]

        inverse_level_mapping = {v: k for k, v in loaded_artifacts['level_mapping'].items()}
        prediction_decoded = inverse_level_mapping[prediction_encoded]

        return prediction_decoded


    # Exemplo de um novo currículo para teste - SINTAXE CORRIGIDA
    new_resume_to_validate = {
        "userId": "gen_user_1",
        "status": "published",
        "fullName": "Maria Sophia Melo",
        "email": "maria.sophia.melo@email.com",
        "phone": "84 3392 5087",
        "linkedinUrl": "https://linkedin.com/in/mariasophiamelo1",
        "mainArea": "UI/UX Design",
        "experienceLevel": "Júnior",
        "summary": "Júnior em UI/UX Design, com foco em impacto real no negócio e entrega de resultados concretos em projetos relevantes.",
        "academicFormations": [
            {
                "level": "Mestrado",
                "courseName": "Mestrado em UI/UX Design",
                "institution": "Almeida",
                "startDate": "2019-06-27",
                "endDate": "2023-06-26"
            }
        ],
        "languages": [
            {"language": "Português", "proficiency": "Nativo"},
            {"language": "Inglês", "proficiency": "Avançado (C1)"}
        ],
        "professionalExperiences": [
            {
                "experienceType": "CLT",
                "companyName": "Ribeiro - EI",
                "role": "Júnior em UI/UX Design",
                "startDate": "2024-06-25",
                "endDate": "2025-06-20",
                "isCurrent": False,
                "activitiesPerformed": [
                    {
                        "activity": "Criei protótipos interativos com base em testes de usabilidade e entrevistas com usuários.",
                        "problemSolved": "Melhorei a taxa de conversão em 25% ao redesenhar fluxos baseados em testes A/B.",
                        "technologies": ["UI/UX Design", "Cloud Computing", "Desenvolvimento Backend"],
                        "appliedSoftSkills": ["Trabalho em equipe", "Pensamento Analítico", "Colaboração"]
                    }
                ]
            },
            {
                "experienceType": "CLT",
                "companyName": "da Rocha S.A.",
                "role": "Júnior em UI/UX Design",
                "startDate": "2024-12-22",
                "endDate": None,
                "isCurrent": True,
                "activitiesPerformed": [
                    {
                        "activity": "Criei protótipos interativos com base em testes de usabilidade e entrevistas com usuários.",
                        "problemSolved": "Melhorei a taxa de conversão em 25% ao redesenhar fluxos baseados em testes A/B.",
                        "technologies": ["Gestão de Produtos", "Análise de Dados", "DevOps"],
                        "appliedSoftSkills": ["Pensamento Analítico", "Organização", "Resolução de Problemas"]
                    }
                ]
            }
        ]
    }

    predicted_level = predict_experience_level(new_resume_to_validate)
    print(f"O nível previsto para o currículo de '{new_resume_to_validate['fullName']}' é: {predicted_level}")
    print(f"O nível real (esperado) é: {new_resume_to_validate['experienceLevel']}")

