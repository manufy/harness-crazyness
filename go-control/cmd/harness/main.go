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

func main() {
	text := flag.String("text", "Hola", "texto que se enviará al modelo")
	requestFile := flag.String("request", "", "archivo JSON con una petición multimodal")
	flag.Parse()

	request, err := loadRequest(*requestFile, *text)
	if err != nil {
		fatal(err)
	}

	command, args := pluginCommand(os.Args[1:])
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	payload, err := json.Marshal(request)
	if err != nil {
		fatal(fmt.Errorf("codificar petición: %w", err))
	}
	payload = append(payload, '\n')

	cmd := exec.CommandContext(ctx, command, args...)
	cmd.Stdin = bytes.NewReader(payload)
	cmd.Stderr = os.Stderr
	output, err := cmd.Output()
	if err != nil {
		fatal(fmt.Errorf("ejecutar plugin %q: %w", command, err))
	}

	var response protocol.Response
	if err := json.Unmarshal(bytes.TrimSpace(output), &response); err != nil {
		fatal(fmt.Errorf("respuesta JSON inválida del plugin: %w", err))
	}
	if response.ProtocolVersion != request.ProtocolVersion || response.ID != request.ID {
		fatal(errors.New("la versión de protocolo o el id de respuesta no coincide con la petición"))
	}
	if response.Error != "" {
		fatal(errors.New(response.Error))
	}
	for _, part := range response.Message.Content {
		if part.Type == "text" {
			fmt.Println(part.Text)
		}
	}
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
		if argument == "--" {
			if i+1 < len(arguments) {
				return arguments[i+1], arguments[i+2:]
			}
			break
		}
	}
	python := os.Getenv("PYTHON")
	if python == "" {
		python = "python3"
	}
	return python, []string{"plugins/ollama/main.py"}
}

func fatal(err error) {
	_, _ = io.WriteString(os.Stderr, "harness: "+strings.TrimSpace(err.Error())+"\n")
	os.Exit(1)
}
