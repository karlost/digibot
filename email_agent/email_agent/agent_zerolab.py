import asyncio
import os
import sys
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Načtení proměnných prostředí z .env souboru
load_dotenv()

async def get_tools_async():
    """Získá nástroje z MCP Email Serveru od ai-zerolab."""
    print("Připojování k MCP Email serveru od ai-zerolab...")

    # Nastavení cesty k adresáři s přílohami
    attachment_dir = os.path.expanduser("~/Documents")

    # Nastavení cesty ke konfiguračnímu souboru
    config_path = Path(os.path.expanduser("~/.config/zerolib/mcp_email_server/config.toml"))

    # Kontrola, zda konfigurační soubor existuje
    if not config_path.exists():
        print(f"Varování: Konfigurační soubor {config_path} nebyl nalezen.")
        print("Je potřeba nejprve nakonfigurovat MCP email server pomocí 'mcp-email-server ui'.")
    else:
        print(f"Konfigurační soubor {config_path} byl nalezen.")

    # Zjištění, jaký příkaz použít pro spuštění MCP email serveru
    command = None
    args = []

    # Zkusíme různé možnosti, jak spustit MCP email server
    options = [
        # Možnost 1: Použití uvx (doporučeno v dokumentaci)
        {"cmd": "uvx", "args": ["mcp-email-server@latest", "stdio"]},
        # Možnost 2: Přímé použití mcp-email-server
        {"cmd": "mcp-email-server", "args": ["stdio"]},
        # Možnost 3: Použití Python modulu
        {"cmd": sys.executable, "args": ["-m", "mcp_email_server", "stdio"]}
    ]

    for option in options:
        cmd = option["cmd"]
        if shutil.which(cmd):
            command = cmd
            args = option["args"]
            print(f"Použiji příkaz: {command} {' '.join(args)}")
            break

    if not command:
        raise RuntimeError("Nelze najít příkaz pro spuštění MCP email serveru. Nainstalujte 'mcp-email-server' pomocí 'pip install mcp-email-server'.")

    print(f"Používám příkaz: {command} {' '.join(args)}")

    tools, exit_stack = await MCPToolset.from_server(
        # Použití StdioServerParameters pro komunikaci s lokálním procesem
        connection_params=StdioServerParameters(
            command=command,  # Příkaz pro spuštění serveru
            args=args,
            # Proměnné prostředí pro SMTP server
            env={
                "MCP_EMAIL_SERVER_CONFIG_PATH": str(config_path),
                # Přidáme také přímé nastavení pro případ, že by bylo potřeba
                "SENDER": os.getenv("EMAIL_SENDER", ""),
                "PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
                "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
                "SMTP_USE_TLS": os.getenv("SMTP_USE_TLS", "TRUE"),
                "SMTP_USE_SSL": os.getenv("SMTP_USE_SSL", "FALSE"),
            }
        )
    )

    print("MCP Toolset úspěšně vytvořen.")
    # MCP vyžaduje udržování spojení s lokálním MCP serverem.
    # exit_stack spravuje ukončení tohoto spojení.
    return tools, exit_stack

async def get_agent_async():
    """Vytvoří ADK agenta vybaveného nástroji z MCP serveru."""
    tools, exit_stack = await get_tools_async()
    print(f"Získáno {len(tools)} nástrojů z MCP serveru.")

    root_agent = LlmAgent(
        model='gemini-2.5-pro-preview-03-25',  # Používáme novější model s lepší podporou nástrojů
        name='email_assistant',
        instruction="""
        Jsi asistent pro práci s emaily. Pomáháš uživatelům s odesíláním emailů, čtením emailů a správou příloh.

        Máš k dispozici následující nástroje pro práci s emaily:

        1. send_email - pro odesílání emailů
           - recipients: seznam emailových adres příjemce (např. ["testbot@digihood.cz"])
           - subject: předmět emailu
           - body: obsah emailu
           - cc: volitelný seznam emailových adres v kopii
           - bcc: volitelný seznam emailových adres ve skryté kopii

        2. page_email - pro čtení a stránkování emailů
           - page: číslo stránky (začíná od 1)
           - page_size: počet emailů na stránku
           - subject: volitelný filtr podle předmětu
           - body: volitelný filtr podle obsahu
           - text: volitelný filtr podle textu kdekoli v emailu
           - from_address: volitelný filtr podle odesílatele
           - to_address: volitelný filtr podle příjemce

        3. list_available_accounts - získá seznam dostupných emailových účtů

        4. add_email_account - přidá nový emailový účet

        Vždy se ujisti, že máš všechny potřebné informace, než odešleš email.
        Pokud uživatel neposkytne všechny potřebné informace, zeptej se na ně.

        Při použití nástroje page_email používej vždy výchozí hodnoty pro page=1 a page_size=10, pokud uživatel nespecifikuje jinak.

        Pro odesílání emailů potřebuješ:
        - Emailové adresy příjemců (jako pole/seznam, i když je jen jeden příjemce)
        - Předmět emailu
        - Obsah emailu
        """,
        tools=tools,  # Poskytnutí MCP nástrojů ADK agentovi
    )

    return root_agent, exit_stack

async def async_main():
    """Hlavní funkce pro spuštění agenta."""
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()

    session = session_service.create_session(
        state={}, app_name='email_assistant_app', user_id='user_email'
    )

    # Počáteční zpráva pro uživatele
    initial_message = """
    Vítejte! Jsem váš emailový asistent. Mohu vám pomoci s:

    1. Odesíláním emailů
    2. Čtením a vyhledáváním emailů
    3. Správou emailových účtů

    Používám emailový účet testbot@digihood.cz nakonfigurovaný v MCP email serveru.

    Jak vám mohu pomoci dnes?
    """

    print(initial_message)

    root_agent, exit_stack = await get_agent_async()

    runner = Runner(
        app_name='email_assistant_app',
        agent=root_agent,
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    try:
        while True:
            # Získání vstupu od uživatele
            user_input = input("\nVy: ")

            if user_input.lower() in ['konec', 'exit', 'quit']:
                print("Ukončuji asistenta...")
                break

            # Vytvoření obsahu zprávy
            content = types.Content(role='user', parts=[types.Part(text=user_input)])

            print("\nZpracovávám váš požadavek...")

            # Spuštění agenta s uživatelským vstupem
            events_async = runner.run_async(
                session_id=session.id, user_id=session.user_id, new_message=content
            )

            # Zpracování událostí a zobrazení odpovědi agenta
            async for event in events_async:
                if hasattr(event, 'content') and event.content.role == 'model':
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(f"\nAsistent: {part.text}")

    finally:
        # Důležité ukončení: Zajištění uzavření spojení s MCP serverem.
        print("Uzavírání spojení s MCP serverem...")
        await exit_stack.aclose()
        print("Ukončení dokončeno.")

def main():
    """Vstupní bod pro spuštění agenta."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nAsistent byl ukončen uživatelem.")
    except Exception as e:
        print(f"Došlo k chybě: {e}")

if __name__ == '__main__':
    main()
