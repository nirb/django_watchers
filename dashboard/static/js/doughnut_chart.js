document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        height = document.getElementById('watchers_table_summary').clientHeight // Set height according to parent height
        console.log("doughut", height)
        const data = [{
            values: chartData.values, // Values for USD, NIS, and EUR
            labels: chartData.labels,
            type: 'pie',
            hole: 0.5, // Creates the "doughnut" effect
            textinfo: 'label+value', // Shows labels and values
            textposition: 'inside',
            marker: {
                colors: ['#636EFA', '#EF553B', '#00CC96'] // Custom colors
            }
        }];

        const layout = {
            title: {
                text: 'Currency Distribution',
                font: { size: 18 }
            },
            showlegend: false, // Hides the legend
            annotations: [
                {
                    font: {
                        size: 16
                    },
                    showarrow: false,
                    text: '',
                    x: 0.5,
                    y: 0.5
                }
            ],
            margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 0,
                pad: 0
            },
            height: height,
            paper_bgcolor: 'rgba(0, 0, 0, 0)',  // Transparent background for the entire plot
            plot_bgcolor: 'rgba(0, 0, 0, 0)'   // Transparent background for the plot area
        };

        Plotly.newPlot('doughnut-chart', data, layout, { displayModeBar: false });
    }, 100);

});
