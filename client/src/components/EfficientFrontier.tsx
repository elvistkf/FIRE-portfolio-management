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

interface DataProps {
    data: DataPoint[];
}

export const options = {
    showLine: true,
    elements: {
        point: {
            radius: 5
        }
    }
};


function EfficientFrontier({ data }: DataProps) {
    const chartData = {
        datasets: [
            {
                label: 'Efficient Frontier',
                data: data,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                elements: {
                    point: {
                        radius: 1
                    }
                }
            },
            {   // TODO: replace this with real data
                label: 'QQQ',
                data: [
                    {
                        x: 0.0160972672,
                        y: 0.0007595723
                    }
                ],
                backgroundColor: 'rgba(0, 99, 255)',
            }
        ],
    };
    return <Scatter options={options} data={chartData} />;
}

export default EfficientFrontier