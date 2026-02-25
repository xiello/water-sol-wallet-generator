# Terminal Setup (Quick)

```bash
git clone https://github.com/xiello/water-sol-wallet-generator.git
cd water-sol-wallet-generator
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm start
```

Notes:
- `npm start` opens the interactive wizard and then launches the dashboard miner.
- Wallet files are saved in `./keys`.
- Keep private key JSON files offline and never share them.
