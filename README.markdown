# PharosBot

PharosBOT is a robust Python-based automation tool designed to streamline interactions with multiple blockchain ecosystems, including Daily Tasks, Zenith, Faroswap, OpenFi, domain registration via Pharosname, Brokex, and Gotchipus ecosystems. It supports multi-wallet operations using private keys, optional proxy integration for enhanced privacy, and automated daily task execution at 7:30 AM. The bot is built with scalability, error handling, and user-friendly logging to ensure reliable performance across diverse blockchain platforms.

## Features

- **Multi-Ecosystem Automation**: Seamlessly interacts with the following ecosystems:
  - **Daily Tasks**: Automates routine activities for consistent engagement.
  - **Zenith Ecosystem**: Handles tasks specific to the Zenith platform.
  - **Faroswap Ecosystem**: Manages decentralized exchange operations on Faroswap.
  - **OpenFi Ecosystem**: Executes tasks for the OpenFi decentralized finance platform.
  - **Register Domain**: Facilitates domain registration through Pharosname.
  - **Brokex Ecosystem**: Automates trading or staking tasks on Brokex.
  - **Gotchipus Ecosystem**: Supports activities within the Gotchipus platform, with robust error handling for potential downtime.
- **Wallet Management**: Processes tasks for multiple Ethereum wallets using private keys loaded from a `pk.txt` file.
- **Proxy Support**: Optional proxy integration for anonymized operations, with proxies loaded from a `proxies.txt` file.
- **Scheduled Execution**: Automatically runs selected tasks daily at 7:30 AM, with configurable delays (5–15 seconds) between ecosystems to prevent rate-limiting.
- **Custom Logging**: Outputs timestamped logs with colored formatting using the `colorama` library for enhanced readability.
- **Error Handling**: Includes robust mechanisms to handle network issues, invalid inputs, or bot-specific failures, ensuring uninterrupted operation.
- **User-Friendly Interface**: Interactive CLI for selecting ecosystems and configuring proxy usage.

## Prerequisites

To run PharosBot, ensure you have the following:

- **Python**: Version 3.11 or higher.
- **Required Python Packages**:
  - `requests`: For HTTP requests.
  - `eth_account`: For Ethereum wallet management.
  - `colorama`: For colored terminal output.
  - `pytz`: For handling timezone conversions.
- **Input Files**:
  - `pk.txt`: A text file containing Ethereum private keys (one per line).
  - `proxies.txt` (optional): A text file containing proxy addresses (one per line) if proxy usage is enabled. The number of proxies must match the number of private keys.
- **Bot Modules**: Ensure the `src` directory contains the following Python modules:
  - `daily.py`
  - `zenith.py`
  - `faroswap.py`
  - `openfi.py`
  - `pharosname.py`
  - `brokex.py`
  - `gotchipus.py`
- **Access Code**: Required to run the bot (see Trial Access section for details).

## Installation

It is highly recommended to use a Python virtual environment (`venv`) to manage dependencies and avoid conflicts with other projects. A virtual environment isolates the project’s dependencies, ensuring a clean and reproducible setup.

### Step 1: Clone the Repository
```bash
git clone https://github.com/IopiXD/PharosBOT.git
cd PharosBOT
```

### Step 2: Set Up a Virtual Environment
1. Create a virtual environment:
   - On Windows
   ```bash
   python -m venv venv
   ```
   - On Linux
   ```bash
   python3 -m venv venv
   ```
2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   Once activated, your terminal prompt should indicate the virtual environment (e.g., `(venv)`).

### Step 3: Install Dependencies
With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 4: Prepare Input Files
- **Private Keys**: Create a `pk.txt` file in the project root and add your Ethereum private keys, one per line. Example:
  ```
  0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
  0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
  ```
- **Proxies (Optional)**: If using proxies, create a `proxies.txt` file in the project root with proxy details, one per line, in the format `http://user:pass@host:port` or `http://host:port`. Example:
  ```
  http://proxy1.example.com:8080
  http://proxy2.example.com:8080
  ```
  Ensure the number of proxies matches the number of private keys.

### Step 5: Verify Bot Modules
Ensure the `src` directory contains all required bot modules (`daily.py`, `zenith.py`, `faroswap.py`, `openfi.py`, `pharosname.py`, `brokex.py`, `gotchipus.py`). These modules implement the specific logic for each ecosystem.

## Usage

1. **Activate the Virtual Environment** (if not already active):
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

2. **Run the Bot**:
   Start the bot by executing the main script:
   ```bash
   python main.py
   ```

3. **Provide Access Code**:
   When prompted, enter the access code for the bot (see Trial Access for details).

4. **Select Ecosystems**:
   - The bot displays a menu of available ecosystems:
     ```
     [1] Daily Tasks
     [2] Zenith Ecosystem
     [3] Faroswap Ecosystem
     [4] OpenFi Ecosystem
     [5] Register Domain
     [6] Brokex Ecosystem
     [7] Gotchipus Ecosystem
     [8] AutoStaking 
     [9] Primuslabs
     [0] Run All
     ```
   - Enter comma-separated numbers to select ecosystems (e.g., `1,3,5`) or `0` to run all ecosystems.
   - Example input: `1,2,3` to run Daily Tasks, Zenith, and Faroswap.

5. **Configure Proxy Usage**:
   - When prompted (`Use proxy? (y/n):`), enter `y` to enable proxies or `n` to proceed without proxies.
   - If proxies are enabled, ensure `proxies.txt` exists and contains the same number of proxies as private keys.

6. **Bot Execution**:
   - The bot processes tasks for each wallet and selected ecosystem, displaying the wallet address and proxy status (if applicable).
   - A random delay (5–15 seconds) is applied between ecosystems to prevent rate-limiting.
   - After completing all tasks, the bot waits until 7:30 AM the next day to restart the cycle.
   - To stop the bot, press `Ctrl+C` to trigger a graceful exit.

## File Structure

```
PharosBot/
├── main.py              # Main script to run the bot
├── pk.txt               # File containing private keys (one per line)
├── proxies.txt          # (Optional) File containing proxies (one per line)
├── src/                 # Directory containing ecosystem-specific bot modules
│   ├── daily.py         # Logic for Daily Tasks
│   ├── zenith.py        # Logic for Zenith Ecosystem
│   ├── faroswap.py      # Logic for Faroswap Ecosystem
│   ├── openfi.py        # Logic for OpenFi Ecosystem
│   ├── pharosname.py    # Logic for domain registration
│   ├── brokex.py        # Logic for Brokex Ecosystem
│   ├── gotchipus.py     # Logic for Gotchipus Ecosystem
├── venv/                # Virtual environment directory (created after setup)
├── README.md            # Project documentation
└── LICENSE              # (Optional) License file
```

## Trial Access

To obtain a trial access code for PharosBot, join our Telegram channel:  
[https://t.me/Iopigarden](https://t.me/Iopigarden)

## Troubleshooting

- **"pk.txt not found" or "pk.txt is empty"**:
  - Ensure `pk.txt` exists in the project root and contains valid Ethereum private keys.
- **"proxies.txt not found" or "proxies.txt is empty"**:
  - If using proxies, ensure `proxies.txt` exists and contains valid proxy addresses.
- **Proxy Mismatch Error**:
  - The number of proxies must match the number of private keys when proxy usage is enabled.
- **Module Not Found**:
  - Verify that all required bot modules are present in the `src` directory.
- **Dependency Issues**:
  - Ensure the virtual environment is activated before running the bot or installing packages.
  - Run `pip list` to verify that `requests`, `eth_account`, `colorama`, and `pytz` are installed in the virtual environment.
- **Bot Fails to Run**:
  - Check for network connectivity issues or ensure all dependencies are installed.
  - Review logs for specific error messages, which include detailed information for debugging.

## Why Use a Virtual Environment?

Using a Python virtual environment (`venv`) is highly recommended for the following reasons:
- **Dependency Isolation**: Prevents conflicts between PharosBot’s dependencies and other Python projects or system-wide packages.
- **Reproducible Environment**: Ensures consistent package versions across different machines or deployments.
- **Clean Uninstall**: Easily remove the project and its dependencies by deleting the `venv` directory.
- **Portability**: Simplifies sharing the project with others, as the virtual environment can be recreated with the same dependencies.

To deactivate the virtual environment when done, simply run:
```bash
deactivate
```

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

Please open an issue first to discuss proposed changes or report bugs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

PharosBot interacts with blockchain ecosystems and uses private keys. Ensure you understand the risks associated with handling private keys and interacting with decentralized platforms. The developers are not responsible for any financial losses or security issues arising from the use of this software. Use at your own risk.
