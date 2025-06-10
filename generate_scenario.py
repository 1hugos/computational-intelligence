import random
import math

# --- Parametry symulacji ---
NUM_CLIENTS = 25
NUM_VEHICLES = 4  # Zgodnie z wymaganiami: od 3 do 6 pojazdów 
NUM_WAREHOUSES = 5  # Zgodnie z wymaganiami na ocenę dobrą 
MAP_RANGE = (0, 100) # Zakres dla współrzędnych x oraz y 

# Definicja typów pojazdów i ich pojemności 
VEHICLE_CAPACITIES = {
    'zielony': 1000,
    'niebieski': 1500,
    'czerwony': 2000
}

# --- Funkcje pomocnicze ---
def calculate_distance(point1, point2):
    """Oblicza odległość euklidesową między dwoma punktami."""
    return math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)

# --- Generowanie danych ---

# 1. Generowanie magazynów
warehouses = []
for i in range(NUM_WAREHOUSES):
    warehouse = {
        'id': f"M{i+1}",
        'x': random.randint(*MAP_RANGE),
        'y': random.randint(*MAP_RANGE)
    }
    warehouses.append(warehouse)
print(f"✅ Wygenerowano {len(warehouses)} magazynów.")


# 2. Generowanie klientów z losowym zapotrzebowaniem
clients = []
for i in range(NUM_CLIENTS):
    # Losowanie wielkości towaru do dostarczenia lub odebrania (pomiędzy 100kg a 200kg) 
    demand = random.randint(100, 200)
    # Losowe określenie, czy to dostawa (dodatnie) czy odbiór (ujemne)
    if random.random() < 0.5:
        demand *= -1

    client = {
        'id': f"K{i+1}",
        'x': random.randint(*MAP_RANGE),
        'y': random.randint(*MAP_RANGE),
        'demand': demand, # >0: dostawa, <0: odbiór
        'serviced': False
    }
    clients.append(client)
print(f"✅ Wygenerowano {len(clients)} klientów.")


# 3. Generowanie pojazdów i przypisanie do magazynów
vehicles = []
vehicle_types = list(VEHICLE_CAPACITIES.keys())

for i in range(NUM_VEHICLES):
    vehicle_type = random.choice(vehicle_types)
    capacity = VEHICLE_CAPACITIES[vehicle_type]
    # Początkowe położenie pojazdów jest losowo przypisane do jednego z magazynów 
    start_warehouse = random.choice(warehouses)

    vehicle = {
        'id': f"P{i+1}",
        'type': vehicle_type,
        'capacity': capacity,
        'current_load': 0, # Pojazdy startują puste
        'location': start_warehouse.copy(), # Aktualna pozycja pojazdu
        'start_warehouse_id': start_warehouse['id'],
        'route': [start_warehouse.copy()], # Trasa zaczyna się w magazynie
        'distance_traveled': 0.0
    }
    vehicles.append(vehicle)
print(f"✅ Wygenerowano {len(vehicles)} pojazdów.")

# --- Wyświetlenie przykładowych wygenerowanych danych ---
print("\n--- Przykładowe dane ---")
print("\nMagazyn:", warehouses[0])
print("\nKlient:", clients[0])
print("\nPojazd:", vehicles[0])