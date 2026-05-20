from pathlib import Path
import pandas as pd
import folium
import numpy as np
from scipy.spatial import ConvexHull

# Визначаємо базові шляхи
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

def generate_bi_map(input_filepath: Path, output_filepath: Path):
    print("Крок 1: Читання результатів кластеризації...")
    df = pd.read_csv(input_filepath)
    
    print("Крок 2: Ініціалізація карти...")
    us_center_lat, us_center_lon = 37.0902, -95.7129
    m = folium.Map(location=[us_center_lat, us_center_lon], zoom_start=4, tiles="OpenStreetMap")
    
    # Яскрава палітра кольорів для відмінності хабів між собою
    colors = [
        'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 
        'darkpurple', 'darkgreen', 'lightblue', 'chocolate', 'deepskyblue'
    ]
    
    print("Крок 3: Побудова математичних зон кластерів (Convex Hull)...")
    unique_clusters = df['CLUSTER'].unique()
    
    for cluster_id in unique_clusters:
        if cluster_id == -1:
            continue # Шум не має спільної зони, це ізольовані точки
            
        cluster_data = df[df['CLUSTER'] == cluster_id]
        points = cluster_data[['LATITUDE', 'LONGITUDE']].values
        
        # Вибираємо колір для цього хабу
        cluster_color = colors[int(cluster_id) % len(colors)]
        
        # Опуклу оболонку можна побудувати, якщо є хоча б 3 унікальні точки
        if len(np.unique(points, axis=0)) >= 3:
            try:
                hull = ConvexHull(points)
                # Отримуємо координати вершин полігону
                hull_vertices = points[hull.vertices]
                
                # Малюємо зону хабу на карті
                folium.Polygon(
                    locations=hull_vertices.tolist(),
                    color=cluster_color,
                    fill=True,
                    fill_color=cluster_color,
                    fill_opacity=0.15,
                    weight=2,
                    popup=f"<b>Зона медичного хабу №{cluster_id}</b><br>Об'єднує заклади в радіусі 50 км.<br>Всього лікарень: {len(cluster_data)}"
                ).add_to(m)
            except Exception as e:
                print(f"Пропущено побудову полігону для хабу {cluster_id}: {e}")

    print("Крок 4: Нанесення лікарень як статичних точок...")
    for _, row in df.iterrows():
        cluster_id = row['CLUSTER']
        
        if cluster_id == -1:
            color = 'red'          # Червоний колір для ізольованих об'єктів (шуму)
            radius = 2.5
            popup_status = "<b>Статус:</b> Ізольований об'єкт (Шум DBSCAN)"
        else:
            color = colors[int(cluster_id) % len(colors)]
            radius = 3.5
            popup_status = f"<b>Статус:</b> Входить у медичний хаб №{int(cluster_id)}"
            
        popup_html = f"""
        <div style='font-family: sans-serif; font-size: 11px; width: 180px;'>
            <b>Назва:</b> {row['NAME']}<br>
            <b>Місто:</b> {row['CITY']}<br>
            <b>Тип:</b> {row['TYPE']}<br>
            <b>Ліжка:</b> {row['BEDS'] if pd.notna(row['BEDS']) else 'Немає даних'}<br>
            {popup_status}
        </div>
        """
        
        # Додаємо легку точку, яка тримає своє місце при будь-якому масштабі
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=220)
        ).add_to(m)
        
    print("Крок 5: Збереження фінальної BI-карти...")
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_filepath))
    print(f"Логічну карту з реальними зонами успішно збережено у: {output_filepath}\n")

if __name__ == "__main__":
    INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clustered_hospitals.csv"
    OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "medical_infrastructure_map.html"
    
    generate_bi_map(INPUT_FILE, OUTPUT_FILE)
