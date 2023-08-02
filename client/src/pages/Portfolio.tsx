// import React from 'react'
import { useEffect, useState } from 'react';
import EfficientFrontier from '../components/EfficientFrontier';


function Portfolio() {
    const [loading, setLoading] = useState(true)
    const [efficientFrontier, setEfficientFrontier] = useState([])
    const [overallMetrics, setOverallMetrics] = useState([])

    const fetchEfficientFrontier = () => {
        return fetch('http://localhost:49255/portfolio/efficient_frontier')     // placeholder for development
                .then(res => res.json())
                .catch(err => console.log(err))
    }

    const fetchOverallMetrics = () => {
        return fetch('http://localhost:49255/portfolio/overall_metrics')        // placeholder for development
                .then(res => res.json())
                .catch(err => console.log(err))
    }

    useEffect(() => {
        Promise.all([fetchEfficientFrontier(), fetchOverallMetrics()])
            .then(([efficientFrontier, overallMetrics]) => {
                setEfficientFrontier(efficientFrontier);
                setOverallMetrics(overallMetrics);
                setLoading(false);
            })
    }, [])

    if (!loading) {
        var portfolio = {
            "x": overallMetrics["volatility"],
            "y": overallMetrics["expected_return"]
        }
        return (
            <EfficientFrontier curve={efficientFrontier["curve"]} tickers={efficientFrontier["tickers"]} portfolio={portfolio} />
        )
    }
    else {
        return (
            <div>Loading...</div>
        )
    }
    
}

export default Portfolio