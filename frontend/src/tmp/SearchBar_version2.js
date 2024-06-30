import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleInputChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearchClick = () => {
        onSearch(query);
    };

    return (
        <div className="search-bar">
            <textarea
                value={query}
                onChange={handleInputChange}
                placeholder="Enter your query..."
                rows="4" // You can adjust the number of rows to fit your needs
            />
            <button onClick={handleSearchClick}>Search</button>
        </div>
    );
};

export default SearchBar;
