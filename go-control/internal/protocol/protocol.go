package protocol

// Request and Response define the versioned NDJSON contract shared by the Go
// host and language-agnostic plugins. Media payloads use base64 in Data.
type Request struct {
	ProtocolVersion string    `json:"protocol_version"`
	ID              string    `json:"id"`
	Messages        []Message `json:"messages"`
}

type Message struct {
	Role    string        `json:"role"`
	Content []ContentPart `json:"content"`
}

type ContentPart struct {
	Type     string `json:"type"`
	Text     string `json:"text,omitempty"`
	MIMEType string `json:"mime_type,omitempty"`
	Data     string `json:"data,omitempty"`
	URL      string `json:"url,omitempty"`
}

type Response struct {
	ProtocolVersion string  `json:"protocol_version"`
	ID              string  `json:"id"`
	Message         Message `json:"message,omitempty"`
	Error           string  `json:"error,omitempty"`
}
