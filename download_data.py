import requests
import os

os.makedirs("data/raw", exist_ok=True)

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
print("Downloading NYC Taxi data... this may take 1-2 minutes")

r = requests.get(url, stream=True)
with open("data/raw/yellow_tripdata_2024-01.parquet", "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print("Done! File saved to data/raw/")