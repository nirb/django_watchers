function fetchWatchersPlotsData(currency, events_type, on_done) {
    fetch(`/watchers_plots_data?currency=${currency}&events_type=${events_type}`)
        .then(response => response.json())
        .then(data => {
            //console.log(currency, data);
            if (events_type !== "Statement") {
                // calculate per quarter
                let quarterlyData = data.reduce((acc, item) => {
                    let date = new Date(item.date);
                    let quarter = Math.floor((date.getMonth() + 3) / 3);
                    let year = date.getFullYear();
                    let key = `${year}-Q${quarter}`;

                    if (!acc[key]) {
                        acc[key] = { date: new Date(year, quarter * 3 - 1, 1), value: 0 };
                    }
                    acc[key].value += item.value;

                    return acc;
                }, {});

                let result = Object.values(quarterlyData).map(item => {
                    item.date = item.date.toISOString().split('T')[0];
                    return item;
                });

                data = result;
            }
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
        paper_bgcolor: 'rgba(0,0,0,0)',  // Transparent background
        plot_bgcolor: 'rgba(0,0,0,0)',   // Transparent plot area
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
            pad: 4
        },
        shapes: [
            {
                type: 'path',  // Other options include 'rect 'circle', 'line', 'path'
                xref: 'paper',
                yref: 'paper',
                x0: 0,
                y0: 0,
                x1: 1,
                y1: 1,
                line: {
                    width: 2,
                    color: 'black'
                }
            }
        ]
    };

    var config = {
        responsive: true
    };

    Plotly.newPlot(plot_id, [trace], layout, config);
}