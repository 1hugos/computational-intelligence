import random
import math
import matplotlib.pyplot as plt
import sys
import copy
from sklearn.cluster import KMeans

# --- Parametry symulacji (bez zmian) ---
NUM_CLIENTS = random.randint(3, 30)
NUM_VEHICLES = random.randint(3, 6)
NUM_WAREHOUSES = 5
MAP_RANGE = (0, 100)
VEHICLE_CAPACITIES = {"zielony": 1000, "niebieski": 1500, "czerwony": 2000}

# --- Funkcje pomocnicze (bez zmian) ---
def calculate_distance(point1, point2):
    return math.sqrt((point1["x"] - point2["x"]) ** 2 + (point1["y"] - point2["y"]) ** 2)

def find_nearest_warehouse(current_location):
    best_distance = sys.float_info.max
    nearest_warehouse = None
    for warehouse in warehouses:
        distance = calculate_distance(current_location, warehouse)
        if distance < best_distance:
            best_distance = distance
            nearest_warehouse = warehouse
    return nearest_warehouse, best_distance

def vehicle_can_service_client(vehicle, client):
    if client["demand"] > 0:
        return vehicle["current_load"] >= client["demand"]
    elif client["demand"] < 0:
        return vehicle["current_load"] + abs(client["demand"]) <= vehicle["capacity"]
    return True

# --- Generowanie Danych ---
# 1. Generowanie magazynów
warehouses = []
for i in range(NUM_WAREHOUSES):
    warehouses.append({"id": f"M{i+1}", "x": random.randint(*MAP_RANGE), "y": random.randint(*MAP_RANGE)})
print(f"Wygenerowano {len(warehouses)} magazynów.")

# 2. Generowanie klientów
clients = []
for i in range(NUM_CLIENTS):
    demand = random.randint(100, 200)
    if random.random() < 0.5:
        demand *= -1
    clients.append({"id": f"K{i+1}", "x": random.randint(*MAP_RANGE), "y": random.randint(*MAP_RANGE), "demand": demand, "serviced": False})
print(f"Wygenerowano {len(clients)} klientów.")

# 3. Generowanie pojazdów
vehicles = []
vehicle_types = list(VEHICLE_CAPACITIES.keys())
for i in range(NUM_VEHICLES):
    vehicle_type = random.choice(vehicle_types)
    capacity = VEHICLE_CAPACITIES[vehicle_type]
    start_warehouse = random.choice(warehouses)
    vehicles.append({
        "id": f"P{i+1}", "type": vehicle_type, "capacity": capacity,
        "current_load": capacity // 2, "location": start_warehouse.copy(),
        "start_warehouse_id": start_warehouse["id"], "route": [start_warehouse.copy()],
        "distance_traveled": 0.0
    })
print(f"\nWygenerowano {len(vehicles)} pojazdów.")

# Szczegółowe informacje o klientach i pojazdach
print("\n--- Dane początkowe klientów ---")
for client in clients:
    action = "Dostawa" if client['demand'] > 0 else "Odbiór"
    print(f"ID: {client['id']}, Zapotrzebowanie: {abs(client['demand'])}kg ({action})")

print("\n--- Dane początkowe pojazdów ---")
for vehicle in vehicles:
    print(f"ID: {vehicle['id']}, Typ: {vehicle['type']}, Pojemność: {vehicle['capacity']}kg, "
          f"Aktualny ładunek: {vehicle['current_load']}kg, Magazyn startowy: {vehicle['start_warehouse_id']}")

# --- Wizualizacja Początkowego Scenariusza ---
print("\n--- Generowanie wizualizacji początkowej scenariusza... ---")
plt.figure(figsize=(12, 9))
plt.title("Początkowe rozmieszczenie magazynów i klientów")

warehouse_x = [w["x"] for w in warehouses]
warehouse_y = [w["y"] for w in warehouses]
plt.scatter(warehouse_x, warehouse_y, c="black", marker="s", s=150, label="Magazyny", zorder=5)
for w in warehouses:
    plt.text(w["x"] + 1, w["y"] + 1, w["id"])

clients_delivery = [c for c in clients if c["demand"] > 0]
clients_pickup = [c for c in clients if c["demand"] < 0]
if clients_delivery:
    plt.scatter([c["x"] for c in clients_delivery], [c["y"] for c in clients_delivery], c="green", marker="o", s=50, label="Klienci (dostawa)")
if clients_pickup:
    plt.scatter([c["x"] for c in clients_pickup], [c["y"] for c in clients_pickup], c="red", marker="o", s=50, label="Klienci (odbiór)")
for c in clients:
    plt.text(c["x"] + 1, c["y"] + 1, c["id"])

plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.xlim(MAP_RANGE[0] - 5, MAP_RANGE[1] + 5)
plt.ylim(MAP_RANGE[0] - 5, MAP_RANGE[1] + 5)
plt.show()
print("Wykres został wygenerowany i wyświetlony.")

# ==============================================================================
# ETAP 1: KLASTERYZACJA KLIENTÓW
# ==============================================================================
print("\n--- ETAP 1: Klasteryzacja klientów (K-Means)... ---")
if NUM_CLIENTS >= NUM_VEHICLES:
    client_coords = [[c['x'], c['y']] for c in clients]
    kmeans = KMeans(n_clusters=NUM_VEHICLES, random_state=42, n_init=10)
    kmeans.fit(client_coords)
    for i, client in enumerate(clients):
        client['cluster'] = kmeans.labels_[i]
    print("Klienci zostali podzieleni na klastry.")

    # --- Wizualizacja Klastrów ---
    plt.figure(figsize=(12, 9))
    plt.title("Podział klientów na klastry")
    
    plt.scatter([c[0] for c in client_coords], [c[1] for c in client_coords], c=kmeans.labels_, cmap='viridis', marker='o', label='Klienci')
    for c in clients:
        plt.text(c['x'] - 2, c['y'] - 2.5, c['id'], fontsize=8)
    
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=250, alpha=0.6, marker='X', label='Centra klastrów')
    
    plt.scatter(warehouse_x, warehouse_y, c="black", marker="s", s=150, label="Magazyny", zorder=5)
    for w in warehouses:
        plt.text(w["x"] + 1, w["y"] + 1, w["id"])
    
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xlim(MAP_RANGE[0] - 5, MAP_RANGE[1] + 5)
    plt.ylim(MAP_RANGE[0] - 5, MAP_RANGE[1] + 5)
    plt.show()
else:
    print("Liczba klientów mniejsza niż liczba pojazdów, pomijam klasteryzację.")
    for i, client in enumerate(clients):
        client['cluster'] = i
    centroids = [[c['x'], c['y']] for c in clients]


# ==============================================================================
# ETAP 2: WYZNACZANIE TRAS DLA KAŻDEGO KLASTRA
# ==============================================================================
print("\n--- ETAP 2: Wyznaczanie tras dla każdego pojazdu w jego klastrze... ---")
vehicles_copy = copy.deepcopy(vehicles)
num_clusters = NUM_VEHICLES if NUM_CLIENTS >= NUM_VEHICLES else NUM_CLIENTS
unassigned_clusters = list(range(num_clusters))
vehicle_assignments = {}
assigned_vehicles = []

for _ in range(num_clusters):
    best_vehicle, best_cluster, min_dist = None, None, sys.float_info.max
    
    current_vehicle = next((v for v in vehicles if v['id'] not in assigned_vehicles), None)
    if not current_vehicle: break

    for cluster_id in unassigned_clusters:
        dist = calculate_distance(current_vehicle['location'], {'x': centroids[cluster_id][0], 'y': centroids[cluster_id][1]})
        if dist < min_dist:
            min_dist, best_cluster = dist, cluster_id
            
    if best_cluster is not None:
        vehicle_assignments[current_vehicle['id']] = best_cluster
        assigned_vehicles.append(current_vehicle['id'])
        unassigned_clusters.remove(best_cluster)

# --- Główna pętla symulacji ---
for vehicle in vehicles:
    cluster_id = vehicle_assignments.get(vehicle['id'])
    if cluster_id is None:
        print(f"Pojazd {vehicle['id']} nie ma przypisanego klastra i nie wykonuje trasy.")
        continue

    clients_in_cluster = [c for c in clients if c.get('cluster') == cluster_id]
    num_clients_in_cluster = len(clients_in_cluster)
    print(f"\n--- Przetwarzanie trasy dla Pojazdu {vehicle['id']} w Klastrze {cluster_id} ({num_clients_in_cluster} klientów) ---")

    while any(not c['serviced'] for c in clients_in_cluster):
        best_client, min_distance = None, sys.float_info.max
        for client in clients_in_cluster:
            if not client['serviced'] and vehicle_can_service_client(vehicle, client):
                distance = calculate_distance(vehicle['location'], client)
                if distance < min_distance:
                    min_distance, best_client = distance, client
        
        if best_client:
            # Aktualizacje danych pojazdu i klienta
            vehicle['distance_traveled'] += min_distance
            vehicle['location'] = best_client
            vehicle['current_load'] -= best_client['demand']
            vehicle['route'].append(best_client)
            best_client['serviced'] = True
            
            # POPRAWKA: Ulepszony, bardziej opisowy format logowania
            action_desc = "odebrał" if best_client['demand'] < 0 else "dostarczył"

            print(
                f"Pojazd {vehicle['id']} ({vehicle['type']}) obsłużył klienta {best_client['id']} "
                f"({action_desc} {abs(best_client['demand'])} kg towaru). "
                f"Aktualny ładunek: {vehicle['current_load']}/{vehicle['capacity']} kg."
            )
        else:
            if any(not c['serviced'] for c in clients_in_cluster):
                action_at_warehouse = "Pobranie towaru"
                new_load = vehicle['capacity']
                if vehicle['current_load'] > vehicle['capacity'] * 0.75:
                    action_at_warehouse = "Zrzucenie towaru"
                    new_load = 0
                                
                nearest_warehouse, dist = find_nearest_warehouse(vehicle['location'])
                vehicle['distance_traveled'] += dist
                vehicle['location'] = nearest_warehouse
                vehicle['route'].append(nearest_warehouse)
                vehicle['current_load'] = new_load
                
                # POPRAWKA: Bardziej opisowy format logowania powrotu do magazynu
                print(
                    f"Pojazd {vehicle['id']} ({vehicle['type']}) nie może obsłużyć klienta, wraca do magazynu {nearest_warehouse['id']}. "
                    f"Akcja: {action_at_warehouse}. Nowy ładunek: {vehicle['current_load']}/{vehicle['capacity']} kg."
                )
            else:
                break

print("\n\n--- Symulacja zakończona! ---")

# --- Podsumowanie i Wizualizacja Końcowa ---
total_distance = 0
print("\n--- Podsumowanie tras ---")
for vehicle in vehicles:
    if len(vehicle['route']) > 1:
        final_destination, distance_to_base = find_nearest_warehouse(vehicle["location"])
        vehicle["distance_traveled"] += distance_to_base
        vehicle["route"].append(final_destination)
    
    route_str = " -> ".join([p["id"] for p in vehicle["route"]])
    print(f"\nTrasa dla pojazdu {vehicle['id']} ({vehicle['type']}):\n{route_str}")
    print(f"Dystans pokonany: {vehicle['distance_traveled']:.2f} km")
    total_distance += vehicle['distance_traveled']

print(f"\nŁĄCZNY DYSTANS POKONANY PRZEZ WSZYSTKIE POJAZDY: {total_distance:.2f} km")

# Wizualizacja tras
plt.figure(figsize=(12, 9))
plt.title("Końcowe rozwiązanie - trasy pojazdów (Cluster-First)")
route_colors = {'czerwony': 'red', 'niebieski': 'blue', 'zielony': 'green'}

plt.scatter([w['x'] for w in warehouses], [w['y'] for w in warehouses], c='black', marker='s', s=150, label='Magazyny', zorder=5)
for w in warehouses:
    plt.text(w['x'] + 1, w['y'] + 1, w['id'])

if NUM_CLIENTS >= NUM_VEHICLES:
    plt.scatter([c['x'] for c in clients], [c['y'] for c in clients], c=[c.get('cluster', -1) for c in clients], cmap='viridis', marker='o', alpha=0.7)
else:
    plt.scatter([c['x'] for c in clients], [c['y'] for c in clients], c='purple', marker='o', alpha=0.7)
    
for c in clients:
    plt.text(c['x'] - 2, c['y'] - 2.5, c['id'], fontsize=8)

for vehicle in vehicles:
    if len(vehicle['route']) > 1:
        route_x = [p['x'] for p in vehicle['route']]
        route_y = [p['y'] for p in vehicle['route']]
        plt.plot(route_x, route_y, color=route_colors.get(vehicle['type'], 'gray'), linestyle='--', marker='>', markersize=4, label=f"Trasa {vehicle['id']}")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.xlim(MAP_RANGE[0] - 5, MAP_RANGE[1] + 5)
plt.ylim(MAP_RANGE[0] - 5, MAP_RANGE[1] + 5)
plt.show()

