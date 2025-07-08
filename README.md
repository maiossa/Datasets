# Berlin Housing Market Analysis

## Projektbeschreibung
Umfassende Analyse der Mietpreisentwicklung in Berlin basierend auf drei Datensätzen aus den Jahren 2018-2019, 2022 und 2025. Das Projekt löst systematisch das kritische PLZ-zu-Bezirk-Mapping-Problem und erstellt eine vollständige Analysepipeline.

## Ziele
- Identifikation von Mietpreistrends über Zeit
- Analyse der Bezirksunterschiede
- Vorhersage zukünftiger Entwicklungen
- Bereitstellung von Entscheidungsgrundlagen für Mieter, Vermieter und Stadtplaner

## Projektstruktur
```
Berlin_Housing_Market_Analysis/
├── 01_Clean_Dataset_2018_2019.ipynb           # Datenbereinigung Dataset 2018-2019
├── 02_Clean_Dataset_2022.ipynb                # Datenbereinigung Dataset 2022
├── 03_Clean_Dataset_2025.ipynb                # Datenbereinigung Dataset 2025
├── 04_Combine_Datasets.ipynb                  # Datenzusammenführung
├── 05_Housing_Market_Analysis.ipynb           # Hauptanalyse und Visualisierung
├── 06_Berlin_Housing_Market_Prediction.ipynb  # Vorhersagemodelle
├── create_enhanced_plz_mapping_with_coords.py # PLZ-Mapping mit Koordinaten
├── create_interactive_price_heatmap_FIXED.py  # Heatmap-Generierung (Aktuelle Version)
├── interactive_price_heatmap_berlin_FIXED.html# Interaktive Preisheatmap
├── Datasets_Info.md                           # Datensatz-Dokumentation
├── README.md                                   # Projektdokumentation
├── data/
│   ├── raw/                                   # Originaldaten
│   │   ├── Dataset_2018_2019.csv
│   │   ├── Dataset_2022.csv
│   │   ├── Dataset_2025.csv
│   │   ├── lor_ortsteile.geojson             # Berliner Ortsteile (GeoJSON)
│   │   └── wohnlagen_enriched.csv            # Wohnlagen-Daten ursprünglich von berlin.de
│   └── processed/                             # Bereinigte und verarbeitete Daten
│       ├── berlin_housing_combined_final.csv
│       ├── berlin_housing_combined_enriched_final.csv
│       ├── berlin_plz_mapping.csv
│       ├── berlin_plz_mapping_detailed.csv
│       ├── berlin_plz_mapping_enhanced.csv
│       ├── dataset_2018_2019_enriched.csv
│       ├── dataset_2018_2019_normalized.csv
│       ├── dataset_2022_enriched.csv
│       ├── dataset_2022_normalized.csv
│       ├── dataset_2025_enriched.csv
│       └── dataset_2025_normalized.csv
```

## Datensätze
1. **Dataset_2018_2019.csv** (10.406 Einträge): Kaggle-Datensatz von Immobilienscout24
https://www.kaggle.com/datasets/corrieaar/apartment-rental-offers-in-germany
2. **Dataset_2022.csv** (2.950 Einträge): Springer-Artikel Daten von Immowelt/Immonet
https://link.springer.com/article/10.1007/s11943-024-00340-6
3. **Dataset_2025.csv** (6.109 Einträge): Eigenes Webscraping von Immobilienscout24 (vom 20.06.2025)

**Gesamt: 19.465 Datenpunkte**

## Hauptdateien

### Datenbereinigung und Preprocessing
- `01_Clean_Dataset_2018_2019.ipynb`: Bereinigung des 2018-2019 Datensatzes
- `02_Clean_Dataset_2022.ipynb`: Bereinigung des 2022 Datensatzes
- `03_Clean_Dataset_2025.ipynb`: Bereinigung des 2025 Datensatzes
- `04_Combine_Datasets.ipynb`: Zusammenführung aller Datensätze

### Analyse und Visualisierung
- `05_Housing_Market_Analysis.ipynb`: Hauptanalyse mit statistischen Tests und Visualisierungen
- `06_Berlin_Housing_Market_Prediction.ipynb`: Machine Learning Vorhersagemodelle
- `interactive_price_heatmap_berlin_FIXED.html`: Interaktive Preisheatmap von Berlin

### Utility Scripts
- `create_enhanced_plz_mapping_with_coords.py`: Erstellung erweiterter PLZ-Mappings
- `create_interactive_price_heatmap_FIXED.py`: Generierung interaktiver Heatmaps

### Deprecated Files (können entfernt werden)
- `check_datasets.py`: Validierung und Überprüfung der Datensätze (nicht mehr benötigt)
- `create_interactive_price_heatmap_clean.py`: Frühere Version der Heatmap-Generierung

### Dokumentation
- `Datasets_Info.md`: Detaillierte Beschreibung aller Datensätze
- `README.md`: Projektübersicht und Anleitung

### Verarbeitete Daten
- `berlin_housing_combined_final.csv`: Zusammengeführter Gesamtdatensatz
- `berlin_housing_combined_enriched_final.csv`: Angereichterter Gesamtdatensatz
- `berlin_plz_mapping_enhanced.csv`: Erweiterte PLZ-zu-Bezirk-Zuordnung mit Koordinaten

## Technische Lösung: PLZ-Mapping
**Problem**: Dataset 2022 enthält nur Postleitzahlen, keine Bezirksnamen
**Lösung**: Vollständige PLZ-zu-Bezirk-Mapping-Tabelle für alle 12 Berliner Bezirke
**Ergebnis**: 96.2% PLZ-Abdeckung, 98.2% Datenzuordnung erfolgreich

## Verwendete Technologien
- **Python**: Pandas, NumPy, Matplotlib, Seaborn, Plotly, Folium
- **Machine Learning**: Scikit-learn für Vorhersagemodelle
- **Statistik**: SciPy für statistische Tests und Analysen
- **Visualisierung**: Matplotlib, Seaborn, Plotly für statische und interaktive Plots
- **Geospatiale Analyse**: GeoPandas, Folium für Karten und räumliche Visualisierungen
- **Web-Technologien**: HTML für interaktive Dashboards

## Ausführung

### Voraussetzungen
Installieren Sie die erforderlichen Python-Bibliotheken:
```bash
pip install pandas numpy matplotlib seaborn plotly scikit-learn geopandas folium scipy
```

### Schritt-für-Schritt Anleitung
1. **Datenbereinigung**: 
   - Führen Sie die Notebooks `01_Clean_Dataset_2018_2019.ipynb`, `02_Clean_Dataset_2022.ipynb`, und `03_Clean_Dataset_2025.ipynb` aus
   
2. **Datenzusammenführung**: 
   - Führen Sie `04_Combine_Datasets.ipynb` aus, um alle Datensätze zu kombinieren
   
3. **Hauptanalyse**: 
   - Führen Sie `05_Housing_Market_Analysis.ipynb` für umfassende Marktanalyse aus
   
4. **Vorhersagemodelle**: 
   - Führen Sie `06_Berlin_Housing_Market_Prediction.ipynb` für ML-basierte Prognosen aus
   
5. **Interaktive Visualisierung**: 
   - Öffnen Sie `interactive_price_heatmap_berlin_FIXED.html` im Browser für interaktive Karten
   - Oder führen Sie `create_interactive_price_heatmap_FIXED.py` aus, um die Heatmap neu zu generieren

### Optional: Aufräumen veralteter Dateien
Entfernen Sie nicht mehr benötigte Dateien:
```bash
# Diese Dateien können sicher gelöscht werden
rm check_datasets.py
rm create_interactive_price_heatmap_clean.py
```

## Projektstatus
✅ **Abgeschlossen**: Datenbereinigung aller drei Datensätze  
✅ **Abgeschlossen**: PLZ-zu-Bezirk-Mapping mit 98.2% Erfolgsrate  
✅ **Abgeschlossen**: Datenzusammenführung und Enrichment  
✅ **Abgeschlossen**: Umfassende Marktanalyse mit statistischen Tests  
✅ **Abgeschlossen**: Machine Learning Vorhersagemodelle  
✅ **Abgeschlossen**: Interaktive Preisheatmap  

## Ergebnisse
Das Projekt liefert detaillierte Einblicke in:
- Mietpreisentwicklung von 2018-2025 in Berlin
- Bezirksspezifische Preisunterschiede und Trends
- Vorhersagen für zukünftige Mietpreisentwicklungen
- Interaktive Visualisierungen für bessere Datenexploration

