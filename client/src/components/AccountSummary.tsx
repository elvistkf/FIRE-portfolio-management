// import React from 'react'
import styled from "styled-components";
import HorizontalDivider from "./HorizontalDivider";
import colorConfigs from "../configs/colorConfigs";

export interface AccountSummaryItem {
    account: number;
    name: string;
    description: string;
    book_value: number;
    cash: number;
    total_market_value: number;
    stock_market_value: number;
    realized_gain: number;
    unrealized_gain: number;
    unrealized_gain_pct: number;
    total_cost: number;
}

interface AccountSummaryProps {
    accountSummary: AccountSummaryItem[];
}

const Container = styled.div`
    padding: 15px;
    background-color: ${colorConfigs.cardBackground};
    border-radius: 10px;
    margin: 0em;
    width: auto;
    /* min-width: 550px; */

    @media screen and (min-width: 1280px) {
        min-width: 400px;
        /* max-width: 700px; */
    }
`

const ItemContainer = styled.div`
    border-radius: 10px;
    padding: 2px;

    transition: background-color 0.2s;

    &:hover {
        cursor: pointer;
        background-color: ${colorConfigs.cardHover};
    }

    -webkit-user-select: none; /* Safari */
    -moz-user-select: none; /* Firefox */
    -ms-user-select: none; /* Edge */
    user-select: none;
`

const TitleContainer = styled.div`
    margin: 0.5em;
`

const Title = styled.div`
    font-size: 1.5em;
    font-weight: bold;
`

const Description = styled.div`
    font-size: 0.9em;
    margin-bottom: 1em;    
`

const MetricsContainer = styled.div`
    /* border: 1px solid red; */
    margin: 0.5em;
    display: flex;
    justify-content: space-between;
    align-items: center;
`

const MetricsItem = styled.div`
    /* border: 1px solid green; */
`

const MetricsTitle = styled.div`
    font-size: 1em;
    font-weight: bold;
    color: #cccccc;
`

const MetricsValue = styled.div`
    font-size: 1.25em;
    font-weight: bold;
`

function onClick(e: any) {
    console.log(e)
}


function AccountSummary({ accountSummary }: AccountSummaryProps) {
    const currencyFormatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    });
    return (
        <Container>
            {
                accountSummary.map((item: AccountSummaryItem, index: number) => (
                    <span key={index}>
                    <ItemContainer onClick={() => onClick(item.account)} >
                        <TitleContainer>
                            <Title>{item.name}</Title>
                            <Description>{item.description}</Description>
                        </TitleContainer>
                        <MetricsContainer>
                            <MetricsItem>
                                <MetricsTitle>Balance</MetricsTitle>
                                <MetricsValue>{currencyFormatter.format(item.total_market_value)}</MetricsValue>
                            </MetricsItem>
                            <MetricsItem>
                                <MetricsTitle>Unrealized Gain</MetricsTitle>
                                <MetricsValue>{currencyFormatter.format(item.unrealized_gain)} | {item.unrealized_gain_pct}%</MetricsValue>
                            </MetricsItem>
                            <MetricsItem>
                                <MetricsTitle>Cash</MetricsTitle>
                                <MetricsValue>{currencyFormatter.format(item.cash)}</MetricsValue>
                            </MetricsItem>
                        </MetricsContainer>
                    </ItemContainer>
                    {index < accountSummary.length - 1 && <HorizontalDivider/>}
                    </span>
                ))
            }
        </Container>

    )
}

export default AccountSummary