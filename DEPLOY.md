# Deploy online — Cloudflare Pages + GitHub

La presentazione è un sito statico: basta servirla da una sottocartella qualsiasi.
Questo repo (`nimau70/presentazione-ai-orientamento`, branch `main`) è la sorgente unica:
**ogni modifica che fai qui e pushi su `main` viene publicada automaticamente**.

## Primo collegamento a Cloudflare (una volta sola, 2 minuti)

1. Vai su [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
2. Autorizza Cloudflare ad accedere a GitHub (OAuth) e seleziona il repo `presentazione-ai-orientamento`
3. Impostazioni di build:
   - **Production branch:** `main`
   - **Framework preset:** `None`
   - **Build command:** *(vuoto)*
   - **Build output directory:** `/`  (la root del repo è già la cartella del sito: `index.html` è lì)
4. Salva → parte il primo deploy → ottieni un URL tipo `https://presentazione-ai-orientamento.pages.dev`

Da ora **ogni `git push` su `main` = nuova versione online** (build log visibile nella dashboard Pages).

### Dominio custom (opzionale)
Pages → il tuo progetto → **Custom domains** → aggiungi es. `orientamento.its-ictacademy.com`.
Se il dominio è già su Cloudflare DNS è immediato; altrimenti copi i 2 record DNS indicati.

## Alternativa senza dashboard: GitHub Action (automatica al push)

Il file `.github/workflows/cloudflare-pages.yml` è già pronto. Ti servono solo 2 secret nel repo:
- Vai su GitHub → repo → **Settings → Secrets and variables → Actions → New repository secret**
- Crea `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID`
  - API token: Cloudflare dashboard → profilo → **API Tokens** → *Create Token* → template **Cloudflare Pages:Edit**
  - Account ID: Cloudflare dashboard → Workers & Pages → in alto a destra (o nell'URL)
- Al primo push con i secret il workflow pubblica su Pages (project name: `presentazione-ai-orientamento`)

> Usa **o** il connect-to-git della dashboard **o** la Action, non entrambi sullo stesso progetto.

## Deploy manuale una tantum (senza Git)
```bash
cd "Orientamento ITS /Presentazione per Orientamento/ai-orientamento"
npx wrangler pages deploy . --project-name=presentazione-ai-orientamento
```
(dopo `npx wrangler login` la prima volta)

## Modifiche future (workflow consigliato)
```bash
cd "Orientamento ITS /Presentazione per Orientamento/ai-orientamento"
# modifichi i file (index.html, css, js, assets...)
git add -A
git commit -m "descrizione modifica"
git push          # → deploy automatico su Cloudflare Pages
```

## Note
- Il sito resta apribile anche in locale: doppio click su `index.html` (i video YouTube richiedono internet).
- I video sono embed YouTube: non occupano spazio sul repo/hosting.
- Il repo è **privato**: per renderlo pubblico (link pubblico senza login GitHub) → repo → Settings → *Change visibility*.
