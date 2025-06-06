from flask import Flask, Response
import os

# Import your existing functions
from fetcher import authenticate, get_latest_chapters, group_by_manga_series
from config import MANGA_IDS

app = Flask(__name__)


@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manga Tracker</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                color: #fff; 
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 { 
                text-align: center; 
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            .controls {
                text-align: center;
                margin-bottom: 30px;
            }
            button { 
                padding: 12px 24px; 
                font-size: 16px; 
                cursor: pointer;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                border: none;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            .loading {
                text-align: center;
                font-size: 18px;
                color: #ffd700;
                margin: 40px 0;
            }
            .manga-container {
                display: grid;
                gap: 20px;
            }
            .manga-series {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .manga-title {
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 10px;
                color: #ffd700;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .chapter-count {
                background: rgba(255, 215, 0, 0.2);
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8em;
                color: #ffd700;
            }
            .chapters-grid {
                display: grid;
                gap: 10px;
                margin-top: 15px;
            }
            .chapter-item {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 12px;
                display: grid;
                grid-template-columns: auto 1fr auto auto;
                gap: 15px;
                align-items: center;
                transition: all 0.3s ease;
                border-left: 4px solid transparent;
            }
            .chapter-item:hover {
                background: rgba(0, 0, 0, 0.5);
                border-left-color: #ff6b6b;
                transform: translateX(5px);
            }
            .chapter-number {
                font-weight: bold;
                color: #4ecdc4;
                min-width: 60px;
                font-size: 1.1em;
            }
            .chapter-title {
                color: #fff;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .chapter-date {
                color: #bbb;
                font-size: 0.9em;
                min-width: 80px;
            }
            .chapter-link {
                color: #ff6b6b;
                text-decoration: none;
                padding: 6px 12px;
                border: 1px solid #ff6b6b;
                border-radius: 15px;
                font-size: 0.9em;
                transition: all 0.3s ease;
                white-space: nowrap;
            }
            .chapter-link:hover {
                background: #ff6b6b;
                color: white;
                transform: scale(1.05);
            }
            .error {
                background: rgba(255, 0, 0, 0.2);
                border: 1px solid #ff4757;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                color: #ff4757;
                margin: 20px 0;
            }
            .last-updated {
                text-align: center;
                color: #bbb;
                margin-top: 20px;
                font-size: 0.9em;
            }
            @media (max-width: 768px) {
                .chapter-item {
                    grid-template-columns: 1fr;
                    gap: 8px;
                    text-align: left;
                }
                .chapter-link {
                    justify-self: start;
                }
                body { padding: 10px; }
                h1 { font-size: 2em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 Manga Tracker</h1>
            <div class="controls">
                <button onclick="fetchManga()">🔄 Refresh Updates</button>
            </div>
            <div id="result" class="loading">Loading manga updates...</div>
            <div id="lastUpdated" class="last-updated"></div>
        </div>

        <script>
            function fetchManga() {
                const resultDiv = document.getElementById('result');
                const lastUpdatedDiv = document.getElementById('lastUpdated');

                resultDiv.innerHTML = '<div class="loading">🔄 Fetching latest manga updates...</div>';
                lastUpdatedDiv.innerHTML = '';

                fetch('/api/manga')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        displayMangaData(data);
                        lastUpdatedDiv.innerHTML = `Last updated: ${new Date().toLocaleString()}`;
                    })
                    .catch(error => {
                        resultDiv.innerHTML = `
                            <div class="error">
                                <h3>❌ Error Loading Manga</h3>
                                <p>${error.message}</p>
                                <p>Please try refreshing or check the console for more details.</p>
                            </div>
                        `;
                        console.error('Fetch error:', error);
                    });
            }

            function displayMangaData(mangaData) {
                const resultDiv = document.getElementById('result');

                if (!mangaData || Object.keys(mangaData).length === 0) {
                    resultDiv.innerHTML = '<div class="error">No manga data found</div>';
                    return;
                }

                let html = '<div class="manga-container">';

                for (const [mangaName, chapters] of Object.entries(mangaData)) {
                    html += `
                        <div class="manga-series">
                            <div class="manga-title">
                                📚 ${mangaName}
                                <span class="chapter-count">${chapters.length} chapters</span>
                            </div>
                            <div class="chapters-grid">
                    `;

                    chapters.forEach(chapter => {
                        const chapterNum = chapter.chapter || 'N/A';
                        const title = chapter.title || 'No Title';
                        const date = chapter.formatted_date || 'Unknown';
                        const url = chapter.url || '';

                        html += `
                            <div class="chapter-item">
                                <div class="chapter-number">Ch. ${chapterNum}</div>
                                <div class="chapter-title" title="${title}">${title}</div>
                                <div class="chapter-date">${date}</div>
                                ${url ? `<a href="${url}" class="chapter-link" target="_blank" rel="noopener">Read</a>` : '<span class="chapter-link" style="opacity:0.5;">No Link</span>'}
                            </div>
                        `;
                    });

                    html += `
                            </div>
                        </div>
                    `;
                }

                html += '</div>';
                resultDiv.innerHTML = html;
            }

            // Load manga data when page loads
            window.addEventListener('load', fetchManga);
        </script>
    </body>
    </html>
    '''


@app.route('/api/manga')
def get_manga():
    try:
        # Use your functions exactly as they are
        token = authenticate()
        if not token:
            return Response('{"error": "Authentication failed"}', mimetype='application/json', status=500)

        all_chapters = []
        for manga_id in MANGA_IDS:
            chapters = get_latest_chapters(token, manga_id)
            all_chapters.extend(chapters)

        grouped = group_by_manga_series(all_chapters, MANGA_IDS)

        # Convert to JSON format for better frontend handling
        json_data = {}

        for manga_name, chapters in grouped.items():
            # Sort chapters by chapter number (highest to lowest)
            sorted_chapters = sorted(
                chapters,
                key=lambda x: float(x.get('attributes', {}).get('chapter', '0') or '0'),
                reverse=True
            )

            processed_chapters = []
            for ch in sorted_chapters:
                attrs = ch.get('attributes', {})
                chapter_num = attrs.get('chapter', 'N/A')
                title = attrs.get('title', 'No Title')
                published_at = attrs.get('publishAt', 'Unknown')
                chapter_url = attrs.get('externalUrl', '')

                # Format the published date
                if published_at != 'Unknown':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%m/%d %H:%M')
                    except:
                        formatted_date = published_at[:10]  # Just date part
                else:
                    formatted_date = 'Unknown'

                processed_chapters.append({
                    'chapter': chapter_num,
                    'title': title,
                    'formatted_date': formatted_date,
                    'url': chapter_url
                })

            json_data[manga_name] = processed_chapters

        return Response(
            f'{json_data}'.replace("'", '"'),  # Quick JSON conversion
            mimetype='application/json'
        )

    except Exception as e:
        return Response(f'{{"error": "{str(e)}"}}', mimetype='application/json', status=500)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    # Check if we're running on Railway (or any cloud platform)
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT'):
        # Production/Railway deployment
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        # Local development
        app.run(debug=True, port=5000)