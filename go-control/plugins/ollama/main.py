#!/usr/bin/env python3
"""Ollama model plugin: reads one JSON request from stdin, writes JSON to stdout."""

import base64
import json
import os
import sys
import urllib.error
import urllib.request

PROTOCOL_VERSION = "1"


def fail(message):
    print(json.dumps({"protocol_version": PROTOCOL_VERSION, "id": request_id,
                      "error": message}, ensure_ascii=False))
    raise SystemExit(0)


def main():
    global request_id
    try:
        request = json.loads(sys.stdin.readline())
    except (json.JSONDecodeError, OSError) as exc:
        request_id = ""
        fail(f"petición JSON inválida: {exc}")

    request_id = request.get("id", "")
    if request.get("protocol_version", PROTOCOL_VERSION) != PROTOCOL_VERSION:
        fail("versión de protocolo no soportada")

    messages = []
    for message in request.get("messages", []):
        converted = {"role": message.get("role", "user"), "content": "", "images": []}
        text_parts = []
        for part in message.get("content", []):
            kind = part.get("type")
            if kind == "text":
                text_parts.append(part.get("text", ""))
            elif kind == "image":
                encoded = part.get("data")
                if not encoded:
                    fail("las imágenes deben incluir data en base64; las URL no están habilitadas en este plugin")
                try:
                    raw = base64.b64decode(encoded, validate=True)
                except (ValueError, TypeError):
                    fail("el contenido de imagen no es base64 válido")
                converted["images"].append(base64.b64encode(raw).decode("ascii"))
            else:
                fail(f"modalidad '{kind}' no soportada por este plugin; el contrato admite plugins multimodales")
        converted["content"] = "\n".join(text_parts)
        messages.append(converted)

    body = json.dumps({
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5vl:3b"),
        "messages": messages,
        "stream": False,
    }).encode("utf-8")
    endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/chat"
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=110) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        fail(f"no se pudo conectar con Ollama ({endpoint}): {exc}. ¿Está iniciado Ollama y descargado el modelo?")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(f"respuesta inválida de Ollama: {exc}")

    answer = result.get("message", {}).get("content", "")
    print(json.dumps({
        "protocol_version": PROTOCOL_VERSION,
        "id": request_id,
        "message": {"role": "assistant", "content": [{"type": "text", "text": answer}]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    request_id = ""
    main()
