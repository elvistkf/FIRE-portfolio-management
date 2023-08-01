// import React from 'react'
import { useEffect, useState } from 'react';
import EfficientFrontier from '../components/EfficientFrontier';


function Portfolio() {
    const [efficientFrontier, setEfficientFrontier] = useState([])

    const fetchData = () => {
        fetch('http://localhost:49255/portfolio/efficient_frontier')   // placeholder for development
            .then(res => res.json())
            .then(data => {
                console.log(data)
                setEfficientFrontier(data)
            })
            .catch(err => console.log(err))
    }

    useEffect(() => {
        fetchData()
    }, [])
    return (
        <EfficientFrontier data={efficientFrontier} />
    )
}

export default Portfolio