#!/usr/bin/env python3
import os, sys
os.chdir("/Users/matsumaepc/Desktop/Claude code/上手フラッグLP")
port = int(os.environ.get("PORT", 8080))
import http.server
handler = http.server.SimpleHTTPRequestHandler
with http.server.HTTPServer(("", port), handler) as httpd:
    httpd.serve_forever()
