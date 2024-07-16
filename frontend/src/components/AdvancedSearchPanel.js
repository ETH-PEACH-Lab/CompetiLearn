import React from 'react';
import '../styles/AdvancedSearchPanel.css';

const AdvancedSearchPanel = ({ temperature, onTemperatureChange, searchMode, onSearchModeChange }) => {
    const handleSliderChange = (event) => {
        onTemperatureChange(parseFloat(event.target.value));
    };

    const handleModeChange = (event) => {
        onSearchModeChange(event.target.value);
    };

    return (
        <div className="advanced-search-panel">
            <h3>Advanced Search Options</h3>
            {/* <div className="slider-container">
                <label>Temperature: {temperature}</label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={temperature}
                    onChange={handleSliderChange}
                />
            </div> */}
            <div className="mode-container">
                <label>Order By:</label>
                <select value={searchMode} onChange={handleModeChange}>
                    <option value="votes">Votes</option>
                    <option value="relevance">Relevance</option>

                    <option value="views">Views</option>
                </select>
            </div>
        </div>
    );
};

export default AdvancedSearchPanel;
