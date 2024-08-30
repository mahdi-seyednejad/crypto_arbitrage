# Installation Guide

Follow these steps to set up and run the Cryptocurrency Exchange Arbitrage tool.

## Prerequisites

Ensure you have the following installed:
- Python 3.8 or later
- Docker (if using containerized setup)
- Git

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/crypto-arbitrage.git
cd crypto-arbitrage
```

## Step 2: Choose Your Setup Method

You can either set up the project directly on your machine or use Docker. Choose the method that best suits your needs.

### Option A: Direct Setup

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up TimescaleDB:
   Follow the official TimescaleDB installation guide for your operating system:
   [TimescaleDB Installation Guide](https://docs.timescale.com/latest/getting-started/installation)

### Option B: Docker Setup

1. Ensure Docker is installed and running on your system.

2. Build and run the Docker container:
   ```bash
   docker build -t crypto-arbitrage .
   docker run -d crypto-arbitrage
   ```

   Note: The Docker setup includes TimescaleDB, so you don't need to install it separately.

## Step 3: Configure API Keys

Create a `.env` file in the root directory of the project (next to the `src` folder) with your API keys:

```
bi_my_hft_key_02 = "Your Binance API key"
bi_my_hft_secret_02 = "Your Binance Secret Key"

cb_hft_key_02 = "Your Coinbase API key"
cb_hft_secret_02 = "Your Coinbase Secret Key"
```

For multiple APIs, you can add additional keys with incremented numbers:

```
bi_my_hft_key_03 = "Your Second Binance API key"
bi_my_hft_secret_03 = "Your Second Binance Secret Key"

cb_hft_key_03 = "Your Second Coinbase API key"
cb_hft_secret_03 = "Your Second Coinbase Secret Key"

bi_my_hft_key_04 = "Your Third Binance API key"
bi_my_hft_secret_04 = "Your Third Binance Secret Key"

cb_hft_key_04 = "Your Third Coinbase API key"
cb_hft_secret_04 = "Your Third Coinbase Secret Key"
```

## Step 4: Configure Multi-API Setup

Modify the `main.py` file according to the instructions within it to enable multi-API functionality. This typically involves specifying which API keys to use and how to distribute tasks among them.

## Step 5: Run the Application

```bash
python main.py
```

## Troubleshooting

If you encounter any issues during installation or running the application, please check our [FAQ](faq.md) or open an issue on our GitHub repository.

For more detailed information on using the tool, refer to our [User Guide](user_guide.md).
