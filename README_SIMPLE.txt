╔═══════════════════════════════════════════════════════════════════╗
║                SOLANA VANITY WALLET - QUICK START                ║
╚═══════════════════════════════════════════════════════════════════╝


QUICK MODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  cd /path/to/wallet-generator
  npm start

The wizard walks you through:

  1. Security check
  2. Prefix input (optional, can set multiple)
  3. Suffix input (optional)
  4. Wallet count
  5. Case sensitivity
  6. Start search

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


ADVANCED MODE (skip wizard)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ./forge.sh --starts-with "SOL"
  ./forge.sh --ends-with "XYZ"
  ./forge.sh --starts-with "So" --ends-with "L"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ./keys/

  Each wallet shows at the end:
    - Public address
    - Private key (do not share)
    - JSON backup file (compatible with solana-keygen)
