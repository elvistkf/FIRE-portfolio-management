// VerticalNavbar.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

interface NavItem {
  title: string;
  url: string;
}

interface VerticalNavbarProps {
  navItems: NavItem[];
}

const VerticalNav = styled.nav`
  background-color: #333;
  padding: 10px;
  width: 200px;
`;

const NavItemsList = styled.ul`
  list-style: none;
  padding: 0;
`;

const NavItemLink = styled(Link)`
  text-decoration: none;
  color: #fff;
  font-size: 16px;
  padding: 8px 16px;
  display: block;
  border-radius: 4px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #555;
    color: #ccc;
  }
`;

function VerticalNavbar({ navItems }: VerticalNavbarProps) {
  return (
    <VerticalNav>
      <NavItemsList>
        {navItems.map((item, index) => (
          <li key={index}>
            <NavItemLink to={item.url}>{item.title}</NavItemLink>
          </li>
        ))}
      </NavItemsList>
    </VerticalNav>
  );
}

export default VerticalNavbar;
