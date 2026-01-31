"""CLI utility for secure Perplexity authentication and session extraction."""

from __future__ import annotations

from pathlib import Path
from sys import exit
from typing import NoReturn

from curl_cffi.requests import Session
from orjson import loads
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt


BASE_URL: str = "https://www.perplexity.ai"
ENV_KEY: str = "PERPLEXITY_SESSION_TOKEN"

console = Console(stderr=True, soft_wrap=True)


def update_env(token: str) -> bool:
    """Securely updates the .env file with the session token."""

    path = Path(".env")
    line_entry = f'{ENV_KEY}="{token}"'

    try:
        lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        updated = False
        new_lines = []

        for line in lines:
            if line.strip().startswith(ENV_KEY):
                new_lines.append(line_entry)
                updated = True
            else:
                new_lines.append(line)

        if not updated:
            if new_lines and new_lines[-1] != "":
                new_lines.append("")
            new_lines.append(line_entry)

        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return True

    except Exception:
        return False


def _initialize_session() -> tuple[Session, str]:
    """Initialize session and obtain CSRF token."""

    session = Session(impersonate="chrome", headers={"Referer": BASE_URL, "Origin": BASE_URL})

    with console.status("[bold green]Initializing secure connection...", spinner="dots"):
        session.get(BASE_URL)
        csrf_data = loads(session.get(f"{BASE_URL}/api/auth/csrf").content)
        csrf = csrf_data.get("csrfToken")

        if not csrf:
            raise ValueError("Failed to obtain CSRF token.")

    return session, csrf


def _request_verification_code(session: Session, csrf: str, email: str) -> None:
    """Send verification code to user's email."""

    with console.status("[bold green]Sending verification code...", spinner="dots"):
        response = session.post(
            f"{BASE_URL}/api/auth/signin/email?version=2.18&source=default",
            json={
                "email": email,
                "csrfToken": csrf,
                "useNumericOtp": "true",
                "json": "true",
                "callbackUrl": f"{BASE_URL}/?login-source=floatingSignup",
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Authentication request failed: {response.text}")


def _validate_and_get_redirect_url(session: Session, email: str, user_input: str) -> str:
    """Validate user input (OTP or magic link) and return redirect URL."""

    with console.status("[bold green]Validating...", spinner="dots"):
        if user_input.startswith("http"):
            return user_input

        response_otp = session.post(
            f"{BASE_URL}/api/auth/otp-redirect-link",
            json={
                "email": email,
                "otp": user_input,
                "redirectUrl": f"{BASE_URL}/?login-source=floatingSignup",
                "emailLoginMethod": "web-otp",
            },
        )

        if response_otp.status_code != 200:
            raise ValueError("Invalid verification code.")

        redirect_path = loads(response_otp.content).get("redirect")

        if not redirect_path:
            raise ValueError("No redirect URL received.")

        return f"{BASE_URL}{redirect_path}" if redirect_path.startswith("/") else redirect_path


def _extract_session_token(session: Session, redirect_url: str) -> str:
    """Extract session token from cookies after authentication."""

    session.get(redirect_url)
    token = session.cookies.get("__Secure-next-auth.session-token")

    if not token:
        raise ValueError("Authentication successful, but token not found.")

    return token


def _display_and_save_token(token: str) -> None:
    """Display token and optionally save to .env file."""

    console.print("\n[bold green]✅ Token generated successfully![/bold green]")
    console.print(f"\n[bold white]Your session token:[/bold white]\n[green]{token}[/green]\n")

    prompt_text = f"Save token to [bold yellow].env[/bold yellow] file ({ENV_KEY})?"

    if Confirm.ask(prompt_text, default=True, console=console):
        if update_env(token):
            console.print("[dim]Token saved to .env successfully.[/dim]")
        else:
            console.print("[red]Failed to save to .env file.[/red]")


def _show_header() -> None:
    """Display welcome header."""

    console.print(
        Panel(
            "[bold white]Perplexity WebUI Scraper[/bold white]\n\n"
            "Automatic session token generator via email authentication.\n"
            "[dim]All session data will be cleared on exit.[/dim]",
            title="🔐 Token Generator",
            border_style="cyan",
        )
    )


def _show_exit_message() -> None:
    """Display security note and wait for user to exit."""

    console.print("\n[bold yellow]⚠️ Security Note:[/bold yellow]")
    console.print("Press [bold white]ENTER[/bold white] to clear screen and exit.")
    console.input()


def get_token() -> NoReturn:
    """Executes the authentication flow within an ephemeral terminal screen."""

    with console.screen():
        try:
            _show_header()

            session, csrf = _initialize_session()

            console.print("\n[bold cyan]Step 1: Email Verification[/bold cyan]")
            email = Prompt.ask("  Enter your Perplexity email", console=console)
            _request_verification_code(session, csrf, email)

            console.print("\n[bold cyan]Step 2: Verification[/bold cyan]")
            console.print("  Check your email for a [bold]6-digit code[/bold] or [bold]magic link[/bold].")
            user_input = Prompt.ask("  Enter code or paste link", console=console).strip()
            redirect_url = _validate_and_get_redirect_url(session, email, user_input)

            token = _extract_session_token(session, redirect_url)

            _display_and_save_token(token)

            _show_exit_message()

            exit(0)

        except KeyboardInterrupt:
            exit(0)

        except Exception as error:
            console.print(f"\n[bold red]⛔ Error:[/bold red] {error}")
            console.input("[dim]Press ENTER to exit...[/dim]")
            exit(1)


if __name__ == "__main__":
    get_token()
