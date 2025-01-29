function searchResults(searchStr) {
    const searchResults = document.getElementById('searchResults');

    // first put the spinner
    searchResults.innerHTML = '<div class="spinner-border text-primary text-center" role="status"><span class="visually-hidden">Loading...</span></div>'

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
                    searchResults.innerHTML = '<h3 class="text-center">No watchers found.</h3>';
                }
            })
            .catch(error => console.error('Error:', error));
    }
    console.log('Search string end');
}

function get_watchers() {
    console.log("get_watchers")
    const watchersList = document.getElementById('watchersListOptions');
    fetch("/search_watchers/__all__!")
        .then(response => response.json())
        .then(data => {
            watchersList.innerHTML = ''; // Clear previous results
            if (data.length > 0) {
                // Build the list-group using template literals
                let content = "";
                data.forEach(item => {
                    let name = item.name
                    content += `<option value="${name}">${name}</option>`;
                });
                watchersList.innerHTML = content;
            }
        })
        .catch(error => console.error('Error:', error));

}