import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowUp } from '@fortawesome/free-solid-svg-icons';
import React, { useState, useEffect, useRef } from 'react';
import { Tooltip } from 'react-tooltip';

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const textareaRef = useRef(null);
    const maxRows = 14; // Maximum number of rows
    const lineHeight = 24; // Adjust based on your CSS line height

    const handleInputChange = (e) => {
        setQuery(e.target.value);
        autoResizeTextarea();
    };

    const handleSearchClick = () => {
        onSearch(query);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {  // Check for Enter key without Shift
            e.preventDefault();  // Prevent default Enter key behavior
            handleSearchClick();
            setQuery('');
            autoResizeTextarea();
        }
    };

    const autoResizeTextarea = () => {
        const textarea = textareaRef.current;
        textarea.style.height = 'auto';
        const newHeight = Math.min(textarea.scrollHeight, maxRows * lineHeight);
        textarea.style.height = `${newHeight}px`;
    };

    useEffect(() => {
        autoResizeTextarea(); // Initial resize on mount
    }, []);

    return (
        <div className="search-bar">
            <textarea
                id="search-textarea"
                ref={textareaRef}
                value={query}
                onChange={handleInputChange}
                onInput={autoResizeTextarea}  // Add onInput event
                onKeyDown={handleKeyDown}  // Add the keydown event listener
                placeholder="Enter your query..."
                rows="1" // You can adjust the number of rows to fit your needs
                style={{ overflow: 'hidden', resize: 'none' }} // Ensure the textarea looks good when resized
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
