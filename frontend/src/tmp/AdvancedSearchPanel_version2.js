import React from 'react';
import './AdvancedSearchPanel.css';

const AdvancedSearchPanel = ({ temperature, onTemperatureChange }) => {
    const handleSliderChange = (event) => {
        onTemperatureChange(parseFloat(event.target.value));
    };

    return (
        <div className="advanced-search-panel">
            <h3>Advanced Search Options</h3>
            <div className="slider-container">
                <label>Temperature: {temperature}</label>
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={temperature}
                    onChange={handleSliderChange}
                />
            </div>
        </div>
    );
};

export default AdvancedSearchPanel;
