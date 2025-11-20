
# 🔥 RAPROXY — Cross-Platform Ghost Proxy Engine

> **"If you're not invisible, you're vulnerable."**  
> A modular, CLI-first proxy framework built for bug bounty hunters, penetration testers, and privacy extremists who demand full control over their traffic obfuscation stack — from Termux to Arch Linux.

---

## 🖼️ Preview — This Is What You Get

### Terminal Vibe (Arch-Level CLI)
```text
  _____                                 
 |  __ \                                
 | |__) |__ _ _ __  _ __ _____  ___   _ 
 |  _  // _` | '_ \| '__/_ _/ \/ / | | |
 | | \ \ (_| | |_) | |  | | >  <| |_| |
 |_|  \_\__,_| .__/|_| |___/_/\_\\__, |
             | |                   __/ |
             |_|                  |___/ 

Ghost Proxy Engine — Cross-Platform Edition

→ Platform: TERMUX-ROOT | Privilege: ROOT | Full Control Mode

[Ghost@u0_a123 ~/raproxy][ROOT]$ set ip-rotation per-request
✓ IP rotation: per-request
[Ghost@u0_a123 ~/raproxy][ROOT]$ enable tor
✓ Tor routing: ENABLED
[Ghost@u0_a123 ~/raproxy][ROOT]$ start
✓ Ghost Core ACTIVE on 127.0.0.1:8080
→ Set browser proxy to: 127.0.0.1:8080
```

### Auto Root Detection & Disclaimer
```text
⚠ NON-ROOT TERMUX DETECTED
Some features will be DISABLED:
  • Tor auto-start
  • MITM HTTPS decryption
  • Low-port binding (<1024)

RECOMMENDED WORKAROUNDS:
  • Use Linux/Windows for full features
  • Root Termux via Magisk + tsu
  • Android: Install VM (Termux + proot-distro)

Press ENTER to continue in LIMITED MODE...
```

### Live Proxy in Action
```bash
# On your browser or curl
curl -x http://127.0.0.1:8080 https://httpbin.org/ip
# → Returns a rotating proxy IP, not your real one
```

---

## 🏷️ Status & Compatibility

![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux%20%7C%20Windows%20%7C%20macOS-black?style=for-the-badge)
![Root](https://img.shields.io/badge/privilege-root--aware-red?style=for-the-badge)

---

## 🧠 Philosophy

Most proxy tools are either:
- **Too simple**: Just rotate IPs, no context awareness.
- **Too bloated**: GUI-heavy, slow, and not hacker-friendly.
- **Platform-locked**: Only work on one OS.

**Raproxy fixes all three.**

It’s designed as a **terminal-native engine** where:
- You **command every layer** of your traffic (headers, TLS, IP, protocol).
- You **choose your privilege level** (root = full power, non-root = safe fallback).
- You **run the same tool everywhere** — from Android (Termux) to Windows to macOS.

This isn’t a “proxy switcher.”  
This is your **personal network ghost protocol**.

---

## ⚠️ Non-Root Reality Check (Especially for Android/Termux)

Raproxy **honestly tells you what’s disabled** based on your privileges:

| Feature | Root / Full OS | Non-Root Termux |
|--------|----------------|------------------|
| **Tor auto-start** | ✅ | ❌ (manual only) |
| **HTTPS MITM decryption** | ✅ (with CA) | ❌ (no cert install) |
| **Low-port binding (<1024)** | ✅ | ❌ |
| **Full browser fingerprint spoofing** | ✅ | ⚠️ Partial |
| **Tor exit-node country lock** | ✅ | ❌ |
| **Encrypted session logging** | ✅ | ✅ |

### 💡 If you're on Android without root:
We **strongly recommend**:
1. **Use a Linux VM** (via Termux + `proot-distro`)
2. **Root your device** (Magisk + `tsu`)
3. **Switch to desktop** (Linux/Windows) for critical operations  
4. **Legacy workaround**: Xposed module *"JustTrustMe"* (Android ≤9)

> Raproxy won’t lie to you. If a feature can’t work, it’ll say so — and suggest a real fix.

---

## 🌐 Core Capabilities

### ✅ Traffic Obfuscation
- **Per-request IP rotation** using live HTTP proxy pools
- **Tor integration** with automatic daemon management
- **Custom header injection** (spoof geolocation, user-agent, etc.)
- **TLS fingerprint spoofing** (via external tools — planned)

### ✅ Protocol Support
- **HTTP/HTTPS forwarding** (`127.0.0.1:8080`)
- **CONNECT method support** for HTTPS tunneling
- **Auto-generated MITM certificates** (for traffic inspection)

### ✅ Platform Coverage
- **Linux** (Debian, Ubuntu, Arch — root or user)
- **Termux** (rooted with `tsu` or non-root with warnings)
- **Windows** (Admin or standard user)
- **macOS** (Intel & Apple Silicon)

### ✅ Security by Design
- **No telemetry**
- **Local-only operation** (no cloud dependencies)
- **Encrypted session logs** (optional, AES-GCM)
- **Auto-wipe mode** on exit

---

## 🚀 When Should You Use Raproxy?

- You’re **testing `.go.id` targets** and need rotating identities  
- You got **blocked by Cloudflare** and need fresh IPs + Tor  
- You want to **inspect HTTPS traffic** without Burp Suite  
- You’re on **Termux** but refuse to sacrifice control  
- You believe **CLI > GUI** for anything serious

---

## 📦 What’s Next?

Raproxy is built to evolve:
- **JA3 TLS spoofing** (via `curl-impersonate` integration)
- **Per-host rule engine** (e.g., `host set target.go.id tls chrome`)
- **Auto-bug-bounty reporter** (XSS/SQLi detection + email)
- **WebSocket & HTTP/2 support**

But the core remains: **one CLI, total control, zero compromise**.

---

> Made by **Redzskid** — for hunters who don’t ask for permission.  
> 🔥 Full stack. Full integrity. Zero fluff.
```