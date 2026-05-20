from pathlib import Path
import pandas as pd
import numpy as np

# Визначаємо базові шляхи відносно розташування цього скрипта (папка src)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

def run_etl(input_filepath: Path, output_filepath: Path):
    print("Крок 1: Extract (Отримання даних)...")
    df = pd.read_csv(input_filepath)
    print(f"Завантажено рядків: {len(df)}")

    print("Крок 2: Transform (Очищення та трансформація)...")
    df = df[df['STATUS'] == 'OPEN']
    
    columns_to_keep = [
        'ID', 'NAME', 'CITY', 'STATE', 'TYPE', 
        'LATITUDE', 'LONGITUDE', 'BEDS', 'POPULATION'
    ]
    df = df[columns_to_keep]
    
    df['BEDS'] = df['BEDS'].replace(-999, np.nan)
    df['POPULATION'] = df['POPULATION'].replace(-999, np.nan)
    df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
    
    print(f"Залишилось рядків після очищення: {len(df)}")

    print("Крок 3: Load (Завантаження очищених даних)...")
    # Створюємо батьківську директорію для вихідного файлу
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_filepath, index=False)
    print(f"Очищені дані збережено у: {output_filepath}\n")

if __name__ == "__main__":
    # Шляхи конструюються незалежно від CWD
    RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "hospitals.csv"
    CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_hospitals.csv"

    run_etl(RAW_DATA_PATH, CLEAN_DATA_PATH)
