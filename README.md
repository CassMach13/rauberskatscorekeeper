# RauberSkat Scorekeeper

Aplicativo web para calcular e registrar a pontuação de partidas de **RauberSkat** (variante do Skat), com regras, multiplicadores e persistência em nuvem.

**Autor:** [Cássio Marques Machado](https://www.linkedin.com/in/cassio-machado-pmo/)  
**Repo:** [CassMach13/rauberskatscorekeeper](https://github.com/CassMach13/rauberskatscorekeeper)

---

## O problema

Em mesas de RauberSkat, a contagem manual (Bock, Ramsch, Kontra, fatores Hand/Schneider etc.) gera erro e atrasa o jogo. O Scorekeeper automatiza o cálculo e guarda o histórico da mesa.

## O que o produto faz

- Fluxo de partida para 3 ou 4 jogadores
- Tipos de jogo (Bock, Ramsch, Grand, Null, Durchmarsch etc.) e multiplicadores
- Interface web responsiva
- API Flask para cálculo e gravação
- Persistência com Firebase (Firestore), quando configurado
- Deploy pensado para Vercel (`/api` + estáticos em `public/`)

Há também uma geração desktop (PyQt) guardada apenas localmente em `archive/` — **não** faz parte do repositório público.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Front-end | HTML, CSS, JavaScript (`public/`) |
| API | Python, Flask (`app.py`, `api/`) |
| Regras / cálculo | `rauberskat_backend_oficial.py` |
| Dados | Firebase Admin + Firestore |
| Deploy | Vercel |

## Estrutura

```text
public/                 # UI (index, CSS v6, JS)
api/index.py            # Entrypoint Vercel → importa app Flask
app.py                  # Rotas Flask + bootstrap Firebase
rauberskat_backend_oficial.py
docs/                   # Contexto de regras / backlog
vercel.json
Dockerfile
requirements.txt
firebase-credentials.example.json
.env.example
```

## Como rodar localmente

**Requisitos:** Python 3.10+ e um projeto Firebase (service account).

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Credenciais (escolha uma):
# A) arquivo local (recomendado no PC)
copy firebase-credentials.example.json firebase-credentials.json
# preencha firebase-credentials.json com a service account

# B) variável de ambiente FIREBASE_CREDENTIALS (JSON), ver .env.example

# Front + API: sirva public/ e rode o Flask, ou use o fluxo Vercel local
python app.py
```

Em produção na Vercel, configure a env `FIREBASE_CREDENTIALS` com o JSON da service account (não faça upload do arquivo no Git).

## Segurança

- `firebase-credentials.json` e `.env` estão no `.gitignore`
- Nunca versionar service account / private key
- Resultados de mesas reais e pastas legadas ficam fora do Git (`archive/`, `resultados_jogos/`)

## Documentação extra

- [Contexto e regras](docs/contexto-e-regras.md)

## Status

Versão online em uso (Vercel + Firebase). Este README descreve o recorte público do projeto — sem credenciais e sem dados de mesas.
