# go-control — harness experimental Go + Python

Host Go pequeño que ejecuta plugins como procesos independientes. El contrato JSON versionado admite mensajes con partes textuales y multimodales; se pueden añadir proveedores sin acoplarlos al host.

## Registro y observabilidad

El host escribe logs de ciclo de vida en `stderr`, en este orden: fecha UTC, tiempo transcurrido desde el inicio, nivel y mensaje. Los niveles usan colores compatibles con terminal y GitHub Actions:

- `INFO` azul: inicio del harness.
- `LOAD` magenta: carga y validación básica de la petición.
- `RUN` azul: selección y ejecución del plugin.
- `OK` verde: respuesta válida y finalización.
- `ERROR` rojo: errores y respuesta fallida.

En GitHub Actions, la salida del plugin aparece dentro de un grupo plegable y los errores generan una anotación. Los logs no muestran claves, payloads completos ni datos base64.

## Probar gratis desde GitHub Mobile, sin API key

El workflow manual ofrece el proveedor **mock**, que no llama a un LLM, no necesita claves y devuelve una respuesta simulada. Sirve para comprobar el runner remoto, Go, Python, el contrato y el workflow.

El workflow está en `.github/workflows/go-control.yml`, la ubicación que GitHub Actions detecta.

## Usar un modelo real

Selecciona `openrouter` en el workflow y configura el Actions secret `OPENROUTER_API_KEY`. Usa `openrouter/free` o un ID terminado en `:free`.

Para cualquier proveedor compatible con la API OpenAI, configura la variable `LLM_BASE_URL` y el secret `LLM_API_KEY`.

**Seguridad:** nunca pongas claves en archivos, prompts o logs.

## Ejecutar localmente

```sh
cd go-control
go run ./cmd/harness --text "Hola" -- python3 plugins/mock/main.py
```

## Multimodalidad y extensión

El protocolo transporta partes `text`, `image`, `audio` o `video`. Los plugins concretan qué modalidades acepta cada proveedor/modelo.
