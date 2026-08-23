# Déployer ATS CV Scorer sur GCP avec CI/CD GitHub

## Architecture cible

```
GitHub (push sur main)
      │
      ▼
GitHub Actions (build + push images)
      │
      ▼
Artifact Registry (stockage des images Docker)
      │
      ▼
Cloud Run backend  ◄──►  Cloud Run frontend
      │
      ▼
Secret Manager (clés Groq, France Travail...)
```

Pourquoi Cloud Run plutôt qu'une VM ou GKE :
- Tu déploies directement une image Docker (aucun changement d'archi requise)
- Scale à 0 quand personne n'utilise l'app → coût quasi nul en essai/v1
- HTTPS automatique, pas de reverse proxy à gérer
- Pas de serveur à patcher/maintenir

C'est le choix "pro" par défaut pour ce genre de projet, avant d'envisager GKE (utile seulement à partir d'une vraie charge/complexité multi-services).

---

## Étape 0 — Pré-requis

```bash
# Installer gcloud CLI (si pas déjà fait)
# macOS : brew install --cask google-cloud-sdk

gcloud auth login
gcloud projects list          # récupère ton PROJECT_ID (essai gratuit)
gcloud config set project TON_PROJECT_ID
```

Définis des variables une fois pour toutes (à réutiliser dans tous les blocs suivants) :

```bash
export PROJECT_ID="ton-project-id"
export REGION="europe-west1"          # Belgique, le plus proche pour un usage FR
export REPO_NAME="ats-cv-scorer"
```

---

## Étape 1 — Activer les APIs nécessaires

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com
```

---

## Étape 2 — Créer le dépôt Artifact Registry

Container Registry (gcr.io) est déprécié — Artifact Registry est la bonne pratique actuelle.

```bash
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Images ATS CV Scorer"
```

Configurer Docker pour pousser vers ce repo :

```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

---

## Étape 3 — Adapter le backend pour Cloud Run

Ton `backend/Dockerfile` actuel fonctionne quasiment tel quel. Une seule chose à savoir : Cloud Run doit connaître le port sur lequel écoute ton conteneur. Ton `uvicorn` écoute en dur sur `8000` (pas de lecture de la variable `$PORT`) — c'est très bien, il suffit de le dire explicitement à Cloud Run au déploiement avec `--port 8000` (étape 6), pas besoin de toucher au Dockerfile.

**⚠️ Piège vécu — l'image fait 5-7 Go à cause de torch CUDA** : par défaut, `torch` (dépendance de `sentence-transformers`) s'installe en version GPU/CUDA, qui pèse plusieurs Go alors que Cloud Run n'a pas de GPU et n'en a aucun besoin. Fixe la version CPU-only dans `backend/pyproject.toml` :

```toml
[tool.uv.sources]
torch = { index = "pytorch-cpu" }

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

Puis régénère le lockfile (obligatoire, sinon `--frozen` dans le Dockerfile refuse de builder) :

```bash
cd backend
uv lock
```

Résultat attendu : image backend qui passe d'environ 5-7 Go à ~1-1.5 Go. Vérifie avant de pousser :

```bash
docker images $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:v1
```

**Important — CORS** : dans `app/main.py`, l'origine autorisée est actuellement figée sur `http://localhost:5173`. Une fois le frontend déployé, il faudra ajouter son URL Cloud Run (ou ton domaine final) :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://TON-FRONTEND-URL.run.app",  # à ajouter après l'étape 7
    ],
    ...
)
```

---

## Étape 4 — Adapter le frontend pour la prod

Ton `frontend/Dockerfile` actuel lance `pnpm dev` — c'est le serveur de développement Vite (hot-reload, non optimisé, jamais fait pour être exposé publiquement). Pour la prod, il faut **builder** l'app en fichiers statiques puis les servir avec un vrai serveur web léger.

Crée `frontend/Dockerfile.prod` :

```dockerfile
# ---- Build stage ----
FROM node:24-alpine AS build
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .

# Vite fige les variables d'env au moment du build, pas au runtime
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN pnpm build

# ---- Serve stage ----
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
```

Crée `frontend/nginx.conf` (Cloud Run attend le port 8080 par défaut) :

```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Point d'attention : `VITE_API_URL` est injecté **au moment du build**, pas au démarrage du conteneur. Il faut donc connaître l'URL du backend Cloud Run *avant* de builder l'image frontend — d'où l'ordre des étapes ci-dessous (backend déployé en premier).

**⚠️ Piège vécu — le build de prod peut révéler des erreurs TypeScript invisibles en dev.** `pnpm dev` ne fait pas de vérification de types stricte, alors que `pnpm build` (utilisé dans `Dockerfile.prod`) lance `tsc -b` avant `vite build`. Si ton code a un type frontend désynchronisé de ce que renvoie réellement le backend (ex. un champ présent dans la réponse JSON mais absent du type TypeScript), le build échoue seulement à ce moment-là. Teste toujours en local avant de lancer un build Docker complet :

```bash
cd frontend
pnpm build
```

Si ça passe sans erreur en local, le build Docker passera aussi — inutile d'attendre un build Docker entier pour découvrir une erreur `tsc`.

---

## Étape 5 — Secrets dans Secret Manager

Ne jamais mettre `GROQ_API_KEY` / `FRANCE_TRAVAIL_CLIENT_SECRET` en variable d'env en clair dans `gcloud run deploy` ou dans le repo. Bonne pratique : Secret Manager.

```bash
echo -n "ta_vraie_cle_groq" | gcloud secrets create groq-api-key --data-file=-
echo -n "ton_client_id_ft" | gcloud secrets create ft-client-id --data-file=-
echo -n "ton_client_secret_ft" | gcloud secrets create ft-client-secret --data-file=-
echo -n "ton_hf_token" | gcloud secrets create hf-token --data-file=-
```

Le `HF_TOKEN` n'est pas strictement obligatoire (le téléchargement du modèle sentence-transformers fonctionne sans), mais sans lui Hugging Face applique des rate limits plus stricts sur les téléchargements anonymes — utile à avoir dès qu'on redéploie souvent, vu que le modèle n'est pas mis en cache dans l'image (voir note à l'étape 6).

**Étape supplémentaire indispensable, découverte à l'usage** : créer un secret ne suffit pas — il faut aussi explicitement autoriser le service account qui exécute le conteneur Cloud Run à le lire. Sans ça, `gcloud run deploy` échoue avec `Permission denied on secret`. C'est le principe du moindre privilège : deux systèmes IAM distincts (créer un secret ≠ avoir le droit de le lire).

```bash
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
export RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SECRET in groq-api-key ft-client-id ft-client-secret hf-token; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:$RUNTIME_SA" \
    --role="roles/secretmanager.secretAccessor"
done
```

---

## Étape 6 — Premier déploiement manuel (pour valider avant d'automatiser)

Toujours faire un premier déploiement à la main avant de brancher le CI/CD — ça isole les problèmes de conf des problèmes de pipeline.

**⚠️ Piège vécu — sur Mac Apple Silicon (M1/M2/M3), il faut forcer l'architecture.** Par défaut, `docker build` construit pour l'architecture de ta machine (arm64). Cloud Run n'exécute que du `linux/amd64` — sans `--platform`, le déploiement échoue avec `exec format error` et le conteneur ne démarre jamais. Ajoute `--platform linux/amd64` à **tous** tes builds locaux destinés à Cloud Run (backend et frontend). Ce n'est pas nécessaire dans le workflow GitHub Actions (étape 8) : les runners `ubuntu-latest` sont déjà en amd64.

```bash
# Build + push de l'image backend
cd backend
docker build --platform linux/amd64 -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:v1 .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:v1

# Déploiement backend
gcloud run deploy ats-backend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/backend:v1 \
  --region=$REGION \
  --platform=managed \
  --port=8000 \
  --allow-unauthenticated \
  --set-secrets="GROQ_API_KEY=groq-api-key:latest,FRANCE_TRAVAIL_CLIENT_ID=ft-client-id:latest,FRANCE_TRAVAIL_CLIENT_SECRET=ft-client-secret:latest,HF_TOKEN=hf-token:latest" \
  --memory=2Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3
```

⚠️ `--memory=2Gi` **minimum recommandé**, pas 1Gi — vécu en pratique : avec 1Gi, le conteneur crashe au démarrage (`Memory limit of 1024 MiB exceeded with 1098 MiB used`) à cause du modèle sentence-transformers chargé en mémoire pendant le préchauffage (`get_semantic_service`). Ajuste encore si tu vois des OOM dans les logs à plus forte charge.

Récupère l'URL générée (affichée en sortie, ou) :

```bash
gcloud run services describe ats-backend --region=$REGION --format='value(status.url)'
```

Puis backend URL en main, build le frontend (`--platform linux/amd64` là aussi) :

```bash
cd ../frontend
docker build --platform linux/amd64 -f Dockerfile.prod \
  --build-arg VITE_API_URL=https://TON-BACKEND-URL.run.app \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:v1 .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:v1

gcloud run deploy ats-frontend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/frontend:v1 \
  --region=$REGION \
  --platform=managed \
  --port=8080 \
  --allow-unauthenticated \
  --memory=256Mi \
  --min-instances=0 \
  --max-instances=3
```

Va maintenant mettre à jour le CORS dans `main.py` (étape 3) avec l'URL frontend obtenue, puis redéploie le backend (rebuild `--platform linux/amd64` + push + `gcloud run deploy ats-backend ...` à nouveau).

Teste que tout marche via l'URL frontend avant de passer au CI/CD.

---

## Étape 7 — Lier GitHub à GCP proprement (sans clé JSON)

**La mauvaise pratique** que tu verras souvent en tutoriel : générer une clé de compte de service JSON et la coller en secret GitHub. Ça marche, mais c'est un secret longue durée qui traîne, difficile à révoquer proprement, mauvaise pratique de sécurité.

**La bonne pratique** : **Workload Identity Federation (WIF)**. GitHub Actions s'authentifie directement auprès de GCP via un jeton temporaire OIDC, sans aucune clé stockée nulle part. C'est la méthode recommandée par Google elle-même depuis 2023.

```bash
export GH_REPO="ton-user/ton-repo"   # ex: dgando-bit/ats-cv-scorer_v2

# 1. Créer un service account dédié au déploiement
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer"

export SA_EMAIL="github-deployer@$PROJECT_ID.iam.gserviceaccount.com"

# 2. Donner les rôles minimaux nécessaires (principe du moindre privilège)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"

# 3. Créer le pool d'identité workload
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 4. Créer le provider OIDC lié à GitHub
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='$GH_REPO'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 5. Autoriser CE dépôt GitHub précis à endosser le service account
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$GH_REPO"
```

Récupère l'identifiant du provider (à mettre dans le workflow GitHub) :

```bash
gcloud iam workload-identity-pools providers describe "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
```

---

## Étape 8 — Le workflow GitHub Actions

Crée `.github/workflows/deploy.yml` :

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

env:
  PROJECT_ID: ton-project-id
  REGION: europe-west1
  REPO_NAME: ats-cv-scorer

permissions:
  contents: read
  id-token: write   # requis pour l'auth OIDC sans clé

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
          service_account: github-deployer@ton-project-id.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev

      - name: Build and push backend
        run: |
          IMAGE=${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO_NAME }}/backend:${{ github.sha }}
          docker build -t $IMAGE ./backend
          docker push $IMAGE
          echo "IMAGE=$IMAGE" >> $GITHUB_ENV

      - name: Deploy backend to Cloud Run
        run: |
          gcloud run deploy ats-backend \
            --image=${{ env.IMAGE }} \
            --region=${{ env.REGION }} \
            --port=8000 \
            --allow-unauthenticated \
            --set-secrets="GROQ_API_KEY=groq-api-key:latest,FRANCE_TRAVAIL_CLIENT_ID=ft-client-id:latest,FRANCE_TRAVAIL_CLIENT_SECRET=ft-client-secret:latest,HF_TOKEN=hf-token:latest" \
            --memory=2Gi

  deploy-frontend:
    needs: deploy-backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
          service_account: github-deployer@ton-project-id.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - name: Get backend URL
        run: |
          URL=$(gcloud run services describe ats-backend --region=${{ env.REGION }} --format='value(status.url)')
          echo "BACKEND_URL=$URL" >> $GITHUB_ENV

      - name: Configure Docker
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev

      - name: Build and push frontend
        run: |
          IMAGE=${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO_NAME }}/frontend:${{ github.sha }}
          docker build -f ./frontend/Dockerfile.prod \
            --build-arg VITE_API_URL=${{ env.BACKEND_URL }} \
            -t $IMAGE ./frontend
          docker push $IMAGE
          echo "IMAGE=$IMAGE" >> $GITHUB_ENV

      - name: Deploy frontend to Cloud Run
        run: |
          gcloud run deploy ats-frontend \
            --image=${{ env.IMAGE }} \
            --region=${{ env.REGION }} \
            --port=8080 \
            --allow-unauthenticated \
            --memory=256Mi
```

Remplace `ton-project-id` et `PROJECT_NUMBER` par tes vraies valeurs (celle récupérée à l'étape 7).

À partir de là : **chaque `git push` sur `main` redéploie automatiquement** backend et frontend. C'est ça, "la bonne pratique" — ton historique GitHub devient ton historique de déploiement, traçable, sans étape manuelle.

---

## Étape 9 — Ce qu'il reste à ajuster une fois que ça tourne

- **CORS** : remets à jour `main.py` avec l'URL frontend finale (celle-ci ne change pas entre déploiements, seule l'image change, donc à faire une fois).
- **Domaine personnalisé** (optionnel) : `gcloud run domain-mappings create` si tu veux `api.tondomaine.com` plutôt qu'une URL `*.run.app`.
- **Environnements séparés** : pour une v1, un seul environnement (prod) suffit. Si tu veux du staging plus tard, duplique simplement les services Cloud Run (`ats-backend-staging`) et déclenche sur une branche `develop`.
- **Coûts** : avec `--min-instances=0`, tu ne payes rien quand personne n'utilise l'app (juste le stockage Artifact Registry, négligeable). Attention au cold-start du modèle sémantique au premier appel après une période d'inactivité — c'est exactement le problème du préchauffage qu'on a réglé en local, il se reproduira ici après une mise en veille Cloud Run. Si ça devient gênant, `--min-instances=1` élimine le cold-start mais fait tourner le conteneur en continu (coût non-nul).
- **Suivi** : dans la console GCP → Cloud Run → clique sur ton service → onglet **Logs** — tu y retrouveras tes logs `[timing]`/`[rerank]`/`[requirements-batch]` tels quels. Onglet **Metrics** pour la charge CPU/mémoire dans le temps, **Revisions** pour l'historique des déploiements et un rollback en un clic si besoin.

  ```bash
  # accès direct
  open "https://console.cloud.google.com/run?project=$PROJECT_ID"
  ```

  Si un lien direct vers un service précis affiche "URL introuvable", c'est généralement un souci de compte Google (`&authuser=`) si plusieurs comptes sont connectés dans le navigateur — repasse par le menu **Services** dans la console plutôt que par le lien.

---

## Annexe — Problèmes rencontrés en pratique et leur fix

Pour référence rapide si tu retombes dessus (ou si quelqu'un d'autre reprend ce déploiement) :

| Symptôme | Cause | Fix |
|---|---|---|
| Image backend de 5-7 Go, `docker push` très long | `torch` installé en version CUDA/GPU par défaut | `[tool.uv.sources]` + `[[tool.uv.index]]` vers `download.pytorch.org/whl/cpu` dans `pyproject.toml`, puis `uv lock` |
| `Permission denied on secret` au déploiement | Le service account d'exécution Cloud Run n'a pas le droit de lire les secrets créés | `gcloud secrets add-iam-policy-binding <secret> --member="serviceAccount:$RUNTIME_SA" --role="roles/secretmanager.secretAccessor"` |
| `failed to load /usr/bin/uv: exec format error` | Image buildée en arm64 (Mac Apple Silicon) alors que Cloud Run attend amd64 | `docker build --platform linux/amd64 ...` sur tous les builds locaux |
| `Memory limit of 1024 MiB exceeded` | Modèle sentence-transformers trop lourd pour 1Gi de RAM | `--memory=2Gi` sur le déploiement backend |
| `Warning: unauthenticated requests to the HF Hub` | Pas de token Hugging Face, rate limit anonyme plus strict | Secret `HF_TOKEN` ajouté via `--set-secrets` |
| `error TS2339: Property 'x' does not exist on type` au build frontend | Type TypeScript désynchronisé de la vraie réponse JSON backend ; invisible avec `pnpm dev` qui ne type-check pas | Corriger le type, puis toujours tester `pnpm build` en local avant un build Docker |
| Lien direct vers la console GCP → "URL introuvable" | Plusieurs comptes Google connectés dans le navigateur (`&authuser=`) | Repasser par le menu **Services** dans la console plutôt que par le lien direct |

---

## Résumé de l'ordre à suivre

1. Étapes 0-2 : setup GCP (une fois)
2. Étape 3-4 : ajuster CORS backend + créer `Dockerfile.prod` + `nginx.conf` frontend
3. Étape 5 : secrets
4. Étape 6 : déploiement manuel de validation (backend d'abord, puis frontend avec son URL)
5. Étape 7 : configurer Workload Identity Federation (une fois)
6. Étape 8 : ajouter le workflow GitHub Actions, push sur `main`
7. Étape 9 : ajustements finaux
