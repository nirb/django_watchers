let watchers = []

function searchResults(searchStr) {
    const searchResults = document.getElementById('searchResults');

    // first put the spinner
    let reloadTimer;

    if (searchStr === "") {
        searchResults.innerHTML = '<div><div class="spinner-border text-primary text-center" role="status"></div><div>Waiting for input</div></div>'
        reloadTimer = setTimeout(() => {
            window.location.reload()
        }, 4000);
    } else {
        clearTimeout(reloadTimer);
        let content = '<h3 class="app_main_color">Search Results</h3>';
        watchers.forEach(watcher => {
            if (watcher.name.toLowerCase().includes(searchStr.toLowerCase()) ||
                watcher.currency.toLowerCase().includes(searchStr.toLowerCase()) ||
                watcher.advisor.toLowerCase().includes(searchStr.toLowerCase())) {
                content += `
                    <div class="w-50 bg-info m-2 p-2 rounded"><a href="/watcher/${watcher.id}">${watcher.name}</a></div>`;
            }
        });
        searchResults.innerHTML = content;
        console.log(content)
    }
}

function get_watchers() {
    const watchersList = document.getElementById('watchersListOptions');
    console.log("get_watchers...")
    fetch("/search_watchers/__all__!")
        .then(response => response.json())
        .then(data => {
            watchersList.innerHTML = ''; // Clear previous results
            if (data.length > 0) {
                watchers = []
                let content = "";
                data.forEach(item => {
                    let name = item.name
                    content += `<option value="${name}">${name}</option>`;
                    watchers.push(item)
                });
                console.log("get_watchers", watchers)
                watchersList.innerHTML = content;
            }
        })
        .catch(error => console.error('Error:', error));

}