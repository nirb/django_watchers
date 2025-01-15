function searchResults(searchStr) {
    const searchResults = document.getElementById('searchResults');

    console.log('Search string:', searchStr);
    if (searchStr.length > 0) {
        fetch(`/search_watchers/${searchStr}`)
            .then(response => response.json())
            .then(data => {
                searchResults.innerHTML = ''; // Clear previous results
                if (data.length > 0) {
                    // Build the list-group using template literals
                    let content = '<h3 class="app_main_color">Search Results</h3><ul class="list-group">';
                    content += `<ul class="list-group">`;
                    data.forEach(item => {
                        content += `
                        <li class="list-group-item p-2"><a href="/watcher/${item.id}" style="font-size: small;">${item.name}</a></li>`;
                    });
                    content += '</ul>';
                    searchResults.innerHTML = content;
                } else {
                    searchResults.innerHTML = '<p class="text-center">No watchers found.</p>';
                }
            })
            .catch(error => console.error('Error:', error));
    }
}