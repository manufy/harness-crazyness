import json
import sys

VERSION = "1"


def main():
    try:
        request = json.loads(sys.stdin.readline())
    except (json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"protocol_version": VERSION, "id": "", "error": f"JSON inválido: {exc}"}))
        return

    request_id = request.get("id", "")
    if request.get("protocol_version", VERSION) != VERSION:
        print(json.dumps({"protocol_version": VERSION, "id": request_id, "error": "versión de protocolo no soportada"}))
        return

    user_text = " ".join(
        part.get("text", "")
        for message in request.get("messages", [])
        for part in message.get("content", [])
        if part.get("type") == "text"
    ).strip()
    image_count = sum(
        1
        for message in request.get("messages", [])
        for part in message.get("content", [])
        if part.get("type") == "image"
    )
    suffix = f" (prueba simulada; {image_count} imagen(es) recibida(s))" if image_count else " (respuesta simulada)"
    answer = f"Hola. He recibido: {user_text}{suffix}" if user_text else f"Hola.{suffix}"

    print(json.dumps({
        "protocol_version": VERSION,
        "id": request_id,
        "message": {"role": "assistant", "content": [{"type": "text", "text": answer}]},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
