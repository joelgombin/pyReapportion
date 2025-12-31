# Roadmap - Améliorations futures pour pyReapportion

Ce document liste les améliorations potentielles identifiées pour enrichir pyReapportion.

## 🎯 Priorité HAUTE

### 1. Méthodes d'agrégation multiples
**Problème actuel** : Seule la somme (`sum`) est supportée comme méthode d'agrégation.

**Amélioration proposée** :
```python
reapportion(..., aggregation_method='sum')  # ou 'mean', 'median', 'min', 'max', 'std'
```

**Cas d'usage** :
- `mean` : Pour des indicateurs comme le revenu moyen, l'âge moyen
- `median` : Pour des données avec outliers
- `min/max` : Pour des seuils (température min/max, altitude)
- Fonction personnalisée : Flexibilité totale

**Difficulté** : ⭐⭐ Moyenne
**Impact** : ⭐⭐⭐⭐ Élevé

---

### 2. Métriques de qualité du réapportionment
**Problème actuel** : Pas d'indication sur la qualité/fiabilité du réapportionment.

**Amélioration proposée** :
```python
result, metrics = reapportion(..., return_metrics=True)

metrics = {
    'coverage_ratio': 0.98,           # % de surface couverte
    'overlap_complexity': 2.3,         # Complexité des intersections
    'data_loss': 0.02,                # Données perdues (zones non couvertes)
    'confidence_score': {              # Score de confiance par zone
        '1': 0.95,
        '2': 0.87
    }
}
```

**Cas d'usage** : Identifier les zones où le réapportionment est moins fiable

**Difficulté** : ⭐⭐⭐ Moyenne-Haute
**Impact** : ⭐⭐⭐⭐ Élevé

---

### 3. Support GeoDataFrame en sortie
**Problème actuel** : Retourne un DataFrame simple, perd la géométrie.

**Amélioration proposée** :
```python
result = reapportion(..., return_geometry=True)
# result est un GeoDataFrame avec les nouvelles géométries
```

**Cas d'usage** : Visualisation directe, export vers Shapefile/GeoJSON

**Difficulté** : ⭐ Facile
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

### 4. Validation et réparation automatique des géométries
**Problème actuel** : Les géométries invalides peuvent causer des erreurs.

**Amélioration proposée** :
```python
reapportion(..., validate_geometries=True, fix_invalid=True)
```

**Fonctionnalités** :
- Détection de géométries invalides (self-intersecting, etc.)
- Réparation automatique avec `buffer(0)` ou `make_valid()`
- Rapport des problèmes détectés et corrigés

**Difficulté** : ⭐⭐ Moyenne
**Impact** : ⭐⭐⭐⭐ Élevé (robustesse)

---

## 🎨 Priorité MOYENNE

### 5. Outils de visualisation intégrés
**Amélioration proposée** :
```python
from pyreapportion.viz import compare_reapportion

compare_reapportion(
    old_geom, new_geom, data, result,
    variable='population',
    save_path='comparison.png'
)
```

**Fonctionnalités** :
- Cartes avant/après côte à côte
- Heatmap des différences
- Diagramme de Sankey pour le flux entre zones
- Animation de la transition

**Difficulté** : ⭐⭐⭐ Moyenne-Haute
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

### 6. Méthodes d'interpolation spatiale avancées
**Amélioration proposée** :
```python
reapportion(
    ...,
    interpolation_method='area_weighted',  # défaut actuel
    # ou:
    # 'distance_weighted' (IDW),
    # 'dasymetric' (avec layer auxiliaire),
    # 'pycnophylactic' (lissage),
    # 'kriging' (géostatistique)
)
```

**Cas d'usage** :
- **IDW** : Quand la distance compte (pollution, bruit)
- **Dasymetric** : Avec données auxiliaires (occupation du sol, bâti)
- **Pycnophylactic** : Pour garder les densités réalistes
- **Kriging** : Pour données avec autocorrélation spatiale

**Difficulté** : ⭐⭐⭐⭐ Élevée
**Impact** : ⭐⭐⭐⭐⭐ Très élevé (précision)

---

### 7. Support des variables catégorielles
**Problème actuel** : Seulement des variables numériques.

**Amélioration proposée** :
```python
reapportion(
    ...,
    variables=['population'],
    categorical_variables=['type_dominant', 'zone_prioritaire'],
    categorical_method='majority'  # ou 'proportional'
)
```

**Méthodes** :
- `majority` : La catégorie majoritaire (par surface ou poids)
- `proportional` : Distribution proportionnelle de chaque catégorie

**Difficulté** : ⭐⭐⭐ Moyenne-Haute
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

### 8. Cache et optimisation pour grandes données
**Amélioration proposée** :
```python
from pyreapportion import ReapportionCache

cache = ReapportionCache()
result1 = reapportion(..., cache=cache)  # Calcule et met en cache
result2 = reapportion(..., cache=cache)  # Réutilise le cache si même géométrie

# Ou parallélisation automatique
result = reapportion(..., n_jobs=-1)  # Utilise tous les CPU
```

**Fonctionnalités** :
- Cache des intersections géométriques (opération coûteuse)
- Traitement parallèle pour grandes datasets
- Support Dask pour données ne tenant pas en mémoire

**Difficulté** : ⭐⭐⭐⭐ Élevée
**Impact** : ⭐⭐⭐⭐ Élevé (performance)

---

### 9. Export détaillé de la matrice de correspondance
**Amélioration proposée** :
```python
result, mapping = reapportion(..., return_mapping=True)

mapping = pd.DataFrame({
    'old_id': ['A', 'A', 'B'],
    'new_id': ['1', '2', '2'],
    'overlap_area': [0.7, 0.3, 1.0],
    'weight': [0.7, 0.3, 1.0]
})
```

**Cas d'usage** :
- Traçabilité : Savoir d'où viennent les données
- Réappliquabilité : Réutiliser la matrice pour d'autres variables
- Validation : Vérifier manuellement le mapping

**Difficulté** : ⭐⭐ Moyenne
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

## 💡 Priorité BASSE / Nice-to-have

### 10. Interface en ligne de commande (CLI)
```bash
pyreapportion \
  --old-geom iris.shp \
  --new-geom bureaux_vote.shp \
  --data population.csv \
  --output result.csv \
  --variables population,emplois \
  --mode count
```

**Difficulté** : ⭐⭐ Moyenne
**Impact** : ⭐⭐ Moyen

---

### 11. Support de formats supplémentaires
**Amélioration proposée** :
```python
# Chargement automatique depuis fichiers
result = reapportion_from_files(
    old_geom='iris.shp',
    new_geom='bureaux.geojson',
    data='population.csv',
    ...
)

# Export vers différents formats
result.to_shapefile('result.shp')
result.to_geojson('result.geojson')
```

**Difficulté** : ⭐⭐ Moyenne
**Impact** : ⭐⭐ Moyen

---

### 12. Gestion des séries temporelles
**Amélioration proposée** :
```python
# Réapportionment de plusieurs années en une fois
results = reapportion_timeseries(
    old_geom, new_geom,
    data_dict={
        '2020': data_2020,
        '2021': data_2021,
        '2022': data_2022
    },
    ...
)
```

**Difficulté** : ⭐⭐ Moyenne
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

### 13. Mode interactif avec interface graphique
**Amélioration proposée** :
```python
from pyreapportion.gui import interactive_reapportion

# Lance une interface Streamlit/Dash
interactive_reapportion()
```

**Fonctionnalités** :
- Upload de fichiers
- Prévisualisation des géométries
- Configuration interactive
- Export des résultats

**Difficulté** : ⭐⭐⭐⭐ Élevée
**Impact** : ⭐⭐⭐ Moyen-Élevé (accessibilité)

---

### 14. Gestion intelligente des données manquantes
**Amélioration proposée** :
```python
reapportion(
    ...,
    missing_data_strategy='interpolate'  # ou 'mean', 'zero', 'drop', 'raise'
)
```

**Stratégies** :
- `interpolate` : Interpolation spatiale des valeurs manquantes
- `mean` : Remplir avec la moyenne des voisins
- `zero` : Valeurs manquantes = 0
- `drop` : Ignorer les zones avec données manquantes
- `raise` : Lever une erreur (comportement actuel)

**Difficulté** : ⭐⭐⭐ Moyenne-Haute
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

### 15. Support des réseaux (lignes) en plus des polygones
**Amélioration proposée** :
```python
# Réapportionner des données sur des réseaux routiers/ferroviaires
reapportion_network(
    old_network=road_network,
    new_zones=districts,
    data=traffic_data,
    ...
)
```

**Difficulté** : ⭐⭐⭐⭐ Élevée
**Impact** : ⭐⭐⭐ Moyen-Élevé

---

## 📊 Matrice de Priorisation

| Feature | Difficulté | Impact | Priorité | Effort estimé |
|---------|-----------|---------|----------|---------------|
| Méthodes d'agrégation | ⭐⭐ | ⭐⭐⭐⭐ | **HAUTE** | 1-2 semaines |
| Métriques de qualité | ⭐⭐⭐ | ⭐⭐⭐⭐ | **HAUTE** | 2-3 semaines |
| GeoDataFrame output | ⭐ | ⭐⭐⭐ | **HAUTE** | 3-5 jours |
| Validation géométries | ⭐⭐ | ⭐⭐⭐⭐ | **HAUTE** | 1 semaine |
| Visualisation | ⭐⭐⭐ | ⭐⭐⭐ | MOYENNE | 2-3 semaines |
| Interpolation avancée | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | MOYENNE | 4-6 semaines |
| Variables catégorielles | ⭐⭐⭐ | ⭐⭐⭐ | MOYENNE | 1-2 semaines |
| Cache/Performance | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | MOYENNE | 3-4 semaines |
| Matrice de correspondance | ⭐⭐ | ⭐⭐⭐ | MOYENNE | 1 semaine |
| CLI | ⭐⭐ | ⭐⭐ | BASSE | 1 semaine |
| Formats supplémentaires | ⭐⭐ | ⭐⭐ | BASSE | 1 semaine |
| Séries temporelles | ⭐⭐ | ⭐⭐⭐ | BASSE | 1-2 semaines |
| GUI interactive | ⭐⭐⭐⭐ | ⭐⭐⭐ | BASSE | 3-4 semaines |
| Données manquantes | ⭐⭐⭐ | ⭐⭐⭐ | BASSE | 1-2 semaines |
| Support réseaux | ⭐⭐⭐⭐ | ⭐⭐⭐ | BASSE | 4-5 semaines |

---

## 🎯 Roadmap suggérée

### Version 0.2.0 (Quick wins)
- [x] Version 0.1.0 : Fonctionnalité de base ✅
- [ ] GeoDataFrame en sortie
- [ ] Validation des géométries
- [ ] Matrice de correspondance

### Version 0.3.0 (Robustesse)
- [ ] Méthodes d'agrégation multiples
- [ ] Métriques de qualité
- [ ] Variables catégorielles

### Version 0.4.0 (Performance & Viz)
- [ ] Cache et optimisations
- [ ] Outils de visualisation
- [ ] Gestion données manquantes

### Version 1.0.0 (Feature-complete)
- [ ] Interpolation spatiale avancée
- [ ] Séries temporelles
- [ ] CLI
- [ ] Documentation complète

### Version 1.x (Advanced)
- [ ] GUI interactive
- [ ] Support réseaux
- [ ] Intégration avec autres outils (QGIS plugin?)

---

## 💭 Suggestions de la communauté

Si vous avez des idées d'améliorations, ouvrez une issue sur GitHub avec le label `enhancement` !

**Critères d'évaluation** :
- Utilité pour les cas d'usage réels
- Maintenabilité du code
- Compatibilité avec l'API existante
- Performance et scalabilité
