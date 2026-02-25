# Water Sol Wallet Generator

Fast Solana vanity wallet generation with OpenCL.

## Quick Start (Wizard)

```bash
# 1) Clone the repo
git clone https://github.com/xiello/water-sol-wallet-generator.git
cd water-sol-wallet-generator

# 2) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
python3 -m pip install -r requirements.txt

# 4) Start the interactive wizard
npm start
```

`npm start` launches the guided wizard (`start.py`) that walks you through:
1. Security check (WiFi off)
2. Prefix/suffix selection
3. Wallet count
4. Case sensitivity
5. Launching the live dashboard miner

Generated wallet JSON files are written to `./keys`.

## Installation

You can install it directly on Windows (not WSL) and on Unix-like systems. For details on supported platforms, check [FAQs.md](./FAQs.md).

```bash
$ python3 -m pip install -r requirements.txt
```

Requires Python 3.6 or higher. This project no longer depends on numpy, so it is compatible with Python 3.13 without extra wheels.

## Docker

Only works on Linux platforms with Nvidia GPUs. [Check this doc](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation).

```bash
$ docker build -t solana-vanity-wallet-generator .
$ docker run --rm -it --gpus all solana-vanity-wallet-generator
```

You will enter the container. The source code is located in the /app directory in the container, and all dependencies have been installed.

Please note:

1. The device’s CUDA version should be greater than 12.0.
2. The source code is located in the /app directory, so you don’t need to download the code from GitHub.

## Advanced CLI (Optional)

```bash
python3 main.py show-device
python3 main.py search-pubkey --starts-with WATER --count 1 --output-dir ./keys
python3 main.py search-pubkey --starts-with So --ends-with L --is-case-sensitive False
```

## FAQs

See [FAQs.md](./FAQs.md).


## Donations

If you find this project helpful, please consider making a donation:

SOLANA: `PRM3ZUA5N2PRLKVBCL3SR3JS934M9TZKUZ7XTLUS223`

EVM: `0x8108003004784434355758338583453734488488`
