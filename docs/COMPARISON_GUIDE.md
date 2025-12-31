# Guide : Choisir entre pyReapportion, tobler et autres

## 🤔 Quel outil pour quel besoin ?

### Décision rapide en 30 secondes

```
Votre besoin ?
│
├─ Transférer simplement des données entre géographies
│  → ✅ pyReapportion (le plus simple !)
│
├─ Utiliser des données satellite/occupation du sol
│  → ✅ tobler (dasymetric mapping)
│
├─ Modélisation géostatistique (kriging, variogrammes)
│  → ✅ pyinterpolate
│
├─ Millions de polygones en production
│  → ✅ tobler (parallélisation, optimisé)
│
└─ Migrer du code R (spReapportion)
   → ✅ pyReapportion (port direct)
```

---

## 📊 Comparaison visuelle rapide

### Simplicité d'usage

```
⭐⭐⭐⭐⭐  pyReapportion    (le + simple)
⭐⭐⭐⭐    GeoPandas DIY
⭐⭐⭐      tobler           (écosystème PySAL)
⭐⭐        pyinterpolate   (technique)
```

### Puissance fonctionnelle

```
⭐⭐⭐⭐⭐  tobler           (le + complet)
⭐⭐⭐⭐    pyinterpolate   (spécialiste kriging)
⭐⭐⭐      pyReapportion   (cas standards)
⭐⭐        GeoPandas DIY
```

### Performance sur grandes données

```
⭐⭐⭐⭐⭐  tobler           (parallèle, optimisé)
⭐⭐⭐      GeoPandas
⭐⭐        pyReapportion
⭐⭐        pyinterpolate
```

---

## 💻 Comparaison de code côte à côte

### Cas simple : Transférer population entre géographies

#### Avec pyReapportion (le plus simple)

```python
from pyreapportion import reapportion
import geopandas as gpd
import pandas as pd

# Charger les données
old_zones = gpd.read_file('iris.shp')
new_zones = gpd.read_file('secteurs.shp')
data = pd.read_csv('population.csv')

# Une seule ligne !
result = reapportion(
    old_zones, new_zones, data,
    old_id='iris_id', new_id='secteur_id', data_id='iris_id',
    variables=['population', 'emplois']
)
```

**✅ Avantages** :
- API ultra-simple
- Gestion auto du CRS
- Fusion auto des polygones dupliqués
- Gestion zones sans intersection

#### Avec tobler

```python
from tobler.area_weighted import area_interpolate
import geopandas as gpd

# Charger les données
old_zones = gpd.read_file('iris.shp')
new_zones = gpd.read_file('secteurs.shp')

# Préparation : fusionner data dans géométries
old_zones = old_zones.merge(data, left_on='iris_id', right_on='iris_id')

# Vérifier/aligner CRS manuellement
if old_zones.crs != new_zones.crs:
    new_zones = new_zones.to_crs(old_zones.crs)

# Interpolation
result = area_interpolate(
    source_df=old_zones,
    target_df=new_zones,
    extensive_variables=['population', 'emplois']
)
```

**✅ Avantages** :
- Plus de contrôle
- Distinction extensive/intensive explicite
- Parallélisation possible (n_jobs)

**❌ Inconvénients** :
- Plus verbeux
- Gestion manuelle CRS
- Fusion data manuelle

#### Avec GeoPandas (DIY)

```python
import geopandas as gpd
import pandas as pd

# Charger
old_zones = gpd.read_file('iris.shp')
new_zones = gpd.read_file('secteurs.shp')
data = pd.read_csv('population.csv')

# Fusionner data
old_zones = old_zones.merge(data, left_on='iris_id', right_on='iris_id')

# Aligner CRS
if old_zones.crs != new_zones.crs:
    new_zones = new_zones.to_crs(old_zones.crs)

# Calculer intersections
intersections = gpd.overlay(old_zones, new_zones, how='intersection')

# Calculer aires
intersections['inter_area'] = intersections.geometry.area
old_zones['total_area'] = old_zones.geometry.area
intersections = intersections.merge(
    old_zones[['iris_id', 'total_area']],
    on='iris_id'
)

# Calculer proportions
intersections['ratio'] = intersections['inter_area'] / intersections['total_area']

# Réapportionner chaque variable
for var in ['population', 'emplois']:
    intersections[f'{var}_allocated'] = intersections[var] * intersections['ratio']

# Agréger
result = intersections.groupby('secteur_id').agg({
    'population_allocated': 'sum',
    'emplois_allocated': 'sum'
}).reset_index()

# Renommer
result.columns = ['secteur_id', 'population', 'emplois']
```

**✅ Avantages** :
- Contrôle total
- Pas de dépendances supplémentaires

**❌ Inconvénients** :
- Beaucoup de code boilerplate
- Facile de faire des erreurs
- Pas de réutilisabilité

---

## 🎯 Matrice de décision

| Critère | pyReapportion | tobler | pyinterpolate | GeoPandas DIY |
|---------|---------------|--------|---------------|---------------|
| **Débutant en GIS** | 🟢 Parfait | 🟡 OK | 🔴 Difficile | 🔴 Difficile |
| **Projet de recherche** | 🟢 Bien | 🟢 Excellent | 🟢 Excellent | 🟡 OK |
| **Production** | 🟡 Petites données | 🟢 Toutes tailles | 🟡 OK | 🟡 OK |
| **Prototype rapide** | 🟢 Parfait | 🟡 OK | 🔴 Lent | 🔴 Lent |
| **Migration R→Python** | 🟢 Parfait | 🟡 Adaptation | 🔴 Différent | 🔴 Réécriture |
| **Besoin dasymetric** | 🔴 Non supporté | 🟢 Excellent | 🔴 Non | 🔴 Manuel |
| **Besoin kriging** | 🔴 Non supporté | 🔴 Non | 🟢 Excellent | 🔴 Non |

---

## 📚 Cas d'usage réels

### 1. Sciences sociales / Démographie

**Besoin** : Harmoniser données recensement sur périodes multiples

```python
# Les frontières des IRIS changent dans le temps
# Besoin de normaliser sur une géographie fixe

# ✅ RECOMMANDÉ : pyReapportion (simple, direct)
result_2010 = reapportion(iris_2010, grid_fixe, data_2010, ...)
result_2015 = reapportion(iris_2015, grid_fixe, data_2015, ...)
result_2020 = reapportion(iris_2020, grid_fixe, data_2020, ...)

# Analyse temporelle maintenant possible
```

**Alternative** : tobler si données massives ou besoin dasymetric

---

### 2. Analyse électorale

**Besoin** : Croiser résultats électoraux (bureaux de vote) avec données socio (IRIS)

```python
# Données électorales par bureau de vote
# Données socio-économiques par IRIS
# Besoin : tout sur la même géographie

# ✅ RECOMMANDÉ : pyReapportion
donnees_iris_vers_bv = reapportion(
    iris_geom, bureaux_vote_geom, donnees_iris,
    old_id='iris', new_id='bureau', data_id='iris',
    variables=['pct_chomage', 'revenu_median'],
    mode='proportion',  # Ce sont des taux
    weights='population'
)

# Maintenant on peut corréler avec résultats électoraux
```

---

### 3. Planification urbaine

**Besoin** : Estimer population dans nouvelles zones d'aménagement avec données satellite

```python
# Utiliser occupation du sol pour affiner estimation

# ✅ RECOMMANDÉ : tobler (dasymetric)
from tobler.dasymetric import masked_area_interpolate

result = masked_area_interpolate(
    source_df=quartiers_existants,
    target_df=nouvelles_zones,
    raster='occupation_sol.tif',  # Zones habitées
    extensive_variables=['population'],
    codes=[21, 22, 23, 24]  # Codes occupation résidentielle
)
```

**Pourquoi pas pyReapportion** : Besoin de données auxiliaires (raster)

---

### 4. Épidémiologie

**Besoin** : Modéliser propagation maladie avec autocorrélation spatiale

```python
# Cas de maladie avec dépendance spatiale
# Besoin kriging pour interpolation

# ✅ RECOMMANDÉ : pyinterpolate
from pyinterpolate import kriging

# Variogramme
variogram = TheoreticalVariogram()
variogram.autofit(points, values)

# Kriging
predictions = kriging(
    unknown_points,
    known_points,
    known_values,
    variogram_model=variogram
)
```

**Pourquoi pas pyReapportion** : Besoin de modélisation géostatistique

---

### 5. Migration depuis R

**Besoin** : Porter un projet R existant vers Python

```R
# Code R original (spReapportion)
library(spReapportion)

result <- spReapportion(
  old_geom = iris,
  new_geom = secteurs,
  data = donnees,
  old_ID = "iris_id",
  new_ID = "secteur_id",
  data_ID = "iris_id",
  variables = c("population", "emplois"),
  mode = "count"
)
```

```python
# ✅ RECOMMANDÉ : pyReapportion (port quasi-identique)
from pyreapportion import reapportion

result = reapportion(
    old_geom=iris,
    new_geom=secteurs,
    data=donnees,
    old_id='iris_id',
    new_id='secteur_id',
    data_id='iris_id',
    variables=['population', 'emplois'],
    mode='count'
)
```

**Avantage** : Migration quasi-transparente, concepts identiques

---

## 🤝 Peut-on les utiliser ensemble ?

### Oui ! Ils sont complémentaires

```python
from pyreapportion import reapportion
from tobler.dasymetric import masked_area_interpolate

# Cas 1 : Simple réapportionment
result_simple = reapportion(old, new, data, ...)

# Cas 2 : Besoin de plus de précision avec raster
result_precis = masked_area_interpolate(
    old, new,
    raster='landuse.tif',
    extensive_variables=['population']
)

# Utiliser le bon outil pour chaque besoin !
```

---

## ✅ Résumé des recommandations

### Utilisez pyReapportion si :
- ✅ Vous débutez en géospatial Python
- ✅ Besoin simple et rapide
- ✅ Migrez depuis R (spReapportion)
- ✅ Projet de taille petite/moyenne
- ✅ Vous voulez du "ça marche du premier coup"

### Utilisez tobler si :
- ✅ Besoin de dasymetric mapping (raster/vecteur auxiliaire)
- ✅ Projet de grande échelle (millions de polygones)
- ✅ Besoin de parallélisation
- ✅ Vous travaillez déjà avec PySAL
- ✅ Besoin de méthodes model-based

### Utilisez pyinterpolate si :
- ✅ Besoin de kriging / géostatistique
- ✅ Modélisation d'autocorrélation spatiale
- ✅ Variables avec structure spatiale complexe
- ✅ Recherche scientifique en statistique spatiale

### Utilisez GeoPandas (DIY) si :
- ✅ Besoin très spécifique non couvert
- ✅ Vous voulez contrôle total
- ✅ Projet d'apprentissage
- ✅ Minimiser les dépendances

---

## 📞 Besoin d'aide pour choisir ?

Posez-vous ces questions :

1. **Ai-je des données auxiliaires (raster/satellite) ?**
   - Non → pyReapportion
   - Oui → tobler

2. **Besoin de modélisation statistique spatiale ?**
   - Non → pyReapportion
   - Oui → pyinterpolate ou tobler

3. **Taille des données ?**
   - < 10k polygones → pyReapportion
   - > 100k polygones → tobler

4. **Expérience en GIS Python ?**
   - Débutant → pyReapportion
   - Expert → tobler ou DIY

5. **Migrez depuis R ?**
   - Oui → pyReapportion
   - Non → Peu importe

---

## 📚 Ressources

- [pyReapportion Documentation](../README.md)
- [tobler Documentation](https://pysal.org/tobler/)
- [pyinterpolate Documentation](https://pyinterpolate.readthedocs.io/)
- [GeoPandas Overlay Guide](https://geopandas.org/en/stable/docs/user_guide/set_operations.html)

---

**Mise à jour** : 2025-12-31
