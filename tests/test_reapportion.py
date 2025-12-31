"""
Tests pour la fonction reapportion
Suivant la méthode TDD, ces tests sont écrits avant l'implémentation
"""

import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
from pyreapportion import reapportion


class TestReapportionValidation:
    """Tests de validation des paramètres"""

    def test_old_id_not_in_old_geom(self):
        """Le old_id doit exister dans old_geom"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])]
        })
        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
                        Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])]
        })
        data = pd.DataFrame({'id': ['A', 'B'], 'pop': [100, 200]})

        with pytest.raises(ValueError, match="nonexistent_id.*not.*variable"):
            reapportion(old_geom, new_geom, data,
                       old_id='nonexistent_id', new_id='id', data_id='id',
                       variables=['pop'])

    def test_new_id_not_in_new_geom(self):
        """Le new_id doit exister dans new_geom"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])]
        })
        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
                        Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])]
        })
        data = pd.DataFrame({'id': ['A', 'B'], 'pop': [100, 200]})

        with pytest.raises(ValueError, match="nonexistent_id.*not.*variable"):
            reapportion(old_geom, new_geom, data,
                       old_id='id', new_id='nonexistent_id', data_id='id',
                       variables=['pop'])

    def test_variables_not_in_data(self):
        """Les variables doivent exister dans data"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])]
        })
        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
                        Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])]
        })
        data = pd.DataFrame({'id': ['A', 'B'], 'pop': [100, 200]})

        with pytest.raises(ValueError, match="nonexistent_var.*not.*variable"):
            reapportion(old_geom, new_geom, data,
                       old_id='id', new_id='id', data_id='id',
                       variables=['nonexistent_var'])

    def test_proportion_mode_requires_weights(self):
        """Le mode proportion nécessite des poids"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])]
        })
        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
                        Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])]
        })
        data = pd.DataFrame({'id': ['A', 'B'], 'proportion': [0.3, 0.4]})

        with pytest.raises(ValueError, match="mode.*proportion.*must provide weights"):
            reapportion(old_geom, new_geom, data,
                       old_id='id', new_id='id', data_id='id',
                       variables=['proportion'], mode='proportion')

    def test_weights_not_in_data(self):
        """La variable de poids doit exister dans data"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])]
        })
        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
                        Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])]
        })
        data = pd.DataFrame({'id': ['A', 'B'], 'proportion': [0.3, 0.4]})

        with pytest.raises(ValueError, match="nonexistent_weight.*not.*variable"):
            reapportion(old_geom, new_geom, data,
                       old_id='id', new_id='id', data_id='id',
                       variables=['proportion'], mode='proportion',
                       weights='nonexistent_weight')


class TestReapportionBasicFunctionality:
    """Tests de fonctionnalité de base"""

    def test_simple_reapportion_count_mode(self):
        """Test simple de réapportionment en mode count"""
        # Deux carrés de 1x1
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),  # Carré gauche
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])   # Carré droit
            ]
        })

        # Deux nouveaux carrés qui se chevauchent à 50% avec les anciens
        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [
                Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),  # Chevauche A (1.0) et B (0.5)
                Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])   # Chevauche B (0.5)
            ]
        })

        # Population de 100 dans A et 200 dans B
        data = pd.DataFrame({
            'id': ['A', 'B'],
            'pop': [100, 200]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop'],
            mode='count'
        )

        # Vérifications
        assert isinstance(result, pd.DataFrame)
        assert 'id' in result.columns
        assert 'pop' in result.columns
        assert len(result) == 2

        # Zone 1 devrait avoir : 100 (tout A) + 100 (50% de B)
        result_1 = result[result['id'] == '1']['pop'].values[0]
        assert np.isclose(result_1, 200, rtol=0.01)

        # Zone 2 devrait avoir : 100 (50% de B)
        result_2 = result[result['id'] == '2']['pop'].values[0]
        assert np.isclose(result_2, 100, rtol=0.01)

    def test_reapportion_with_multiple_variables(self):
        """Test avec plusieurs variables"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A'],
            'geometry': [Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
            ]
        })

        data = pd.DataFrame({
            'id': ['A'],
            'pop': [200],
            'votes': [150]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop', 'votes'],
            mode='count'
        )

        # Chaque nouvelle zone devrait avoir 50% des valeurs
        assert len(result) == 2
        assert all(np.isclose(result['pop'], 100, rtol=0.01))
        assert all(np.isclose(result['votes'], 75, rtol=0.01))

    def test_reapportion_proportion_mode(self):
        """Test du mode proportion"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
            ]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1'],
            'geometry': [Polygon([(0, 0), (2, 0), (2, 1), (0, 1)])]
        })

        # Proportions avec poids
        data = pd.DataFrame({
            'id': ['A', 'B'],
            'prop': [0.3, 0.5],  # Proportions
            'total': [100, 200]  # Poids
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['prop'],
            mode='proportion',
            weights='total'
        )

        # La proportion résultante devrait être la moyenne pondérée
        # (0.3 * 100 + 0.5 * 200) / (100 + 200) = (30 + 100) / 300 = 0.433
        assert len(result) == 1
        assert np.isclose(result['prop'].values[0], 0.433, rtol=0.01)

    def test_default_variables_parameter(self):
        """Test que variables par défaut inclut toutes les colonnes sauf l'ID"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        data = pd.DataFrame({
            'id': ['A'],
            'pop': [100],
            'votes': [75],
            'area': [50]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id'
            # variables non spécifié, devrait utiliser toutes les colonnes sauf 'id'
        )

        assert 'pop' in result.columns
        assert 'votes' in result.columns
        assert 'area' in result.columns


class TestReapportionEdgeCases:
    """Tests des cas limites"""

    def test_no_intersection(self):
        """Test quand il n'y a pas d'intersection"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1'],
            'geometry': [Polygon([(10, 10), (11, 10), (11, 11), (10, 11)])]
        })

        data = pd.DataFrame({
            'id': ['A'],
            'pop': [100]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop']
        )

        # Devrait retourner un DataFrame avec la nouvelle zone mais des valeurs à 0 ou NaN
        assert len(result) == 1
        assert result['id'].values[0] == '1'

    def test_duplicate_polygons_same_id(self):
        """Test quand plusieurs polygones ont le même ID (fusion nécessaire)"""
        # Deux polygones séparés avec le même ID
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'A'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
            ]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1'],
            'geometry': [Polygon([(0, 0), (3, 0), (3, 1), (0, 1)])]
        })

        data = pd.DataFrame({
            'id': ['A'],
            'pop': [200]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop']
        )

        # Devrait fusionner les polygones et réapportionner correctement
        # Les deux carrés A (aire totale 2) sont complètement couverts par la nouvelle zone
        # Donc on devrait avoir toute la population (200)
        assert len(result) == 1
        assert np.isclose(result['pop'].values[0], 200, rtol=0.01)

    def test_different_crs(self):
        """Test avec des systèmes de coordonnées différents"""
        # old_geom en WGS84
        old_geom = gpd.GeoDataFrame({
            'id': ['A'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        }, crs='EPSG:4326')

        # new_geom en Web Mercator
        new_geom = gpd.GeoDataFrame({
            'id': ['1'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        }, crs='EPSG:3857')

        data = pd.DataFrame({
            'id': ['A'],
            'pop': [100]
        })

        # Devrait automatiquement reprojeter
        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop']
        )

        # Devrait réussir sans erreur
        assert len(result) == 1


class TestReapportionWithWeightMatrix:
    """Tests avec matrice de poids"""

    def test_reapportion_with_weight_matrix(self):
        """Test avec une matrice de poids (points)"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A', 'B'],
            'geometry': [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
            ]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1', '2'],
            'geometry': [
                Polygon([(0, 0), (1.5, 0), (1.5, 1), (0, 1)]),
                Polygon([(1.5, 0), (2, 0), (2, 1), (1.5, 1)])
            ]
        })

        data = pd.DataFrame({
            'id': ['A', 'B'],
            'pop': [100, 200]
        })

        # Matrice de poids : points avec des poids
        # A a 2 points de poids 1, B a 4 points de poids 1
        weight_matrix = gpd.GeoDataFrame({
            'weight': [1, 1, 1, 1, 1, 1],
            'geometry': [
                Point(0.25, 0.5), Point(0.75, 0.5),  # Dans A
                Point(1.25, 0.5), Point(1.5, 0.5),   # Dans B
                Point(1.75, 0.5), Point(1.9, 0.5)    # Dans B
            ]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop'],
            mode='count',
            weight_matrix=weight_matrix,
            weight_matrix_var='weight'
        )

        # La distribution devrait suivre la localisation des points
        # plutôt que simplement les aires
        assert len(result) == 2
        assert 'pop' in result.columns


class TestReapportionReturnFormat:
    """Tests du format de retour"""

    def test_return_dataframe(self):
        """Test que la fonction retourne un DataFrame"""
        old_geom = gpd.GeoDataFrame({
            'id': ['A'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        new_geom = gpd.GeoDataFrame({
            'id': ['1'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        data = pd.DataFrame({
            'id': ['A'],
            'pop': [100]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='id',
            new_id='id',
            data_id='id',
            variables=['pop']
        )

        assert isinstance(result, pd.DataFrame)
        assert not isinstance(result, gpd.GeoDataFrame)  # Devrait être un DataFrame simple

    def test_return_has_new_id_column(self):
        """Test que le résultat a une colonne avec le new_id"""
        old_geom = gpd.GeoDataFrame({
            'old_zone': ['A'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        new_geom = gpd.GeoDataFrame({
            'new_zone': ['1'],
            'geometry': [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])]
        })

        data = pd.DataFrame({
            'zone': ['A'],
            'pop': [100]
        })

        result = reapportion(
            old_geom=old_geom,
            new_geom=new_geom,
            data=data,
            old_id='old_zone',
            new_id='new_zone',
            data_id='zone',
            variables=['pop']
        )

        assert 'new_zone' in result.columns
        assert 'old_zone' not in result.columns
