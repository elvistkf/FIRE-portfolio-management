// import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import colorConfigs from '../configs/colorConfigs';

export interface NavItem {
    title: string;
    url: string;
    icon: any;
}

interface NavbarProps {
    navItems: NavItem[];
}

const Container = styled.nav`
    background-color: ${colorConfigs.navbar};
    padding: 10px;
    width: 175px;
    display: none;

    @media screen and (min-width: 1024px) {
        display: block;
    }
`;

const NavItemsList = styled.ul`
    list-style: none;
    padding: 0;
`;


const NavItemLink = styled(Link)`
  text-decoration: none;
  color: #eee;
  font-size: 16px;
  padding: 8px 16px;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  border-radius: 4px;
  transition: background-color 0.3s;
  margin-bottom: 2px;

  &:hover {
    background-color: ${colorConfigs.navbarHover};
    color: #fff;
  }
`;

const NavItemLinkTitle = styled.div`
    margin-left: 5px;
`;

function NavBar({ navItems }: NavbarProps) {
    console.log(navItems)

    return (
        <Container>
            <NavItemsList>
                {navItems.map((item: NavItem, index: number) => (
                    <li key={index}>
                        {
                            item.url.startsWith('http') ? (
                                <NavItemLink to={item.url} target="_blank" rel="noopener noreferrer">
                                    {item.icon}
                                    <NavItemLinkTitle>
                                        {item.title}
                                    </NavItemLinkTitle>
                                </NavItemLink>
                            ) : (
                                <NavItemLink to={item.url}>
                                    {item.icon}
                                    <NavItemLinkTitle>
                                        {item.title}
                                    </NavItemLinkTitle>
                                </NavItemLink>
                            )
                        }
                    </li>
                ))}
            </NavItemsList>
        </Container>
    );
}

export default NavBar;
