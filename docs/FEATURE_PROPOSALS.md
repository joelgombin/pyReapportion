# Propositions de features détaillées

Ce document détaille les implémentations possibles pour les features prioritaires.

## 1. Méthodes d'agrégation multiples

### API proposée

```python
def reapportion(
    ...,
    aggregation_method: Union[str, Callable] = 'sum',
    aggregation_per_variable: Optional[Dict[str, Union[str, Callable]]] = None
):
    """
    aggregation_method : 'sum', 'mean', 'median', 'min', 'max', 'std', ou fonction custom
    aggregation_per_variable : Méthode différente par variable
    """
```

### Exemple d'utilisation

```python
# Cas 1: Même méthode pour toutes les variables
result = reapportion(
    old_geom, new_geom, data,
    old_id='zone', new_id='secteur', data_id='zone',
    variables=['population', 'surface_batie'],
    mode='count',
    aggregation_method='sum'  # Par défaut
)

# Cas 2: Méthodes différentes par variable
result = reapportion(
    old_geom, new_geom, data,
    old_id='zone', new_id='secteur', data_id='zone',
    variables=['population', 'revenu_median', 'temperature_max'],
    mode='count',
    aggregation_per_variable={
        'population': 'sum',           # Total de population
        'revenu_median': 'median',     # Médiane des revenus
        'temperature_max': 'max'       # Température maximum
    }
)

# Cas 3: Fonction personnalisée
def weighted_percentile_90(values, weights):
    """Calcule le 90e percentile pondéré"""
    import numpy as np
    sorted_idx = np.argsort(values)
    sorted_values = values[sorted_idx]
    sorted_weights = weights[sorted_idx]
    cum_weights = np.cumsum(sorted_weights)
    percentile_idx = np.searchsorted(cum_weights, 0.9 * cum_weights[-1])
    return sorted_values[percentile_idx]

result = reapportion(
    ...,
    aggregation_method=weighted_percentile_90
)
```

### Implémentation suggérée

```python
# Dans reapportion.py

AGGREGATION_METHODS = {
    'sum': lambda df, var: df[var].sum(),
    'mean': lambda df, var: df[var].mean(),
    'median': lambda df, var: df[var].median(),
    'min': lambda df, var: df[var].min(),
    'max': lambda df, var: df[var].max(),
    'std': lambda df, var: df[var].std(),
    'weighted_mean': lambda df, var, weight: (df[var] * df[weight]).sum() / df[weight].sum()
}

# Dans la fonction reapportion, section agrégation:
if aggregation_per_variable:
    agg_dict = {}
    for var in variables:
        method = aggregation_per_variable.get(var, 'sum')
        if isinstance(method, str):
            agg_dict[f'{var}_inpoly'] = AGGREGATION_METHODS[method]
        else:
            agg_dict[f'{var}_inpoly'] = method
else:
    method = aggregation_method
    agg_dict = {f'{var}_inpoly': AGGREGATION_METHODS[method] for var in variables}
```

---

## 2. Métriques de qualité

### API proposée

```python
def reapportion(
    ...,
    return_metrics: bool = False
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
    """
    Si return_metrics=True, retourne (result, metrics)
    """
```

### Exemple d'utilisation

```python
result, metrics = reapportion(
    old_geom, new_geom, data,
    old_id='iris', new_id='bv', data_id='iris',
    variables=['population'],
    return_metrics=True
)

print(metrics)
# {
#     'global': {
#         'coverage_ratio': 0.982,          # 98.2% de surface couverte
#         'total_intersections': 247,       # Nombre d'intersections
#         'avg_splits_per_source': 2.3,     # Moyenne de splits par zone source
#         'data_conservation': 0.999,       # Conservation des données (proche de 1.0)
#         'processing_time': 1.23           # Temps de traitement en secondes
#     },
#     'by_target_zone': {
#         'bv_001': {
#             'n_source_zones': 3,          # Nombre de zones sources contributives
#             'coverage_completeness': 1.0, # Zone complètement couverte
#             'dominant_source': 'iris_75',  # Zone source dominante
#             'confidence': 0.95            # Score de confiance
#         },
#         'bv_002': {
#             'n_source_zones': 1,
#             'coverage_completeness': 0.87,
#             'dominant_source': 'iris_76',
#             'confidence': 0.78
#         },
#         # ...
#     },
#     'warnings': [
#         "Zone 'bv_045' has low coverage (0.65), results may be unreliable",
#         "Zone 'bv_112' is composed of 12 source zones, complexity is high"
#     ]
# }

# Utilisation des métriques pour filtrer les résultats peu fiables
reliable_zones = [
    zone_id for zone_id, m in metrics['by_target_zone'].items()
    if m['confidence'] > 0.8
]
result_filtered = result[result['bv'].isin(reliable_zones)]
```

### Implémentation suggérée

```python
def _compute_metrics(
    intersections: gpd.GeoDataFrame,
    old_geom: gpd.GeoDataFrame,
    new_geom: gpd.GeoDataFrame,
    result: pd.DataFrame,
    processing_time: float
) -> Dict:
    """Calcule les métriques de qualité du réapportionment"""

    metrics = {
        'global': {
            'coverage_ratio': intersections.geometry.area.sum() / new_geom.geometry.area.sum(),
            'total_intersections': len(intersections),
            'avg_splits_per_source': len(intersections) / len(old_geom),
            'processing_time': processing_time
        },
        'by_target_zone': {},
        'warnings': []
    }

    # Métriques par zone cible
    for new_id in result[new_id_col].unique():
        zone_intersections = intersections[intersections['new_id'] == new_id]
        zone_geom = new_geom[new_geom['new_id'] == new_id].geometry.iloc[0]

        # Calcul du score de confiance
        n_sources = len(zone_intersections)
        coverage = zone_intersections.geometry.area.sum() / zone_geom.area

        # Score simple : pénalise faible coverage et haute fragmentation
        confidence = coverage * (1 / (1 + np.log(n_sources)))

        metrics['by_target_zone'][new_id] = {
            'n_source_zones': n_sources,
            'coverage_completeness': coverage,
            'dominant_source': zone_intersections.nlargest(1, 'polyarea')['old_id'].iloc[0],
            'confidence': confidence
        }

        # Warnings
        if coverage < 0.8:
            metrics['warnings'].append(
                f"Zone '{new_id}' has low coverage ({coverage:.2f}), results may be unreliable"
            )
        if n_sources > 10:
            metrics['warnings'].append(
                f"Zone '{new_id}' is composed of {n_sources} source zones, complexity is high"
            )

    return metrics
```

---

## 3. GeoDataFrame en sortie

### API proposée

```python
def reapportion(
    ...,
    return_geometry: bool = False
) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
    """
    Si return_geometry=True, retourne un GeoDataFrame avec géométries
    """
```

### Exemple d'utilisation

```python
# Sans géométrie (comportement actuel)
result = reapportion(...)
print(type(result))  # <class 'pandas.core.frame.DataFrame'>

# Avec géométrie
result_with_geom = reapportion(..., return_geometry=True)
print(type(result_with_geom))  # <class 'geopandas.geodataframe.GeoDataFrame'>

# Visualisation directe
result_with_geom.plot(column='population', legend=True, cmap='YlOrRd')

# Export
result_with_geom.to_file('result.shp')
result_with_geom.to_file('result.geojson', driver='GeoJSON')

# Opérations spatiales
nearby_zones = result_with_geom[
    result_with_geom.distance(point_of_interest) < 1000
]
```

### Implémentation suggérée

```python
# Dans la fonction reapportion, à la fin:

if return_geometry:
    # Joindre les géométries de new_geom au résultat
    result_with_geom = result.merge(
        new_geom[[new_id, 'geometry']],
        on=new_id,
        how='left'
    )
    return gpd.GeoDataFrame(result_with_geom, geometry='geometry', crs=new_geom.crs)
else:
    return result
```

---

## 4. Validation et réparation des géométries

### API proposée

```python
def reapportion(
    ...,
    validate_geometries: bool = True,
    fix_invalid: bool = True,
    validation_report: bool = False
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
    """
    validate_geometries : Vérifier la validité des géométries
    fix_invalid : Tenter de réparer les géométries invalides
    validation_report : Retourner un rapport de validation
    """
```

### Exemple d'utilisation

```python
# Validation simple (par défaut)
result = reapportion(
    old_geom, new_geom, data,
    validate_geometries=True,  # Défaut
    fix_invalid=True           # Défaut
)

# Avec rapport détaillé
result, validation = reapportion(
    old_geom, new_geom, data,
    validation_report=True
)

print(validation)
# {
#     'old_geom': {
#         'valid_count': 98,
#         'invalid_count': 2,
#         'fixed_count': 2,
#         'issues': [
#             {'id': 'iris_045', 'type': 'Self-intersection', 'fixed': True},
#             {'id': 'iris_123', 'type': 'Invalid ring', 'fixed': True}
#         ]
#     },
#     'new_geom': {
#         'valid_count': 150,
#         'invalid_count': 0,
#         'fixed_count': 0,
#         'issues': []
#     }
# }

# Mode strict : lever une erreur si géométries invalides
try:
    result = reapportion(
        old_geom, new_geom, data,
        validate_geometries=True,
        fix_invalid=False  # Ne pas réparer, juste vérifier
    )
except ValueError as e:
    print(f"Géométries invalides détectées: {e}")
    # Réparer manuellement avant de réessayer
```

### Implémentation suggérée

```python
def _validate_and_fix_geometries(
    gdf: gpd.GeoDataFrame,
    name: str,
    fix_invalid: bool = True
) -> Tuple[gpd.GeoDataFrame, Dict]:
    """Valide et répare les géométries"""

    report = {
        'valid_count': 0,
        'invalid_count': 0,
        'fixed_count': 0,
        'issues': []
    }

    gdf = gdf.copy()

    for idx, row in gdf.iterrows():
        geom = row.geometry

        if geom.is_valid:
            report['valid_count'] += 1
        else:
            report['invalid_count'] += 1
            issue_type = explain_validity(geom)  # Shapely 2.0+

            if fix_invalid:
                try:
                    # Méthode 1: buffer(0)
                    fixed_geom = geom.buffer(0)
                    if not fixed_geom.is_valid:
                        # Méthode 2: make_valid (Shapely 2.0+)
                        from shapely import make_valid
                        fixed_geom = make_valid(geom)

                    gdf.at[idx, 'geometry'] = fixed_geom
                    report['fixed_count'] += 1
                    report['issues'].append({
                        'id': row[id_col],
                        'type': issue_type,
                        'fixed': True
                    })
                except Exception as e:
                    report['issues'].append({
                        'id': row[id_col],
                        'type': issue_type,
                        'fixed': False,
                        'error': str(e)
                    })
            else:
                report['issues'].append({
                    'id': row[id_col],
                    'type': issue_type,
                    'fixed': False
                })

    if not fix_invalid and report['invalid_count'] > 0:
        raise ValueError(
            f"{name} contains {report['invalid_count']} invalid geometries. "
            f"Set fix_invalid=True to attempt automatic repair."
        )

    return gdf, report
```

---

## 5. Interpolation dasymetric (exemple avancé)

### Concept

L'interpolation dasymetric utilise des données auxiliaires (ex: occupation du sol, densité de bâti)
pour améliorer la redistribution des données.

### API proposée

```python
def reapportion(
    ...,
    interpolation_method: str = 'area_weighted',
    ancillary_data: Optional[gpd.GeoDataFrame] = None,
    ancillary_weight_var: Optional[str] = None
):
    """
    interpolation_method :
        - 'area_weighted' (défaut) : Distribution proportionnelle à l'aire
        - 'dasymetric' : Utilise ancillary_data pour affiner
        - 'pycnophylactic' : Lissage avec conservation de masse
    """
```

### Exemple d'utilisation

```python
# Données auxiliaires : occupation du sol
land_use = gpd.read_file('land_use.shp')
# land_use contient des polygones avec 'type' = 'residential', 'commercial', etc.

# On veut réapportionner la population
# Hypothèse : population principalement dans zones résidentielles
result = reapportion(
    old_geom=communes,
    new_geom=quartiers,
    data=population_data,
    old_id='commune_id',
    new_id='quartier_id',
    data_id='commune_id',
    variables=['population'],
    mode='count',
    interpolation_method='dasymetric',
    ancillary_data=land_use,
    ancillary_weight_var='residential_density'  # Colonne de pondération
)

# Le réapportionment sera plus précis car il concentre la population
# dans les zones résidentielles plutôt que de la distribuer uniformément
```

### Schéma conceptuel

```
Sans dasymetric (area_weighted):
┌─────────────────┐
│  Commune A      │
│  Pop: 1000      │
│  ┌──────┬───────┤
│  │ Q1   │  Q2   │
│  │ 50%  │  50%  │  → Q1 = 500, Q2 = 500 (distribution uniforme)
│  └──────┴───────┘
└─────────────────┘

Avec dasymetric (zones résidentielles):
┌─────────────────┐
│  Commune A      │
│  Pop: 1000      │
│  ┌──────┬───────┤
│  │ Q1   │  Q2   │
│  │ 🏘️🏘️ │  🏭   │  → Q1 = 900, Q2 = 100 (suit la densité résidentielle)
│  │ 90%  │  10%  │
│  └──────┴───────┘
└─────────────────┘
```

---

## Prochaines étapes

1. **Priorisation** : Discuter avec la communauté pour prioriser
2. **Prototypage** : Créer des branches de développement pour chaque feature
3. **Tests** : Ajouter des tests pour chaque nouvelle fonctionnalité (TDD)
4. **Documentation** : Documenter les nouvelles API
5. **Benchmarks** : Évaluer l'impact sur les performances

---

## Questions ouvertes

- **Rétrocompatibilité** : Comment maintenir la compatibilité avec v0.1.0 ?
- **Performance** : Quel est le coût de la validation automatique ?
- **Defaults** : Quels devraient être les comportements par défaut ?
- **Extensibilité** : Comment permettre aux utilisateurs d'ajouter leurs propres méthodes ?

Feedback bienvenu !
