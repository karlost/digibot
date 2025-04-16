# Email Agent

Email Agent je asistent založený na Google ADK (Agent Development Kit), který využívá MCP (Model Context Protocol) email server pro odesílání emailů a vyhledávání příloh.

## Instalace

1. Naklonujte tento repozitář:
   ```
   git clone <url-repozitáře>
   cd email_agent
   ```

2. Vytvořte a aktivujte virtuální prostředí:
   ```
   python -m venv .venv
   source .venv/bin/activate  # Na Windows: .venv\Scripts\activate
   ```

3. Nainstalujte balíček:
   ```
   pip install -e .
   ```

## Konfigurace

1. Upravte soubor `.env` a nastavte své API klíče a SMTP údaje:
   ```
   # Pro Google AI Studio API
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=YOUR_API_KEY_HERE

   # Pro emailový server
   EMAIL_SENDER=your-email@example.com
   EMAIL_PASSWORD=your-app-password

   # SMTP nastavení
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=TRUE
   # SMTP_USE_SSL=FALSE
   ```

   **Poznámka:** Pro Gmail a jiné služby budete pravděpodobně potřebovat heslo specifické pro aplikaci.

2. Konfigurační soubor pro MCP email server je uložen v `~/.config/zerolib/mcp_email_server/config.toml`. Tento soubor je vytvořen při prvním spuštění příkazu `mcp-email-server ui`.

## Použití

K dispozici jsou dva agenti:

### Standardní agent (používá @modelcontextprotocol/server-email)

1. Spusťte agenta:
   ```bash
   email-agent
   ```

### Agent pro ai-zerolab MCP email server

1. Nejprve nainstalujte MCP email server od ai-zerolab:
   ```bash
   pip install mcp-email-server
   ```

2. Nakonfigurujte server (povinné při prvním použití):
   ```bash
   mcp-email-server ui
   ```

   Tento příkaz otevře uživatelské rozhraní pro konfiguraci emailového serveru. Zde je potřeba nastavit:
   - Jméno účtu (např. "Gmail")
   - Popis účtu
   - Vaše jméno
   - Vaši emailovou adresu
   - SMTP server pro odchozí poštu (např. smtp.gmail.com)
   - SMTP port (např. 587)
   - Uživatelské jméno pro SMTP
   - Heslo pro SMTP (pro Gmail použijte heslo pro aplikace)
   - IMAP server pro příchozí poštu (např. imap.gmail.com)
   - IMAP port (např. 993)
   - Uživatelské jméno pro IMAP
   - Heslo pro IMAP

3. Spusťte agenta:

   ```bash
   email-agent-zerolab
   ```

### Komunikace s agentem

Komunikujte s agentem pomocí příkazů:

- Pro odeslání emailu: "Pošli email na adresu 'uzivatel[at]example.com' s předmětem 'Test' a obsahem 'Toto je testovací email'."
- Pro vyhledání příloh: "Najdi soubory obsahující 'report' v názvu."
- Pro ukončení: "konec", "exit" nebo "quit"

## Funkce

- **Odesílání emailů**: Agent může odesílat emaily s předmětem, obsahem a volitelně s přílohami.
- **Vyhledávání příloh**: Agent může vyhledávat soubory podle vzoru v názvu, které lze použít jako přílohy.
- **Čtení emailů**: Agent může číst emaily z vaší schránky (pouze s ai-zerolab MCP email serverem).
- **Stránkování emailů**: Agent může procházet emaily po stránkách (pouze s ai-zerolab MCP email serverem).

## Požadavky

- Python 3.9+
- Google ADK
- MCP Email Server (buď @modelcontextprotocol/server-email nebo mcp-email-server)
- Pro Gmail: Heslo pro aplikace (viz [Vytvoření a použití hesel pro aplikace](https://support.google.com/accounts/answer/185833))

## Poznámky k bezpečnosti

- Hesla a citlivé údaje ukládejte pouze v souboru `.env`, který by neměl být sdílen nebo nahrán do verzovacího systému.
- Pro Gmail a jiné služby používejte hesla specifická pro aplikaci místo vašeho hlavního hesla.
