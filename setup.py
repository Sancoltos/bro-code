import getpass
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

from setuptools import Command, setup
from setuptools.command.install import install

CONSOLE_URL = "https://console.anthropic.com/settings/keys"
ENV_VAR_NAME = "ANTHROPIC_API_KEY"
REPO_ROOT = Path(__file__).resolve().parent


def ensure_npm_user_path_windows() -> None:
    """Append %APPDATA%\\npm to the user PATH on Windows if missing."""
    if sys.platform != "win32":
        return

    npm_bin = os.path.join(os.environ.get("APPDATA", ""), "npm")
    if not os.path.isdir(npm_bin):
        return

    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "[Environment]::GetEnvironmentVariable('PATH', 'User')"],
            capture_output=True,
            text=True,
        )
        current_path = result.stdout.strip()
        entries = [e for e in current_path.split(";") if e]

        if npm_bin not in entries:
            new_path = ";".join(entries + [npm_bin])
            subprocess.run(
                ["powershell", "-Command",
                 f"[Environment]::SetEnvironmentVariable('PATH', '{new_path}', 'User')"],
                check=True,
            )
            print(f"Added {npm_bin} to your user PATH. Restart the terminal for it to apply.")
    except Exception as e:
        print(f"Could not update PATH automatically: {e}")
        print(f"Add this directory to your user PATH manually: {npm_bin}")


def _notify_windows_environment_changed() -> None:
    try:
        import ctypes

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_ulong()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result),
        )
    except Exception:
        pass


def _read_windows_user_env(name: str) -> str | None:
    if sys.platform != "win32":
        return None
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as k:
            value, _ = winreg.QueryValueEx(k, name)
            return value if isinstance(value, str) else value.decode()
    except OSError:
        return None


def _read_unix_exported_key(name: str) -> str | None:
    """Best-effort: find `export NAME='value'` or `export NAME=value` in common rc files."""
    pattern = re.compile(
        rf"^export\s+{re.escape(name)}=(?:'([^']*)'|\"([^\"]*)\"|([^'\"\s#]+))\s*(?:#.*)?$",
        re.MULTILINE,
    )
    home = Path.home()
    for rel in (".profile", ".zshrc", ".bashrc"):
        p = home / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = pattern.search(text)
        if m:
            return m.group(1) or m.group(2) or m.group(3)
    return None


def _read_persisted_api_key() -> str | None:
    if sys.platform == "win32":
        return _read_windows_user_env(ENV_VAR_NAME)
    return _read_unix_exported_key(ENV_VAR_NAME)


def _save_api_key_windows(value: str) -> None:
    import winreg

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment") as k:
        winreg.SetValueEx(k, ENV_VAR_NAME, 0, winreg.REG_SZ, value)
    _notify_windows_environment_changed()


def _upsert_shell_export(profile_path: Path, name: str, value: str) -> None:
    """Add or replace `export NAME=...` in a shell startup file."""
    line = f"export {name}={shlex.quote(value)}\n"
    marker = f"\n# bro-code: {name}\n"
    text = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    pattern = re.compile(rf"^export\s+{re.escape(name)}=.*$", re.MULTILINE)
    if pattern.search(text):
        new_text = pattern.sub(line.rstrip("\n"), text)
    else:
        suffix = "" if text.endswith("\n") or not text else "\n"
        new_text = text + suffix + marker + line
    profile_path.write_text(new_text, encoding="utf-8")


def _save_api_key_unix(value: str) -> None:
    home = Path.home()
    candidates = [home / ".profile", home / ".zshrc", home / ".bashrc"]
    targets = [p for p in candidates if p.exists()]
    if not targets:
        targets = [home / ".profile"]
    for p in targets:
        _upsert_shell_export(p, ENV_VAR_NAME, value)
    print("Updated:\n  " + "\n  ".join(str(p) for p in targets))


def save_api_key_to_user_env(value: str) -> None:
    """Persist ANTHROPIC_API_KEY for the current user (OS-specific)."""
    if sys.platform == "win32":
        _save_api_key_windows(value)
    else:
        _save_api_key_unix(value)


class PostInstall(install):
    def run(self):
        install.run(self)
        ensure_npm_user_path_windows()
        print(
            "\nFirst time here? From this folder run:\n"
            "  python setup.py first_setup\n"
            "That installs dependencies, fixes PATH (Windows), and walks through your API key.\n"
            "\nAPI key only:\n"
            "  python setup.py configure_anthropic\n"
        )


class ConfigureAnthropic(Command):
    description = (
        f"Prompt for {ENV_VAR_NAME} and save it to your user environment "
        "(Windows: user registry; macOS/Linux: ~/.profile and ~/.zshrc if present)"
    )
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(
            f"\nOpen the Anthropic Console and create an API key:\n  {CONSOLE_URL}\n"
            f"\nThen paste it below (input is hidden).\n"
        )
        key = getpass.getpass(f"{ENV_VAR_NAME}: ").strip()
        if not key:
            print("No key entered; nothing was saved.", file=sys.stderr)
            sys.exit(1)

        save_api_key_to_user_env(key)

        print(
            f"\nSaved {ENV_VAR_NAME} for your user account.\n"
            "Open a new terminal (or restart your IDE) so `bro` picks it up.\n"
        )


class FirstTimeSetup(Command):
    description = (
        "Guided setup: pip install this project, npm PATH (Windows), then optional API key"
    )
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(
            "\n=== bro-code: first-time setup ===\n"
            "You will be prompted a few times. Use a new terminal afterward so PATH and "
            "environment variables apply.\n"
        )

        # Step 1: install package + dependencies (editable)
        print("[1/3] Installing bro-code and Python packages (pip install -e .) …\n")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=str(REPO_ROOT),
        )
        if r.returncode != 0:
            print(
                "\n pip install failed. Fix the error above, then run:\n"
                "  python setup.py first_setup\n",
                file=sys.stderr,
            )
            sys.exit(r.returncode)

        # Step 2: npm global bin on PATH (Windows)
        print("\n[2/3] Checking npm global bin on your PATH …")
        ensure_npm_user_path_windows()
        if sys.platform != "win32":
            print("  (Skipped on non-Windows; add npm’s global bin to PATH if `bro` is not found.)\n")

        # Step 3: API key
        print(
            f"\n[3/3] Anthropic API key for `bro`\n"
            f"  Create a key: {CONSOLE_URL}\n"
        )
        existing = _read_persisted_api_key()
        if existing:
            hint = existing[:16] + "…" if len(existing) > 16 else existing
            print(
                f"  A saved {ENV_VAR_NAME} was found (starts with: {hint})\n"
                "  Paste a new key to replace it, or press Enter to leave it unchanged.\n"
            )
        else:
            print(
                f"  Paste your key below (hidden). Press Enter to skip if you will set "
                f"{ENV_VAR_NAME} yourself (e.g. Windows Environment Variables).\n"
            )

        key = getpass.getpass(f"{ENV_VAR_NAME}: ").strip()
        if not key:
            if existing:
                print(f"\nKept your existing {ENV_VAR_NAME}.\n")
            else:
                print(
                    f"\nSkipped saving {ENV_VAR_NAME}. Set it in the OS environment or run:\n"
                    f"  python setup.py configure_anthropic\n"
                )
        else:
            save_api_key_to_user_env(key)
            print(f"\nSaved {ENV_VAR_NAME} for your user account.\n")

        print(
            "=== Setup finished ===\n"
            "Open a new terminal (or restart your IDE), then run:\n"
            "  bro\n"
        )


setup(
    name="bro-code",
    version="0.1",
    py_modules=["main", "ui", "brain"],
    install_requires=["rich", "typer", "anthropic"],
    entry_points='''
        [console_scripts]
        bro=main:main
    ''',
    cmdclass={
        "install": PostInstall,
        "configure_anthropic": ConfigureAnthropic,
        "first_setup": FirstTimeSetup,
    },
)
