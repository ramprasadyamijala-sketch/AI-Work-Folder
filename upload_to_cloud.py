#!/usr/bin/env python3
"""
Upload Script for Sanātana Dharma Scriptural Archive PDFs
Supports:
  1. Google Cloud Storage (GCS)
  2. Cloudflare R2 (S3-compatible, recommended for zero egress fees)
  3. AWS S3 / MinIO / DigitalOcean Spaces
"""

import os
import sys
import argparse
from pathlib import Path

SOURCE_DIR = Path("/Users/chanduyamijala/Documents/Ai folders /Google/Hindu_Scriptures")

TARGET_CATEGORIES = [
    "01_Upanishads",
    "02_Vedas",
    "03_Puranas",
    "04_Pancharatna_Gita",
    "05_Shiva_Stutis",
    "06_Devi_Stutis",
    "07_Vivekachudamani",
    "08_Valmiki_Ramayana_Bhashyam_and_Inner_Meaning",
    "09_Ashtavakra_Gita"
]

def collect_files(source_dir):
    files = []
    total_size = 0
    for cat in TARGET_CATEGORIES:
        cat_dir = source_dir / cat
        if not cat_dir.exists():
            continue
        for root, _, filenames in os.walk(cat_dir):
            for f in filenames:
                if f.startswith(".") or not f.lower().endswith(".pdf"):
                    continue
                full_path = Path(root) / f
                rel_path = full_path.relative_to(source_dir)
                size = full_path.stat().st_size
                files.append((full_path, str(rel_path), size))
                total_size += size
    return files, total_size

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def upload_to_gcs(files, bucket_name, dry_run=False):
    if dry_run:
        print(f"\n[DRY-RUN] Simulating upload to gs://{bucket_name}/...")
        for idx, (_, rel_path, size) in enumerate(files[:10], 1):
            print(f"[{idx}/{len(files)}] [DRY-RUN] Target: gs://{bucket_name}/{rel_path} ({format_size(size)})")
        if len(files) > 10:
            print(f"... and {len(files) - 10} more PDF files.")
        print(f"\n[DRY-RUN] Verified {len(files)} files ({format_size(sum(f[2] for f in files))}). Ready to upload.")
        print(f"👉 Once uploaded, set your base URL in index.html to: https://storage.googleapis.com/{bucket_name}")
        return

    try:
        from google.cloud import storage
    except ImportError:
        print("\n❌ Error: 'google-cloud-storage' package is not installed.")
        print("Install it using: pip install google-cloud-storage\n")
        sys.exit(1)

    print(f"Connecting to Google Cloud Storage bucket: {bucket_name}...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    print(f"\nStarting upload of {len(files)} PDFs...")
    uploaded = 0
    for idx, (local_path, rel_path, size) in enumerate(files, 1):
        blob = bucket.blob(rel_path)
        if dry_run:
            print(f"[{idx}/{len(files)}] [DRY-RUN] Would upload: {rel_path} ({format_size(size)})")
            continue

        print(f"[{idx}/{len(files)}] Uploading: {rel_path} ({format_size(size)})...", end="\r")
        blob.upload_from_filename(str(local_path), content_type="application/pdf")
        uploaded += 1

    print(f"\n✅ Upload complete! {uploaded} files uploaded to gs://{bucket_name}/")
    print(f"👉 Set your base URL in index.html to: https://storage.googleapis.com/{bucket_name}")

def upload_to_s3_compatible(files, bucket_name, endpoint_url, access_key, secret_key, dry_run=False):
    if dry_run:
        print(f"\n[DRY-RUN] Simulating upload to S3/R2 bucket '{bucket_name}' at {endpoint_url}...")
        for idx, (_, rel_path, size) in enumerate(files[:10], 1):
            print(f"[{idx}/{len(files)}] [DRY-RUN] Target: {rel_path} ({format_size(size)})")
        if len(files) > 10:
            print(f"... and {len(files) - 10} more PDF files.")
        print(f"\n[DRY-RUN] Verified {len(files)} files ({format_size(sum(f[2] for f in files))}). Ready to upload.")
        return

    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("\n❌ Error: 'boto3' package is not installed.")
        print("Install it using: pip install boto3\n")
        sys.exit(1)

    print(f"Connecting to S3/R2 endpoint: {endpoint_url} (Bucket: {bucket_name})...")
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4')
    )

    print(f"\nStarting upload of {len(files)} PDFs...")
    uploaded = 0
    for idx, (local_path, rel_path, size) in enumerate(files, 1):
        if dry_run:
            print(f"[{idx}/{len(files)}] [DRY-RUN] Would upload: {rel_path} ({format_size(size)})")
            continue

        print(f"[{idx}/{len(files)}] Uploading: {rel_path} ({format_size(size)})...", end="\r")
        with open(local_path, 'rb') as f:
            s3_client.upload_fileobj(
                f,
                bucket_name,
                rel_path,
                ExtraArgs={'ContentType': 'application/pdf', 'CacheControl': 'public, max-age=31536000'}
            )
        uploaded += 1

    print(f"\n✅ Upload complete! {uploaded} files uploaded to bucket: {bucket_name}")

def main():
    parser = argparse.ArgumentParser(description="Upload Hindu Scriptures library to Cloud Storage")
    parser.add_argument("--provider", choices=["gcs", "r2", "s3"], default="gcs", help="Cloud provider (default: gcs)")
    parser.add_argument("--bucket", default="sanatanawikiproject", help="Target bucket name (default: sanatanawikiproject)")
    parser.add_argument("--endpoint", help="Custom S3/R2 endpoint URL (required for r2)")
    parser.add_argument("--access-key", help="Access key / token (for r2/s3)")
    parser.add_argument("--secret-key", help="Secret key / secret token (for r2/s3)")
    parser.add_argument("--dry-run", action="store_true", help="List files without uploading")

    args = parser.parse_args()

    if not SOURCE_DIR.exists():
        print(f"❌ Source directory not found: {SOURCE_DIR}")
        sys.exit(1)

    print(f"Scanning source directory: {SOURCE_DIR}")
    files, total_size = collect_files(SOURCE_DIR)
    print(f"Found {len(files)} PDF documents ({format_size(total_size)}) ready for upload.")

    if args.provider == "gcs":
        upload_to_gcs(files, args.bucket, dry_run=args.dry_run)
    elif args.provider in ["r2", "s3"]:
        endpoint = args.endpoint or ("https://<account_id>.r2.cloudflarestorage.com" if args.provider == "r2" else None)
        access_key = args.access_key or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = args.secret_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        if not access_key or not secret_key:
            print("❌ Error: Access key and secret key must be provided via arguments or environment variables.")
            sys.exit(1)
        upload_to_s3_compatible(files, args.bucket, endpoint, access_key, secret_key, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
