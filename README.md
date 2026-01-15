# JS Hunt - JavaScript Credentials Hunter

This Python toolkit is designed to hunt for high-value secrets, API keys, and database credentials exposed within JavaScript files found on target web applications.

## **Image Preview**
![Sample](https://raw.githubusercontent.com/khadafigans/JSHUNT/refs/heads/main/image.jpeg)

## 🧾 main.py
### 📌 Purpose
Automated scanning and extraction of sensitive credentials from JS files (e.g., target.com). Identifies:
- **AWS Keys**: AKIA/ASIA Access Keys + Secret Keys + Region extraction.
- **Stripe**: Live secret keys with optional Telegram alerts.
- **Database Connection Strings**: Validated MongoDB, PostgreSQL, MySQL, Redis, and MSSQL URLs.
- **Tokens**: GitHub Personal Access Tokens (PAT) and Slack Tokens.

### 🛠 How It Works
1. **Target Gathering**: Accepts single URLs or lists. Automatically probes for `.js`, `.ts`, `.mjs`, and `.env` files.
2. **Spidering**: Curls the base URL to find scripts via HTML tags and regex-based discovery of hidden paths.
3. **Logic Gate V4**: Filters out "library noise" from common JS libraries like JSEncrypt or RSA components to minimize false positives.
4. **Validation**: Uses entropy checks (V5 logic) to ensure detected AWS secret keys are genuine and not random garbage.
5. **Notification**: Integrates with Telegram API to send real-time alerts when Stripe Live keys are discovered.

### 📥 Usage
1. `pip3 install requests beautifulsoup4 colorama`
2. `python3 main.py`
3. Enter targets file: `targets.txt`
4. Enter threads: `100` (default)

**Piped**: `echo "targets.txt\n100" | python3 main.py`

### 📁 Output
Results are organized in a timestamped directory `JS_Results_YYYY-MM-DD_HH-MM-SS/`:
- `RESULT-AWS.txt`: Formatted AWS credentials.
- `RESULT-STRIPE.txt`: Stripe secret keys.
- `RESULT-DB.txt`: Database connection strings.
- `RESULT-TOKENS.txt`: GitHub and Slack tokens.
- `fingerprinted.txt`: List of processed URLs.

### 📦 Dependencies
```
requests
beautifulsoup4
colorama
```
`pip install requests beautifulsoup4 colorama`

## ⚠️ Legal Disclaimer
For authorized penetration testing & educational purposes only (user confirmed permission under ToS). Unauthorized use illegal/unethical.

## 👨‍💻 Author
[Bob Marley](https://github.com/khadafigans)

Buy me a Coffee:
```
₿ BTC: 17sbbeTzDMP4aMELVbLW78Rcsj4CDRBiZh
```

©2025 khadafigans
