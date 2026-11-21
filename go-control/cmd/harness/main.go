package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"strings"
	"time"

	"example.com/go-control/internal/protocol"
)

var startedAt = time.Now()

func logLine(level, color, message string) {
	timestamp := time.Now().UTC().Format(time.RFC3339Nano)
	elapsed := time.Since(startedAt).Round(time.Millisecond)
	fmt.Fprintf(os.Stderr, "\033[%sm[%s] [%s] %-7s %s — %s\033[0m\n", color, timestamp, elapsed, level, message, strings.TrimSpace(message))
}

func logInfo(message string)   { logLine("INFO", "36", message) }
func logLoad(message string)   { logLine("LOAD", "35", message) }
func logRun(message string)    { logLine("RUN", "34", message) }
func logSuccess(message string) { logLine("OK", "32", message) }
func logError(message string)  { logLine("ERROR", "31", message) }

func main() {
	logInfo("Inicio del harness")
	text := flag.String("text", "Hola", "texto que se enviará al modelo")
	requestFile := flag.String("request", "", "archivo JSON con una petición multimodal")
	flag.Parse()

	logLoad("Cargando petición")
	request, err := loadRequest(*requestFile, *text)
	if err != nil {
		fatal(err)
	}
	logLoad(fmt.Sprintf("Petición cargada: protocolo=%s id=%s partes=%d", request.ProtocolVersion, request.ID, countParts(request)))

	command, args := pluginCommand(os.Args[1:])
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	payload, err := json.Marshal(request)
	if err != nil {
		fatal(fmt.Errorf("codificar petición: %w", err))
	}
	payload = append(payload, '\n')

	if os.Getenv("GITHUB_ACTIONS") != "" {
		fmt.Fprintf(os.Stderr, "::group::Resultado del plugin %s\n", strings.Join(append([]string{command}, args...), " "))
	}
	logRun(fmt.Sprintf("Ejecutando plugin: %s", strings.Join(append([]string{command}, args...), " ")))
	pluginStarted := time.Now()

	cmd := exec.CommandContext(ctx, command, args...)
	cmd.Stdin = bytes.NewReader(payload)
	cmd.Stderr = os.Stderr
	output, err := cmd.Output()
	pluginElapsed := time.Since(pluginStarted).Round(time.Millisecond)
	if err != nil {
		if os.Getenv("GITHUB_ACTIONS") != "" {
			fmt.Fprintln(os.Stderr, "::endgroup::")
		}
		fatal(fmt.Errorf("ejecutar plugin %q tras %s: %w", command, pluginElapsed, err))
	}

	var response protocol.Response
	if err := json.Unmarshal(bytes.TrimSpace(output), &response); err != nil {
		if os.Getenv("GITHUB_ACTIONS") != "" {
			fmt.Fprintln(os.Stderr, "::endgroup::")
		}
		fatal(fmt.Errorf("respuesta JSON inválida del plugin tras %s: %w", pluginElapsed, err))
	}
	if response.ProtocolVersion != request.ProtocolVersion || response.ID != request.ID {
		if os.Getenv("GITHUB_ACTIONS") != "" {
			fmt.Fprintln(os.Stderr, "::endgroup::")
		}
		fatal(errors.New("la versión de protocolo o el id de respuesta no coincide con la petición"))
	}
	if response.Error != "" {
		if os.Getenv("GITHUB_ACTIONS") != "" {
			fmt.Fprintln(os.Stderr, "::endgroup::")
		}
		fatal(errors.New(response.Error))
	}

	textParts := 0
	for _, part := range response.Message.Content {
		if part.Type == "text" {
			textParts++
		}
	}
	logSuccess(fmt.Sprintf("Respuesta válida: %d parte(s) de texto — plugin=%s duración=%s", textParts, command, pluginElapsed))
	if os.Getenv("GITHUB_ACTIONS") != "" {
		fmt.Fprintln(os.Stderr, "::endgroup::")
	}

	for _, part := range response.Message.Content {
		if part.Type == "text" {
			fmt.Println(part.Text)
		}
	}
	logSuccess(fmt.Sprintf("Ejecución finalizada correctamente — duración total=%s", time.Since(startedAt).Round(time.Millisecond)))
}

func countParts(request protocol.Request) int {
	total := 0
	for _, message := range request.Messages {
		total += len(message.Content)
	}
	return total
}

func loadRequest(path, text string) (protocol.Request, error) {
	if path != "" {
		data, err := os.ReadFile(path)
		if err != nil {
			return protocol.Request{}, fmt.Errorf("leer petición: %w", err)
		}
		var request protocol.Request
		if err := json.Unmarshal(data, &request); err != nil {
			return protocol.Request{}, fmt.Errorf("decodificar petición: %w", err)
		}
		if request.ProtocolVersion == "" {
			request.ProtocolVersion = "1"
		}
		if request.ID == "" {
			request.ID = "request-1"
		}
		return request, nil
	}
	return protocol.Request{
		ProtocolVersion: "1",
		ID:              "hello-1",
		Messages: []protocol.Message{{
			Role:    "user",
			Content: []protocol.ContentPart{{Type: "text", Text: text}},
		}},
	}, nil
}

func pluginCommand(arguments []string) (string, []string) {
	for i, argument := range arguments {
		if argument == "--" && i+1 < len(arguments) {
			return arguments[i+1], arguments[i+2:] 
		}
	}
	python := os.Getenv("PYTHON")
	if python == "" {
		python = "python3"
	}
	return python, []string{"plugins/mock/main.py"}
}

func fatal(err error) {
	logError(strings.TrimSpace(err.Error()))
	if os.Getenv("GITHUB_ACTIONS") != "" {
		_, _ = fmt.Fprintf(os.Stderr, "::error::harness: %s\n", strings.TrimSpace(err.Error()))
	}
	logError(fmt.Sprintf("Ejecución fallida — duración total=%s", time.Since(startedAt).Round(time.Millisecond)))
	os.Exit(1)
}

