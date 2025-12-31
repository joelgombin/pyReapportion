# Contributing to pyReapportion

Merci de votre intérêt pour contribuer à pyReapportion !

## Développement

### Installation pour le développement

```bash
git clone https://github.com/joelgombin/pyReapportion.git
cd pyReapportion
pip install -r requirements.txt
```

### Lancer les tests

```bash
pytest tests/
```

### Méthode TDD

Ce projet suit la méthodologie TDD (Test-Driven Development) :

1. **RED** : Écrire un test qui échoue
2. **GREEN** : Écrire le code minimal pour faire passer le test
3. **REFACTOR** : Améliorer le code tout en gardant les tests verts

### Structure du code

```
pyReapportion/
├── pyreapportion/          # Code source
│   ├── __init__.py
│   └── reapportion.py      # Fonction principale
├── tests/                   # Tests unitaires
│   └── test_reapportion.py
├── examples/               # Exemples d'utilisation
│   └── basic_usage.py
└── docs/                   # Documentation
```

### Soumettre une contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Écrire les tests pour votre fonctionnalité
4. Implémenter la fonctionnalité
5. Vérifier que tous les tests passent
6. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
7. Push vers la branche (`git push origin feature/AmazingFeature`)
8. Ouvrir une Pull Request

## Style de code

- Suivre PEP 8
- Documenter les fonctions avec des docstrings
- Ajouter des tests pour toute nouvelle fonctionnalité
- Maintenir la couverture de tests > 90%

## Rapporter des bugs

Utilisez les Issues GitHub pour rapporter des bugs. Incluez :

- Description du problème
- Étapes pour reproduire
- Comportement attendu vs observé
- Version de Python et des dépendances
- Exemple de code minimal

Merci !
