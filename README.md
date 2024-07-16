# My-Alpaca-Trading

My-Alpaca-Trading is a Python application that automates the trading of leveraged ETFs using the Alpaca API. The application includes functionality to check network connection, verify trading eligibility, fetch real-time prices, and execute trades based on predefined conditions.

## Features

- **Network Whitelisting**: Ensures that the application only runs on specified Wi-Fi networks.
- **Real-Time Price Fetching**: Uses the Alpaca API to fetch the latest stock quotes.
- **Automated Trading**: Automatically buys and sells leveraged ETFs based on predicted future prices and predefined profit margins.
- **GUI Interface**: Includes a simple Tkinter-based GUI for manual operation and real-time monitoring.

## Prerequisites

- Python 3.7+
- Alpaca API account with API key and secret key

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/auth-Afham/My-Alpaca-Trading.git
   cd My-Alpaca-Trading
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Alpaca API credentials**:
   - Create a `.env` file in the root directory of the project
   - Add your Alpaca API credentials to the `.env` file:
     ```
     ALPACA_API_KEY=your_api_key_here
     ALPACA_API_SECRET=your_secret_key_here
     ```

## Usage

Run the application:

```bash
python LETFs.py
```

## Configuration

- Edit the `config.py` file to customize trading parameters, network whitelisting, and other settings.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request

Please make sure to update tests as appropriate and adhere to the project's coding standards.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Use at your own risk. The authors and contributors are not responsible for any financial losses incurred through the use of this application.

## Additional Notes

- Ensure all required packages are listed in the `requirements.txt` file for easy installation.
- Always use environment variables or a secure method to store API keys. Never commit sensitive information directly to the repository.
- Regularly update the dependencies to ensure security and compatibility.
- Consider adding a `CONTRIBUTING.md` file with detailed guidelines for contributors.
