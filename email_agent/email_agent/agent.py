import asyncio
import os
import json
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
    """Získá nástroje z MCP Email Serveru."""
    print("Připojování k MCP Email serveru...")

    # Nastavení cesty k adresáři s přílohami
    attachment_dir = os.path.expanduser("~/Documents")

    # Nastavení cesty ke konfiguračnímu souboru
    config_path = Path(__file__).parent.parent / "email_config.json"

    # Kontrola, zda konfigurační soubor existuje
    if not config_path.exists():
        print(f"Varování: Konfigurační soubor {config_path} nebyl nalezen.")
        email_config = None
    else:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                email_config = json.dumps(json.load(f))
                print(f"Konfigurační soubor {config_path} byl úspěšně načten.")
        except Exception as e:
            print(f"Chyba při čtení konfiguračního souboru: {e}")
            email_config = None

    tools, exit_stack = await MCPToolset.from_server(
        # Použití StdioServerParameters pro komunikaci s lokálním procesem
        connection_params=StdioServerParameters(
            command='npx',  # Příkaz pro spuštění serveru
            args=["-y",     # Argumenty pro příkaz
                  "@modelcontextprotocol/server-email",
                  "--dir", attachment_dir],
            # Proměnné prostředí pro SMTP server
            env={
                "SENDER": os.getenv("EMAIL_SENDER", ""),
                "PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
                "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
                "SMTP_USE_TLS": os.getenv("SMTP_USE_TLS", "TRUE"),
                "SMTP_USE_SSL": os.getenv("SMTP_USE_SSL", "FALSE"),
                "EMAIL_CONFIG": email_config if email_config else "",
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
        model='gemini-2.0-flash',  # Upravte název modelu podle dostupnosti
        name='email_assistant',
        instruction="""
        Jsi asistent pro práci s emaily. Pomáháš uživatelům s odesíláním emailů a vyhledáváním příloh.

        Máš k dispozici tyto nástroje:
        1. send_email - pro odesílání emailů s možností příloh
           - receiver: seznam emailových adres příjemců
           - body: obsah emailu
           - subject: předmět emailu
           - attachments: volitelné přílohy (názvy souborů)

        2. search_attachments - pro vyhledávání souborů podle vzoru
           - pattern: textový vzor pro vyhledávání v názvech souborů

        Vždy se ujisti, že máš všechny potřebné informace, než odešleš email.
        Pokud uživatel neposkytne všechny potřebné informace, zeptej se na ně.
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

    1. Odesíláním emailů (včetně příloh)
    2. Vyhledáváním souborů pro přílohy

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
