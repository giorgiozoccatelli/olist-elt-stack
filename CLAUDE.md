# olist-elt-stack — contesto del progetto

Pipeline batch end-to-end per portfolio data engineering (GitHub).
Dataset: Olist Brazilian E-commerce (Kaggle), simulato come batch giornalieri.
Stack: Docker Compose, MinIO (data lake), Postgres 16 (DWH), dbt-core, Airflow + Astronomer Cosmos, Streamlit, GitHub Actions.
Altri due progetti (streaming, RAG) sono separati: non trattarli qui.

## Metodo di lavoro (IMPORTANTE)
- L'utente non ha formazione tecnica formale (WordPress avanzato, HTML/CSS discreto, DNS, Excel). Vuole piena comprensione e controllo.
- Prima di ogni passo: spiega il concetto e la motivazione, poi l'implementazione a blocchi piccoli.
- NON creare o modificare file in autonomia: mostra il contenuto, spiega riga per riga, lascia che sia l'utente a scriverlo. Procedi solo se lo chiede esplicitamente.
- Ad ogni fase elenca esplicitamente i requisiti da installare e se serve creare account.
- Dopo ogni passo chiedi l'output reale dei comandi (non fidarti di "fatto"); verifica sul disco prima di ipotizzare cause.
- Rispondi in italiano; codice, commenti e description dbt in inglese.
- Sii diretto, segnala errori e limiti onestamente, non inventare: se non sai, dillo.
- Fai commit a fine di ogni blocco compiuto, controllando prima `git status` (mai `.env` o `data/`).

## Ambiente
- macOS (Apple Silicon), VSCode, Python 3.12 (Homebrew), venv in `.venv` ricreato il 2026-10-20 (il 3.13 framework era sparito) (attivare con `source .venv/bin/activate`).
- Container: olist_postgres, olist_minio (minio-init rimosso: il bucket lo crea ensure_bucket() in ingestion/config.py). Rete: olist-elt-stack_default.
- Credenziali in `.env` (non versionato); `.env.example` versionato.
- Comandi Makefile: make up / down / restart / logs / ps / clean / psql.
- Kaggle: token nuovo formato in `~/.kaggle/access_token` (permessi 600). Il token mostrato in chat va considerato compromesso: da rigenerare.

## Stato: Fasi 0, 1, 2 COMPLETATE e verificate
- Fase 0: docker-compose (postgres, minio, minio-init), init-db.sql crea schema `raw` e `analytics`.
- Fase 1 (ingestion, script in `ingestion/`, eseguiti a mano):
  - download_dataset.py (Kaggle API -> data/raw_source)
  - prepare_batches.py (batch giornalieri 2018-08-01..07 in data/batches: 4 tabelle transazionali per giorno + master/)
  - upload_to_minio.py (boto3 -> bucket raw, partizioni Hive `batch_date=YYYY-MM-DD/`)
  - load_to_postgres.py (MinIO -> schema raw; replace al primo giorno, append dopo)
  - Verifica: raw.orders = 2190 righe.
- Fase 2 (dbt in `dbt_project/`, dbt-core 1.12.0 + dbt-postgres 1.11.0):
  - staging (view, schema analytics_staging): 9 modelli stg_*, source in `_sources.yml`, test in `_staging.yml`
  - intermediate (view, analytics_intermediate): int_order_items_summary, int_order_payments_summary, int_order_reviews_summary (una riga per ordine)
  - marts (table, analytics_marts): dim_customers (su customer_unique_id, 96096), dim_products (left join traduzione, 623 senza traduzione), dim_sellers, fct_orders (2190), fct_order_items (2477)
  - 44 test dbt tutti passati.

## Scelte e trappole già incontrate
- Usare `pip install "dbt-core<2" "dbt-postgres<2"`: dbt Fusion 2.x (preview) non supporta bene Postgres. Se `dbt --version` mostra "fusion", lanciare `hash -r` o aprire un nuovo terminale (esistono altri binari dbt nel PATH).
- Profilo dbt in `~/.dbt/profiles.yml` (host localhost, schema analytics, user/db da .env). Fuori dal repo.
- `review_id` non è univoco da solo in order_reviews (chiave: review_id + order_id). `customer_id` è per ordine, `customer_unique_id` per persona.
- Dentro Docker l'host di Postgres/MinIO è il nome servizio (`postgres`, `minio`), da fuori è `localhost`.
- `make psql` usa `sh -c` con `$$POSTGRES_USER` perché le variabili esistono solo nel container.
- Tenere requirements.txt aggiornato con `pip freeze > requirements.txt` solo dopo installazioni volute.
- Config condivisa in `ingestion/config.py`: host default localhost; in Docker impostare MINIO_ENDPOINT, POSTGRES_HOST, POSTGRES_PORT (porte interne 9000/5432).
- load_to_postgres.py è idempotente (TRUNCATE + append): `replace` falliva perché le view dbt dipendono da raw.*.
- requirements.txt ridotto alle sole dipendenze dirette (era un freeze di 1400+ righe). Il `dbt` in ~/.local/bin è Fusion 2.x: usare sempre quello del venv.

## PROSSIMO PASSO: Fase 3 — Airflow + Cosmos
Piano concordato (spiegare prima il concetto, poi scrivere a blocchi):
1. Estendere docker-compose.yml (non riscriverlo): Postgres separato per metadati Airflow, webserver, scheduler, airflow-init. Immagine Airflow custom con astronomer-cosmos, dbt-core<2, dbt-postgres<2 e le librerie degli script (boto3, pandas, sqlalchemy, psycopg2-binary, python-dotenv, kaggle).
2. Punti critici da affrontare con calma: connessioni (Airflow Connections per Postgres e MinIO), host = nomi servizio Docker, profilo dbt utilizzabile dal container (quello in ~/.dbt non è visibile), montaggio di dags/, ingestion/, dbt_project/ e data/.
3. Un DAG: TaskGroup ingestion (prepare -> upload -> load; valutare se il download Kaggle va nel DAG o resta una tantum) -> DbtTaskGroup Cosmos (un task per modello) -> dbt test come gate di qualità -> task di notifica (log).
4. Aggiornare .env.example, README, Makefile.
Poi: Fase 4 Streamlit, Fase 5 GitHub Actions (lint ruff/sqlfluff, pytest, dbt test), Fase 6 README con diagramma Mermaid e screenshot (dbt docs lineage, dashboard).