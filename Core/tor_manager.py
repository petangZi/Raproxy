# core/tor_manager.py
import os
import platform
import subprocess
import socket
import time

class TorManager:
    def get_tor_cmd(self):
        system = platform.system().lower()
        if "com.termux" in os.environ.get("PREFIX", ""):
            return "tor"
        elif system == "linux":
            return "tor"
        elif system == "darwin":  # macOS
            paths = ["/opt/homebrew/bin/tor", "/usr/local/bin/tor"]
            for p in paths:
                if os.path.exists(p):
                    return p
            return "tor"
        elif system == "windows":
            try:
                result = subprocess.run(["where", "tor.exe"], shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            except:
                pass
            candidates = [
                os.path.expanduser("~/tor/tor.exe"),
                "C:/tor/tor.exe",
                "tor.exe"
            ]
            for cand in candidates:
                if os.path.exists(cand):
                    return cand
            return None
        return "tor"

    def ensure_running(self):
        try:
            sock = socket.socket()
            sock.connect(("127.0.0.1", 9150))
            sock.close()
            return True
        except:
            tor_cmd = self.get_tor_cmd()
            if not tor_cmd:
                raise Exception("Tor not found. Install manually.")
            try:
                subprocess.Popen([tor_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(3)  # Wait for Tor to initialize
                return True
            except Exception as e:
                raise Exception(f"Tor start failed: {e}")
