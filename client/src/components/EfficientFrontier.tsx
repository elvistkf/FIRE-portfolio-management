// import React from 'react'
import { Scatter } from 'react-chartjs-2';

import {
    Chart as ChartJS,
    LinearScale,
    PointElement,
    LineElement,
    Tooltip,
    Legend
} from 'chart.js'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

interface DataPoint {
    x: number;
    y: number;
}

interface TickerDataPoint {
    ticker: string;
    x: number;
    y: number;
}

interface DataProps {
    tickers: TickerDataPoint[];
    curve: DataPoint[];
    portfolio: DataPoint;
}

function EfficientFrontier({ curve, tickers, portfolio }: DataProps) {
    const options = {
        showLine: true,
        elements: {
            point: {
                radius: 5
            }
        }
    };

    var datasets: any = [{
        label: 'Efficient Frontier',
        data: curve,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        order: 1,
        elements: {
            point: {
                radius: 1
            }
        }
    }]

    if (tickers) {
        const mappedTickers: any = tickers.map((ticker) => ({
            label: ticker.ticker,
            data: [
                {
                    x: ticker.x,
                    y: ticker.y
                }
            ],
            backgroundColor: 'rgb(' + Math.floor(Math.random() * 100 + 50).toString() + ', '
                + Math.floor(Math.random() * 200 + 55).toString() + ', '
                + Math.floor(Math.random() * 225 + 30).toString() + ')',
        }));
        datasets.push(...mappedTickers);
    }

    if (portfolio) {
        const mappedOverall: any = {
            label: 'Portfolio',
            data: [
                {
                    x: portfolio.x,
                    y: portfolio.y
                }
            ],
            backgroundColor: 'rgb(200, 200, 200)',
            borderColor: 'rgb(132, 99, 255)',
        }
        datasets.push(mappedOverall);
    }

    var chartData = {
        datasets: datasets
    };

    return <Scatter options={options} data={chartData} />;
}

export default EfficientFrontier