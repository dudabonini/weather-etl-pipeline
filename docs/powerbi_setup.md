# Dashboard Power BI — Weather ETL Pipeline

Guia para conectar o Power BI Desktop ao PostgreSQL alimentado pelo pipeline e montar o dashboard.

---

## 1. Pré-requisitos

- Power BI Desktop instalado.
- Containers do projeto rodando (`docker compose up -d`), com o pipeline já tendo executado pelo menos uma vez para ter dados em `weather_data`.
- Se preferir rodar sem Docker: um PostgreSQL local com as credenciais de `config/.env`.

## 2. Conectar ao banco

1. Power BI Desktop → **Obter Dados** → **Banco de Dados** → **Banco de dados PostgreSQL**.
2. Preencha:
   - **Servidor**: `localhost:5434` (porta 5434, não 5432 — o 5432 já está ocupado pelo Postgres local instalado na sua máquina; o container `postgres_weather` do pipeline foi mapeado para 5434 no host)
   - **Banco de dados**: `weather_db`
3. Modo de conectividade de dados:
   - **Importação** (recomendado): copia os dados para o Power BI e permite agendar atualizações (Power BI Service, plano gratuito atualiza algumas vezes ao dia). Melhor para performance e para não depender do Postgres estar sempre online.
   - **DirectQuery**: consulta o Postgres em tempo real a cada interação. Só funciona enquanto o container estiver rodando e acessível.
4. Usuário/senha: os valores de `DB_USER`/`DB_PASSWORD` do seu `config/.env`.
5. Selecione a tabela `weather_data` e clique em **Carregar**.

> Se o Postgres não estiver acessível publicamente, o Power BI Service (nuvem) não vai conseguir atualizar automaticamente — nesse caso use o **Gateway de Dados Local** (On-premises Data Gateway, gratuito) para permitir atualização agendada mesmo com o banco rodando só na sua máquina.

## 3. Modelagem

A tabela `weather_data` chega "larga" (uma linha por cidade por execução do pipeline). Colunas principais:

| Coluna | Descrição |
|---|---|
| `city_name` | Nome da cidade |
| `country` | País (BR) |
| `datetime` | Data/hora da observação (America/Sao_Paulo) |
| `temperature`, `feels_like`, `temp_min`, `temp_max` | Temperaturas (°C) |
| `humidity` | Umidade (%) |
| `pressure` | Pressão atmosférica (hPa) |
| `wind_speed`, `wind_deg` | Vento |
| `clouds` | Cobertura de nuvens (%) |
| `weather_main`, `weather_description` | Condição do tempo |
| `latitude`, `longitude` | Coordenadas (para mapa) |
| `sunrise`, `sunset` | Nascer/pôr do sol |

Passos sugeridos no Power Query / modelo:

1. Crie uma **tabela calendário** (Nova Tabela → `DateTable = CALENDAR(MIN(weather_data[datetime]), MAX(weather_data[datetime]))`) e relacione com `weather_data[datetime]`.
2. Marque essa tabela como "Tabela de Datas" (Modelagem → Marcar como Tabela de Datas).
3. Confirme que `datetime`, `sunrise`, `sunset` vieram como tipo Data/Hora (não texto).

## 4. Medidas DAX sugeridas

```DAX
Temp Média = AVERAGE(weather_data[temperature])

Temp Máxima = MAX(weather_data[temp_max])

Temp Mínima = MIN(weather_data[temp_min])

Umidade Média = AVERAGE(weather_data[humidity])

Cidade Mais Quente = 
CALCULATE(
    VALUES(weather_data[city_name]),
    TOPN(1, VALUES(weather_data[city_name]), CALCULATE(AVERAGE(weather_data[temperature])), DESC)
)

Amplitude Térmica = MAX(weather_data[temp_max]) - MIN(weather_data[temp_min])

Última Atualização = MAX(weather_data[datetime])

Qtde Leituras = COUNTROWS(weather_data)
```

## 5. Visuais recomendados

- **Cartões (KPI)**: Temp Média, Umidade Média, Última Atualização.
- **Mapa** (Mapa do Azure ou Mapa padrão): usando `latitude`/`longitude`, tamanho da bolha por `temperature`, para visualizar o clima das 20 capitais de uma vez.
- **Gráfico de linhas**: `temperature` ao longo de `datetime`, com `city_name` como legenda — mostra a variação horária/diária por cidade.
- **Gráfico de barras**: ranking das cidades por Temp Média (do mais quente ao mais frio).
- **Gráfico de rosca/pizza**: distribuição de `weather_main` (Clear, Clouds, Rain...) para entender o clima predominante.
- **Slicer**: por `city_name` e por intervalo de datas (usando a tabela calendário).

## 6. Publicar e exibir no GitHub

Arquivos `.pbix` não são renderizados pelo GitHub. Duas opções, pode usar as duas:

1. **Print/export estático** (mais simples): Arquivo → Exportar → Exportar para PDF, ou um print do dashboard. Salve como `docs/dashboard_preview.png` e referencie no `README.md` (`![Dashboard](docs/dashboard_preview.png)`).
2. **Publicar no Power BI Service**: Página inicial → Publicar → escolha um workspace. Depois, em "Arquivo → Inserir relatório → Publicar na web (público)" você gera um link/iframe público para colocar no README (atenção: "Publicar na Web" torna o relatório acessível a qualquer pessoa com o link — não use se os dados fossem sensíveis; aqui é só clima público, então é seguro).

Recomendo fazer as duas coisas: link do Power BI Service publicado + uma imagem estática no README, para quem só quer bater o olho.

## 7. Nota sobre credenciais

As credenciais em `docker-compose.yml` (`postgres_weather`) e `config/.env` são valores de desenvolvimento local, não segredos de produção — ok para um projeto de portfólio. Ainda assim, `config/.env` está no `.gitignore` e não deve ser commitado.
