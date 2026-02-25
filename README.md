## Quickstart
1. Install prerequisites
   - [VSCode](https://code.visualstudio.com/download)
   - [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions)
   - [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-latest.php)
2. Create a Conda environment and install Python packages.
```
conda create -n algo-trading python=3.13 -y
conda activate algo-trading
pip install -r requirements.txt
```
3. Copy `.env.example` to `.env` and fill in your IB account ID.
4. Run **IB Gateway** and log in with your account.
5. In the upper menu of **IB Gateway**, go to "Configure->Settings" and uncheck "Read-Only API".
6. Run `python login_test.py` to test the connection to IB Gateway.
7. Run `python test.py` to 