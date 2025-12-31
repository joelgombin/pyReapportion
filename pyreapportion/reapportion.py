"""
Fonction principale de réapportionment spatial
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from typing import List, Optional, Union


def reapportion(
    old_geom: gpd.GeoDataFrame,
    new_geom: gpd.GeoDataFrame,
    data: pd.DataFrame,
    old_id: str,
    new_id: str,
    data_id: str,
    variables: Optional[List[str]] = None,
    mode: str = "count",
    weights: Optional[str] = None,
    weight_matrix: Optional[gpd.GeoDataFrame] = None,
    weight_matrix_var: Optional[str] = None
) -> pd.DataFrame:
    """
    Réapportionner des données d'une géographie à une autre.

    Cette fonction permet de redistribuer des données numériques d'un ensemble
    de polygones vers un autre ensemble de polygones en utilisant des intersections
    spatiales.

    Parameters
    ----------
    old_geom : gpd.GeoDataFrame
        GeoDataFrame contenant la géométrie initiale (polygones source)
    new_geom : gpd.GeoDataFrame
        GeoDataFrame contenant la géométrie cible (polygones de destination)
    data : pd.DataFrame
        DataFrame contenant les données à réapportionner
    old_id : str
        Nom de la colonne d'identifiant dans old_geom
    new_id : str
        Nom de la colonne d'identifiant dans new_geom
    data_id : str
        Nom de la colonne d'identifiant dans data
    variables : List[str], optional
        Liste des noms de colonnes à réapportionner.
        Par défaut, toutes les colonnes sauf data_id
    mode : str, default "count"
        Mode de réapportionment : "count" pour valeurs absolues,
        "proportion" pour proportions (0-1)
    weights : str, optional
        En mode "proportion", nom de la colonne contenant les poids
    weight_matrix : gpd.GeoDataFrame, optional
        GeoDataFrame de points avec pondération spatiale
    weight_matrix_var : str, optional
        Nom de la colonne de poids dans weight_matrix

    Returns
    -------
    pd.DataFrame
        DataFrame avec les données réapportionnées sur la nouvelle géographie

    Raises
    ------
    ValueError
        Si les paramètres sont invalides ou les colonnes n'existent pas

    Examples
    --------
    >>> old_geom = gpd.GeoDataFrame({
    ...     'id': ['A', 'B'],
    ...     'geometry': [polygon_a, polygon_b]
    ... })
    >>> new_geom = gpd.GeoDataFrame({
    ...     'id': ['1', '2'],
    ...     'geometry': [polygon_1, polygon_2]
    ... })
    >>> data = pd.DataFrame({'id': ['A', 'B'], 'pop': [100, 200]})
    >>> result = reapportion(old_geom, new_geom, data, 'id', 'id', 'id', ['pop'])
    """

    # Validation des paramètres
    if old_id not in old_geom.columns:
        raise ValueError(f"{old_id} is not a variable from old_geom!")

    if new_id not in new_geom.columns:
        raise ValueError(f"{new_id} is not a variable from new_geom!")

    # Si variables n'est pas spécifié, utiliser toutes les colonnes sauf data_id
    if variables is None:
        variables = [col for col in data.columns if col != data_id]

    # Vérifier que toutes les variables existent dans data
    for var in variables:
        if var not in data.columns:
            raise ValueError(f"{var} is not a variable from data!")

    # Vérifier le mode proportion
    if mode == "proportion" and weights is None:
        raise ValueError("When mode = 'proportion', you must provide weights.")

    if mode == "proportion" and weights is not None:
        if weights not in data.columns:
            raise ValueError(f"{weights} is not a variable from data!")

    # Copier les géométries pour ne pas modifier les originaux
    old_geom = old_geom.copy()
    new_geom = new_geom.copy()
    data = data.copy()

    # Fusionner les polygones avec le même ID si nécessaire
    if len(old_geom[old_id]) > len(old_geom[old_id].unique()):
        old_geom = old_geom.dissolve(by=old_id, as_index=False)

    if len(new_geom[new_id]) > len(new_geom[new_id].unique()):
        new_geom = new_geom.dissolve(by=new_id, as_index=False)

    # Renommer data_id en old_id pour faciliter les jointures
    data = data.rename(columns={data_id: 'old_id'})
    old_geom = old_geom.rename(columns={old_id: 'old_id'})
    new_geom = new_geom.rename(columns={new_id: 'new_id'})

    # S'assurer que les deux géométries ont la même projection
    if old_geom.crs != new_geom.crs:
        new_geom = new_geom.to_crs(old_geom.crs)

    # Gérer la matrice de poids si fournie
    use_weight_matrix = weight_matrix is not None
    if use_weight_matrix:
        # S'assurer que la matrice de poids a la même projection
        if weight_matrix.crs != old_geom.crs:
            weight_matrix = weight_matrix.to_crs(old_geom.crs)

        # Filtrer les points qui sont dans old_geom
        weight_matrix = weight_matrix[weight_matrix.within(old_geom.unary_union)]

        # Joindre les identifiants old_id aux points
        weight_matrix = gpd.sjoin(weight_matrix, old_geom[['old_id', 'geometry']],
                                  how='left', predicate='within')

    # Filtrer les polygones old_geom qui intersectent new_geom
    old_geom_filtered = old_geom[old_geom.intersects(new_geom.unary_union)]

    if len(old_geom_filtered) == 0:
        # Pas d'intersection, retourner un DataFrame vide ou avec des valeurs nulles
        result = pd.DataFrame({
            new_id: new_geom['new_id'].unique()  # Utiliser le nom original
        })
        for var in variables:
            result[var] = 0.0 if mode == "count" else np.nan
        if mode == "proportion" and weights:
            result[weights] = 0.0
        return result

    # Calculer les intersections
    intersections = gpd.overlay(old_geom_filtered, new_geom, how='intersection')

    # Calculer les aires ou utiliser les poids
    if use_weight_matrix:
        # Utiliser la matrice de poids
        # Pour chaque intersection, compter les points qui tombent dedans
        intersection_weights = []
        old_weights = []

        for idx, row in intersections.iterrows():
            # Points dans cette intersection
            points_in_intersection = weight_matrix[
                weight_matrix.within(row.geometry)
            ]
            weight_sum = points_in_intersection[weight_matrix_var].sum()
            intersection_weights.append(weight_sum)

            # Poids total dans l'ancien polygone
            old_poly_weight = weight_matrix[
                weight_matrix['old_id'] == row['old_id']
            ][weight_matrix_var].sum()
            old_weights.append(old_poly_weight)

        intersections['polyarea'] = intersection_weights
        intersections['departarea'] = old_weights
    else:
        # Utiliser les aires géométriques
        intersections['polyarea'] = intersections.geometry.area

        # Calculer l'aire de chaque ancien polygone
        old_areas = old_geom_filtered.set_index('old_id').geometry.area
        intersections['departarea'] = intersections['old_id'].map(old_areas)

    # Joindre avec les données
    intersections = intersections.merge(data, on='old_id', how='left')

    # Calculer les valeurs réapportionnées
    if mode == "count":
        # Mode count : valeur * (aire_intersection / aire_source)
        for var in variables:
            intersections[f'{var}_inpoly'] = (
                intersections[var] * (intersections['polyarea'] / intersections['departarea'])
            )

        # Agréger par new_id
        agg_dict = {f'{var}_inpoly': 'sum' for var in variables}
        result = intersections.groupby('new_id', as_index=False).agg(agg_dict)

        # Renommer les colonnes
        result.columns = ['new_id'] + variables

    else:  # mode == "proportion"
        # Mode proportion : (valeur * poids) * (aire_intersection / aire_source) / poids_total
        for var in variables:
            intersections[f'{var}_inpoly'] = (
                intersections[var] * intersections[weights] *
                (intersections['polyarea'] / intersections['departarea'])
            )

        intersections['weights_inpoly'] = (
            intersections[weights] * (intersections['polyarea'] / intersections['departarea'])
        )

        # Agréger par new_id
        agg_dict = {f'{var}_inpoly': 'sum' for var in variables}
        agg_dict['weights_inpoly'] = 'sum'
        result = intersections.groupby('new_id', as_index=False).agg(agg_dict)

        # Calculer les proportions
        for var in variables:
            result[var] = result[f'{var}_inpoly'] / result['weights_inpoly']
            result = result.drop(columns=[f'{var}_inpoly'])

        # Renommer la colonne weights
        result = result.rename(columns={'weights_inpoly': weights})

    # Renommer new_id avec le nom original
    result = result.rename(columns={'new_id': new_id})

    return result
