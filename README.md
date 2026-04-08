# Bot Saniteck (Telegram + Protheus)

Bot do Telegram integrado com **Protheus** para realizar **consultas de forma simples e rápida** via chat.

> Descrição do repositório: _"Bot integrado com Protheus para consultas mais facéis via telegram"_

---

## Visão geral

Este projeto é um bot em **Python** usando **pyTelegramBotAPI**, com arquitetura **modular**, separando comandos/rotas por áreas:

- **Geral**
- **Vendas**
- **Logística**
- **CRM**
- **Financeiro**

O bot carrega variáveis de ambiente via `.env`, inicializa um SQLite local e mantém o polling ativo.

---

## Tecnologias

- **Python 3.10+**
- **pyTelegramBotAPI**
- **python-dotenv**
- **pyodbc** (para conexão ODBC com SQL Server / ambiente do Protheus)
- **Docker / Docker Compose**

---

## Estrutura do projeto (alto nível)

- `main.py` — entrada principal do bot (inicializa e registra handlers)
- `handlers/` — comandos e fluxos do Telegram organizados por domínio
- `services/` — regras de negócio/integrações (ex.: consultas no Protheus)
- `middleware/` — camadas intermediárias (autenticação, logs, etc.)
- `utils/` — utilitários gerais
- `database/` — arquivos de banco local (SQLite) e gerenciamento

---

## Configuração (.env)

Crie um arquivo `.env` baseado no `.env.example`:

```env
DB_SERVER=your-db-host
DB_DATABASE=your-database-name
DB_USER=your-db-user
DB_PASS=your-db-password
TELEGRAM_TOKEN=your-telegram-bot-token
DB_DRIVER={ODBC Driver 18 for SQL Server}
```

### Variáveis importantes

- `TELEGRAM_TOKEN`: token do seu bot no Telegram (BotFather)
- `DB_*`: credenciais de acesso ao banco (normalmente SQL Server no contexto Protheus)
- `DB_DRIVER`: driver ODBC instalado no ambiente/container

---

## Rodando localmente (sem Docker)

1. Crie e ative um ambiente virtual (opcional, mas recomendado)
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Crie o `.env`
4. Execute:
   ```bash
   python main.py
   ```

---

## Rodando com Docker

### Build e execução com Docker Compose

1. Crie o `.env` na raiz do projeto
2. Suba o serviço:
   ```bash
   docker compose up --build -d
   ```

Para ver logs:
```bash
docker compose logs -f
```

Para parar:
```bash
docker compose down
```

> Observação: o `Dockerfile` instala o `msodbcsql17` e dependências de ODBC para suportar o `pyodbc`.

---

## Como adicionar novos comandos (handlers)

Os handlers são registrados no `main.py` via `register(bot)` para cada módulo.

Sugestão de padrão:
1. Crie um novo arquivo em `handlers/` (ex.: `handlers/rh.py`)
2. Implemente uma função `register(bot)` que define os comandos/mensagens
3. Importe e registre no `main.py`

---

## Segurança

- Não commite o arquivo `.env`
- Use `.env.example` apenas como modelo
- Evite logar credenciais (DB_USER/DB_PASS/TELEGRAM_TOKEN)

---

## Status

Projeto em desenvolvimento. Ajustes podem ser necessários conforme o ambiente Protheus/SQL Server e os comandos implementados nos handlers.

---

## Licença

Nenhuma licença definida no repositório até o momento.
