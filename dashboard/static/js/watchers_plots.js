function fetchWatchersPlotsData(currency, on_done) {
    fetch('/watchers_plots_data/' + currency)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            on_done(data, currency);
        });
}

// generate plot using plotly, data is an array of objects with keys date and value
function generateCurrencyPlot(data, title, xaxis_title, yaxis_title, plot_id) {
    var dates = data.map(d => d.date);
    var values = data.map(d => d.value);

    var trace = {
        x: dates,
        y: values,
        mode: 'lines',
        type: 'scatter'
    };

    var layout = {
        title: title,
        xaxis: {
            title: xaxis_title
        },
        yaxis: {
            title: yaxis_title
        },
    };

    var config = {
        responsive: true
    };

    Plotly.newPlot(plot_id, [trace], layout, config);
}