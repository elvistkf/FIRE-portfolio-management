// import React from 'react';
import styled from 'styled-components';
import colorConfigs from '../configs/colorConfigs';

const Divider = styled.hr`
    height: 0px;
    border: none;
    border-top: 1px solid ${colorConfigs.divider};
    /* border-top: 1px solid #606060; */
`;

function HorizontalDivider() {
    return <Divider />;
};

export default HorizontalDivider;
