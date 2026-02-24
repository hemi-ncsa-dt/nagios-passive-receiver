# Nagios Passive Receiver

A FastAPI-based HTTP server that receives external requests from Nagios monitoring plugins and writes passive check results to the `nagios.cmd` file.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **API Key Authentication**: Each monitoring plugin has a dedicated API key for secure access
- **Data Validation**: Validates incoming requests to ensure correct format and prevent injection attacks
- **TLS Support**: Optional TLS/HTTPS encryption for secure communication
- **Docker Ready**: Containerized deployment with Docker and Docker Compose
- **Health Checks**: Built-in endpoint to verify service status and nagios.cmd writability

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

## Installation

### Local Development

1. Clone the repository and navigate to the project directory

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables and API keys:
```bash
cp .env.example .env
cp api_keys.example.json api_keys.json
# Edit .env and api_keys.json with your configuration
```

4. Run the server:
```bash
python main.py
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. Or build the Docker image manually:
```bash
docker build -t nagios-passive-receiver .
docker run -d -p 8000:8000 \
  -e NAGIOS_CMD_PATH=/var/nagios/rw/nagios.cmd \
  -e API_KEYS_FILE=/app/api_keys.json \
  -v /path/to/nagios/rw:/var/nagios/rw \
  -v /path/to/api_keys.json:/app/api_keys.json:ro \
  nagios-passive-receiver
```

## Configuration

Configuration is done via environment variables (can be set in `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `NAGIOS_CMD_PATH` | Path to nagios.cmd file | `/var/nagios/rw/nagios.cmd` |
| `API_KEYS_FILE` | Path to API keys JSON file | `api_keys.json` |
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `TLS_CERT_FILE` | Path to TLS certificate (optional) | None |
| `TLS_KEY_FILE` | Path to TLS key (optional) | None |

### API Keys Configuration

API keys are stored in a JSON file (default: `api_keys.json`) for better management and security.

**Format:**
```json
{
  "api_keys": [
    {
      "key": "your-secret-key-1",
      "name": "monitoring-plugin-1",
      "description": "Production monitoring plugin",
      "enabled": true
    },
    {
      "key": "your-secret-key-2",
      "name": "monitoring-plugin-2",
      "description": "Backup monitoring plugin",
      "enabled": true
    }
  ]
}
```

**Benefits:**
- Easy to read and maintain
- Can disable keys without deleting them (set `enabled: false`)
- Supports comments via description field
- Can be version controlled (with proper .gitignore)
- No need to restart server - can be reloaded dynamically

## API Endpoints

### POST `/api/v1/passive-check`

Submit a passive check result to Nagios.

**Headers:**
- `X-API-Key`: Your API key (required)
- `Content-Type`: application/json

**Request Body:**
```json
{
  "host_name": "webserver01",
  "service_description": "HTTP Check",
  "return_code": 0,
  "plugin_output": "HTTP OK - Response time: 0.234s"
}
```

**Return Codes:**
- `0`: OK
- `1`: WARNING
- `2`: CRITICAL
- `3`: UNKNOWN

**Response:**
```json
{
  "status": "success",
  "message": "Passive check result submitted for webserver01/HTTP Check",
  "timestamp": "2026-02-24T12:34:56.789"
}
```

### GET `/health`

Check service health and nagios.cmd writability.

**Response:**
```json
{
  "status": "healthy",
  "nagios_cmd_writable": true,
  "timestamp": "2026-02-24T12:34:56.789"
}
```

### GET `/`

Get API information and available endpoints.

## Usage Examples

### Python Client

See [example_client.py](example_client.py) for a complete example:

```python
import requests

API_URL = "http://localhost:8000/api/v1/passive-check"
API_KEY = "your-secret-key-1"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "host_name": "webserver01",
    "service_description": "HTTP Check",
    "return_code": 0,
    "plugin_output": "HTTP OK - Response time: 0.234s"
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json())
```

### Bash/cURL Client

See [example_client.sh](example_client.sh) for a complete example:

```bash
curl -X POST "http://localhost:8000/api/v1/passive-check" \
  -H "X-API-Key: your-secret-key-1" \
  -H "Content-Type: application/json" \
  -d '{
    "host_name": "webserver01",
    "service_description": "HTTP Check",
    "return_code": 0,
    "plugin_output": "HTTP OK - Response time: 0.234s"
  }'
```

## Security Considerations

1. **TLS/HTTPS**: Always use TLS in production by configuring `TLS_CERT_FILE` and `TLS_KEY_FILE`
2. **API Keys**: Use strong, randomly generated API keys and store them in `api_keys.json`
3. **File Security**: Keep `api_keys.json` readable only by the application user, not in version control
4. **Network**: Run in a private network or use firewall rules to restrict access
5. **File Permissions**: Ensure proper permissions on nagios.cmd file and directory
6. **Input Validation**: The server validates all inputs to prevent injection attacks

## Architecture

The server consists of several modules:

- **main.py**: FastAPI application with endpoints and authentication
- **models.py**: Pydantic models for request/response validation
- **config.py**: Configuration management using environment variables and JSON API keys
- **nagios_writer.py**: Handles writing to nagios.cmd file
- **api_keys.json**: Secure storage for API keys (not in version control)

## Nagios Command Format

The server writes commands to nagios.cmd in the following format:

```
[<timestamp>] PROCESS_SERVICE_CHECK_RESULT;<host_name>;<service_description>;<return_code>;<plugin_output>
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `401`: Authentication failed (missing or invalid API key)
- `422`: Validation error (invalid request data)
- `500`: Internal server error
- `503`: Service unavailable (cannot write to nagios.cmd)

## API Documentation

When the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

This project is provided as-is for use with Nagios monitoring systems.
