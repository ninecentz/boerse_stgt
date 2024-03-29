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
            # to print the time without the date, you can use time = singleSale["timestamp"].time()
            time = singleSale["timestamp"].strftime('%d.%m. %H:%M:%S')
            print(f'\t{time}  at  {singleSale["price"]:.2f} €')