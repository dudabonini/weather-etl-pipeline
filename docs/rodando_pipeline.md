# Como rodar o pipeline (passo a passo)

Roteiro pra subir o projeto do zero na sua máquina e confirmar que os dados estão realmente caindo no Postgres. Todos os comandos rodam no **seu terminal** (PowerShell/CMD), na pasta do projeto.

---

## 1. Confirme que o Docker Desktop está rodando

Ícone da baleia na bandeja do Windows, sem o triângulo de "carregando". Se não estiver, abra e espere ficar verde/estável antes de continuar.

## 2. Suba os containers

Na pasta do projeto:

```bash
docker compose up -d
```

O que isso faz: lê o `docker-compose.yml` e sobe todos os serviços definidos nele — os dois bancos Postgres (`postgres` = metastore interno do Airflow, `postgres_weather` = banco do seu pipeline), o Redis (fila de tarefas do Airflow), e os processos do Airflow (`airflow-init`, `airflow-apiserver`, `airflow-scheduler`, `airflow-dag-processor`, `airflow-worker`, `airflow-triggerer`). O `-d` roda tudo em segundo plano (destacado do terminal).

Na primeira vez isso demora alguns minutos (baixa as imagens do Postgres/Airflow).

## 3. Confira se subiu tudo certo

```bash
docker compose ps
```

Isso lista os containers e o status de cada um. Você quer ver `running` ou `healthy` na maioria. O `airflow-init` aparece como "exited (0)" — isso é esperado, ele só roda uma vez pra preparar o banco e sai. Se algum serviço mostrar `restarting` em loop, tem algo errado — nesse caso rode `docker compose logs <nome-do-serviço>` (ex: `docker compose logs postgres_weather`) e me manda o que aparecer.

## 4. Acesse o Airflow

Abra `http://localhost:8080` no navegador. Login: `airflow` / senha: `airflow`.

Procure a DAG **`weather_pipeline`** na lista. Ela deve estar pausada (toggle cinza à esquerda do nome) — isso é o padrão de segurança do Airflow pra você não disparar nada sem querer.

## 5. Ative e dispare a DAG

- Clique no toggle pra ativar (fica azul/verde).
- Clique no botão de "play" (▶) à direita da linha da DAG → "Trigger DAG" pra rodar uma vez manualmente, sem esperar a próxima hora cheia.
- Clique no nome da DAG pra ver o grafo das 3 tasks (`extract` → `transform` → `load`) e acompanhar em tempo real. Verde = sucesso, vermelho = falhou (clica na task vermelha → "Logs" pra ver o erro).

Depois disso ela roda sozinha a cada hora (`schedule: '0 * * * *'`), sem você precisar disparar de novo.

## 6. Confira os dados no Postgres

Aqui entra o que você já manja bem — SQL. Conecte no banco `weather_db` (pelo DBeaver, pgAdmin, `psql`, ou o client que preferir):

- **Host**: `localhost`
- **Porta**: `5434` (não 5432 — essa porta já está ocupada pelo seu Postgres local; o container do pipeline foi mapeado pra 5434)
- **Banco**: `weather_db`
- **Usuário**: `postgres`
- **Senha**: `postgres123`

Query pra conferir que os dados estão chegando:

```sql
SELECT city_name, temperature, humidity, weather_main, datetime
FROM weather_data
ORDER BY datetime DESC
LIMIT 20;
```

Se a DAG já rodou mais de uma vez (dispare manualmente de novo pra testar), rode:

```sql
SELECT datetime::date AS dia, COUNT(*) AS registros
FROM weather_data
GROUP BY 1
ORDER BY 1 DESC;
```

Isso mostra quantos registros existem por dia — é a prova de que o `append` está funcionando (acumulando, não sobrescrevendo).

## 7. Se algo der errado

- **Container não sobe / fica reiniciando**: `docker compose logs <serviço>` mostra o motivo.
- **Task da DAG fica vermelha**: clique nela no Airflow → "Logs". Erros comuns: `API_KEY` inválida/vazia em `config/.env`, ou o `config/.env` não foi criado.
- **Porta ocupada** (`port is already allocated`): algum outro processo já usa a porta. Pra saber o que está na 5434 (não deveria ter nada): `netstat -ano | findstr 5434` no PowerShell.

---

Não precisa rodar tudo de uma vez — vai passo a passo e me chama se travar em algum. É mais valioso você entender cada etapa do que só copiar e colar.
