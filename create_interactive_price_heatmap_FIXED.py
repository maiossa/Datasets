#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Price Heatmap Berlin Generator - FIXED VERSION
=========================================================

Generiert eine interaktive Folium-Karte mit Preis-Heatmap für Berlin.
Basierend auf dem funktionierenden Debug-Test.

Feature        # Erstelle Marker-Cluster für dieses Jahr
        marker_cluster = MarkerCluster(
            name=f'📍 Angebote {year} ({len(year_data_sample)} Stück)',
            overlay=True,
            control=True,
            show=False  # Standardmäßig ausgeblendet, damit Choropleth sichtbar ist
        )reis-Farbkodierung (4 Kategorien basierend auf Quantilen)
- Jahresfilter mit separaten Layern
- Choropleth-Layer mit Berlin Ortsteilen
- Detaillierte Tooltips
- Interaktive Layer-Kontrolle
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import numpy as np
import random
import os

# Versuche geopandas zu importieren
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    print("⚠️  GeoPandas nicht verfügbar. Choropleth-Features werden deaktiviert.")
    GEOPANDAS_AVAILABLE = False

# Konfiguration
OUTPUT_FILE = 'interactive_price_heatmap_berlin_FIXED.html'
DATA_PATH = 'data/processed/berlin_housing_combined_enriched_final.csv'
GEOJSON_PATH = 'data/raw/lor_ortsteile.geojson'
SAMPLE_SIZE = 1000  # Max Punkte pro Jahr für Performance

# Bezirk-Koordinaten für Simulation
DISTRICT_COORDS = {
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
    'Friedrichshain': [52.515, 13.455],
    'Kreuzberg': [52.500, 13.420],
    'Charlottenburg': [52.520, 13.295],
    'Wilmersdorf': [52.495, 13.315],
    'Schöneberg': [52.485, 13.365],
    'Tempelhof': [52.465, 13.385],
    'Zehlendorf': [52.435, 13.255],
    'Steglitz': [52.455, 13.315],
}

def load_data():
    """Lade und bereite Daten vor."""
    print("Lade Daten...")
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Datei nicht gefunden: {DATA_PATH}")
        return None
    
    df = pd.read_csv(DATA_PATH, dtype={'plz': 'string'})
    print(f"✅ Daten geladen: {len(df):,} Zeilen")
    
    # Berechne Preis pro m²
    df['price_per_sqm'] = df['price'] / df['size']
    df['price_per_sqm'] = df['price_per_sqm'].replace([np.inf, -np.inf], np.nan)
    
    # Entferne Zeilen mit fehlenden Werten
    df = df.dropna(subset=['price', 'size', 'district'])
    
    print(f"✅ Daten bereinigt: {len(df):,} Zeilen")
    print(f"   • Zeitraum: {df['year'].min()} - {df['year'].max()}")
    print(f"   • Bezirke: {df['district'].nunique()}")
    
    if 'ortsteil' in df.columns:
        print(f"   • Ortsteile: {df['ortsteil'].nunique()}")
    
    return df

def calculate_price_categories(df):
    """Berechne Preiskategorien basierend auf Quantilen."""
    print("Berechne Preiskategorien...")
    
    price_quantiles = df['price'].quantile([0.25, 0.5, 0.75]).values
    print(f"  Preis-Quantile: 25%={price_quantiles[0]:.0f}€, 50%={price_quantiles[1]:.0f}€, 75%={price_quantiles[2]:.0f}€")
    
    def get_price_color(price):
        if price <= price_quantiles[0]:
            return 'green'
        elif price <= price_quantiles[1]:
            return 'lightgreen'
        elif price <= price_quantiles[2]:
            return 'orange'
        else:
            return 'red'
    
    def get_price_category(price):
        if price <= price_quantiles[0]:
            return 'Günstig'
        elif price <= price_quantiles[1]:
            return 'Günstig-Mittel'
        elif price <= price_quantiles[2]:
            return 'Mittel-Teuer'
        else:
            return 'Teuer'
    
    df['price_color'] = df['price'].apply(get_price_color)
    df['price_category'] = df['price'].apply(get_price_category)
    
    return df, price_quantiles

def get_coordinates(row):
    """Verwende echte Koordinaten oder fallback zu simulierten."""
    if 'lat' in row and 'lon' in row and pd.notna(row['lat']) and pd.notna(row['lon']):
        return row['lat'], row['lon']
    
    district = row.get('district', 'Unknown')
    if district in DISTRICT_COORDS:
        base_lat, base_lon = DISTRICT_COORDS[district]
    else:
        base_lat, base_lon = 52.52, 13.405
    
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
    """
    
    if 'plz' in row and pd.notna(row['plz']):
        tooltip_text += f"<b>PLZ:</b> {row['plz']}<br>"
    
    if 'ortsteil' in row and pd.notna(row['ortsteil']):
        tooltip_text += f"<b>Ortsteil:</b> {row['ortsteil']}<br>"
    
    tooltip_text += f"<b>Jahr:</b> {row['year']}<br>"
    
    if 'rooms' in row and pd.notna(row['rooms']):
        tooltip_text += f"<b>Zimmer:</b> {row['rooms']}<br>"
    
    return tooltip_text

def create_choropleth_layers(m, df):
    """Erstelle Choropleth-Layer."""
    if not GEOPANDAS_AVAILABLE:
        print("   Überspringe Choropleth - GeoPandas nicht verfügbar")
        return m
    
    if not os.path.exists(GEOJSON_PATH):
        print(f"   Überspringe Choropleth - GeoJSON nicht gefunden: {GEOJSON_PATH}")
        return m
    
    try:
        print("  Erstelle Choropleth-Layer...")
        
        # Lade GeoJSON
        gdf = gpd.read_file(GEOJSON_PATH)
        
        # Aggregiere Ortsteil-Daten (alle Jahre zusammen)
        if 'ortsteil' in df.columns:
            ortsteil_stats = df.groupby('ortsteil').agg({
                'price': ['mean', 'count'],
                'price_per_sqm': ['mean']
            }).round(2)
            ortsteil_stats.columns = ['price_mean', 'price_count', 'price_per_sqm_mean']
            ortsteil_stats = ortsteil_stats.reset_index()
            
            # Merge mit GeoJSON
            gdf_merged = gdf.merge(ortsteil_stats, left_on='spatial_alias', right_on='ortsteil', how='left')
            gdf_merged['price_mean'] = gdf_merged['price_mean'].fillna(0)
            gdf_merged['price_count'] = gdf_merged['price_count'].fillna(0)
            gdf_merged['price_per_sqm_mean'] = gdf_merged['price_per_sqm_mean'].fillna(0)
            
            print(f"    Choropleth-Daten: {(gdf_merged['price_mean'] > 0).sum()} von {len(gdf_merged)} Ortsteilen mit Daten")
            
            # Erstelle Choropleth für Durchschnittspreis
            choropleth_price = folium.Choropleth(
                geo_data=gdf_merged,
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
                show=True  # Zeige als Standard
            )
            choropleth_price.add_to(m)
            
            # Erstelle Choropleth für Anzahl Angebote
            choropleth_count = folium.Choropleth(
                geo_data=gdf_merged,
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
            
            # Erstelle Choropleth für Preis pro m²
            choropleth_sqm = folium.Choropleth(
                geo_data=gdf_merged,
                name='📈 Preis pro m² pro Ortsteil',
                data=gdf_merged,
                columns=['spatial_alias', 'price_per_sqm_mean'],
                key_on='feature.properties.spatial_alias',
                fill_color='Greens',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='Preis pro m² (€)',
                overlay=True,
                control=True,
                show=False
            )
            choropleth_sqm.add_to(m)
            
            # Füge Ortsteil-Grenzen hinzu
            grenzen_layer = folium.GeoJson(
                gdf_merged,
                name='🗺️ Ortsteil-Grenzen',
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'blue',
                    'weight': 2,
                    'fillOpacity': 0
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['spatial_alias', 'BEZIRK', 'price_mean', 'price_count'],
                    aliases=['Ortsteil:', 'Bezirk:', 'Ø Preis (€):', 'Anzahl Angebote:'],
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                ),
                overlay=True,
                control=True,
                show=False  # Ausgeblendet wenn Choropleth aktiv ist
            )
            grenzen_layer.add_to(m)
            
            print("    ✅ Choropleth-Layer hinzugefügt")
        
    except Exception as e:
        print(f"    ❌ Fehler bei Choropleth: {e}")
    
    return m

def create_interactive_map(df, price_quantiles):
    """Erstelle die interaktive Folium-Karte."""
    print("Erstelle interaktive Karte...")
    
    # Erstelle Basis-Karte
    m = folium.Map(location=[52.52, 13.405], zoom_start=11)
    
    # Füge Choropleth-Layer hinzu
    m = create_choropleth_layers(m, df)
    
    # Erstelle Layer für jedes Jahr
    years = sorted(df['year'].unique())
    print(f"  Erstelle Marker-Layer für Jahre: {years}")
    
    for year in years:
        year_data = df[df['year'] == year]
        print(f"    Jahr {year}: {len(year_data)} Angebote")
        
        # Erstelle Sample für Performance
        if len(year_data) > SAMPLE_SIZE:
            year_data_sample = year_data.sample(n=SAMPLE_SIZE, random_state=42)
        else:
            year_data_sample = year_data
        
        # Erstelle Marker-Cluster für dieses Jahr
        marker_cluster = MarkerCluster(
            name=f'📍 Angebote {year} ({len(year_data)} Stück)',
            overlay=True,
            control=True,
            show=True if year == years[-1] else False
        )
        
        # Füge Marker hinzu
        for idx, row in year_data_sample.iterrows():
            lat, lon = get_coordinates(row)
            radius = get_marker_size(row['size'])
            tooltip_text = create_tooltip(row)
            
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
        
        marker_cluster.add_to(m)
    
    return m

def create_legend(price_quantiles, df):
    """Erstelle HTML-Legende."""
    years = sorted(df['year'].unique())
    total_offers = len(df)
    
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 220px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 15px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
    <h4 style="margin: 0 0 10px 0; color: #333;">🎯 Preiskategorien</h4>
    <div style="margin-bottom: 5px;">
        <i class="fa fa-circle" style="color:green"></i> Günstig (≤{price_quantiles[0]:.0f}€)
    </div>
    <div style="margin-bottom: 5px;">
        <i class="fa fa-circle" style="color:lightgreen"></i> Günstig-Mittel ({price_quantiles[0]:.0f}-{price_quantiles[1]:.0f}€)
    </div>
    <div style="margin-bottom: 5px;">
        <i class="fa fa-circle" style="color:orange"></i> Mittel-Teuer ({price_quantiles[1]:.0f}-{price_quantiles[2]:.0f}€)
    </div>
    <div style="margin-bottom: 15px;">
        <i class="fa fa-circle" style="color:red"></i> Teuer (>{price_quantiles[2]:.0f}€)
    </div>
    
    <hr style="margin: 10px 0;">
    <h4 style="margin: 5px 0; color: #333;">📅 Zeitstrahl-Daten</h4>
    <div style="font-size: 11px; margin-bottom: 10px;">
        <div><strong>📊 Gesamt:</strong> {total_offers:,} Angebote</div>
        <div><strong>⏳ Zeitraum:</strong> {years[0]} - {years[-1]}</div>
    </div>
    
    <hr style="margin: 10px 0;">
    <div style="font-size: 11px; color: #666; line-height: 1.4;">
        <strong>💡 Bedienung:</strong><br>
        • Verwende <strong>Layer-Kontrolle</strong> (oben rechts) zum Wechseln zwischen Ansichten<br>
        • <strong>Choropleth-Layer:</strong> Zeigen aggregierte Daten pro Ortsteil<br>
        • <strong>Marker-Layer:</strong> Zeigen einzelne Angebote pro Jahr
    </div>
    </div>
    '''
    
    return legend_html

def main():
    """Hauptfunktion."""
    try:
        print("="*80)
        print("INTERACTIVE PRICE HEATMAP BERLIN GENERATOR - FIXED")
        print("="*80)
        
        # Setze Random Seed
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
        
        # Füge Layer-Kontrolle hinzu
        folium.LayerControl(
            position='topright',
            collapsed=False,
            autoZIndex=True
        ).add_to(m)
        
        # Füge Legende hinzu
        legend_html = create_legend(price_quantiles, df)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Speichere Karte
        m.save(OUTPUT_FILE)
        
        print(f"\n🎉 ERFOLGREICH ABGESCHLOSSEN!")
        print(f"📁 Datei: {OUTPUT_FILE}")
        print(f"🌐 Öffne die Datei in deinem Browser!")
        
        print(f"\n✨ FEATURES:")
        print(f"  • Preis-Farbkodierung (4 Kategorien)")
        print(f"  • Jahresfilter mit separaten Layern")
        print(f"  • Choropleth-Layer mit Berlin Ortsteilen")
        print(f"  • Detaillierte Tooltips")
        print(f"  • Erweiterte Layer-Kontrolle")
        print(f"  • Interaktive Legende mit Bedienungshinweisen")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
