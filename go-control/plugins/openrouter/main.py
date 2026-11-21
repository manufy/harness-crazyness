import base64
import json
import os
import sys
import urllib.error
import urllib.request

PROTOCOL_VERSION = "1"


def emit_error(request_id, message):
    print(json.dumps({
        "protocol_version": PROTOCOL_VERSION,
        "id": request_id,
        "error": message,
    }, ensure_ascii=False))
    raise SystemExit(0)


def main():
    try:
        request = json.loads(sys.stdin.readline())
    except (json.JSONDecodeError, OSError) as exc:
        emit_error("", f"petición JSON inválida: {exc}")

    request_id = request.get("id", "")
    if request.get("protocol_version", PROTOCOL_VERSION) != PROTOCOL_VERSION:
        emit_error(request_id, "versión de protocolo no soportada")

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        emit_error(request_id, "falta OPENROUTER_API_KEY")

    messages = []
    for message in request.get("messages", []):
        content = []
        for part in message.get("content", []):
            kind = part.get("type")
            if kind == "text":
                content.append({"type": "text", "text": part.get("text", "")})
            elif kind == "image":
                encoded = part.get("data", "")
                if not encoded:
                    emit_error(request_id, "las imágenes deben incluir data en base64")
                try:
                    base64.b64decode(encoded, validate=True)
                except (ValueError, TypeError):
                    emit_error(request_id, "el contenido de imagen no es base64 válido")
                mime_type = part.get("mime_type", "image/jpeg")
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                })
            else:
                emit_error(request_id, f"modalidad '{kind}' no soportada por este plugin")
        messages.append({"role": message.get("role", "user"), "content": content})

    body = json.dumps({
        "model": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        "messages": messages,
    }).encode("utf-8")

    endpoint = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
    req = urllib.request.Request(endpoint, data=body, method="POST", headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://github.com/manufy/harness-crazyness"),
        "X-Title": os.getenv("OPENROUTER_APP_NAME", "go-control harness"),
    })

    try:
        with urllib.request.urlopen(req, timeout=110) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        emit_error(request_id, f"OpenRouter respondió HTTP {exc.code}: {detail[:500]}")
    except urllib.error.URLError as exc:
        emit_error(request_id, f"no se pudo conectar con OpenRouter: {exc}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        emit_error(request_id, f"respuesta inválida de OpenRouter: {exc}")

    choices = result.get("choices", [])
    if not choices:
        emit_error(request_id, "OpenRouter no devolvió opciones de respuesta")

    answer = choices[0].get("message", {}).get("content", "")
    print(json.dumps({
        "protocol_version": PROTOCOL_VERSION,
        "id": request_id,
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": answer}],
        },
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
