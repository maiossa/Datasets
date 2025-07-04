# Berlin Housing Market Analysis

## Projektbeschreibung
Analyse der Mietpreisentwicklung in Berlin basierend auf Datensätzen aus den Jahren 2018-2019, 2022 und 2025.

## Ziele
- Identifikation von Mietpreistrends über Zeit
- Analyse der Bezirksunterschiede
- Vorhersage zukünftiger Entwicklungen
- Bereitstellung von Entscheidungsgrundlagen für Mieter, Vermieter und Stadtplaner

## Datensätze
1. **Dataset_2018_2019.csv**: Kaggle-Datensatz von Immobilienscout24 (2018-2019)
2. **Dataset_2022.csv**: Springer-Artikel Daten von Immowelt/Immonet (2022)
3. **Dataset_2025.csv**: Eigenes Webscraping von Immobilienscout24 (Juni 2025)

## Hauptdateien
- `Berlin_Housing_Market_Analysis.ipynb`: Jupyter Notebook mit kompletter Analyse
- `Berlin_Housing_Market_Cleaned.csv`: Bereinigter und zusammengeführter Datensatz
- `Berlin_Housing_Summary.csv`: Zusammenfassung der wichtigsten Kennzahlen
- `Berlin_Top_Districts.csv`: Top 10 Bezirke nach Mietpreis
- `Datasets_Info.md`: Detaillierte Informationen zu den Datensätzen

## Verwendete Technologien
- **Python**: Pandas, NumPy, Matplotlib, Seaborn, Plotly
- **Machine Learning**: Scikit-learn (Linear Regression, Random Forest)
- **Statistik**: SciPy für statistische Tests
- **Visualisierung**: Matplotlib, Seaborn, Plotly

## Ergebnisse
- Mietpreise sind zwischen 2018 und 2025 statistisch signifikant gestiegen
- Zentrale Bezirke (Mitte, Tiergarten) haben die höchsten Preise
- Machine Learning-Modelle können Preise mit R² > 0.7 vorhersagen

## Ausführung
1. Klonen Sie das Repository
2. Installieren Sie die erforderlichen Bibliotheken: `pip install pandas numpy matplotlib seaborn plotly scikit-learn`
3. Öffnen Sie `Berlin_Housing_Market_Analysis.ipynb` in Jupyter Notebook
4. Führen Sie alle Zellen der Reihe nach aus

## Präsentation
Das Projekt erfüllt alle Bewertungskriterien:
- Business Questions (20%): Klar definierte Fragestellungen
- Datenqualität (20%): Umfassende Bereinigung und Normalisierung
- EDA & Visualisierung (20%): Vielfältige Analysen und Grafiken
- Statistik & ML (20%): Tests und Vorhersagemodelle
- Code-Qualität (10%): Gut dokumentierter Code
- Präsentation (10%): Strukturierte Aufbereitung der Ergebnisse

## Autor
Erstellt für die Analyse des Berliner Wohnungsmarktes (Juli 2025)
