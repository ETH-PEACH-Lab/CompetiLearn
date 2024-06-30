import React, { useState } from 'react';
import './App.css';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import ResultDisplay from '../components/ResultDisplay';
import axios from 'axios';

function App() {
    const [result, setResult] = useState(null);
    const [activeButton, setActiveButton] = useState('rag_with_link');
    const [isLoading, setIsLoading] = useState(false); // Add loading state

    const handleSearch = (query, mode) => {
        console.log('Search query:', query);
        console.log('Query mode:', mode);

        setIsLoading(true); // Set loading state to true when search starts

        axios.post('http://localhost:5001/search', { query, mode })
            .then(response => {
                console.log('Response from server:', response.data);
                setResult(response.data);  // Store the result in the state
            })
            .catch(error => {
                console.error('There was an error sending the query:', error);
            })
            .finally(() => {
                setIsLoading(false); // Set loading state to false when search ends
            });
    };

    const handleButtonClick = (mode) => {
        setActiveButton(mode);
        setResult(null);  // Clear the result when changing the mode
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
            <SearchBar onSearch={(query) => handleSearch(query, activeButton)} />
            <ResultDisplay result={result} activeButton={activeButton} isLoading={isLoading} /> {/* Pass isLoading state */}
        </div>
    );
}

export default App;
