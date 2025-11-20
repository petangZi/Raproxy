# core/proxy_engine.py
import threading
import http.server
import socketserver
import requests
import time
import ssl
import os
from urllib.parse import urlparse

class ProxyEngine:
    def __init__(self):
        self.config = {
            "ip_rotation": "disabled",
            "tor_enabled": False,
            "anti_fingerprint": False,
            "headers": {},
            "proxy_pool": [],
            "mitm_enabled": False
        }
        self.port = 8080
        self.proxy_pool = []
        self._running = False
        self._server = None
        self.cert_dir = os.path.expanduser("~/.raproxy/certs")
        os.makedirs(self.cert_dir, exist_ok=True)

    def set_config(self, key, value):
        self.config[key] = value

    def add_header(self, key, val):
        self.config["headers"][key] = val

    def update_proxy_pool(self, proxies):
        self.proxy_pool = proxies

    def generate_cert(self, hostname):
        cert_path = os.path.join(self.cert_dir, f"{hostname}.pem")
        key_path = os.path.join(self.cert_dir, f"{hostname}.key")
        
        if os.path.exists(cert_path) and os.path.exists(key_path):
            return cert_path, key_path
        
        # Generate self-signed cert (simplified)
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=30)
            ).add_extension(
                x509.SubjectAlternativeName([x509.DNSName(hostname)]),
                critical=False
            ).sign(key, hashes.SHA256())
            
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            with open(key_path, "wb") as f:
                f.write(key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.TraditionalOpenSSL,
                    serialization.NoEncryption()
                ))
            return cert_path, key_path
        except ImportError:
            console.print("[yellow]→ Install 'cryptography' for auto-cert: pip install cryptography[/yellow]")
            return None, None

    def start_proxy(self):
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()

    def _run_server(self):
        socketserver.TCPServer.allow_reuse_address = True
        self._server = socketserver.TCPServer(("", self.port), self._make_handler())
        self._server.serve_forever()

    def _make_handler(self):
        outer_self = self
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_CONNECT(self2):
                if not outer_self.config["mitm_enabled"]:
                    self2.send_response(403)
                    self2.end_headers()
                    return
                
                hostname = self2.path.split(":")[0]
                cert, key = outer_self.generate_cert(hostname)
                if not cert or not key:
                    self2.send_response(500)
                    self2.end_headers()
                    return
                
                self2.send_response(200, "Connection Established")
                self2.end_headers()
                
                try:
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    context.load_cert_chain(certfile=cert, keyfile=key)
                    ssl_sock = context.wrap_socket(self2.connection, server_side=True, suppress_ragged_eofs=True)
                    self2.connection = ssl_sock
                    self2.rfile = ssl_sock.makefile('rb', self2.rbufsize)
                    self2.wfile = ssl_sock.makefile('wb', self2.wbufsize)
                    self2.handle_one_request()
                except Exception as e:
                    pass

            def do_GET(self2):
                try:
                    url = self2.path
                    if not url.startswith(("http://", "https://")):
                        url = "http://" + url.lstrip("/")
                    
                    headers = outer_self.config["headers"].copy()
                    headers["Host"] = urlparse(url).netloc
                    proxies = {}

                    if outer_self.config["tor_enabled"]:
                        proxies = {"http": "socks5://127.0.0.1:9150", "https": "socks5://127.0.0.1:9150"}
                    elif outer_self.config["ip_rotation"] == "per-request" and outer_self.proxy_pool:
                        idx = hash(url) % len(outer_self.proxy_pool)
                        p = outer_self.proxy_pool[idx]
                        proxies = {"http": f"http://{p}", "https": f"http://{p}"}

                    resp = requests.get(url, headers=headers, proxies=proxies, timeout=20, stream=True)
                    self2.send_response(resp.status_code)
                    for k, v in resp.headers.items():
                        if k.lower() not in ["content-encoding", "transfer-encoding", "connection"]:
                            self2.send_header(k, v)
                    self2.end_headers()
                    for chunk in resp.iter_content(chunk_size=8192):
                        self2.wfile.write(chunk)
                except Exception as e:
                    self2.send_response(502)
                    self2.end_headers()
                    self2.wfile.write(b"Proxy Error")
            def log_message(self2, format, *args): pass
        return Handler