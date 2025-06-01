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
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
            pre { background: #000; color: #00ff00; padding: 20px; border-radius: 8px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🔥 Manga Tracker</h1>
        <button onclick="fetchManga()">Get Latest Manga Updates</button>
        <pre id="result">Click button to get updates...</pre>

        <script>
            function fetchManga() {
                document.getElementById('result').innerHTML = 'Loading...';
                fetch('/api/manga')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('result').innerHTML = data;
                    })
                    .catch(error => {
                        document.getElementById('result').innerHTML = 'Error: ' + error;
                    });
            }
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
            return Response("Authentication failed", mimetype='text/plain', status=500)

        all_chapters = []
        for manga_id in MANGA_IDS:
            chapters = get_latest_chapters(token, manga_id)
            all_chapters.extend(chapters)

        grouped = group_by_manga_series(all_chapters, MANGA_IDS)

        # Generate human-readable formatted text (same as display_grouped_manga)
        output_lines = []
        output_lines.append("🔥 MangaDex Latest Chapters")
        output_lines.append("=" * 80)

        for manga_name, chapters in grouped.items():
            output_lines.append(f"\n📚 {manga_name}")
            output_lines.append(f"Latest chapters: {len(chapters)}")
            output_lines.append("-" * 80)

            # Sort chapters by chapter number (highest to lowest)
            sorted_chapters = sorted(
                chapters,
                key=lambda x: float(x.get('attributes', {}).get('chapter', '0') or '0'),
                reverse=True
            )

            # Table header
            output_lines.append(f"{'Ch#':<8} {'Title':<35} {'Published':<20} {'URL'}")
            output_lines.append("─" * 80)

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

                # Truncate long titles
                display_title = title[:33] + ".." if len(title) > 35 else title

                output_lines.append(f"{chapter_num:<8} {display_title:<35} {formatted_date:<20} {chapter_url}")

            output_lines.append("═" * 80)

        formatted_text = "\n".join(output_lines)
        return Response(formatted_text, mimetype='text/plain')

    except Exception as e:
        return Response(f"Error: {str(e)}", mimetype='text/plain', status=500)


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