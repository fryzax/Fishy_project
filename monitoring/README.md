# Monitoring Stack - Fish Classifier API

## 📊 Vue d'ensemble

Ce dossier contient la configuration complète du monitoring pour l'API de classification de poissons, utilisant:
- **Prometheus**: Collecte des métriques
- **Grafana**: Visualisation des données
- **cAdvisor**: Métriques des conteneurs Docker

## 🚀 Démarrage

### 1. Lancer le stack de monitoring

```bash
docker-compose up -d prometheus grafana cadvisor
```

### 2. Accéder aux interfaces

- **Prometheus**: http://localhost:9090
  - Exploration des métriques brutes
  - Vérifier les targets: http://localhost:9090/targets
  
- **Grafana**: http://localhost:3001
  - Identifiants par défaut:
    - Username: `admin`
    - Password: `admin`
  - Dashboard pré-configuré: "Fish Classifier API Monitoring"

- **cAdvisor**: http://localhost:8081
  - Métriques détaillées des conteneurs

## 📈 Métriques disponibles

### Métriques API (fish_api:8000/metrics)

| Métrique | Type | Description |
|----------|------|-------------|
| `http_requests_total` | Counter | Nombre total de requêtes par endpoint et status |
| `http_request_duration_seconds` | Histogram | Latence des requêtes HTTP |
| `model_inference_duration_seconds` | Histogram | Temps d'inférence du modèle CNN |
| `prediction_confidence` | Histogram | Distribution de la confiance des prédictions |
| `predicted_class_total` | Counter | Nombre de prédictions par classe de poisson |

### Métriques conteneurs (cAdvisor)

- `container_cpu_usage_seconds_total`: Utilisation CPU
- `container_memory_usage_bytes`: Utilisation mémoire
- `container_network_receive_bytes_total`: Trafic réseau entrant
- `container_network_transmit_bytes_total`: Trafic réseau sortant

## 🎨 Dashboard Grafana

Le dashboard "Fish Classifier API Monitoring" contient 8 panneaux:

1. **Requests per Second by Endpoint**: Taux de requêtes par endpoint
2. **Error Rate (5xx)**: Jauge du taux d'erreurs serveur
3. **Request Latency (p50 & p95)**: Latence des requêtes (médiane et 95e percentile)
4. **Model Inference Latency**: Temps d'inférence du modèle
5. **Predictions by Class**: Distribution des prédictions par espèce de poisson
6. **Prediction Confidence**: Confiance médiane des prédictions
7. **Container CPU Usage**: Utilisation CPU de fish_api
8. **Container Memory Usage**: Utilisation mémoire de fish_api

## 🔍 Requêtes Prometheus utiles

### Taux de requêtes
```promql
rate(http_requests_total[1m])
```

### Latence P95
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Taux d'erreur
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

### Top 3 des classes prédites
```promql
topk(3, rate(predicted_class_total[5m]))
```

## 📁 Structure des fichiers

```
monitoring/
├── README.md                         # Ce fichier
├── prometheus.yml                    # Configuration Prometheus
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── prometheus.yml        # Auto-provision datasource Prometheus
        └── dashboards/
            ├── dashboard.yml         # Configuration provider
            └── fish-api-dashboard.json  # Dashboard JSON
```

## 🛠️ Configuration

### Modifier l'intervalle de scrape

Dans `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s  # Modifier ici (actuellement 15s)
```

### Ajouter de nouvelles métriques

1. Ajouter dans `app/main.py` (côté API):
```python
from prometheus_client import Gauge

NEW_METRIC = Gauge('my_metric_name', 'Description de la métrique')
```

2. Prometheus collectera automatiquement cette nouvelle métrique

### Personnaliser le dashboard

1. Modifier dans Grafana UI (http://localhost:3001)
2. Exporter le JSON (Share → Export)
3. Remplacer `monitoring/grafana/provisioning/dashboards/fish-api-dashboard.json`

## 🔧 Troubleshooting

### Prometheus ne scrape pas fish_api

Vérifier:
```bash
docker logs prometheus
curl http://localhost:8000/metrics
```

### Grafana n'affiche pas de données

1. Vérifier que Prometheus collecte: http://localhost:9090/targets
2. Tester la requête dans Prometheus UI
3. Vérifier la datasource dans Grafana: Configuration → Data Sources

### cAdvisor ne démarre pas sur Windows

Sur Windows, cAdvisor peut avoir des limitations. Alternatives:
- Utiliser Docker Desktop metrics intégré
- Monitorer via `docker stats`

## 📝 Notes

- Toutes les données sont locales et gratuites
- Les données Prometheus sont persistées dans le volume `prometheus_data`
- Les dashboards Grafana sont persistés dans le volume `grafana_data`
- Refresh automatique des dashboards: 10 secondes

## 🎯 Prochaines étapes

- [ ] Ajouter des alertes Prometheus (alertmanager)
- [ ] Métriques de santé du modèle (model_loaded, model_version)
- [ ] Intégration avec MLflow pour tracking des expériences
- [ ] Dashboard pour MinIO et MySQL (si nécessaire)
