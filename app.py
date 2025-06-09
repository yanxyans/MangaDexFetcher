from flask import Flask, Response, render_template
import os
import json
from datetime import datetime

# Import your existing functions
from fetcher import authenticate, get_latest_chapters, group_by_manga_series
from config import MANGA_IDS

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/manga')
def get_manga():
    try:
        # Use your functions exactly as they are
        token = authenticate()
        if not token:
            return Response(json.dumps({"error": "Authentication failed"}), mimetype='application/json', status=500)

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
            json.dumps(json_data, ensure_ascii=False, indent=2),
            mimetype='application/json'
        )

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype='application/json', status=500)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    # Check if we're running on Railway (or any cloud platform)
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PORT'):
        # Production/Railway deployment
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        # Local development
        app.run(debug=True, port=5000)