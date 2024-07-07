import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUp } from '@fortawesome/free-solid-svg-icons';
import React, { useState } from 'react';

import { Tooltip } from 'react-tooltip';

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
            setQuery('');
        }
    };

    return (
        <div className="search-bar">
            <textarea
                id="search-textarea"
                value={query}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}  // Add the keydown event listener
                placeholder="Enter your query..."
                rows="1" // You can adjust the number of rows to fit your needs
            />
            <button onClick={handleSearchClick} className='primary-button'> 
                    <Tooltip id="my-tooltip-search" />
                    <a data-tooltip-id="my-tooltip-search" data-tooltip-content="Send Query">
                    <FontAwesomeIcon icon={faArrowUp}/>
                    </a>
            </button>
        </div>
    );
};

export default SearchBar;
