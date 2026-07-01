# Dashboard de Vendas Pro

Dashboard comercial desenvolvido com **Python, Streamlit, Pandas, Plotly, scikit-learn e SQLAlchemy**. O projeto demonstra tratamento e validação de dados, indicadores de negócio, autenticação, metas, previsão de faturamento, integração com PostgreSQL, testes automatizados e CI.

## Funcionalidades

- Login com senhas protegidas por PBKDF2-HMAC-SHA256.
- Base demonstrativa, upload de CSV ou consulta PostgreSQL.
- Validação de schema e relatório de qualidade dos dados.
- Filtros por período, região, estado, categoria, produto, vendedor, canal e pagamento.
- KPIs de faturamento, lucro, pedidos, itens, ticket médio e margem.
- Comparação mensal dos principais indicadores.
- Rankings, participação por canal e análise de margem.
- Insights automáticos.
- Metas mensais de faturamento e lucro.
- Previsão demonstrativa com regressão linear.
- Exportação da base filtrada.
- Docker, GitHub Actions, Ruff, Pytest e cobertura mínima de 90%.

## Estrutura

```text
Dashboard-Vendas-Pro/
├── app.py
├── data/
├── docs/
├── scripts/
├── sql/
├── src/dashboard/
│   ├── auth.py
│   ├── charts.py
│   ├── config.py
│   ├── data_processing.py
│   ├── data_sources.py
│   ├── filters.py
│   ├── forecasting.py
│   ├── goals.py
│   ├── insights.py
│   ├── metrics.py
│   └── ui.py
├── tests/
├── .streamlit/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Instalação rápida no Windows

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
python -m streamlit run app.py
```

Credenciais demonstrativas:

```text
Usuário: admin
Senha: Demo@123
```

> Troque a senha antes de publicar. Gere um novo hash com `python scripts/hash_password.py`.

## Qualidade

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

## Docker

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
docker compose up --build
```

Abra `http://localhost:8501`.

## Dados

Consulte [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md). Arquivos em português também são aceitos quando usam os aliases documentados no código.

## Segurança

- `.streamlit/secrets.toml` e `.env` estão no `.gitignore`.
- O projeto não armazena senhas em texto puro.
- A consulta configurável ao banco aceita apenas `SELECT`.
- A autenticação é apropriada para demonstração e aplicações internas; sistemas críticos devem usar um provedor de identidade dedicado.

## Licença

MIT.
