// src/Header.js
import { useState } from 'react';
import React from 'react';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';

const Header = ({ handleButtonClickCallback }) => {
    const [activeButton, setActiveButton] = useState('rag_with_link');

    const handleButtonClick = (mode) => {
        setActiveButton(mode);
        handleButtonClickCallback(mode);  // Clear results and local storage
    };
    return (
        <header>
        <Navbar expand="lg" className="bg-body-tertiary">
            <Container>
                <Navbar.Brand>
                    <h1>CompetiLearn</h1>
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <NavDropdown title="Condition" id="basic-nav-dropdown">
                            <NavDropdown.Item active={activeButton=== 'rag_with_link'} onClick={() => handleButtonClick('rag_with_link')}>
                                Alpha
                            </NavDropdown.Item>
                            <NavDropdown.Item active={activeButton=== 'rag_without_link'} onClick={() => handleButtonClick('rag_without_link')}>
                                Beta
                            </NavDropdown.Item>
                            <NavDropdown.Item active={activeButton=== 'gpt4o'} onClick={() => handleButtonClick('gpt4o')}>
                                Gamma
                            </NavDropdown.Item>
                        </NavDropdown>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
        </header>
    );
};

export default Header;
