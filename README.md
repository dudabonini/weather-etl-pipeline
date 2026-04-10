# 🌦️ Weather ETL Pipeline

Pipeline de dados meteorológicos da cidade de São Paulo, construído com Apache Airflow, Docker, PostgreSQL e Python.

---

## 📌 Sobre o Projeto

Este projeto implementa um pipeline ETL (Extract, Transform, Load) automatizado que coleta dados climáticos em tempo real da API OpenWeatherMap, transforma os dados e os armazena em um banco de dados PostgreSQL — tudo orquestrado pelo Apache Airflow rodando em containers Docker.

---

## 🏗️ Arquitetura

```
OpenWeatherMap API
        ↓
   [ Extract ]  → Coleta dados meteorológicos de São Paulo
        ↓
   [ Transform ] → Limpeza e transformação dos dados
        ↓
   [ Load ]     → Armazena no PostgreSQL
        ↓
   PostgreSQL Database (sp_weather)
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|---|---|
| **Python** | Linguagem principal |
| **Apache Airflow** | Orquestração do pipeline |
| **Docker / Docker Compose** | Containerização dos serviços |
| **PostgreSQL** | Armazenamento dos dados |
| **OpenWeatherMap API** | Fonte dos dados meteorológicos |
| **Pandas** | Transformação dos dados |
| **SQLAlchemy** | Conexão com o banco de dados |

---

## 📁 Estrutura do Projeto

```
weather-etl-pipeline/
├── dags/
│   └── weather_dag.py       # DAG principal do Airflow
├── src/
│   ├── extract_data.py      # Extração da API
│   ├── transform_data.py    # Transformação dos dados
│   └── load_data.py         # Carga no PostgreSQL
├── config/
│   └── .env                 # Variáveis de ambiente (não versionado)
├── data/                    # Dados temporários
├── logs/                    # Logs do Airflow
├── docker-compose.yml       # Configuração dos containers
└── README.md
```

---

## ⚙️ Como Executar

### Pré-requisitos

- Docker Desktop instalado e rodando
- Conta na [OpenWeatherMap API](https://openweathermap.org/api) (gratuita)

### Passo a Passo

**1. Clone o repositório**
```bash
git clone https://github.com/dudabonini/weather-etl-pipeline.git
cd weather-etl-pipeline
```

**2. Configure as variáveis de ambiente**

Crie um arquivo `.env` na pasta `config/`:
```dotenv
API_KEY=sua_chave_da_api
user=airflow
password=airflow
database=airflow
```

**3. Crie o arquivo `.env` na raiz do projeto**
```bash
echo "AIRFLOW_UID=1000" > .env
```

**4. Suba os containers**
```bash
docker compose up -d
```

**5. Acesse o Airflow**

Abra o navegador em: `http://localhost:8080`
- Usuário: `airflow`
- Senha: `airflow`

**6. Ative e acione o DAG `youtube_weather_pipeline`**

---

## 🔄 Pipeline ETL

### Extract
Coleta dados meteorológicos de São Paulo em tempo real via API OpenWeatherMap.

### Transform
Processa e transforma os dados brutos em um formato estruturado usando Pandas.

### Load
Armazena os dados transformados na tabela `sp_weather` do PostgreSQL.

---

## 📊 Agendamento

O pipeline é executado **a cada hora** automaticamente:
```
schedule: '0 */1 * * *'
```

---

## 📬 Contato

Feito por **Eduarda Bonini** — [LinkedIn](www.linkedin.com/in/eduardabonini) | [GitHub](https://github.com/dudabonini)
