# Guia de instalação no Windows e Visual Studio Code

## 1. Criar o ambiente virtual

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## 2. Configurar usuário

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Credencial demonstrativa do arquivo de exemplo:

- Usuário: `admin`
- Senha: `Demo@123`

Para criar outro hash:

```powershell
python scripts\hash_password.py
```

Substitua o `password_hash` no `secrets.toml`.

## 3. Executar

```powershell
python -m streamlit run app.py
```

Acesse `http://localhost:8501`.

## 4. Testar

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
```

## 5. PostgreSQL opcional

```powershell
docker compose up -d postgres
$env:DATABASE_URL="postgresql+psycopg://dashboard:dashboard@localhost:5432/dashboard"
python scripts\seed_database.py
```

Depois selecione `PostgreSQL` na barra lateral.
