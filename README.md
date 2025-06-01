# MangaDex Chapter Fetcher

Simple script to latest updates using mangadex API https://api.mangadex.org/docs/
For personal use, checking updates fast

## Setup

1. Create `.env` file:
```bash
MANGADEX_USERNAME=your_username
MANGADEX_PASSWORD=your_password  
MANGADEX_CLIENT_ID=your_client_id
MANGADEX_CLIENT_SECRET=your_client_secret
```

2. Run:
```bash
python mangadex_fetcher.py
```

## Get Credentials

1. Go to [MangaDex](https://mangadex.org) → Settings → API
2. Create Personal Client
3. Copy to `.env` file

## Output

```
🚀 MangaDex Latest Chapters
Did not find updates for:  ['Black Clover']
================================================================================
🔥 MangaDex Latest Chapters
================================================================================

📚 Chainsaw Man
Latest chapters: 3
--------------------------------------------------------------------------------
Ch#      Title                               Published            URL
────────────────────────────────────────────────────────────────────────────────
204      With One Life                       05/27 15:05          https://mangaplus.shueisha.co.jp/viewer/1024133
203      Human Shield                        05/20 15:05          https://mangaplus.shueisha.co.jp/viewer/1024132
202      Devil Combination                   05/06 15:01          https://mangaplus.shueisha.co.jp/viewer/1024131
════════════════════════════════════════════════════════════════════════════════
```