# go-control — harness experimental Go + Python

Andamiaje mínimo para un host en Go que ejecuta plugins como procesos independientes. El contrato JSONL versionado desacopla el host de los plugins; el primer plugin Python compatible es [OpenRouter](https://openrouter.ai/), que puede usar modelos gratuitos sin alojar Ollama.

## Prueba remota gratis desde GitHub Mobile

1. Añade una clave de OpenRouter como **Actions secret** de nombre `OPENROUTER_API_KEY`:
   - Abre el repositorio en GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
   - En iOS, también puedes abrir el repositorio en el navegador y usar esa configuración.
2. Abre **Actions** → **go-control OpenRouter smoke test** → **Run workflow**.
3. Elige la rama `dev`, escribe el texto opcional y pulsa **Run workflow**.
4. Abre la ejecución y revisa el paso **Ejecutar el harness con OpenRouter**.

El workflow usa `OPENROUTER_MODEL=openrouter/free`. OpenRouter seleccionará una variante gratuita disponible. La selección puede cambiar y algunos modelos gratuitos tienen límites o disponibilidad temporal. También puedes fijar otro modelo gratuito cambiando esa variable en el workflow.

## Ejecutar desde un terminal local

```sh
cd go-control
export OPENROUTER_API_KEY="tu-clave"
go run ./cmd/harness -- python3 plugins/openrouter/main.py
```

Para texto personalizado:

```sh
printf '{"protocol_version":"1","id":"hello-1","messages":[{"role":"user","content":[{"type":"text","text":"Hola"}]}]}\n' |
  python3 plugins/openrouter/main.py
```

## Contrato multimodal

Las peticiones y respuestas son objetos JSON con `protocol_version`, `id` y mensajes compuestos por partes `text`, `image`, `audio` o `video`. Los datos binarios se transportan como base64 en `data`. El plugin OpenRouter convierte imágenes base64 al formato `data:<mime>;base64,...` admitido por modelos con visión.

Ejemplo:

```json
{
  "protocol_version": "1",
  "id": "vision-1",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "¿Qué aparece en esta imagen?"},
      {"type": "image", "mime_type": "image/jpeg", "data": "<BASE64>"}
    ]
  }]
}
```

Audio y vídeo requieren un plugin o modelo compatible y pueden no estar disponibles entre los modelos gratuitos.

## Diseño

- **Host Go:** timeout, validación de versión e ID y ejecución del plugin como proceso independiente.
- **Plugins:** proceso con entrada/salida JSON en una sola línea; stdout reservado al protocolo y stderr a logs.
- **Plugin inicial:** Python para OpenRouter sin dependencias externas.
