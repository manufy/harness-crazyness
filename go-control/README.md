# go-control — harness experimental Go + Python

Host Go pequeño que ejecuta plugins como procesos independientes. El contrato JSON versionado admite mensajes con partes textuales y multimodales; se pueden añadir proveedores sin acoplarlos al host.

## Probar gratis desde GitHub Mobile, sin API key

El workflow manual ofrece el proveedor **mock**, que no llama a un LLM, no necesita claves y devuelve una respuesta simulada. Sirve para comprobar que el runner remoto, Go, Python, el contrato y el plugin funcionan. En GitHub iOS abre **Actions → go-control remote harness test → Run workflow**, selecciona `dev`, `mock` y escribe un prompt.

El workflow está en `.github/workflows/go-control.yml`, la ubicación que GitHub Actions detecta.

## Usar un modelo real

Selecciona `openrouter` en el workflow y configura el Actions secret `OPENROUTER_API_KEY`. Usa `openrouter/free` o un ID de modelo terminado en `:free`; la disponibilidad y los límites los decide OpenRouter y pueden variar. El plugin conserva el soporte de imágenes cuando el modelo elegido las admite.

Para cualquier proveedor compatible con la API OpenAI Chat Completions, configura la Actions variable `LLM_BASE_URL` (URL base hasta `/v1`, por ejemplo la URL documentada por el proveedor) y el Actions secret `LLM_API_KEY`; selecciona `openai-compatible` y especifica `LLM_MODEL`. Comprueba los precios del proveedor: el workflow no puede garantizar que un modelo arbitrario sea gratuito.

**Seguridad:** nunca pongas claves en archivos, prompts o logs; usa Actions secrets. La prueba `mock` es la única que garantiza no hacer solicitudes externas ni usar una API key.

## Ejecutar localmente

```sh
cd go-control
go run ./cmd/harness --text "Hola" -- python3 plugins/mock/main.py
```

OpenRouter:

```sh
export OPENROUTER_API_KEY="tu-clave"
go run ./cmd/harness -- python3 plugins/openrouter/main.py
```

## Multimodalidad y extensión

El protocolo transporta partes `text`, `image`, `audio` o `video` (binario como base64 en `data`). Los plugins concretan qué modalidades acepta cada proveedor/modelo. Los plugins OpenRouter y OpenAI-compatible traducen texto e imágenes al formato de chat compatible; audio y vídeo requieren adaptadores/modelos que los admitan. El plugin simulado prueba la ruta del protocolo, no interpreta medios.

Añadir proveedores significa añadir un plugin que traduzca el contrato común, sin cambiar el host Go. Se incluyen OpenRouter, cualquier proveedor compatible con la API OpenAI Chat Completions y `mock` para pruebas offline.
