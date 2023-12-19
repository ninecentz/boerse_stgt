# About
This tool collects sales data for knock-out-certificates traded at the Boerse Stuttgart, Germany for a given day and time range.
The collected data is based on the continuous reporting of the most traded certificates of the day. The report is provided at the discretion of the Boerse Stuttgart.

Sample Output:
```
WKN: GQ59N8     Title: NVIDIA Corp./Faktor/Long [15]/GOLDS
2000 pieces:
        14:47:57  at  3.73 €
110 pieces:
        12:53:16  at  3.99 €
210 pieces:
        10:25:15  at  4.98 €
Found 12 rows in the table

WKN: DJ49TY     Title: NVIDIA Corp./KO/Call [endlos]/DZ
2100 pieces:
        12:52:07  at  12.34 €
9100 pieces:
        09:33:09  at  12.70 €
Found 7 rows in the table

WKN: ME33BJ     Title: NVIDIA Corp./KO/Call [endlos]/MS
3000 pieces:
        15:02:48  at  7.73 €
```
# Installation
1. Download and install the Chrome browser (https://www.google.com/intl/en_us/chrome/)
2. Download the chromedriver from https://chromedriver.chromium.org/getting-started and include the ChromeDriver location in your PATH environment variable.
3. Install the Python language bindings for Selenium WebDriver, for example using pip:
```
pip install -U selenium
```
# Use
Run
```
from kos_sold_in_stgt import BoerseStgt
import datetime

STARTTIME = datetime.time(hour=7)
ENDTIME = datetime.time(hour=22)
TODAY = datetime.date.today()

# Get instance of BoerseStgt() class
conn = BoerseStgt()

# Retrieve dictionary of the most traded certificates
kos = conn.getKOs()

for ko in kos:
    # Get sales data for a specific certificate
    sales = conn.inspectKo(ko, TODAY, STARTTIME, ENDTIME)

    # Show data
    print(f'\nWKN: {ko}\tTitle: {kos[ko]}')
    for volume in sales:
        print(f'{volume} pieces:')
        for singleSale in sales[volume]:
            print(f'\t{singleSale["timestamp"].time()}  at  {singleSale["price"]:.2f} €')
```
