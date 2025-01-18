function fetchWatchersPlotsData(currency, events_type, on_done) {
    fetch(`/watchers_plots_data?currency=${currency}&events_type=${events_type}`)
        .then(response => response.json())
        .then(data => {
            console.log(currency, data);
            on_done(data, currency, events_type);
        });
}

function fetchWatcherPlotsData(watcher_name, events_type, on_done) {
    console.log("fetchWatcherPlotsData", watcher_name, events_type);
    fetch(`/watcher_plots_data?watcher=${watcher_name}&events_type=${events_type}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            on_done(data, events_type);
        });
}

// generate plot using plotly, data is an array of objects with keys date and value
function generateCurrencyPlot(data, title, xaxis_title, yaxis_title, plot_id) {
    var dates = data.map(d => d.date);
    var values = data.map(d => d.value);

    var trace = {
        x: dates,
        y: values,
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            shape: title.includes("Statement") ? "spline" : "line",   // Makes the line curved
            color: "blue",     // Optional: Customize the color
            width: 4           // Optional: Set the line width
        },
        marker: {
            size: 6,           // Customize marker size
            color: "red"       // Customize marker color
        }
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