#!/usr/bin/env python3
# raproxy.py - Redzskid's Cross-Platform Ghost Proxy 🔥😤
import sys
import os
import platform
import subprocess
import threading
import time
import getpass

# Add core to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(BASE_DIR, "core")
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

try:
    from proxy_engine import ProxyEngine
    from tor_manager import TorManager
    from stealth import StealthManager
    from network import NetworkUtils
except ImportError as e:
    print(f"[ERROR] Missing core module: {e}")
    print("Ensure 'core/' folder exists in the same directory.")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.text import Text
except ImportError:
    print("Installing 'rich'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL)
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.text import Text

console = Console()
OS = platform.system().lower()
IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
IS_ROOT = False

def detect_platform():
    global IS_ROOT
    if IS_TERMUX:
        # Check root in Termux
        try:
            su_check = subprocess.run(["tsu", "-c", "id -u"], capture_output=True, text=True, timeout=2)
            if su_check.returncode == 0 and su_check.stdout.strip() == "0":
                IS_ROOT = True
                return "termux-root"
            else:
                IS_ROOT = False
                return "termux-nonroot"
        except:
            IS_ROOT = False
            return "termux-nonroot"
    elif OS == "linux":
        IS_ROOT = (os.geteuid() == 0)
        return "linux-root" if IS_ROOT else "linux-user"
    elif OS == "darwin":
        IS_ROOT = (os.geteuid() == 0)
        return "macos-root" if IS_ROOT else "macos-user"
    elif OS == "windows":
        IS_ROOT = (subprocess.run(["net", "session"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0)
        return "windows-admin" if IS_ROOT else "windows-user"
    else:
        IS_ROOT = False
        return "unknown"

def install_deps():
    plat = detect_platform()
    console.print(f"[bold cyan]→ Platform: {plat.upper()}[/bold cyan]")
    
    # Auto-install Python deps
    try:
        import requests
    except ImportError:
        console.print("[yellow]→ Installing 'requests'...[/yellow]")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL)

def show_disclaimer():
    if "termux-nonroot" in detect_platform():
        console.print("\n[bold red]⚠ NON-ROOT TERMUX DETECTED[/bold red]")
        console.print("[dim]Some features will be DISABLED:[/dim]")
        console.print("  • Tor auto-start")
        console.print("  • MITM HTTPS decryption")
        console.print("  • Low-port binding (<1024)")
        console.print("  • Full fingerprint spoofing\n")
        
        console.print("[bold yellow]RECOMMENDED WORKAROUNDS:[/bold yellow]")
        console.print("  • Use Linux/Windows for full features")
        console.print("  • Root Termux via Magisk + tsu")
        console.print("  • Android: Install VM (Termux + proot-distro)")
        console.print("  • Legacy: Xposed module 'JustTrustMe'\n")
        
        Prompt.ask("[bold red]Press ENTER to continue in LIMITED MODE[/bold red]")

def banner():
    ascii_art = r"""
  _____                                 
 |  __ \                                
 | |__) |__ _ _ __  _ __ _____  ___   _ 
 |  _  // _` | '_ \| '__/_ _/ \/ / | | |
 | | \ \ (_| | |_) | |  | | >  <| |_| |
 |_|  \_\__,_| .__/|_| |___/_/\_\\__, |
             | |                   __/ |
             |_|                  |___/ 
"""
    console.print(f"[bold yellow]{ascii_art}[/bold yellow]")
    console.print("[bold cyan]Ghost Proxy Engine — Cross-Platform Edition[/bold cyan]\n")
    plat = detect_platform()
    root_status = "[green]ROOT[/green]" if IS_ROOT else "[red]NON-ROOT[/red]"
    console.print(f"[dim]Platform: {plat.upper()} | Privilege: {root_status} | Full Control Mode[/dim]")

# Global instances
engine = ProxyEngine()
tor = TorManager()
stealth = StealthManager()
net = NetworkUtils()

def cmd_start():
    console.print("[bold green]→ Initializing Ghost Core...[/bold green]")
    
    if engine.config.get("tor_enabled"):
        if not IS_ROOT and "termux" in detect_platform():
            console.print("[red]✗ Tor auto-start requires ROOT on Termux. Skipping.[/red]")
        else:
            try:
                tor.ensure_running()
            except Exception as e:
                console.print(f"[red]✗ Tor failed: {e}[/red]")
                return
    
    if engine.config.get("ip_rotation") != "disabled":
        net.fetch_proxies()
        if net.proxies:
            engine.update_proxy_pool(net.proxies)
            console.print(f"[green]✓ Loaded {len(net.proxies)} live proxies[/green]")
        else:
            console.print("[yellow]⚠ No proxies fetched. Continuing without rotation.[/yellow]")
    
    if engine.config.get("anti_fingerprint"):
        stealth.apply_fingerprint_protection()
    
    try:
        engine.start_proxy()
        console.print(f"[bold green]✓ Ghost Core ACTIVE on 127.0.0.1:{engine.port}[/bold green]")
        console.print(f"[dim]→ Set browser proxy to: 127.0.0.1:{engine.port}[/dim]")
    except PermissionError:
        console.print("[red]✗ Binding failed. Try port >1024 or run as root.[/red]")

def cmd_set_ip_rotation(mode):
    if mode in ["per-request", "disabled"]:
        engine.set_config("ip_rotation", mode)
        console.print(f"[green]✓ IP rotation: {mode}[/green]")
    else:
        console.print("[red]Mode: per-request | disabled[/red]")

def cmd_enable_tor():
    if not IS_ROOT and "termux" in detect_platform():
        console.print("[red]✗ Tor requires ROOT on Termux. Use workaround or skip.[/red]")
        return
    engine.set_config("tor_enabled", True)
    console.print("[green]✓ Tor routing: ENABLED[/green]")

def cmd_enable_anti_fp():
    engine.set_config("anti_fingerprint", True)
    console.print("[green]✓ Anti-fingerprint: ACTIVE[/green]")

def cmd_set_header(key, val):
    engine.add_header(key, val)
    console.print(f"[green]✓ Header '{key}' = '{val}'[/green]")

def cmd_status():
    console.print("[bold cyan]Engine Status:[/bold cyan]")
    for k, v in engine.config.items():
        console.print(f"  {k}: {v}")
    if engine.proxy_pool:
        console.print(f"  proxy_pool: [{len(engine.proxy_pool)} proxies]")

def main():
    install_deps()
    show_disclaimer()
    banner()
    while True:
        try:
            prompt_suffix = "[green]ROOT[/green]" if IS_ROOT else "[red]USER[/red]"
            cmd = Prompt.ask(f"\n[bold purple][Ghost@{getpass.getuser()} {os.getcwd()}][/bold purple][{prompt_suffix}]$ ").strip()
            if not cmd: continue
            parts = cmd.split()
            action = parts[0].lower()

            if action == "set":
                if len(parts) >= 3 and parts[1] == "ip-rotation":
                    cmd_set_ip_rotation(parts[2])
                elif len(parts) >= 4 and parts[1] == "header":
                    cmd_set_header(parts[2], " ".join(parts[3:]))
                else:
                    console.print("[red]Usage: set ip-rotation <mode> | set header <key> <val>[/red]")
            elif action == "enable":
                if len(parts) >= 2:
                    if parts[1] == "tor":
                        cmd_enable_tor()
                    elif parts[1] == "anti-fingerprint":
                        cmd_enable_anti_fp()
                    else:
                        console.print("[red]Feature: tor | anti-fingerprint[/red]")
                else:
                    console.print("[red]Usage: enable <feature>[/red]")
            elif action == "start":
                cmd_start()
            elif action == "status":
                cmd_status()
            elif action == "exit":
                console.print("[red]✓ Ghost Core shutdown.[/red]")
                sys.exit(0)
            else:
                console.print("[red]Commands: set, enable, start, status, exit[/red]")
        except KeyboardInterrupt:
            console.print("\n[red]Use 'exit' to quit.[/red]")
        except EOFError:
            break

if __name__ == "__main__":
    main()