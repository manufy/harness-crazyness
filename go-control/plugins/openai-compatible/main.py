import base64
import json
import os
import sys
import urllib.error
import urllib.request

VERSION = "1"


def fail(request_id, message):
    print(json.dumps({"protocol_version": VERSION, "id": request_id, "error": message}, ensure_ascii=False))
    raise SystemExit(0)


def main():
    try:
        request = json.loads(sys.stdin.readline())
    except (json.JSONDecodeError, OSError) as exc:
        fail("", f"petición JSON inválida: {exc}")

    request_id = request.get("id", "")
    if request.get("protocol_version", VERSION) != VERSION:
        fail(request_id, "versión de protocolo no soportada")

    messages = []
    for message in request.get("messages", []):
        parts = []
        for part in message.get("content", []):
            if part.get("type") == "text":
                parts.append({"type": "text", "text": part.get("text", "")})
            elif part.get("type") == "image":
                encoded = part.get("data", "")
                if not encoded:
                    fail(request_id, "las imágenes deben incluir data en base64")
                try:
                    base64.b64decode(encoded, validate=True)
                except (ValueError, TypeError):
                    fail(request_id, "el contenido de imagen no es base64 válido")
                mime = part.get("mime_type", "image/jpeg")
                parts.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}})
            else:
                fail(request_id, f"modalidad '{part.get('type')}' no soportada por la API compatible")
        messages.append({"role": message.get("role", "user"), "content": parts})

    base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
    model = os.getenv("LLM_MODEL", "")
    if not base_url or not model:
        fail(request_id, "configura LLM_BASE_URL y LLM_MODEL para el proveedor")

    body = json.dumps({"model": model, "messages": messages}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("LLM_API_KEY", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(base_url + "/chat/completions", data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=110) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        fail(request_id, f"proveedor respondió HTTP {exc.code}: {detail[:500]}")
    except urllib.error.URLError as exc:
        fail(request_id, f"no se pudo conectar con el proveedor: {exc}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(request_id, f"respuesta inválida del proveedor: {exc}")

    choices = result.get("choices", [])
    if not choices:
        fail(request_id, "el proveedor no devolvió opciones de respuesta")
    answer = choices[0].get("message", {}).get("content", "")
    print(json.dumps({"protocol_version": VERSION, "id": request_id,
                      "message": {"role": "assistant", "content": [{"type": "text", "text": answer}]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
