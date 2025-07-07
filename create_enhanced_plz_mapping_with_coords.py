#!/usr/bin/env python3
"""
Script to create an enhanced PLZ mapping from wohnlagen_enriched.csv
that maps PLZ to Ortsteil (sub-district) with coordinates instead of just Bezirk (district).

This provides much more granular and accurate geolocation for the Berlin Housing Market Analysis.
"""

import pandas as pd
import csv
from collections import defaultdict, Counter

# Ortsteil coordinates for Berlin (manually curated for high accuracy)
# These are the centroids of the respective Ortsteile
ORTSTEIL_COORDS = {
    # Mitte
    'Mitte': [52.5200, 13.4050],
    'Tiergarten': [52.5147, 13.3507],
    'Wedding': [52.5500, 13.3650],
    'Gesundbrunnen': [52.5511, 13.3885],
    'Moabit': [52.5280, 13.3430],
    
    # Friedrichshain-Kreuzberg
    'Friedrichshain': [52.5159, 13.4533],
    'Kreuzberg': [52.4987, 13.4030],
    
    # Pankow
    'Prenzlauer Berg': [52.5409, 13.4134],
    'Weißensee': [52.5547, 13.4774],
    'Pankow': [52.5692, 13.4018],
    'Buch': [52.6289, 13.4999],
    'Französisch Buchholz': [52.6140, 13.4200],
    'Karow': [52.6082, 13.4816],
    'Wilhelmsruh': [52.5897, 13.4186],
    'Rosenthal': [52.5944, 13.3778],
    'Blankenfelde': [52.6033, 13.3889],
    'Heinersdorf': [52.5755, 13.4456],
    'Malchow': [52.5733, 13.4667],
    'Wartenberg': [52.5667, 13.5167],
    'Blankenburg': [52.5964, 13.4564],
    'Niederschönhausen': [52.5756, 13.4000],
    
    # Charlottenburg-Wilmersdorf
    'Charlottenburg': [52.5170, 13.3043],
    'Wilmersdorf': [52.4867, 13.3189],
    'Schmargendorf': [52.4667, 13.2833],
    'Grunewald': [52.4833, 13.2667],
    'Westend': [52.5167, 13.2833],
    'Halensee': [52.4958, 13.3056],
    
    # Spandau
    'Spandau': [52.5333, 13.2000],
    'Hakenfelde': [52.5500, 13.1833],
    'Gatow': [52.4833, 13.1833],
    'Kladow': [52.4500, 13.1500],
    'Staaken': [52.5333, 13.1333],
    'Falkenhagener Feld': [52.5500, 13.1667],
    'Wilhelmstadt': [52.5167, 13.1833],
    
    # Steglitz-Zehlendorf
    'Steglitz': [52.4500, 13.3167],
    'Zehlendorf': [52.4333, 13.2500],
    'Wannsee': [52.4167, 13.1833],
    'Nikolassee': [52.4167, 13.2167],
    'Dahlem': [52.4667, 13.2833],
    'Lichterfelde': [52.4333, 13.3000],
    'Lankwitz': [52.4333, 13.3500],
    'Mariendorf': [52.4333, 13.3833],
    'Marienfelde': [52.4000, 13.3667],
    'Lichtenrade': [52.3833, 13.4000],
    
    # Tempelhof-Schöneberg
    'Tempelhof': [52.4500, 13.3833],
    'Schöneberg': [52.4833, 13.3500],
    'Friedenau': [52.4667, 13.3333],
    
    # Neukölln
    'Neukölln': [52.4500, 13.4333],
    'Britz': [52.4167, 13.4167],
    'Buckow': [52.4167, 13.4333],
    'Rudow': [52.4000, 13.4667],
    'Gropiusstadt': [52.4000, 13.4333],
    
    # Treptow-Köpenick
    'Treptow': [52.4833, 13.4667],
    'Köpenick': [52.4333, 13.5667],
    'Oberschöneweide': [52.4500, 13.5167],
    'Niederschöneweide': [52.4333, 13.5000],
    'Johannisthal': [52.4333, 13.5333],
    'Adlershof': [52.4167, 13.5333],
    'Altglienicke': [52.3833, 13.5333],
    'Bohnsdorf': [52.3833, 13.5667],
    'Grünau': [52.4000, 13.5833],
    'Schmöckwitz': [52.3667, 13.6500],
    'Friedrichshagen': [52.4333, 13.6167],
    'Rahnsdorf': [52.4167, 13.6833],
    'Hessenwinkel': [52.4167, 13.6167],
    'Müggelheim': [52.3833, 13.6833],
    'Wendenschloß': [52.4167, 13.6000],
    'Plänterwald': [52.4833, 13.4833],
    'Baumschulenweg': [52.4667, 13.5000],
    'Karlshorst': [52.4833, 13.5333],
    'Köllnische Heide': [52.4167, 13.5000],
    
    # Marzahn-Hellersdorf
    'Marzahn': [52.5333, 13.5500],
    'Hellersdorf': [52.5167, 13.5833],
    'Biesdorf': [52.5000, 13.5500],
    'Kaulsdorf': [52.5167, 13.5833],
    'Mahlsdorf': [52.5000, 13.6167],
    
    # Lichtenberg
    'Lichtenberg': [52.5167, 13.5000],
    'Friedrichsfelde': [52.5000, 13.5167],
    'Rummelsburg': [52.5000, 13.4667],
    'Fennpfuhl': [52.5333, 13.4833],
    'Hohenschönhausen': [52.5500, 13.5000],
    'Falkenberg': [52.5833, 13.5333],
    
    # Reinickendorf
    'Reinickendorf': [52.5833, 13.3333],
    'Tegel': [52.5833, 13.2833],
    'Heiligensee': [52.6167, 13.2500],
    'Frohnau': [52.6333, 13.3000],
    'Hermsdorf': [52.6167, 13.3167],
    'Waidmannslust': [52.6000, 13.3167],
    'Lübars': [52.6167, 13.3667],
    'Wittenau': [52.5833, 13.3333],
    'Märkisches Viertel': [52.6000, 13.3833],
    'Borsigwalde': [52.5833, 13.3000],
    'Konradshöhe': [52.5833, 13.2500],
    'Tegelort': [52.6000, 13.2667],
}

def get_ortsteil_coordinates(ortsteil):
    """Get coordinates for an Ortsteil. Returns None if not found."""
    # Try exact match first
    if ortsteil in ORTSTEIL_COORDS:
        return ORTSTEIL_COORDS[ortsteil]
    
    # Try case-insensitive match
    for key, coords in ORTSTEIL_COORDS.items():
        if key.lower() == ortsteil.lower():
            return coords
    
    # Try partial match
    for key, coords in ORTSTEIL_COORDS.items():
        if ortsteil.lower() in key.lower() or key.lower() in ortsteil.lower():
            return coords
    
    return None

def create_enhanced_plz_mapping():
    """
    Create enhanced PLZ mapping from wohnlagen_enriched.csv.
    For PLZ that map to multiple Ortsteile, we take the most frequent one.
    """
    
    print("Reading wohnlagen_enriched.csv...")
    
    # Read the wohnlagen data
    # Expected columns: id,schluessel,bezname,plz,strasse,hnr,wol,stadtteil,plr_name,bezirk_neu,ortsteil_neu
    df = pd.read_csv('data/raw/wohnlagen_enriched.csv', dtype={'plz': str})
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Filter out rows with missing PLZ or Ortsteil
    df_clean = df.dropna(subset=['plz', 'ortsteil_neu'])
    df_clean = df_clean[df_clean['plz'].str.len() == 5]  # Only 5-digit PLZ
    
    print(f"Rows with valid PLZ and Ortsteil: {len(df_clean)}")
    
    # Count PLZ-Ortsteil combinations
    plz_ortsteil_counts = defaultdict(Counter)
    
    for _, row in df_clean.iterrows():
        plz = row['plz']
        ortsteil = row['ortsteil_neu']
        bezirk = row['bezirk_neu']
        
        # Count this combination
        plz_ortsteil_counts[plz][ortsteil] += 1
    
    # Create the enhanced mapping
    enhanced_mapping = []
    missing_coords = []
    
    for plz, ortsteil_counter in plz_ortsteil_counts.items():
        # Get the most frequent Ortsteil for this PLZ
        most_common_ortsteil = ortsteil_counter.most_common(1)[0][0]
        total_entries = sum(ortsteil_counter.values())
        
        # Get the corresponding Bezirk
        bezirk_row = df_clean[df_clean['plz'] == plz].iloc[0]
        bezirk = bezirk_row['bezirk_neu']
        
        # Get coordinates for the Ortsteil
        coords = get_ortsteil_coordinates(most_common_ortsteil)
        lat, lon = coords if coords else [None, None]
        
        enhanced_mapping.append({
            'PLZ': plz,
            'Ortsteil': most_common_ortsteil,
            'Bezirk': bezirk,
            'Lat': lat,
            'Lon': lon,
            'Entries': total_entries,
            'Ortsteile_Count': len(ortsteil_counter)
        })
        
        # Track missing coordinates
        if not coords:
            missing_coords.append(most_common_ortsteil)
        
        # Print info for PLZ with multiple Ortsteile
        if len(ortsteil_counter) > 1:
            print(f"PLZ {plz} has {len(ortsteil_counter)} Ortsteile: {dict(ortsteil_counter)}")
            print(f"  → Using most frequent: {most_common_ortsteil}")
    
    # Sort by PLZ
    enhanced_mapping.sort(key=lambda x: x['PLZ'])
    
    # Print summary of missing coordinates
    if missing_coords:
        print(f"\n⚠️  Missing coordinates for {len(set(missing_coords))} unique Ortsteile:")
        for ortsteil in sorted(set(missing_coords)):
            print(f"   - {ortsteil}")
    
    # Create the simple mapping file (PLZ, Ortsteil, Bezirk, Lat, Lon)
    simple_mapping = []
    for entry in enhanced_mapping:
        simple_mapping.append({
            'PLZ': entry['PLZ'],
            'Ortsteil': entry['Ortsteil'],
            'Bezirk': entry['Bezirk'],
            'Lat': entry['Lat'],
            'Lon': entry['Lon']
        })
    
    return enhanced_mapping, simple_mapping

def save_mappings(enhanced_mapping, simple_mapping):
    """Save the mappings to files."""
    
    # Save detailed mapping with statistics
    with open('data/processed/berlin_plz_mapping_detailed.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['PLZ', 'Ortsteil', 'Bezirk', 'Lat', 'Lon', 'Entries', 'Ortsteile_Count'])
        writer.writeheader()
        writer.writerows(enhanced_mapping)
    
    # Save simple mapping for use in analysis
    with open('data/processed/berlin_plz_mapping_enhanced.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['PLZ', 'Ortsteil', 'Bezirk', 'Lat', 'Lon'])
        writer.writeheader()
        writer.writerows(simple_mapping)
    
    print(f"Saved detailed mapping to: data/processed/berlin_plz_mapping_detailed.csv")
    print(f"Saved enhanced mapping to: data/processed/berlin_plz_mapping_enhanced.csv")

def compare_with_old_mapping():
    """Compare with the old Bezirk-only mapping."""
    
    print("\n=== Comparison with old mapping ===")
    
    # Load old mapping
    old_df = pd.read_csv('data/processed/berlin_plz_mapping.csv', dtype={'PLZ': str})
    print(f"Old mapping: {len(old_df)} PLZ → Bezirk entries")
    
    # Load new mapping
    new_df = pd.read_csv('data/processed/berlin_plz_mapping_enhanced.csv', dtype={'PLZ': str})
    print(f"New mapping: {len(new_df)} PLZ → Ortsteil + Coordinates entries")
    
    # Check coordinate coverage
    coords_available = new_df[new_df['Lat'].notna()]
    print(f"Coordinates available: {len(coords_available)} / {len(new_df)} ({100*len(coords_available)/len(new_df):.1f}%)")
    
    # Show some examples where Ortsteil provides more detail
    print("\nExamples of enhanced granularity:")
    for plz in ['10249', '12355', '10553', '13347', '14050']:
        if plz in old_df['PLZ'].values and plz in new_df['PLZ'].values:
            old_bezirk = old_df[old_df['PLZ'] == plz]['Bezirk'].iloc[0]
            new_row = new_df[new_df['PLZ'] == plz].iloc[0]
            new_ortsteil = new_row['Ortsteil']
            new_bezirk = new_row['Bezirk']
            lat, lon = new_row['Lat'], new_row['Lon']
            
            coord_str = f"({lat:.4f}, {lon:.4f})" if pd.notna(lat) else "(no coords)"
            print(f"PLZ {plz}: {old_bezirk} → {new_ortsteil} ({new_bezirk}) {coord_str}")

if __name__ == "__main__":
    print("Creating enhanced PLZ mapping with coordinates...")
    print("=" * 60)
    
    enhanced_mapping, simple_mapping = create_enhanced_plz_mapping()
    
    print(f"\nCreated enhanced mapping with {len(enhanced_mapping)} PLZ entries")
    print(f"Total unique Ortsteile: {len(set(entry['Ortsteil'] for entry in enhanced_mapping))}")
    
    # Count entries with coordinates
    with_coords = sum(1 for entry in enhanced_mapping if entry['Lat'] is not None)
    print(f"Entries with coordinates: {with_coords} / {len(enhanced_mapping)} ({100*with_coords/len(enhanced_mapping):.1f}%)")
    
    save_mappings(enhanced_mapping, simple_mapping)
    
    compare_with_old_mapping()
    
    print("\n" + "=" * 60)
    print("Enhanced PLZ mapping with coordinates created successfully!")
    print("🎯 The new mapping provides Ortsteil-level granularity WITH coordinates!")
    print("🗺️  This enables precise geolocation for the Berlin Housing Market Analysis.")
