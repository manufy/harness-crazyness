# go-control — harness experimental Go + Python

Andamiaje mínimo para un host en Go que ejecuta plugins como procesos independientes. El contrato JSONL versionado desacopla el host de los plugins; el primer plugin Python conecta con Ollama. No requiere una API key: Ollama y el modelo se ejecutan localmente.

## Ejecutar el ejemplo «Hola»

Requisitos: Go 1.22+, Python 3 y [Ollama](https://ollama.com/).

```sh
ollama pull qwen2.5vl:3b
ollama serve # si Ollama aún no está ejecutándose
cd go-control
go run ./cmd/harness
```

El host envía `Hola` al plugin Python, que consulta el modelo local y devuelve la respuesta. Configuración opcional:

```sh
OLLAMA_MODEL=qwen2.5vl:3b OLLAMA_URL=http://localhost:11434 go run ./cmd/harness --text "¡Hola!"
```

El comando de plugin se puede sustituir después de `--`:

```sh
go run ./cmd/harness -- python3 plugins/ollama/main.py
```

## Protocolo multimodal

Las peticiones y respuestas son objetos JSON con `protocol_version`, `id` y mensajes compuestos por partes `text`, `image`, `audio` o `video`. Los datos binarios se transportan como base64 en `data`. El ejemplo del plugin Ollama implementa texto e imágenes (la imagen debe venir como base64); devuelve un error explícito para audio/vídeo si el modelo/adaptador no los admite. Se pueden añadir plugins con soporte de audio o vídeo sin cambiar el contrato ni el host.

Para enviar una petición multimodal, crea un archivo JSON, por ejemplo `request.json`:

```json
{
  "protocol_version": "1",
  "id": "vision-1",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "¿Qué aparece en esta imagen?"},
      {"type": "image", "mime_type": "image/jpeg", "data": "<BASE64_DE_LA_IMAGEN>"}
    ]
  }]
}
```

Y ejecútalo con `go run ./cmd/harness --request request.json`. El modelo configurado debe admitir visión.

## Diseño

- **Host Go:** supervisa una ejecución de plugin, aplica timeout y valida versión e ID de la respuesta.
- **Plugins:** procesos independientes con una línea JSON de entrada/salida; stdout queda reservado al protocolo y stderr a logs. El contrato vive en `internal/protocol`.
- **Plugin inicial:** Python, sin dependencias externas, para Ollama.

Este es un punto de partida: aún no incluye registro dinámico de plugins, reintentos, streaming ni gestión de sesiones.
