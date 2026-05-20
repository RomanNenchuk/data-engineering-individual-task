from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

# Визначаємо базові шляхи відносно розташування цього скрипта (папка src)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

def run_clustering(input_filepath: Path, output_filepath: Path, distance_km: float = 50.0, min_hospitals: int = 5):
    print("Крок 1: Завантаження очищених даних...")
    df = pd.read_csv(input_filepath)
    
    print("Крок 2: Підготовка просторових даних (перевід у радіани)...")
    coords = np.radians(df[['LATITUDE', 'LONGITUDE']].values)
    
    print("Крок 3: Налаштування та запуск DBSCAN...")
    EARTH_RADIUS_KM = 6371.0088
    epsilon = distance_km / EARTH_RADIUS_KM
    
    db = DBSCAN(eps=epsilon, min_samples=min_hospitals, metric='haversine', n_jobs=-1)
    df['CLUSTER'] = db.fit_predict(coords)
    
    num_clusters = len(set(df['CLUSTER'])) - (1 if -1 in df['CLUSTER'] else 0)
    num_noise = list(df['CLUSTER']).count(-1)
    
    print(f"Знайдено кластерів (медичних хабів): {num_clusters}")
    print(f"Кількість лікарень, що визначені як шум (ізольовані): {num_noise}")
    
    print("Крок 4: Збереження результатів...")
    # Створюємо директорію для вихідного файлу, якщо її немає (.parent повертає шлях до папки файлу)
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_filepath, index=False)
    print(f"Результати кластеризації збережено у: {output_filepath}\n")

if __name__ == "__main__":
    # Шляхи будуються динамічно від кореня проєкту
    CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_hospitals.csv"
    CLUSTERED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clustered_hospitals.csv"
    
    run_clustering(CLEAN_DATA_PATH, CLUSTERED_DATA_PATH, distance_km=15.0, min_hospitals=7)
