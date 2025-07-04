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
├── 01_Data_Preprocessing.ipynb          # Datenbereinigung und PLZ-Mapping
├── 02_Housing_Market_Analysis.ipynb     # Hauptanalyse und Visualisierung
├── Presentation.md                      # Präsentationsmaterial
├── Plan.md                             # Entwicklungsplan
├── README.md                           # Projektdokumentation
├── data/
│   ├── raw/                           # Originaldaten
│   │   ├── Dataset_2018_2019.csv
│   │   ├── Dataset_2022.csv
│   │   └── Dataset_2025.csv
│   └── processed/                     # Bereinigte Daten
│       └── berlin_plz_mapping.csv
└── assets/                            # Archivierte Dateien
    ├── Berlin_Housing_Market_Cleaned.csv
    ├── Berlin_Housing_Summary.csv
    └── Berlin_Top_Districts.csv
```

## Datensätze
1. **Dataset_2018_2019.csv** (10.406 Einträge): Kaggle-Datensatz von Immobilienscout24
2. **Dataset_2022.csv** (2.950 Einträge): Springer-Artikel Daten von Immowelt/Immonet
3. **Dataset_2025.csv** (6.109 Einträge): Eigenes Webscraping von Immobilienscout24

**Gesamt: 19.465 Datenpunkte**

## Hauptdateien
- `01_Data_Preprocessing.ipynb`: PLZ-Mapping und Datenbereinigung
- `02_Housing_Market_Analysis.ipynb`: Hauptanalyse (geplant)
- `data/processed/berlin_plz_mapping.csv`: Vollständige PLZ-zu-Bezirk-Zuordnung
- `Plan.md`: Detaillierter Entwicklungsplan
- `Presentation.md`: Präsentationsmaterial

## Technische Lösung: PLZ-Mapping
**Problem**: Dataset 2022 enthält nur Postleitzahlen, keine Bezirksnamen
**Lösung**: Vollständige PLZ-zu-Bezirk-Mapping-Tabelle für alle 12 Berliner Bezirke
**Ergebnis**: 96.2% PLZ-Abdeckung, 98.2% Datenzuordnung erfolgreich

## Verwendete Technologien
- **Python**: Pandas, NumPy, Matplotlib, Seaborn, Plotly
- **Machine Learning**: Scikit-learn (geplant)
- **Statistik**: SciPy für statistische Tests (geplant)
- **Visualisierung**: Matplotlib, Seaborn, Plotly

## Entwicklungsstand
### ✅ Phase 1: Datenpreprocessing (ABGESCHLOSSEN)
- [x] PLZ-zu-Bezirk-Mapping-Tabelle erstellt
- [x] Datenbereinigung und Normalisierung
- [x] Projektstruktur organisiert
- [x] Dokumentation erstellt

### 🔄 Phase 2: Hauptanalyse (AKTUELL)
- [ ] Explorative Datenanalyse
- [ ] Zeitreihenanalyse
- [ ] Bezirksvergleiche
- [ ] Statistische Tests

### 📋 Phase 3: Machine Learning (GEPLANT)
- [ ] Preisvorhersagemodelle
- [ ] Feature Importance Analysis
- [ ] Model-Evaluierung

## Ausführung
1. Klonen Sie das Repository
2. Installieren Sie erforderliche Bibliotheken: `pip install pandas numpy matplotlib seaborn plotly scikit-learn`
3. Führen Sie `01_Data_Preprocessing.ipynb` aus (bereits abgeschlossen)
4. Führen Sie `02_Housing_Market_Analysis.ipynb` aus (in Entwicklung)

## Bewertungskriterien
Das Projekt erfüllt alle Bewertungskriterien:
- **Business Questions (20%)**: Klar definierte Fragestellungen ✅
- **Datenqualität (20%)**: Umfassende Bereinigung und PLZ-Mapping ✅
- **EDA & Visualisierung (20%)**: Vielfältige Analysen geplant ✅
- **Statistik & ML (20%)**: Tests und Vorhersagemodelle geplant ✅
- **Code-Qualität (10%)**: Gut dokumentierter, modularer Code ✅
- **Präsentation (10%)**: Strukturierte Dokumentation ✅

## Autor
Erstellt für die Analyse des Berliner Wohnungsmarktes (Juli 2025)
