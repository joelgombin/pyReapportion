"""
Exemple d'utilisation basique de pyReapportion

Ce script montre comment réapportionner des données d'une géographie à une autre.
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
from pyreapportion import reapportion


def example_count_mode():
    """Exemple simple en mode count (valeurs absolues)"""
    print("=" * 60)
    print("Exemple 1 : Mode COUNT (valeurs absolues)")
    print("=" * 60)

    # Créer une géographie source (2 carrés)
    old_geom = gpd.GeoDataFrame({
        'zone_id': ['A', 'B'],
        'geometry': [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),  # Carré gauche
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])   # Carré droit
        ]
    })

    # Créer une nouvelle géographie (2 rectangles qui se chevauchent différemment)
    new_geom = gpd.GeoDataFrame({
        'secteur_id': ['1', '2'],
        'geometry': [
            Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),  # 75% de A, 50% de B
            Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])   # 50% de B
        ]
    })

    # Données à réapportionner
    data = pd.DataFrame({
        'zone_id': ['A', 'B'],
        'population': [100, 200],
        'emplois': [50, 150]
    })

    print("\nGéographie source:")
    print(old_geom)
    print("\nNouvelle géographie:")
    print(new_geom)
    print("\nDonnées à réapportionner:")
    print(data)

    # Réapportionner
    result = reapportion(
        old_geom=old_geom,
        new_geom=new_geom,
        data=data,
        old_id='zone_id',
        new_id='secteur_id',
        data_id='zone_id',
        variables=['population', 'emplois'],
        mode='count'
    )

    print("\nRésultat du réapportionment:")
    print(result)
    print(f"\nTotal population avant: {data['population'].sum()}")
    print(f"Total population après: {result['population'].sum():.2f}")
    print(f"Conservation de la somme: {abs(data['population'].sum() - result['population'].sum()) < 0.01}")


def example_proportion_mode():
    """Exemple en mode proportion (pourcentages avec poids)"""
    print("\n" + "=" * 60)
    print("Exemple 2 : Mode PROPORTION (pourcentages)")
    print("=" * 60)

    # Géographie source
    old_geom = gpd.GeoDataFrame({
        'quartier': ['Nord', 'Sud'],
        'geometry': [
            Polygon([(0, 0), (2, 0), (2, 1), (0, 1)]),
            Polygon([(0, 1), (2, 1), (2, 2), (0, 2)])
        ]
    })

    # Nouvelle géographie
    new_geom = gpd.GeoDataFrame({
        'district': ['Est', 'Ouest'],
        'geometry': [
            Polygon([(0, 0), (1, 0), (1, 2), (0, 2)]),
            Polygon([(1, 0), (2, 0), (2, 2), (1, 2)])
        ]
    })

    # Données avec proportions (ex: taux de chômage, % de diplômés)
    data = pd.DataFrame({
        'quartier': ['Nord', 'Sud'],
        'taux_chomage': [0.08, 0.12],  # 8% et 12%
        'population': [1000, 1500]      # Poids pour la moyenne
    })

    print("\nDonnées à réapportionner:")
    print(data)

    # Réapportionner
    result = reapportion(
        old_geom=old_geom,
        new_geom=new_geom,
        data=data,
        old_id='quartier',
        new_id='district',
        data_id='quartier',
        variables=['taux_chomage'],
        mode='proportion',
        weights='population'
    )

    print("\nRésultat du réapportionment:")
    print(result)
    print("\nLe taux de chômage est maintenant une moyenne pondérée par la population")


def example_with_weight_matrix():
    """Exemple avec matrice de poids (distribution précise)"""
    print("\n" + "=" * 60)
    print("Exemple 3 : Avec MATRICE DE POIDS (distribution précise)")
    print("=" * 60)

    # Géographie source
    old_geom = gpd.GeoDataFrame({
        'id': ['A', 'B'],
        'geometry': [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
        ]
    })

    # Nouvelle géographie
    new_geom = gpd.GeoDataFrame({
        'id': ['1', '2'],
        'geometry': [
            Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
            Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])
        ]
    })

    # Données
    data = pd.DataFrame({
        'id': ['A', 'B'],
        'population': [100, 200]
    })

    # Matrice de poids : points représentant la localisation réelle des habitants
    # Dans la vraie vie, cela pourrait être des adresses, des bâtiments, etc.
    weight_matrix = gpd.GeoDataFrame({
        'habitants': [20, 30, 50, 40, 80, 80],  # Nombre d'habitants à chaque point
        'geometry': [
            Point(0.2, 0.5), Point(0.8, 0.5),   # Dans A
            Point(1.2, 0.5), Point(1.4, 0.5),   # Dans B (zone qui ira dans 1)
            Point(1.7, 0.5), Point(1.9, 0.5)    # Dans B (zone qui ira dans 2)
        ]
    })

    print("\nMatrice de poids (localisation des habitants):")
    print(weight_matrix[['habitants', 'geometry']])

    # Réapportionner AVEC matrice de poids
    result_with_weights = reapportion(
        old_geom=old_geom,
        new_geom=new_geom,
        data=data,
        old_id='id',
        new_id='id',
        data_id='id',
        variables=['population'],
        mode='count',
        weight_matrix=weight_matrix,
        weight_matrix_var='habitants'
    )

    # Réapportionner SANS matrice de poids (distribution homogène)
    result_without_weights = reapportion(
        old_geom=old_geom,
        new_geom=new_geom,
        data=data,
        old_id='id',
        new_id='id',
        data_id='id',
        variables=['population'],
        mode='count'
    )

    print("\nRésultat AVEC matrice de poids (suit la localisation réelle):")
    print(result_with_weights)

    print("\nRésultat SANS matrice de poids (distribution homogène):")
    print(result_without_weights)

    print("\nDifférence: La matrice de poids permet une redistribution plus précise")


def example_multiple_polygons_same_id():
    """Exemple avec fusion de polygones ayant le même ID"""
    print("\n" + "=" * 60)
    print("Exemple 4 : Fusion de polygones avec le même ID")
    print("=" * 60)

    # Géographie source avec des îles (même ID, géométries séparées)
    old_geom = gpd.GeoDataFrame({
        'commune': ['Paris', 'Paris', 'Marseille'],
        'geometry': [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),      # Paris centre
            Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),      # Paris annexe
            Polygon([(4, 0), (5, 0), (5, 1), (4, 1)])       # Marseille
        ]
    })

    # Nouvelle géographie
    new_geom = gpd.GeoDataFrame({
        'region': ['Ile-de-France', 'PACA'],
        'geometry': [
            Polygon([(0, 0), (3.5, 0), (3.5, 1), (0, 1)]),
            Polygon([(3.5, 0), (5, 0), (5, 1), (3.5, 1)])
        ]
    })

    # Données (une seule ligne pour Paris malgré 2 polygones)
    data = pd.DataFrame({
        'commune': ['Paris', 'Marseille'],
        'population': [2000, 800]
    })

    print("\nGéographie source (Paris a 2 polygones séparés):")
    print(old_geom)

    print("\nDonnées (une seule ligne pour Paris):")
    print(data)

    # Réapportionner
    result = reapportion(
        old_geom=old_geom,
        new_geom=new_geom,
        data=data,
        old_id='commune',
        new_id='region',
        data_id='commune',
        variables=['population'],
        mode='count'
    )

    print("\nRésultat (les polygones de Paris sont automatiquement fusionnés):")
    print(result)


if __name__ == '__main__':
    example_count_mode()
    example_proportion_mode()
    example_with_weight_matrix()
    example_multiple_polygons_same_id()

    print("\n" + "=" * 60)
    print("Tous les exemples ont été exécutés avec succès!")
    print("=" * 60)
