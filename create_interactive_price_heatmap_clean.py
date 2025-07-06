#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Price Heatmap Berlin Generator
==========================================

Generiert eine interaktive Folium-Karte mit Preis-Heatmap für Berlin.
Basierend auf dem Code aus 06_Geospatial_Analysis.ipynb.

Features:
- Preis-Farbkodierung (4 Kategorien basierend auf Quantilen)
- Jahresfilter mit separaten Layern
- Detaillierte Tooltips mit Preis, Bezirk, Wohnlage
- Groessenkodierung basierend auf Wohnungsgroesse
- Interaktive Legende und Layer-Kontrolle
- Clustering für bessere Performance
- Mehrere Kartenstile zur Auswahl
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import numpy as np
import random
import os
from pathlib import Path

# Konfiguration
OUTPUT_FILE = 'interactive_price_heatmap_berlin.html'
DATA_PATH = 'data/processed/berlin_housing_combined_final.csv'
SAMPLE_SIZE = 1000  # Max Punkte pro Jahr für Performance

# Bezirk-Koordinaten für Simulation (da keine echten Koordinaten verfügbar)
DISTRICT_COORDS = {
    'Mitte': [52.520, 13.405],
    'Friedrichshain': [52.515, 13.455],
    'Charlottenburg': [52.520, 13.295],
    'Pankow': [52.565, 13.405],
    'Neukoelln': [52.475, 13.435],
    'Schoeneberg': [52.485, 13.365],
    'Reinickendorf': [52.585, 13.335],
    'Zehlendorf': [52.435, 13.255],
    'Hellersdorf': [52.535, 13.595],
    'Spandau': [52.535, 13.195]
}

def load_data():
    """Lade und bereite Daten vor."""
    print("Lade Daten...")
    
    # Prüfe ob Datei existiert
    if not os.path.exists(DATA_PATH):
        print(f"Datei nicht gefunden: {DATA_PATH}")
        print("Verfügbare Dateien im data/processed/ Verzeichnis:")
        data_dir = Path('data/processed/')
        if data_dir.exists():
            for file in data_dir.glob('*.csv'):
                print(f"  {file.name}")
        else:
            print("  Verzeichnis data/processed/ nicht gefunden")
        return None
    
    # Lade Daten
    df = pd.read_csv(DATA_PATH)
    print(f"Daten geladen: {len(df):,} Zeilen")
    
    # Prüfe erforderliche Spalten
    required_cols = ['price', 'size', 'district', 'year']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Fehlende Spalten: {missing_cols}")
        print(f"Verfügbare Spalten: {list(df.columns)}")
        return None
    
    # Berechne Preis pro m²
    df['price_per_sqm'] = df['price'] / df['size']
    df['price_per_sqm'] = df['price_per_sqm'].replace([np.inf, -np.inf], np.nan)
    
    # Entferne Zeilen mit fehlenden Werten
    df = df.dropna(subset=['price', 'size', 'district'])
    
    print(f"Daten bereinigt: {len(df):,} Zeilen")
    print(f"  Zeitraum: {df['year'].min()} - {df['year'].max()}")
    print(f"  Bezirke: {df['district'].nunique()}")
    
    return df

def calculate_price_categories(df):
    """Berechne Preiskategorien basierend auf Quantilen."""
    print("Berechne Preiskategorien...")
    
    # Berechne Preis-Quantile für bessere Farbverteilung
    price_quantiles = df['price'].quantile([0.25, 0.5, 0.75]).values
    print(f"  Preis-Quantile: 25%={price_quantiles[0]:.0f}€, 50%={price_quantiles[1]:.0f}€, 75%={price_quantiles[2]:.0f}€")
    
    def get_price_color(price):
        if price <= price_quantiles[0]:
            return 'green'      # Guenstig (unterste 25%)
        elif price <= price_quantiles[1]:
            return 'lightgreen' # Guenstig-mittel (25-50%)
        elif price <= price_quantiles[2]:
            return 'orange'     # Mittel-teuer (50-75%)
        else:
            return 'red'        # Teuer (oberste 25%)
    
    def get_price_category(price):
        if price <= price_quantiles[0]:
            return 'Guenstig'
        elif price <= price_quantiles[1]:
            return 'Guenstig-Mittel'
        elif price <= price_quantiles[2]:
            return 'Mittel-Teuer'
        else:
            return 'Teuer'
    
    # Füge Farb- und Kategorie-Spalten hinzu
    df['price_color'] = df['price'].apply(get_price_color)
    df['price_category'] = df['price'].apply(get_price_category)
    
    return df, price_quantiles

def get_coordinates(district):
    """Simuliere Koordinaten basierend auf Bezirk."""
    if district in DISTRICT_COORDS:
        base_lat, base_lon = DISTRICT_COORDS[district]
    else:
        base_lat, base_lon = 52.52, 13.405  # Standard Berlin-Koordinaten
    
    # Füge zufällige Variation hinzu für Streuung
    lat = base_lat + random.uniform(-0.02, 0.02)
    lon = base_lon + random.uniform(-0.02, 0.02)
    
    return lat, lon

def get_marker_size(size):
    """Bestimme Marker-Größe basierend auf Wohnungsgröße."""
    if size <= 40:
        return 5
    elif size <= 80:
        return 7
    else:
        return 10

def create_tooltip(row):
    """Erstelle detaillierte Tooltip-Informationen."""
    tooltip_text = f"""
    <b>{row['price']:.0f}€</b> | {row['size']:.0f}m² | {row['price_per_sqm']:.1f}€/m²<br>
    <b>Kategorie:</b> {row['price_category']}<br>
    <b>Bezirk:</b> {row['district']}<br>
    <b>Jahr:</b> {row['year']}<br>
    """
    
    # Füge Zimmeranzahl hinzu falls verfügbar
    if 'rooms' in row and pd.notna(row['rooms']):
        tooltip_text += f"<b>Zimmer:</b> {row['rooms']}<br>"
    
    return tooltip_text

def create_legend(price_quantiles):
    """Erstelle HTML-Legende für Preiskategorien."""
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Preiskategorien</h4>
    <i class="fa fa-circle" style="color:green"></i> Guenstig (≤{price_quantiles[0]:.0f}€)<br>
    <i class="fa fa-circle" style="color:lightgreen"></i> Guenstig-Mittel ({price_quantiles[0]:.0f}-{price_quantiles[1]:.0f}€)<br>
    <i class="fa fa-circle" style="color:orange"></i> Mittel-Teuer ({price_quantiles[1]:.0f}-{price_quantiles[2]:.0f}€)<br>
    <i class="fa fa-circle" style="color:red"></i> Teuer (>{price_quantiles[2]:.0f}€)<br>
    </div>
    '''
    return legend_html

def create_interactive_map(df, price_quantiles):
    """Erstelle die interaktive Folium-Karte."""
    print("Erstelle interaktive Karte...")
    
    # Erstelle Basis-Karte mit explizit hellem Standard-Stil
    m = folium.Map(
        location=[52.52, 13.405], 
        zoom_start=11,
        tiles=None  # Keine automatischen Tiles
    )
    
    # Füge Tile-Layer manuell hinzu in der gewünschten Reihenfolge
    # Standard-Layer (wird als erstes und als Standard verwendet)
    folium.TileLayer(
        tiles='CartoDB positron',
        name='CartoDB Positron (Standard)',
        overlay=False,
        control=True,
        show=True  # Explizit als Standard anzeigen
    ).add_to(m)
    
    # Alternative Layers
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True,
        show=False
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='CartoDB Dark',
        overlay=False,
        control=True,
        show=False
    ).add_to(m)
    
    # Erstelle Layer für jedes Jahr
    years = sorted(df['year'].unique())
    print(f"  Erstelle Layer für Jahre: {years}")
    
    for year in years:
        year_data = df[df['year'] == year]
        print(f"    Jahr {year}: {len(year_data)} Angebote")
        
        # Erstelle Marker-Cluster für dieses Jahr
        marker_cluster = MarkerCluster(
            name=f'Angebote {year} ({len(year_data)} Stück)',
            overlay=True,
            control=True,
            show=True if year == years[-1] else False  # Nur letztes Jahr standardmäßig anzeigen
        ).add_to(m)
        
        # Erstelle Sample für bessere Performance
        if len(year_data) > SAMPLE_SIZE:
            year_data_sample = year_data.sample(n=SAMPLE_SIZE, random_state=42)
            print(f"      Sample erstellt: {len(year_data_sample)} Punkte")
        else:
            year_data_sample = year_data
        
        # Füge Marker für jede Immobilie hinzu
        for idx, row in year_data_sample.iterrows():
            # Simuliere Koordinaten
            lat, lon = get_coordinates(row['district'])
            
            # Bestimme Marker-Größe
            radius = get_marker_size(row['size'])
            
            # Erstelle Tooltip
            tooltip_text = create_tooltip(row)
            
            # Erstelle Marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                color='white',
                weight=1,
                fillColor=row['price_color'],
                fillOpacity=0.7,
                popup=tooltip_text,
                tooltip=f"{row['price']:.0f}€ | {row['district']}"
            ).add_to(marker_cluster)
    
    return m

def save_map(m, price_quantiles, output_path):
    """Speichere Karte mit Legende."""
    print("Speichere Karte...")
    
    # Füge Legende hinzu
    legend_html = create_legend(price_quantiles)
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Füge Layer-Kontrolle hinzu
    folium.LayerControl().add_to(m)
    
    # Speichere die Karte
    m.save(output_path)
    
    print(f"Karte gespeichert: {output_path}")

def main():
    """Hauptfunktion."""
    try:
        print("="*80)
        print("INTERACTIVE PRICE HEATMAP BERLIN GENERATOR")
        print("="*80)
        
        # Setze Random Seed für Reproduzierbarkeit
        random.seed(42)
        np.random.seed(42)
        
        # Lade Daten
        df = load_data()
        if df is None:
            return
        
        # Berechne Preiskategorien
        df, price_quantiles = calculate_price_categories(df)
        
        # Erstelle interaktive Karte
        m = create_interactive_map(df, price_quantiles)
        
        # Speichere Karte
        save_map(m, price_quantiles, OUTPUT_FILE)
        
        print(f"\nFEATURES DER GENERIERTEN KARTE:")
        print(f"  - Preis-Farbkodierung (4 Kategorien)")
        print(f"  - Jahresfilter mit separaten Layern")
        print(f"  - Detaillierte Tooltips mit Preis, Bezirk, Wohnlage")
        print(f"  - Groessenkodierung basierend auf Wohnungsgroesse")
        print(f"  - Interaktive Legende und Layer-Kontrolle")
        print(f"  - Clustering für bessere Performance")
        print(f"  - Mehrere Kartenstile zur Auswahl")
        
        print(f"\nERFOLGREICH ABGESCHLOSSEN!")
        print(f"Oeffne '{OUTPUT_FILE}' in deinem Browser.")
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
