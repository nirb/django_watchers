function fetchWatchersPlotsData(currency, on_done) {
    fetch('/watchers_plots_data/' + currency)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            on_done(data);
        });
}