import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './Header';
import SearchBar from './SearchBar';
import ResultDisplay from './ResultDisplay';
import axios from 'axios';
import AdvancedSearchPanel from './AdvancedSearchPanel';

function App() {
    const [results, setResults] = useState([]);
    const [activeButton, setActiveButton] = useState('rag_with_link');
    const [isLoading, setIsLoading] = useState(false);
    const [isAdvancedSearchOpen, setIsAdvancedSearchOpen] = useState(false);
    const [temperature, setTemperature] = useState(0.7);  // Default temperature
    const [searchMode, setSearchMode] = useState('relevance');  // Default search mode

    useEffect(() => {
        localStorage.removeItem('chatHistory');
    }, []);

    useEffect(() => {
        localStorage.setItem('chatHistory', JSON.stringify(results));
    }, [results]);

    const handleSearch = (query, mode) => {
        console.log('Search query:', query);
        console.log('Query mode:', mode);

        setIsLoading(true);

        axios.post('/search', { query, mode, temperature, search_mode: searchMode }, {
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log('Response from server:', response.data);
                const newResult = { query, response: response.data.result, mode, source_documents: response.data.source_documents || [] };
                setResults(prevResults => [...prevResults, newResult]);
            })
            .catch(error => {
                console.error('There was an error sending the query:', error);
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    const handleButtonClick = (mode) => {
        setActiveButton(mode);
        handleNewChat();  // Clear results and local storage
    };

    const handleNewChat = () => {
        setResults([]);
        setIsAdvancedSearchOpen(false);  // Close advanced search if open
        localStorage.removeItem('chatHistory');  // Clear local storage
    };

    const toggleAdvancedSearch = () => {
        setIsAdvancedSearchOpen(!isAdvancedSearchOpen);
    };

    const handleTemperatureChange = (value) => {
        setTemperature(value);
    };

    const handleSearchModeChange = (value) => {
        setSearchMode(value);
    };

    return (
        <div className="App">
            <Header />
            <div className="button-group">
                <button
                    className={`mode-button ${activeButton === 'rag_with_link' ? 'active' : ''}`}
                    onClick={() => handleButtonClick('rag_with_link')}
                >
                    RAG (with link)
                </button>
                <button
                    className={`mode-button ${activeButton === 'rag_without_link' ? 'active' : ''}`}
                    onClick={() => handleButtonClick('rag_without_link')}
                >
                    RAG (without link)
                </button>
                <button
                    className={`mode-button ${activeButton === 'gpt4o' ? 'active' : ''}`}
                    onClick={() => handleButtonClick('gpt4o')}
                >
                    GPT-4o
                </button>
            </div>
            <ResultDisplay results={results} activeButton={activeButton} isLoading={isLoading} />
            <div className="search-bar-container">
                <button className="new-chat-button" onClick={handleNewChat}>Start a new chat</button>
                <SearchBar onSearch={(query) => handleSearch(query, activeButton)} />
                <button className="advanced-search-button" onClick={toggleAdvancedSearch}>
                    Advanced Search
                </button>
            </div>
            {isAdvancedSearchOpen && (
                <AdvancedSearchPanel
                    temperature={temperature}
                    onTemperatureChange={handleTemperatureChange}
                    searchMode={searchMode}
                    onSearchModeChange={handleSearchModeChange}
                />
            )}
        </div>
    );
}

export default App;
