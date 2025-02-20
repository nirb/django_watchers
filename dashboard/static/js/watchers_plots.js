function fetchWatchersPlotsData(currency, events_type, on_done) {
    fetch(`/watchers_plots_data?currency=${currency}&events_type=${events_type}`)
        .then(response => response.json())
        .then(data => {
            //console.log(currency, data);
            if (events_type !== "Statement") {
                // if (currency === "USD") {
                //     console.log("fetchWatchersPlotsData", data);
                // }
                // calculate per quarter
                let quarterlyData = data.reduce((acc, item) => {
                    let date = new Date(item.date);
                    let quarter = Math.floor(date.getMonth() / 3) + 1;
                    let year = date.getFullYear().toString().slice(-2);
                    let key = `Q${quarter}-${year}`;

                    if (!acc[key]) {
                        acc[key] = { date: new Date(year, quarter * 3, 1), value: 0 };
                    }
                    acc[key].value += item.value;

                    return acc;
                }, {});

                // if (currency === "USD") {
                //     console.log("fetchWatchersPlotsData", quarterlyData);
                // }

                let result = [];
                for (let key in quarterlyData) {
                    result.push({ "date": key, "value": quarterlyData[key].value });
                }

                data = result;
                // if (currency === "USD") {
                //     console.log("fetchWatchersPlotsData", result);
                // }
            }
            on_done(data, currency, events_type);
        });
}

function fetchWatcherPlotsData(watcher_id, events_type, on_done) {
    console.log("fetchWatcherPlotsData", watcher_id, events_type);
    fetch(`/watcher_plots_data?watcher_id=${watcher_id}&events_type=${events_type}`)
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
        mode: 'lines+markers', // show dots on the plot
        type: 'scatter'
    };

    var layout = {
        title: title,
        xaxis: {
            title: xaxis_title
        },
        yaxis: {
            title: yaxis_title,
            rangemode: 'tozero'
        },
    };

    var config = {
        responsive: false,
        displayModeBar: false
    };

    Plotly.newPlot(plot_id, [trace], layout, config);
}

function get_profit(data) {
    let first = data.find(d => d.value !== 0).value;
    let last = data[data.length - 1].value;
    let diff = last - first;
    console.log(first, last, diff);
    let profit = ((diff / first) * 100).toFixed(2)
    return (diff < 0 ? '(' : '') + profit + (diff < 0 ? ')' : '') + "%";
}