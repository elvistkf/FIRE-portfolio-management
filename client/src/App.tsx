// import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import NavBar, { NavItem } from './components/Navbar';
import Landing from './pages/Landing';
import Portfolio from './pages/Portfolio';
import {AiOutlineLineChart, AiOutlineHome, AiOutlineGithub} from 'react-icons/ai';


const Container = styled.div`
    display: flex;
    margin: 0;
    height: 100vh;
    width: 100%;
`;

const MainContent = styled.div`
    /* flex: 1; */
    padding: 20px;
    width: 100%;
`;

function App() {
    const navItems: NavItem[] = [
        { title: 'Home', url: '/', icon: <AiOutlineHome /> },
        { title: 'Portfolio', url: '/portfolio', icon: <AiOutlineLineChart /> },
        { title: 'GitHub', url: 'https://github.com/elvistkf/FIRE-portfolio-management', icon: <AiOutlineGithub />}
    ];

    return (
        <Router>
            <Container>
                <NavBar navItems={navItems} />
                <MainContent>
                    <Routes>
                        <Route path="/" element={<Landing />} />
                        <Route path="/portfolio" element={<Portfolio />} />
                    </Routes>
                </MainContent>
            </Container>
        </Router>
    );
};

export default App;
