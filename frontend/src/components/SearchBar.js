import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleInputChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearchClick = () => {
        onSearch(query);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {  // Check for Enter key without Shift
            e.preventDefault();  // Prevent default Enter key behavior
            handleSearchClick();
        }
    };

    return (
        <div className="search-bar">
            <textarea
                value={query}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}  // Add the keydown event listener
                placeholder="Enter your query..."
                rows="4" // You can adjust the number of rows to fit your needs
            />
            <button onClick={handleSearchClick}>Search</button>
        </div>
    );
};

export default SearchBar;
