# WhatsApp Quote Bot (Flask + WhatsApp Cloud API)

A WhatsApp bot that collects quote requests from customers: language selection, product weight, and photos. Each request is stored in a SQLite database with its photos, so a reviewer can check them and reply with a price.

Built as a portfolio project. It runs on the WhatsApp Cloud API test number provided by Meta.

## Demo

Video: [add your link here]

## Conversation flow

1. The user sends any message. The bot asks for a language:
   1) English, 2) Traditional Chinese, 3) Spanish
2. The bot asks, in the chosen language, for the quantity in grams.
3. The bot asks for photos, one at a time. The user types `done`, `listo` or `完成` to finish.
4. The request is saved with status `completo`. Sending a new message starts a new request.

## Features

- Multi-language flow (English, Traditional Chinese, Spanish)
- Input validation for numeric quantities
- Photo download from the WhatsApp Cloud API, saved per phone number
- Request storage in SQLite (`pedidos.db`)
- Webhook verification and handling of incoming messages

## Tech stack

- Python 3.10+
- Flask (webhook server)
- requests (calls to the Graph API)
- SQLite (built into Python)
- WhatsApp Cloud API (Meta)
- ngrok (local tunnel for development)

## Project structure

```
BotCalculos/
├── app.py              # Flask server and conversation logic
├── requirements.txt    # Python dependencies
├── README.md
├── pedidos.db          # Created automatically (not in the repo)
└── fotos/              # Created automatically (not in the repo)
    └── <phone>/        # Photos for each phone number
```

## Setup

### 1. Requirements

- Python 3.10 or newer
- A Meta developer app with the WhatsApp product enabled
- ngrok (free account) for local testing

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

The bot reads its credentials from environment variables. Never write them into the code.

| Variable | Description |
|---|---|
| `WA_TOKEN` | Access token from the Meta developer panel |
| `WA_PHONE_ID` | Phone Number ID of the WhatsApp number |
| `WA_VERIFY` | Verify token you choose; must match the one set in Meta |

PowerShell (Windows):
```powershell
$env:WA_TOKEN="your_token"
$env:WA_PHONE_ID="your_phone_number_id"
$env:WA_VERIFY="your_verify_token"
```

Bash (Linux/macOS):
```bash
export WA_TOKEN="your_token"
export WA_PHONE_ID="your_phone_number_id"
export WA_VERIFY="your_verify_token"
```

### 4. Run the server

```bash
python app.py
```

The server listens on `http://127.0.0.1:5000`.

### 5. Expose the server and connect Meta

```bash
ngrok http 5000
```

In the Meta developer panel, under **WhatsApp > Configuration > Webhook**:
- **Callback URL:** `https://<your-ngrok-url>/webhook`
- **Verify token:** the same value as `WA_VERIFY`
- Subscribe to the **messages** field.

## Limitations

- The test number only accepts messages from numbers registered as recipients in the Meta panel.
- Tokens from the test panel expire (about 24 hours). For production, create a permanent system user token.
- Free ngrok URLs change when the tunnel restarts; update the Callback URL in Meta when that happens.
- WhatsApp allows free-form replies only within 24 hours after the user's last message.
- Data is stored locally. This version has no admin panel; a reviewer opens `pedidos.db` with a SQLite viewer.

## Security and privacy

- Credentials are read from environment variables and are not stored in the repository.
- `pedidos.db` and `fotos/` contain customer data and are excluded from Git by `.gitignore`.
- A production deployment would need a privacy notice for customers, data retention rules, and HTTPS hosting.

## Next steps

- Admin page to list and review requests
- Automatic quote calculation based on weight and photo review
- Deployment to a cloud server with a permanent token

## License

MIT
