import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from datetime import datetime, timedelta
import csv

# Load Amadeus credentials
load_dotenv()
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

# Hubs and destination
ORIGINS = ["LON", "PAR", "FRA", "AMS", "MAD"]
DESTINATION = "TYO"  # Tokyo (HND + NRT)

OUTFILE = "C:\\DATA_ANALYSIS\\JAPAN\\data_raw\\flights.csv"

# Time window
START_DATE = datetime.today()
END_DATE = START_DATE + timedelta(days=365)
STEP = 10
MAX_RETRY_DAYS = 3


with open(OUTFILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["origin", "destination", "departure_date", "price", "currency"])

    current_date = START_DATE
    while current_date <= END_DATE:
        for origin in ORIGINS:
            date = current_date
            success = False

            for _ in range(MAX_RETRY_DAYS + 1):
                try:
                    response = amadeus.shopping.flight_offers_search.get(
                        originLocationCode=origin,
                        destinationLocationCode=DESTINATION,
                        departureDate=date.strftime("%Y-%m-%d"),
                        adults=1,
                        currencyCode="EUR",
                        max=1
                    )
                    offer = response.data[0]
                    price = offer["price"]["total"]
                    currency = offer["price"]["currency"]

                    print(f"{origin}->{DESTINATION} {date.strftime('%Y-%m-%d')}: {price} {currency}")
                    writer.writerow([origin, DESTINATION, date.strftime("%Y-%m-%d"), price, currency])
                    success = True
                    break

                except ResponseError as e:
                    print(f"No flights {origin}->{DESTINATION} on {date.strftime('%Y-%m-%d')}: {e}")
                    date += timedelta(days=1)

            if not success:
                print(f"Skipped {origin}->{DESTINATION} around {current_date.strftime('%Y-%m-%d')}")

        current_date += timedelta(days=STEP)

print(f"Done! Data saved to {OUTFILE}")
