import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import VerticalNavbar from './components/Navbar';
import Landing from './pages/Landing';
import Optimization from './pages/Optimization';

// Define the NavItem interface (you can define it here or in a separate file)
interface NavItem {
    title: string;
    url: string;
}

const Container = styled.div`
    display: flex;
    margin: 0;
    height: 100vh;
`;

const MainContent = styled.div`
    flex: 1;
    padding: 20px;
`;

const App: React.FC = () => {
    const navItems: NavItem[] = [
        { title: 'Home', url: '/' },
        { title: 'Optimization', url: '/optimization' },
        { title: 'About', url: '/about' },
        { title: 'Contact', url: '/contact' },
    ];

    return (
        <Router>
            <Container>
                {/* Use the VerticalNavbar component */}
                <VerticalNavbar navItems={navItems} />

                <MainContent>
                    {/* Define your routes and components */}
                    <Routes>
                        <Route path="/" element={<Landing />} />
                        <Route path="/optimization" element={<Optimization />} />
                        <Route path="/about" element={<AboutComponent />} />
                        <Route path="/contact" element={<ContactComponent />} />
                    </Routes>
                </MainContent>
            </Container>
        </Router>
    );
};

// Define your components for each route (replace HomeComponent, AboutComponent, and ContactComponent with your actual components)
const AboutComponent: React.FC = () => <div>About Content</div>;
const ContactComponent: React.FC = () => <div>Contact Content</div>;

export default App;
