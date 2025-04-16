# Digibot - Email Agent

Digibot je emailový asistent založený na Google ADK (Agent Development Kit), který využívá MCP (Model Context Protocol) email server od ai-zerolab pro práci s emaily. Agent umožňuje odesílání emailů, čtení emailů a správu emailových účtů.

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

Pro konfiguraci emailového serveru použijte grafické rozhraní MCP email serveru:

```bash
mcp-email-server ui
```

Tento příkaz otevře uživatelské rozhraní, kde můžete nastavit svůj emailový účet. Konfigurační soubor je uložen v `~/.config/zerolib/mcp_email_server/config.toml`.

## Použití

1. Nejprve nainstalujte MCP email server od ai-zerolab (pokud ještě není nainstalovaný):

   ```bash
   pip install mcp-email-server
   ```

2. Nakonfigurujte emailový server (pokud jste to ještě neudělali):

   ```bash
   mcp-email-server ui
   ```

3. Spusťte emailového agenta:

   ```bash
   python email_agent/email_agent/agent_zerolab.py
   ```

   Nebo pokud jste nainstalovali balíček v režimu vývoje:

   ```bash
   python -m email_agent.agent_zerolab
   ```

### Komunikace s agentem

Komunikujte s agentem pomocí příkazů:

- Pro odeslání emailu: "Pošli email na adresu 'uzivatel[at]example.com' s předmětem 'Test' a obsahem 'Toto je testovací email'."
- Pro čtení emailů: "Zobraz poslední emaily" nebo "Najdi emaily s předmětem 'Důležité'."
- Pro přeposlání emailu: "Přepošli email s předmětem 'Test' na adresu 'jiny[at]example.com'."
- Pro ukončení: "konec", "exit" nebo "quit"

## Funkce

- **Odesílání emailů**: Agent může odesílat emaily s předmětem a obsahem.
- **Čtení emailů**: Agent může číst emaily z vaší schránky.
- **Vyhledávání emailů**: Agent může vyhledávat emaily podle předmětu, obsahu nebo odesílatele.
- **Přeposílání emailů**: Agent může přeposílat emaily na jiné adresy.
- **Správa účtů**: Agent může zobrazit seznam dostupných emailových účtů.

## Požadavky

- Python 3.9+
- Google ADK
- MCP Email Server od ai-zerolab
- Přístup k emailovému serveru (IMAP a SMTP)

## Model

Agent používá model `gemini-2.5-pro-preview-03-25` od Google, který poskytuje lepší podporu pro práci s nástroji MCP email serveru.

## Poznámky k bezpečnosti

- Hesla a citlivé údaje jsou uloženy v konfiguračním souboru MCP email serveru.
- Pro veřejné emailové služby jako Gmail používejte hesla specifická pro aplikaci místo vašeho hlavního hesla.
