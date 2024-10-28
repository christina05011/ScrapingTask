import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from decimal import Decimal
import concurrent.futures
import time

url_base = "https://www.booking.com/searchresults.es.html?ss=Barcelona%2C+Catalu%C3%B1a%2C+Espa%C3%B1a&ssne=Centro+de+Barcelona&ssne_untouched=Centro+de+Barcelona&label=gen173nr-1BCAEoggI46AdIM1gEaLEBiAEBmAEKuAEXyAEM2AEB6AEBiAIBqAIDuAKNg_C4BsACAdICJDJkNTBiNGFjLTkxYzYtNDY5NC04ODRjLWUyZDRmMmFlMTA1N9gCBeACAQ&sid=1ef1df8611a2f3cf3f5b5032a1be8f48&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=-372490&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=ab307ed007be015b&ac_meta=GhBhYjMwN2VkMDA3YmUwMTViIAAoATICZXM6AWJAAEoAUAA%3D&checkin=2024-11-20&checkout=2024-11-21&group_adults=1&no_rooms=1&group_children=0&offset=5&soz=1&lang_changed=1&explicit_lang_change=1&selected_currency=EUR&explicit_curr_change=1&offset={offset}"
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5042.108 Safari/537.36"}

# Función para scraping de una sola página
def scrape_page(offset):
    response = requests.get(url_base.format(offset=offset), headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    page_hotels = []

    for el in soup.find_all("div", {"data-testid": "property-card"}):
        hotel_info = {
            "NameProperty": el.find("div", {"data-testid": "title"}).text.strip(),
            "Rating": Decimal(el.find("div", {"data-testid": "review-score"}).text.strip().split(' ')[1].replace(',', '.')), # Incluyendo limpieza de datos
            "RoomRate": Decimal(el.find("span", {"data-testid": "price-and-discounted-price"}).text.strip().replace('€\xa0', '').replace(',', '.')), # Incluyendo limpieza de datos
            "TouristTax": Decimal(el.find("div", {"data-testid": "taxes-and-charges"}).text.strip().split(' ')[1].replace('€\xa0', '').replace(',', '.')) # Incluyendo limpieza de datos
        }
        page_hotels.append(hotel_info)
    return page_hotels

# Función de concurrencia
def get_all_pages(num_pages=20):
    all_hotels = []
    seen_hotels = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_page, offset * 25) for offset in range(num_pages)]
        for future in concurrent.futures.as_completed(futures):
            for hotel in future.result():
                hotel_id = (hotel["NameProperty"], hotel["RoomRate"])  # Clave para evitar elementos duplicados

                if hotel_id not in seen_hotels:
                    seen_hotels.add(hotel_id)
                    all_hotels.append({
                        # Booking
                        "PropertyId": np.nan,
                        "Property_BookingId": np.nan,
                        "BookingCreatedDate": "2024-10-26",
                        "ArrivalDate": "2024-11-20",
                        "DepartureDate": "2024-11-21",
                        "Adults": 1,
                        "Children": 0,
                        "Infants": 0,
                        "Persons": 1,
                        "NumNights": 1,
                        "Channel": "Booking.com",
                        "RoomRate": hotel["RoomRate"],
                        "CleaningFee": 0,
                        "Revenue": hotel["RoomRate"], # RoomRate × NumNights (1)
                        "ADR": hotel["RoomRate"], # Revenue / NumNights (1)
                        "TouristTax": hotel["TouristTax"],
                        "TotalPaid": hotel["RoomRate"] + hotel["TouristTax"],  # Revenue + TouristTax + CleaningFee (0)
                        # Propiedades
                        "RealProperty": "Yes",
                        "Capacity": 1,
                        "Square": float("nan"),
                        "PropertyType": "Hotel",
                        "NumBedrooms": 1,
                        "ReadyDate": "2024-11-20",
                        # Datos creados
                        "NameProperty": hotel["NameProperty"],
                        "Ubication": "Barcelona",
                        "Rating": hotel["Rating"]
                    })
    return all_hotels

start_time = time.time()
results = get_all_pages(num_pages=100)

# Guardando resultados
df = pd.DataFrame(results)
df.to_csv('booking_results.csv', index=False, encoding='utf-8-sig')
print(f"Total unique items: {len(results)}")
print(f"Time taken: {time.time() - start_time} seconds")