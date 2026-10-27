import os
import re

src = open("frontend/nginx.conf.template").read()
assert "${BACKEND_URL}" in src, "template must use braced BACKEND_URL"
assert not re.search(r"\$\{(?!BACKEND_URL\b)\w+\}", src), "no other braced vars allowed"
out = src.replace("${BACKEND_URL}", "https://setucredit-backend.onrender.com")
proxy_passes = [l.strip() for l in out.splitlines() if "proxy_pass" in l]
assert proxy_passes == [
    "proxy_pass https://setucredit-backend.onrender.com;",
    "proxy_pass https://setucredit-backend.onrender.com;",
], proxy_passes
nginx_vars = [l.strip() for l in out.splitlines() if "$" in l]
assert all(
    "$host" in l or "$proxy_add_x_forwarded_for" in l or "$uri" in l for l in nginx_vars
), nginx_vars
print("OK: braced BACKEND_URL substituted; nginx-native vars stay literal")

# config.js.template: only PWA_API_BASE is braced, and it substitutes cleanly
cfg = open("frontend/config.js.template").read()
assert "${PWA_API_BASE}" in cfg
assert not re.search(r"\$\{(?!PWA_API_BASE\b)\w+\}", cfg), "stray braced vars in config.js.template"
sub = cfg.replace("${PWA_API_BASE}", "https://setucredit-backend.onrender.com")
assert 'window.SETUCREDIT_API_BASE = "https://setucredit-backend.onrender.com";' in sub
print("OK: config.js.template substitutes PWA_API_BASE and nothing else")
