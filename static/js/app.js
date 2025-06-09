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