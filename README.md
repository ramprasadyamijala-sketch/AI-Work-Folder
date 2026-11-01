# Sanātana Dharma Scriptural Archive & AI Copilot | सनातन शास्त्र भाण्डार

A modern, responsive web application and digital archive cataloging 4,460+ sacred Hindu scriptures (Upanishads, Vedas, Puranas, Pancharatna Gita, Shiva & Devi Stutis, Vivekachudamani, Valmiki Ramayana, and Ashtavakra Gita) with an integrated AI Copilot.

---

## 🚀 Features

- **4,460+ Scriptural Records**: Instant live search, filtering by language (Sanskrit Devanagari, English, Telugu, Hindi, etc.) and category.
- **Embedded AI Copilot**: Ask questions about scriptures, verses, philosophy, and meanings with citation footnotes.
  - Supports **Local Ollama** (e.g. `llama3` on `http://localhost:11434`), **OpenAI-compatible APIs**, or custom endpoints.
- **Pure Client-Side Architecture**: Zero backend server required for the catalog and search; runs directly in any modern browser.
- **Dark Gold Theme**: Optimized typography featuring *Cinzel*, *Yatra One*, and *Inter*.

---

## 💻 Local Development & Preview

You can preview the project locally using any of the following methods:

### Method 1: Using Node.js / npx
```bash
npx serve -p 3000 .
```
Then open [http://localhost:3000](http://localhost:3000) in your browser.

### Method 2: Using Python
```bash
python3 -m http.server 3000
```
Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🌐 Deployment Options

### 1. Vercel (Recommended)
1. Install the Vercel CLI (or connect via GitHub):
   ```bash
   npx vercel
   ```
2. Accept the defaults (`vercel.json` is already configured).
3. Your application is live within seconds on a `.vercel.app` domain.

### 2. Netlify
1. Drag and drop the folder into [Netlify Drop](https://app.netlify.com/drop), or deploy via Netlify CLI:
   ```bash
   npx netlify-cli deploy --prod
   ```
2. Configuration is pre-set in `netlify.toml`.

### 3. GitHub Pages
1. Push this directory to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Sanatana Dharma Scriptural Archive"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. In your GitHub repository, go to **Settings** > **Pages**.
3. Under **Build and deployment**, select **Source: Deploy from a branch** and pick `main` / `/ (root)`.

### 4. Docker / Google Cloud Run
Build and run locally:
```bash
docker build -t sanatana-dharma-archive .
docker run -p 8080:80 sanatana-dharma-archive
```
To deploy to Google Cloud Run:
```bash
gcloud run deploy sanatana-archive --source . --platform managed --allow-unauthenticated
```

---

## 📚 Cloud Hosting for the 7.6 GB PDF Library

The web application catalogs 4,460+ sacred texts totaling ~7.6 GB. `index.html` dynamically resolves all document links through a configurable base prefix.

### Configuring the Cloud Bucket URL in `index.html`

1. Open the application in your browser.
2. Click **⚙️ Settings** in the Copilot / Top Bar.
3. In **PDF Cloud Bucket / CDN Base URL**, enter your public cloud storage URL prefix:
   - **Google Cloud Storage (GCS)**: `https://storage.googleapis.com/<YOUR_BUCKET_NAME>`
   - **Cloudflare R2**: `https://pub-<id>.r2.dev` (or your custom domain like `https://library.yourdomain.com`)
   - **AWS S3**: `https://<YOUR_BUCKET_NAME>.s3.<region>.amazonaws.com`
4. Click **Save Settings**. All 4,460+ document buttons, citations, and footnotes will immediately point to your cloud bucket!
   *(Leaving this field blank automatically falls back to local relative paths).*

---

### Uploading PDFs to Cloud Storage

An automated script `upload_to_cloud.py` is included to sync all PDFs:

#### Option A: Google Cloud Storage (GCS)
```bash
# 1. Install Google Cloud Storage client
pip install google-cloud-storage

# 2. Dry run first to verify
python3 upload_to_cloud.py --provider gcs --bucket your-scriptures-bucket --dry-run

# 3. Upload all PDFs
python3 upload_to_cloud.py --provider gcs --bucket your-scriptures-bucket
```

#### Option B: Cloudflare R2 (Recommended for 100% Free Egress)
Cloudflare R2 offers 10 GB of free storage and **$0 egress fees**, making it ideal for hosting a public PDF archive.
```bash
# 1. Install boto3
pip install boto3

# 2. Upload to Cloudflare R2
python3 upload_to_cloud.py --provider r2 \
  --bucket your-scriptures-bucket \
  --endpoint https://<YOUR_ACCOUNT_ID>.r2.cloudflarestorage.com \
  --access-key <YOUR_R2_ACCESS_KEY> \
  --secret-key <YOUR_R2_SECRET_KEY>
```


