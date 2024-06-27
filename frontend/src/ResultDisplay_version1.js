import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import * as monaco from 'monaco-editor';

const ResultDisplay = ({ result, activeButton, isLoading }) => {
    const [expandedIndexes, setExpandedIndexes] = useState([]);
    const [cellContents, setCellContents] = useState({});
    const [loadingIndexes, setLoadingIndexes] = useState([]);
    const editorRefs = useRef({});

    useEffect(() => {
        // Clear content when the active button changes
        setExpandedIndexes([]);
        setCellContents({});
        if (result && activeButton === 'rag_with_link') {
            result.source_documents.forEach((doc, index) => {
                handlePreviewClick(doc.metadata.title, doc.metadata.first_cell_index, index, true);
            });
        }
        return () => {
            // Clean up editors
            Object.values(editorRefs.current).forEach(editor => editor.dispose());
            editorRefs.current = {};
        };
    }, [activeButton, result]);

    const handlePreviewClick = async (title, cellIndex, index, initialLoad = false) => {
        if (!initialLoad && expandedIndexes.includes(index)) {
            setExpandedIndexes(expandedIndexes.filter(i => i !== index)); // Collapse if already expanded
            return;
        }

        setLoadingIndexes(prev => [...prev, index]);

        try {
            const response = await fetch(`http://localhost:5001/get_cell_content?title=${title}&cell_index=${cellIndex}`);
            const data = await response.json();
            if (response.ok) {
                if (data.error) {
                    console.error('Error fetching cell content:', data.error);
                } else {
                    setCellContents(prev => ({ ...prev, [index]: data }));
                    setExpandedIndexes(prev => [...prev, index]);
                }
            } else {
                console.error('Error fetching cell content:', data.error);
            }
        } catch (error) {
            console.error('Error fetching cell content:', error);
        } finally {
            setLoadingIndexes(prev => prev.filter(i => i !== index));
        }
    };

    const handleContentClick = async (kernelId) => {
        try {
            const response = await fetch(`http://localhost:5001/get_kernel_url?kernel_id=${kernelId}`);
            const data = await response.json();
            if (response.ok) {
                window.open(data.url, '_blank');  // Open Kaggle link in a new tab
            } else {
                console.error('Error fetching URL:', data.error);
            }
        } catch (error) {
            console.error('Error fetching URL:', error);
        }
    };

    const initializeEditor = useCallback((container, value, cellId) => {
        if (container) {
            if (editorRefs.current[cellId]) {
                const editor = editorRefs.current[cellId];
                const model = editor.getModel();
                if (model) {
                    model.setValue(value);
                } else {
                    editor.setModel(monaco.editor.createModel(value, "python"));
                }
            } else {
                const editor = monaco.editor.create(container, {
                    value,
                    language: "python",
                    automaticLayout: true,
                    theme: "vs",
                    readOnly: true,
                });
                editorRefs.current[cellId] = editor;
            }
        }
    }, []);

    const calculateEditorHeight = (value) => {
        const lineHeight = 19; // Default line height in Monaco Editor
        const numberOfLines = value.split('\n').length;
        const height = lineHeight * (numberOfLines + 1);
        return height;
    };

    return (
        <div className="result-display">
            {isLoading ? (
                <div className="loader"></div>
            ) : (
                <>
                    {result && (
                        <>
                            <div className="chat-bubble user-bubble">
                                {result.query}
                            </div>
                            <div className="chat-bubble model-bubble">
                                <ReactMarkdown>{result.result}</ReactMarkdown>
                                {activeButton === 'rag_with_link' && (
                                    <>
                                        <hr className="separator" />
                                        <h2>Source Documents:</h2>
                                        <ul>
                                            {result.source_documents.map((doc, index) => (
                                                <li key={index}>
                                                    <p><strong>Source {index + 1}:</strong>
                                                        <button onClick={() => handlePreviewClick(doc.metadata.title, doc.metadata.first_cell_index, index)}>
                                                            {expandedIndexes.includes(index) ? 'Hide Preview' : 'Show Preview'}
                                                        </button>
                                                    </p>
                                                    {expandedIndexes.includes(index) && (
                                                        <div
                                                            className="cell-content clickable-content"
                                                            onClick={() => handleContentClick(doc.metadata.title)}
                                                        >
                                                            {loadingIndexes.includes(index) ? (
                                                                <div className="loader"></div>
                                                            ) : (
                                                                cellContents[index]?.map((cell, idx) => (
                                                                    cell.cell_type === 'code' ? (
                                                                        <div
                                                                            key={`${index}-${idx}`}
                                                                            style={{ height: calculateEditorHeight(cell.source), border: '1px solid #ddd', marginBottom: '10px' }}
                                                                            ref={(container) => initializeEditor(container, cell.source, `${index}-${idx}`)}
                                                                        />
                                                                    ) : (
                                                                        <div key={`${index}-${idx}`} className="markdown-cell">
                                                                            <ReactMarkdown>{cell.source}</ReactMarkdown>
                                                                        </div>
                                                                    )
                                                                ))
                                                            )}
                                                        </div>
                                                    )}
                                                </li>
                                            ))}
                                        </ul>
                                    </>
                                )}
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
};

export default ResultDisplay;
