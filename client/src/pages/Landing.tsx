// import React from 'react'
import { useEffect, useState } from 'react';
import AccountSummary from '../components/AccountSummary';
import EfficientFrontier from '../components/EfficientFrontier';

function Landing() {
    const [accountSummary, setAccountSummary] = useState([])
    const [efficientFrontier, setEfficientFrontier] = useState([])

    const fetchData = () => {
        fetch('http://localhost:49255/portfolio/summary')   // placeholder for development
            .then(res => res.json())
            .then(data => {
                console.log(data)
                setAccountSummary(data)
            })
            .catch(err => console.log(err));

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
        <AccountSummary accountSummary={accountSummary} />
    )
}

export default Landing