# Terminal Setup (Quick)

```bash
git clone https://github.com/<your-username>/water-sol-wallet-generator.git
cd water-sol-wallet-generator
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py show-device
python3 main.py search-pubkey --starts-with WATER --count 1 --output-dir ./keys
```

Notes:
- Wallet files are saved in `./keys`.
- Keep private key JSON files offline and never share them.
