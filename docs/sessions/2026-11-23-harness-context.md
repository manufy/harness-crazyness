# Contexto de sesión — endurecimiento del harness

- Fecha: 2026-11-23
- Usuario: manufy
- Repositorio: `manufy/harness-crazyness`
- Rama base acordada: `dev`
- Rama de trabajo: `feature/harness-hardening`

## Objetivo

Revisar el endurecimiento del harness experimental Go + Python en `go-control`, identificar vulnerabilidades, implementar mejoras, ejecutar pruebas y preparar un pull request hacia `dev`.

## Estado confirmado

- El usuario quiere no perder el contexto de esta conversación.
- La rama `feature/harness-hardening` ya existe.
- El repositorio fue convertido a público y puede consultarse sin autorización adicional.
- La rama todavía no tiene cambios nuevos confirmados respecto a `dev` en las comprobaciones realizadas.
- No se ha abierto ni confirmado ningún pull request.
- No se han ejecutado cambios de código ni pruebas durante esta sesión.

## Componentes conocidos

- `go-control/cmd/harness/main.go`: host Go que lanza plugins como procesos independientes.
- `go-control/internal/protocol/protocol.go`: contrato JSON y validación de protocolo.
- `go-control/plugins/mock/main.py`: proveedor simulador sin API key.
- `go-control/plugins/openrouter/main.py`: integración OpenRouter.
- `go-control/plugins/openai-compatible/main.py`: integración compatible con API OpenAI.
- `go-control/plugins/ollama/main.py`: integración Ollama local.
- `.github/workflows/go-control.yml`: workflow manual del harness.
- `go-control/README.md`: documentación de uso y seguridad.

## Revisión pendiente

Priorizar estas áreas:

1. Ejecución segura de procesos y argumentos.
2. Límites de tiempo, procesos colgados y cancelación.
3. Validación estricta de JSON y del contrato de protocolo.
4. Validación de modalidades y tamaños de mensajes/multimedia.
5. Manejo de errores y códigos de salida.
6. Prevención de fugas de API keys, payloads y datos base64 en logs.
7. Manejo robusto de respuestas HTTP y JSON.
8. Pruebas unitarias, integración y casos límite.
9. Seguridad y mantenimiento del workflow de GitHub Actions.

## Próxima acción

Cuando se autorice continuar, revisar el contenido real de `dev`, implementar las mejoras prioritarias en `feature/harness-hardening`, ejecutar las pruebas disponibles y abrir un pull request hacia `dev`.
