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
from folium.plugins import MarkerCluster, TimeSliderChoropleth
import numpy as np
import random
import os
from pathlib import Path
import datetime

# Versuche geopandas zu importieren
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    print("⚠️  GeoPandas nicht verfügbar. Choropleth-Features werden deaktiviert.")
    print("   Installiere mit: pip install geopandas")
    GEOPANDAS_AVAILABLE = False

import json

# Konfiguration
OUTPUT_FILE = 'interactive_price_heatmap_berlin.html'
DATA_PATH = 'data/processed/berlin_housing_combined_enriched_final.csv'
GEOJSON_PATH = 'data/raw/lor_ortsteile.geojson'
SAMPLE_SIZE = 1000  # Max Punkte pro Jahr für Performance
DEBUG_COORDS = False  # Setze auf True für Debug-Output der Koordinaten
ENABLE_CHOROPLETH = True and GEOPANDAS_AVAILABLE  # Aktiviere Choropleth-Layer basierend auf Ortsteilen

# Bezirk-Koordinaten für Simulation (komplette Berliner Bezirke)
DISTRICT_COORDS = {
    # Offizielle Berliner Bezirke
    'Mitte': [52.520, 13.405],
    'Friedrichshain-Kreuzberg': [52.515, 13.455],
    'Charlottenburg-Wilmersdorf': [52.520, 13.295],
    'Pankow': [52.565, 13.405],
    'Neukölln': [52.475, 13.435],
    'Tempelhof-Schöneberg': [52.485, 13.365],
    'Reinickendorf': [52.585, 13.335],
    'Steglitz-Zehlendorf': [52.435, 13.255],
    'Marzahn-Hellersdorf': [52.535, 13.595],
    'Spandau': [52.535, 13.195],
    'Lichtenberg': [52.545, 13.485],
    'Treptow-Köpenick': [52.455, 13.575],
    
    # Alte/alternative Schreibweisen
    'Friedrichshain': [52.515, 13.455],
    'Kreuzberg': [52.500, 13.420],
    'Charlottenburg': [52.520, 13.295],
    'Wilmersdorf': [52.495, 13.315],
    'Schöneberg': [52.485, 13.365],
    'Tempelhof': [52.465, 13.385],
    'Zehlendorf': [52.435, 13.255],
    'Steglitz': [52.455, 13.315],
    'Hellersdorf': [52.535, 13.595],
    'Marzahn': [52.545, 13.545],
    'Köpenick': [52.455, 13.575],
    'Treptow': [52.485, 13.515],
    
    # Häufige Varianten
    'Neukoelln': [52.475, 13.435],
    'Tempelhof-Schoeneberg': [52.485, 13.365],
    'Steglitz-Zehlendorf': [52.435, 13.255],
    'Marzahn-Hellersdorf': [52.535, 13.595],
    'Treptow-Koepenick': [52.455, 13.575],
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
    
    # Lade Daten mit korrekten PLZ-Typ
    df = pd.read_csv(DATA_PATH, dtype={'plz': 'string'})
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
    
    print(f"✅ Daten bereinigt: {len(df):,} Zeilen")
    print(f"   • Zeitraum: {df['year'].min()} - {df['year'].max()}")
    print(f"   • Bezirke: {df['district'].nunique()}")
    
    # Check PLZ and coordinate coverage
    if 'plz' in df.columns:
        plz_count = df['plz'].count()
        plz_pct = (plz_count / len(df)) * 100
        print(f"   • PLZ-Abdeckung: {plz_count:,}/{len(df):,} ({plz_pct:.1f}%)")
    
    if 'lat' in df.columns and 'lon' in df.columns:
        coords_count = df[['lat', 'lon']].dropna().shape[0]
        coords_pct = (coords_count / len(df)) * 100
        print(f"   • Koordinaten-Abdeckung: {coords_count:,}/{len(df):,} ({coords_pct:.1f}%)")
    
    # Debug: Zeige alle eindeutigen Bezirke
    unique_districts = sorted(df['district'].unique())
    print(f"   • Eindeutige Bezirke in Daten: {unique_districts[:10]}...")  # Zeige erste 10
    
    # Debug: Zeige welche Bezirke NICHT in DISTRICT_COORDS sind
    missing_coords = [d for d in unique_districts if d not in DISTRICT_COORDS]
    if missing_coords:
        print(f"   • Bezirke OHNE Koordinaten: {missing_coords[:10]}...")  # Zeige erste 10
    
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

def get_coordinates(row):
    """Verwende echte Koordinaten aus dem Dataset oder fallback zu simulierten Koordinaten."""
    # Prüfe ob echte Koordinaten verfügbar sind
    if 'lat' in row and 'lon' in row and pd.notna(row['lat']) and pd.notna(row['lon']):
        lat, lon = row['lat'], row['lon']
        if DEBUG_COORDS:
            district = row.get('district', 'N/A')
            plz = row.get('plz', 'N/A')
            print(f"    DEBUG: Echte Koordinaten für '{district}' (PLZ: {plz}): {lat}, {lon}")
        return lat, lon
    
    # Fallback zu simulierten Koordinaten basierend auf Bezirk
    district = row.get('district', 'Unknown')
    if district in DISTRICT_COORDS:
        base_lat, base_lon = DISTRICT_COORDS[district]
        if DEBUG_COORDS:
            print(f"    DEBUG: Simulierte Koordinaten für '{district}': {base_lat}, {base_lon}")
    else:
        base_lat, base_lon = 52.52, 13.405  # Standard Berlin-Koordinaten
        if DEBUG_COORDS:
            print(f"    DEBUG: Bezirk '{district}' -> NICHT in DISTRICT_COORDS! Verwende Standard-Koordinaten.")
    
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
    """Erstelle detaillierte Tooltip-Informationen mit PLZ- und Ortsdaten."""
    # Erstelle eindeutige ID (Index verwenden)
    unique_id = f"ID_{row.name}" if hasattr(row, 'name') else f"ID_{hash(str(row))}"
    
    tooltip_text = f"""
    <b>{row['price']:.0f}€</b> | {row['size']:.0f}m² | {row['price_per_sqm']:.1f}€/m²<br>
    <b>Kategorie:</b> {row['price_category']}<br>
    <b>Bezirk:</b> {row['district']}<br>
    """
    
    # Füge PLZ hinzu falls verfügbar
    if 'plz' in row and pd.notna(row['plz']):
        tooltip_text += f"<b>PLZ:</b> {row['plz']}<br>"
    
    # Füge Ortsteil hinzu falls verfügbar
    if 'ortsteil' in row and pd.notna(row['ortsteil']):
        tooltip_text += f"<b>Ortsteil:</b> {row['ortsteil']}<br>"
    
    # Füge Wohnlage hinzu falls verfügbar
    if 'wol' in row and pd.notna(row['wol']):
        tooltip_text += f"<b>Wohnlage:</b> {row['wol']}<br>"
    
    tooltip_text += f"<b>Jahr:</b> {row['year']}<br>"
    
    # Füge Zimmeranzahl hinzu falls verfügbar
    if 'rooms' in row and pd.notna(row['rooms']):
        tooltip_text += f"<b>Zimmer:</b> {row['rooms']}<br>"
    
    # Füge Koordinaten-Info hinzu
    if 'lat' in row and 'lon' in row and pd.notna(row['lat']) and pd.notna(row['lon']):
        tooltip_text += f"<b>Koordinaten:</b> {row['lat']:.3f}, {row['lon']:.3f}<br>"
    
    # Debug-Informationen
    tooltip_text += f"<b>Debug-ID:</b> {unique_id}<br>"
    tooltip_text += f"<b>Dataset:</b> {row.get('dataset_id', 'N/A')}<br>"
    tooltip_text += f"<b>Quelle:</b> {row.get('source', 'N/A')}<br>"
    
    return tooltip_text
    
    return tooltip_text

def create_legend(price_quantiles, df=None):
    """Erstelle HTML-Legende für Preiskategorien und Zeitstrahl-Info."""
    
    # Basis-Legende für Preiskategorien
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px; border-radius: 5px;">
    <h4 style="margin: 0 0 10px 0;">Preiskategorien</h4>
    <div style="margin-bottom: 5px;">
        <i class="fa fa-circle" style="color:green"></i> Guenstig (≤{price_quantiles[0]:.0f}€)
    </div>
    <div style="margin-bottom: 5px;">
        <i class="fa fa-circle" style="color:lightgreen"></i> Guenstig-Mittel ({price_quantiles[0]:.0f}-{price_quantiles[1]:.0f}€)
    </div>
    <div style="margin-bottom: 5px;">
        <i class="fa fa-circle" style="color:orange"></i> Mittel-Teuer ({price_quantiles[1]:.0f}-{price_quantiles[2]:.0f}€)
    </div>
    <div style="margin-bottom: 10px;">
        <i class="fa fa-circle" style="color:red"></i> Teuer (>{price_quantiles[2]:.0f}€)
    </div>
    '''
    
    # Füge Zeitstrahl-Info hinzu falls verfügbar
    if df is not None:
        years = sorted(df['year'].unique())
        total_offers = len(df)
        
        legend_html += f'''
        <hr style="margin: 5px 0;">
        <h4 style="margin: 5px 0;">Zeitstrahl-Daten</h4>
        <div style="font-size: 11px;">
            <div>📅 Jahre: {years[0]} - {years[-1]}</div>
            <div>🏠 Gesamt: {total_offers:,} Angebote</div>
        '''
        
        # Zeige Angebote pro Jahr
        for year in years:
            year_count = len(df[df['year'] == year])
            legend_html += f'<div>  {year}: {year_count:,}</div>'
        
        legend_html += '</div>'
    
    legend_html += '''
    <hr style="margin: 5px 0;">
    <div style="font-size: 10px; color: #666;">
        💡 Verwende Layer-Kontrolle (oben rechts) um verschiedene Ansichten zu wechseln
    </div>
    </div>
    '''
    
    return legend_html

def load_geojson_data():
    """Lade GeoJSON-Daten für Berlin Ortsteile."""
    print("Lade GeoJSON-Daten...")
    
    if not GEOPANDAS_AVAILABLE:
        print("❌ GeoPandas nicht verfügbar")
        return None
    
    if not os.path.exists(GEOJSON_PATH):
        print(f"❌ GeoJSON-Datei nicht gefunden: {GEOJSON_PATH}")
        return None
    
    try:
        gdf = gpd.read_file(GEOJSON_PATH)
        print(f"✅ GeoJSON geladen: {len(gdf)} Ortsteile")
        
        # Zeige verfügbare Spalten
        print(f"   Verfügbare Spalten: {list(gdf.columns)}")
        
        # Prüfe auf wichtige Spalten
        if 'OTEIL' in gdf.columns:
            print(f"   Beispiel-Ortsteile: {gdf['OTEIL'].head(5).tolist()}")
        
        return gdf
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der GeoJSON-Datei: {e}")
        return None

def aggregate_data_by_district(df, gdf=None):
    """Aggregiere Daten pro Bezirk und Ortsteil für Choropleth."""
    print("Aggregiere Daten für Choropleth...")
    
    # Aggregiere nach Bezirk
    district_stats = df.groupby('district').agg({
        'price': ['mean', 'median', 'count'],
        'price_per_sqm': ['mean', 'median'],
        'size': ['mean', 'median']
    }).round(2)
    
    # Flatten column names
    district_stats.columns = ['_'.join(col).strip() for col in district_stats.columns.values]
    district_stats = district_stats.reset_index()
    
    print(f"   Bezirks-Statistiken erstellt: {len(district_stats)} Bezirke")
    
    # Aggregiere nach Ortsteil falls verfügbar
    ortsteil_stats = None
    if 'ortsteil' in df.columns:  # Korrigiert: 'ortsteil' statt 'ortsteil_neu'
        ortsteil_stats = df.groupby('ortsteil').agg({
            'price': ['mean', 'median', 'count'],
            'price_per_sqm': ['mean', 'median'],
            'size': ['mean', 'median']
        }).round(2)
        
        # Flatten column names
        ortsteil_stats.columns = ['_'.join(col).strip() for col in ortsteil_stats.columns.values]
        ortsteil_stats = ortsteil_stats.reset_index()
        
        print(f"   Ortsteil-Statistiken erstellt: {len(ortsteil_stats)} Ortsteile")
        print(f"   Beispiel-Ortsteile: {ortsteil_stats['ortsteil'].head(5).tolist()}")
    else:
        print("   ❌ Spalte 'ortsteil' nicht gefunden")
    
    return district_stats, ortsteil_stats

def create_choropleth_layer(m, gdf, ortsteil_stats):
    """Erstelle Choropleth-Layer basierend auf Ortsteilen."""
    print("Erstelle Choropleth-Layer...")
    
    if gdf is None:
        print("   Überspringe Choropleth - keine GeoJSON-Daten verfügbar")
        return m
    
    # Prüfe verfügbare Spalten in GeoJSON
    print(f"   GeoJSON Spalten: {list(gdf.columns)}")
    
    # Verwende die richtige Spalte für Ortsteile (OTEIL basierend auf der Analyse)
    ortsteil_col = 'OTEIL'
    
    if ortsteil_col not in gdf.columns:
        print(f"   ❌ Spalte '{ortsteil_col}' nicht in GeoJSON gefunden")
        return m
    
    print(f"   Verwende Ortsteil-Spalte: {ortsteil_col}")
    
    # Wenn wir Ortsteil-Statistiken haben, merge sie
    if ortsteil_stats is not None:
        # Merge mit Statistiken - verwende spatial_alias als Match
        gdf_merged = gdf.merge(
            ortsteil_stats, 
            left_on='spatial_alias',  # spatial_alias ist der lesbare Name
            right_on='ortsteil',      # Korrigiert: 'ortsteil' statt 'ortsteil_neu'
            how='left'
        )
        
        # Fülle NaN-Werte mit 0
        for col in ['price_mean', 'price_count', 'price_per_sqm_mean']:
            if col in gdf_merged.columns:
                gdf_merged[col] = gdf_merged[col].fillna(0)
        
        print(f"   Merge erfolgreich: {len(gdf_merged)} Ortsteile")
        
        # Erstelle Choropleth für Durchschnittspreis
        if 'price_mean' in gdf_merged.columns:
            choropleth_price = folium.Choropleth(
                geo_data=gdf_merged.__geo_interface__,
                name='💰 Durchschnittspreis pro Ortsteil',
                data=gdf_merged,
                columns=['spatial_alias', 'price_mean'],
                key_on='feature.properties.spatial_alias',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Durchschnittspreis (€)',
                overlay=True,
                control=True,
                show=False
            )
            choropleth_price.add_to(m)
        
        # Erstelle Choropleth für Anzahl Angebote
        if 'price_count' in gdf_merged.columns:
            choropleth_count = folium.Choropleth(
                geo_data=gdf_merged.__geo_interface__,
                name='📊 Anzahl Angebote pro Ortsteil',
                data=gdf_merged,
                columns=['spatial_alias', 'price_count'],
                key_on='feature.properties.spatial_alias',
                fill_color='BuPu',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Anzahl Angebote',
                overlay=True,
                control=True,
                show=False
            )
            choropleth_count.add_to(m)
        
        # Verwende gdf_merged für Tooltips
        gdf_for_tooltips = gdf_merged
    else:
        # Ohne Statistiken, nur Grenzen zeigen
        gdf_for_tooltips = gdf
        print("   Keine Ortsteil-Statistiken verfügbar - zeige nur Grenzen")
    
    # Füge GeoJSON-Layer mit Tooltips hinzu
    tooltip_fields = ['spatial_alias', 'BEZIRK']
    tooltip_aliases = ['Ortsteil:', 'Bezirk:']
    
    # Füge Statistik-Felder hinzu falls verfügbar
    if ortsteil_stats is not None:
        for field, alias in [('price_mean', 'Ø Preis (€):'), ('price_count', 'Anzahl Angebote:'), ('price_per_sqm_mean', 'Ø €/m²:')]:
            if field in gdf_for_tooltips.columns:
                tooltip_fields.append(field)
                tooltip_aliases.append(alias)
    
    geojson_layer = folium.GeoJson(
        gdf_for_tooltips,
        name='🗺️ Ortsteil-Grenzen',
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        ),
        overlay=True,
        control=True,
        show=True  # Zeige Grenzen standardmäßig
    )
    geojson_layer.add_to(m)
    
    print("   ✅ Choropleth-Layer hinzugefügt")
    return m

def create_time_slider_data(df, gdf, ortsteil_stats_by_year):
    """Erstelle Daten für den Zeitstrahl-Slider."""
    print("Erstelle Zeitstrahl-Daten...")
    
    if gdf is None or ortsteil_stats_by_year is None:
        return None
    
    # Erstelle Zeitstrahl-Daten für jeden Ortsteil und jedes Jahr
    time_data = []
    years = sorted(df['year'].unique())
    
    for year in years:
        year_stats = ortsteil_stats_by_year.get(year, pd.DataFrame())
        
        if not year_stats.empty:
            # Merge mit GeoJSON
            gdf_year = gdf.merge(
                year_stats,
                left_on='spatial_alias',
                right_on='ortsteil_neu',
                how='left'
            )
            
            # Fülle NaN-Werte
            gdf_year['price_mean'] = gdf_year['price_mean'].fillna(0)
            
            # Erstelle Datum für TimeSlider
            timestamp = datetime.datetime(year, 1, 1).strftime('%Y-%m-%d')
            
            time_data.append({
                'timestamp': timestamp,
                'geodata': gdf_year,
                'data': gdf_year[['spatial_alias', 'price_mean']].copy()
            })
    
    return time_data

def aggregate_data_by_year_and_district(df, gdf=None):
    """Aggregiere Daten pro Jahr, Bezirk und Ortsteil."""
    print("Aggregiere Daten pro Jahr für Zeitstrahl...")
    
    # Aggregiere nach Jahr und Bezirk
    district_stats_by_year = {}
    ortsteil_stats_by_year = {}
    
    years = sorted(df['year'].unique())
    
    for year in years:
        year_df = df[df['year'] == year]
        
        # Bezirks-Statistiken
        district_stats = year_df.groupby('district').agg({
            'price': ['mean', 'median', 'count'],
            'price_per_sqm': ['mean', 'median'],
            'size': ['mean', 'median']
        }).round(2)
        
        district_stats.columns = ['_'.join(col).strip() for col in district_stats.columns.values]
        district_stats = district_stats.reset_index()
        district_stats_by_year[year] = district_stats
        
        # Ortsteil-Statistiken (falls verfügbar)
        if 'ortsteil' in year_df.columns:  # Korrigiert: 'ortsteil' statt 'ortsteil_neu'
            ortsteil_stats = year_df.groupby('ortsteil').agg({
                'price': ['mean', 'median', 'count'],
                'price_per_sqm': ['mean', 'median'],
                'size': ['mean', 'median']
            }).round(2)
            
            ortsteil_stats.columns = ['_'.join(col).strip() for col in ortsteil_stats.columns.values]
            ortsteil_stats = ortsteil_stats.reset_index()
            ortsteil_stats_by_year[year] = ortsteil_stats
    
    print(f"   Daten für {len(years)} Jahre aggregiert")
    return district_stats_by_year, ortsteil_stats_by_year

def create_interactive_map(df, price_quantiles, gdf=None, ortsteil_stats=None, ortsteil_stats_by_year=None):
    """Erstelle die interaktive Folium-Karte."""
    print("Erstelle interaktive Karte...")
    
    # Erstelle Basis-Karte OHNE automatische Tiles
    m = folium.Map(
        location=[52.52, 13.405], 
        zoom_start=11,
        tiles=None
    )
    
    # Füge Basis-Tile-Layer manuell hinzu
    base_layer = folium.TileLayer(
        tiles='CartoDB positron',
        name='Helle Karte',
        overlay=False,
        control=True
    )
    base_layer.add_to(m)
    
    # Füge alternative Tile-Layer hinzu
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='Dunkle Karte',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Erstelle Layer für jedes Jahr
    years = sorted(df['year'].unique())
    print(f"  Erstelle Layer für Jahre: {years}")
    
    for year in years:
        year_data = df[df['year'] == year]
        print(f"    Jahr {year}: {len(year_data)} Angebote")
        
        # Erstelle Marker-Cluster für dieses Jahr
        marker_cluster = MarkerCluster(
            name=f'📍 Angebote {year} ({len(year_data)} Stück)',
            overlay=True,
            control=True,
            show=True if year == years[-1] else False  # Nur letztes Jahr standardmäßig anzeigen
        )
        marker_cluster.add_to(m)
        
        # Erstelle Sample für bessere Performance
        if len(year_data) > SAMPLE_SIZE:
            year_data_sample = year_data.sample(n=SAMPLE_SIZE, random_state=42)
            print(f"      Sample erstellt: {len(year_data_sample)} Punkte")
        else:
            year_data_sample = year_data
        
        # Füge Marker für jede Immobilie hinzu
        for idx, row in year_data_sample.iterrows():
            # Verwende echte oder simulierte Koordinaten
            lat, lon = get_coordinates(row)
            
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
    
    # Füge Choropleth-Layer hinzu wenn verfügbar
    if ENABLE_CHOROPLETH and gdf is not None and ortsteil_stats is not None:
        m = create_choropleth_layer(m, gdf, ortsteil_stats)
    
    # Füge Zeitstrahl-Funktionalität hinzu
    if ENABLE_CHOROPLETH and gdf is not None and ortsteil_stats_by_year is not None:
        print("  Füge Zeitstrahl-Funktionalität hinzu...")
        
        # Erstelle Zeitstrahl-Daten
        time_data = create_time_slider_data(df, gdf, ortsteil_stats_by_year)
        
        if time_data:
            # Implementiere einen vereinfachten Zeitstrahl mit separaten Choropleth-Layern pro Jahr
            years = sorted(df['year'].unique())
            
            for year in years:
                if year in ortsteil_stats_by_year:
                    year_stats = ortsteil_stats_by_year[year]
                    
                    # Merge mit GeoJSON
                    gdf_year = gdf.merge(
                        year_stats,
                        left_on='spatial_alias',
                        right_on='ortsteil',  # Korrigiert: 'ortsteil' statt 'ortsteil_neu'
                        how='left'
                    )
                    
                    # Fülle NaN-Werte
                    gdf_year['price_mean'] = gdf_year['price_mean'].fillna(0)
                    
                    # Erstelle Choropleth für dieses Jahr
                    choropleth_year = folium.Choropleth(
                        geo_data=gdf_year.__geo_interface__,
                        name=f'📅 Preisentwicklung {year}',
                        data=gdf_year,
                        columns=['spatial_alias', 'price_mean'],
                        key_on='feature.properties.spatial_alias',
                        fill_color='YlOrRd',
                        fill_opacity=0.7,
                        line_opacity=0.2,
                        legend_name=f'Durchschnittspreis {year} (€)',
                        overlay=True,
                        control=True,
                        show=False  # Standardmäßig ausgeblendet
                    )
                    choropleth_year.add_to(m)
    
    return m

def save_map(m, price_quantiles, df, output_path):
    """Speichere Karte mit Legende."""
    print("Speichere Karte...")
    
    # Füge Layer-Kontrolle hinzu - WICHTIG: Vor der Legende!
    layer_control = folium.LayerControl(
        position='topright',
        collapsed=False,  # Zeige Layer-Kontrolle geöffnet
        autoZIndex=True
    )
    layer_control.add_to(m)
    
    # Füge Legende hinzu
    legend_html = create_legend(price_quantiles, df)
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Speichere die Karte
    m.save(output_path)
    
    print(f"✅ Karte gespeichert: {output_path}")
    print(f"📋 Layer-Kontrolle: Oben rechts (sollte sichtbar sein)")
    print(f"🎛️  Verwende die Layer-Kontrolle zum Wechseln zwischen Ansichten")

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
        
        # Lade GeoJSON-Daten für Ortsteile
        gdf = None
        ortsteil_stats = None
        ortsteil_stats_by_year = None
        
        if ENABLE_CHOROPLETH:
            gdf = load_geojson_data()
            if gdf is not None:
                # Aggregiere Daten für Choropleth (alle Jahre zusammen)
                district_stats, ortsteil_stats = aggregate_data_by_district(df, gdf)
                
                # Aggregiere Daten pro Jahr für Zeitstrahl
                district_stats_by_year, ortsteil_stats_by_year = aggregate_data_by_year_and_district(df, gdf)
        
        # Berechne Preiskategorien
        df, price_quantiles = calculate_price_categories(df)
        
        # Erstelle interaktive Karte
        m = create_interactive_map(df, price_quantiles, gdf, ortsteil_stats, ortsteil_stats_by_year)
        
        # Speichere Karte
        save_map(m, price_quantiles, df, OUTPUT_FILE)
        
        print(f"\nFEATURES DER GENERIERTEN KARTE:")
        print(f"  - Preis-Farbkodierung (4 Kategorien)")
        print(f"  - Jahresfilter mit separaten Layern")
        print(f"  - Detaillierte Tooltips mit Preis, Bezirk, Wohnlage")
        print(f"  - Groessenkodierung basierend auf Wohnungsgroesse")
        print(f"  - Interaktive Legende und Layer-Kontrolle")
        print(f"  - Clustering für bessere Performance")
        print(f"  - Mehrere Kartenstile zur Auswahl")
        if ENABLE_CHOROPLETH and gdf is not None:
            print(f"  - Choropleth-Layer mit Ortsteils-Grenzen")
            print(f"  - Aggregierte Statistiken pro Ortsteil")
            print(f"  - Mehrere Choropleth-Visualisierungen (Preis, Anzahl, €/m²)")
        
        print(f"\nERFOLGREICH ABGESCHLOSSEN!")
        print(f"Oeffne '{OUTPUT_FILE}' in deinem Browser.")
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
