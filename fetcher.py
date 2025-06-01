#!/usr/bin/env python3
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import MANGA_IDS

def authenticate():
    load_dotenv()
    username = os.getenv("MANGADEX_USERNAME")
    password = os.getenv("MANGADEX_PASSWORD")
    client_id = os.getenv("MANGADEX_CLIENT_ID")
    client_secret = os.getenv("MANGADEX_CLIENT_SECRET")

    if not all([username, password, client_id, client_secret]):
        print("Missing .env credentials")
        return None

    auth_data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret
    }

    r = requests.post("https://auth.mangadex.org/realms/mangadex/protocol/openid-connect/token", data=auth_data)
    return r.json()["access_token"] if r.status_code == 200 else None

def get_latest_chapters(access_token, manga_id, days_back=30):
    one_month_ago = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        "translatedLanguage[]": ["en"],
        "order[publishAt]": "desc",
        "publishAtSince": one_month_ago,
        "limit": 20
    }

    r = requests.get(
        "https://api.mangadex.org/manga/" + manga_id + "/feed",
        params=params,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if r.status_code != 200:
        print("Failed to get chapters")
        return []

    chapters = r.json()["data"]

    # Filter out weird dates (future dates beyond 2025)
    valid_chapters = []
    for chapter in chapters:
        date_str = chapter['attributes']['publishAt'][:10]
        year = int(date_str[:4])

        if year <= datetime.today().year:  # Filter out weird future dates
            valid_chapters.append(chapter)

    return valid_chapters

def group_by_manga_series(chapters, id_to_name_dict):
    """
    Groups a list of chapter objects by manga series.

    Args:
        chapters: List of chapter dictionaries

    Returns:
        dict: Dictionary with manga IDs as keys and lists of chapters as values
    """
    manga_groups = {}

    for chapter in chapters:
        # Find the manga relationship
        manga_id = None
        for relationship in chapter.get('relationships', []):
            if relationship.get('type') == 'manga':
                manga_id = relationship.get('id')
                break

        if manga_id:
            if manga_id not in manga_groups:
                manga_groups[manga_id] = []
            manga_groups[manga_id].append(chapter)

    manga_name_groups = {}
    manga_no_updates = []
    res = {}
    for manga_id, manga_name in id_to_name_dict.items():
        if manga_id not in manga_groups:
            manga_no_updates.append(manga_name)
        else:
            res[id_to_name_dict[manga_id]] = manga_groups[manga_id]
    print("Did not find updates for: ", manga_no_updates)
    print("=" * 80)
    return res


def display_grouped_manga(manga_groups):
    """Display manga groups with detailed chapter information, sorted by chapter number"""
    print("🔥 MangaDex Latest Chapters")
    print("=" * 80)

    for manga_name, chapters in manga_groups.items():
        print(f"\n📚 {manga_name}")
        print(f"Latest chapters: {len(chapters)}")
        print("-" * 80)

        # Sort chapters by chapter number (highest to lowest)
        sorted_chapters = sorted(
            chapters,
            key=lambda x: float(x.get('attributes', {}).get('chapter', '0') or '0'),
            reverse=True
        )

        # Table header
        print(f"{'Ch#':<8} {'Title':<35} {'Published':<20} {'URL'}")
        print("─" * 80)

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
            chapter_url = f"{chapter_url}"

            print(f"{chapter_num:<8} {display_title:<35} {formatted_date:<20} {chapter_url}")

        print("═" * 80)

def main():
    print("🚀 MangaDex Latest Chapters")

    access_token = authenticate()
    if not access_token:
        print("Authentication failed")
        return

    latest_chapters = []
    for manga_id in MANGA_IDS:
        latest_chapters.extend(get_latest_chapters(access_token, manga_id))

    grouped_manga = group_by_manga_series(latest_chapters, MANGA_IDS)
    display_grouped_manga(grouped_manga)

if __name__ == "__main__":
    main()