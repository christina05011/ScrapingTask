import pandas as pd
import numpy as np

### Limpiando datos de archivo 'Properties.csv'
properties = pd.read_csv('Properties.csv', encoding='utf-8')
#print(len(properties))

# Filtrando datos
clean_properties = properties[(properties["RealProperty"] == "Yes") &  
                              (properties["Capacity"] > 0) &
                              (properties["Square"] > 0) &
                              (properties["NumBedrooms"] > 0)].copy()

# Estandarizando datos
clean_properties["PropertyType"] = clean_properties["PropertyType"].replace({"Apa": "Apartment"}).fillna("Unknown")
clean_properties["ReadyDate"] = pd.to_datetime(clean_properties["ReadyDate"]).dt.date
clean_properties = clean_properties.drop_duplicates()
#print(len(clean_properties))
# Opcional: Guardar el resultado en un nuevo archivo CSV limpio
clean_properties.to_csv('Clean_Properties.csv', index=False, encoding='utf-8')

# Verificar valores unicos por columna
# unique_values = properties["PropertyId"].unique()
# print("Valores únicos:", unique_values)

# -----------------

### Limpiando datos de archivo 'Bookings.csv'
bookings = pd.read_csv('Bookings.csv', encoding='utf-8')
bookings_property_id = bookings["PropertyId"]
#print(len(bookings_property_id))

clean_bookings = bookings[(bookings["Adults"] + bookings["Children"] + bookings["Infants"] > 0) & 
                              (bookings["NumNights"] > 0) & 
                              (bookings["RoomRate"] > 0) & 
                              (bookings["RoomRate"].notna())].copy()

# Función para formatear fecha
def parse_date(date_str):
    try:
        return pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return pd.to_datetime(date_str, format="%d/%m/%Y")
        except ValueError:
            return pd.NaT

clean_bookings["BookingCreatedDate"] = clean_bookings["BookingCreatedDate"].apply(parse_date)
clean_bookings["BookingCreatedDate"] = clean_bookings["BookingCreatedDate"].dt.date
clean_bookings["ArrivalDate"] = pd.to_datetime(clean_bookings["ArrivalDate"]).dt.date
clean_bookings["DepartureDate"] = pd.to_datetime(clean_bookings["DepartureDate"]).dt.date
clean_bookings["Persons"] = clean_bookings["Adults"] + clean_bookings["Children"] + clean_bookings["Infants"]
clean_bookings["Channel"] = clean_bookings["Channel"].fillna("Unknown")
clean_bookings["CleaningFee"] = clean_bookings["CleaningFee"].fillna(0.0).apply(lambda x: max(x, 0.0))
clean_bookings["Revenue"] = (clean_bookings["RoomRate"] * clean_bookings["NumNights"]).round(2) # RoomRate × NumNights
clean_bookings["ADR"] = (clean_bookings["Revenue"] / clean_bookings["NumNights"]).round(2) # Revenue / NumNights
clean_bookings["TouristTax"] = clean_bookings["TouristTax"].fillna(0.0).apply(lambda x: max(x, 0.0))
clean_bookings["TotalPaid"] = (clean_bookings["Revenue"] + clean_bookings["TouristTax"] + clean_bookings["CleaningFee"]).round(2) # Revenue + TouristTax + CleaningFee

clean_bookings = clean_bookings[
    (clean_bookings["BookingCreatedDate"] <= clean_bookings["ArrivalDate"]) &
    (clean_bookings["ArrivalDate"] <= clean_bookings["DepartureDate"])
]

clean_bookings = clean_bookings.drop_duplicates()
#print(len(clean_bookings))
# Opcional: Guardar el resultado en un nuevo archivo CSV limpio
clean_bookings.to_csv('clean_bookings.csv', index=False, encoding='utf-8')

# -----------------

### Unir todos los archivos
# Realiza un merge por la columna de 'PropertyId' en ambos archivos
merged_data = clean_bookings.merge(clean_properties, on='PropertyId', how='inner')

# Filtrar datos de acuerdo a los datos unidos
final_data = merged_data[
    (merged_data["Persons"] <= merged_data["Capacity"]) & 
    (merged_data["ArrivalDate"] >= merged_data["ReadyDate"])
]

# Se agregan datos extras en archivo 'scraping.py'
final_data = final_data.assign(
    NameProperty="Unknown",
    Ubication="Barcelona",
    Rating=np.nan
)

# Reorganizar columnas como en archivo 'scraping.py'
columns_to_keep = [
    # Booking
    "PropertyId",
    "Property_BookingId",
    "BookingCreatedDate",
    "ArrivalDate",
    "DepartureDate",
    "Adults",
    "Children",
    "Infants",
    "Persons",
    "NumNights",
    "Channel",
    "RoomRate",
    "CleaningFee",
    "Revenue",
    "ADR",
    "TouristTax",
    "TotalPaid",
    # Propiedades
    "RealProperty",
    "Capacity",
    "Square",
    "PropertyType",
    "NumBedrooms",
    "ReadyDate",
    # Datos creados
    "NameProperty",
    "Ubication",
    "Rating"
]

final_data = final_data[columns_to_keep]

# Leer datos creados en 'scraping.py'
booking_results = pd.read_csv('booking_results.csv', encoding='utf-8')
# Unir todos los datos
join_data = final_data.to_dict(orient='records') + booking_results.to_dict(orient='records')
join_data_df = pd.DataFrame(join_data)
join_data_df.to_csv('joined_data.csv', index=False, encoding='utf-8-sig')