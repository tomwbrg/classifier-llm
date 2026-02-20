# Classifier LLM — Système de Classification Avancé assisté par IA

Système de classification de messages clients en 6 catégories sémantiquement
subtiles, avec transparence, feedback loop et auto-évaluation sans dataset.

## Architecture

5 composants principaux :
- **Classifier Engine** : classification via LLM avec Chain-of-Thought
- **Feedback Store** : SQLite pour stocker corrections et historique
- **Few-shot Optimizer** : amélioration automatique des exemples via feedback
- **Auto-Evaluator** : génération et évaluation de cas de test synthétiques
- **Interface Streamlit** : 3 onglets (Classification / Historique / Admin)

## Setup (< 5 minutes)

### Prérequis
- Python 3.10+
- Clé API Anthropic (https://console.anthropic.com)

### Installation
```bash
git clone https://github.com/tomwbrg/classifier-llm
cd classifier-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Ouvrir `.env` et ajouter votre clé :
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Lancement
```bash
PYTHONPATH=. python3 -m streamlit run app/main.py
```

Ouvre automatiquement http://localhost:8501

## Utilisation

### Classifier un message
1. Onglet "Classification" → coller le message → cliquer "Classifier"
2. Le système retourne : catégorie, confiance, facteurs clés, raisonnement
3. Donner un feedback : 👍 correct / 👎 incorrect / 🤔 ambigu

### Améliorer le système (Feedback Loop)
1. Onglet "Admin" → tab "Optimisation"
2. Corriger des classifications via 👎 dans l'onglet Classification
3. Quand assez de feedbacks → "Optimiser les exemples"
4. Le système met à jour ses few-shots automatiquement

### Évaluer les performances
1. Onglet "Admin" → tab "Évaluation"
2. Choisir le nombre de cas de test → "Lancer l'évaluation"
3. Le système génère des cas synthétiques, les classifie, et se juge lui-même
4. Résultats : accuracy globale, détail par catégorie, cas ratés cliquables

## Configuration

Deux fichiers à modifier selon votre domaine :
```
config/categories.yaml  →  définir vos catégories et descriptions
config/examples.json    →  2 exemples par catégorie (mis à jour automatiquement via le feedback loop)
```

Paramètres système dans `config/system.yaml` (valeurs par défaut fonctionnelles).

## Choix techniques

### Pourquoi les LLM ?
Les 6 catégories nécessitent une compréhension de l'intention : urgence implicite,
sarcasme, question masquant une réclamation. Un classifieur TF-IDF/BERT capture
des patterns lexicaux, pas l'intention réelle.

### Stratégie de prompting
- Chain-of-Thought : le modèle raisonne en 5 étapes avant de décider
- Few-shot dynamique : 2 exemples par catégorie, mis à jour par le feedback loop
- Output structuré JSON : parsing fiable avec guardrails et retry automatique
- Inspiré de promptingguide.ai/applications/generating et platform.claude.com/docs/en/test-and-evaluate/develop-tests

### Évaluation sans dataset
Le système génère ses propres cas de test (easy/medium/hard), les classifie,
puis utilise un LLM-as-judge avec rubric binaire (correct/incorrect).
Limite connue : les étiquettes générées peuvent être imparfaites sur les cas
ambigus — limitation inhérente à l'évaluation sans dataset humain.

### Performance observée
- Accuracy globale : ~90% sur 30 cas synthétiques
- Cas difficiles : ~80%
- Catégories les plus robustes : question, constructive, positive (100%)
- Catégories à améliorer via feedback : non_urgent, negative (60%)

## Structure du repo
```
classifier-llm/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── classifier.py
│   │   ├── prompt_builder.py
│   │   ├── response_parser.py
│   │   └── llm_client.py
│   ├── views/
│   │   ├── classify.py
│   │   ├── history.py
│   │   └── admin.py
│   ├── data/
│   │   ├── database.py
│   │   └── models.py
│   ├── feedback/
│   │   └── optimizer.py
│   └── evaluation/
│       ├── generator.py
│       ├── judge.py
│       └── evaluator.py
├── config/
│   ├── categories.yaml
│   ├── system.yaml
│   └── examples.json
├── .env.example
├── requirements.txt
└── README.md
```
└── README.md
```
