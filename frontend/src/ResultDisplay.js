import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import * as monaco from 'monaco-editor';

const ResultDisplay = ({ results, activeButton, isLoading }) => {
    const [expandedIndexes, setExpandedIndexes] = useState(new Set());
    const [cellContents, setCellContents] = useState({});
    const [loadingIndexes, setLoadingIndexes] = useState(new Set());
    const editorRefs = useRef({});
    const queryBubbleRefs = useRef([]);

    const [additionalInfo, setAdditionalInfo] = useState({});

    useEffect(() => {
        setExpandedIndexes(new Set());
        setCellContents({});
    }, [results, activeButton]);

    useEffect(() => {
        if (results.length > 0 && activeButton === 'rag_with_link') {
            results.forEach((result, resultIndex) => {
                result.source_documents.forEach((doc, docIndex) => {
                    const kernelId = doc.metadata.title;
                    fetchAdditionalInfo(kernelId, resultIndex, docIndex);
                    const index = `${resultIndex}-${docIndex}`;
                    if (!cellContents[index]) {
                        handlePreviewClick(doc.metadata.title, doc.metadata.first_cell_index, index, true);
                    }
                });
            });
        }
    }, [results, activeButton]);

    const fetchAdditionalInfo = async (kernelId, resultIndex, docIndex) => {
        try {
            const [responseUsername, responseVotes, responseViews] = await Promise.all([
                fetch(`http://localhost:5001/get_username?kernel_id=${kernelId}`),
                fetch(`http://localhost:5001/get_kernel_vote?kernel_id=${kernelId}`),
                fetch(`http://localhost:5001/get_kernel_view?kernel_id=${kernelId}`)
            ]);

            const dataUsername = await responseUsername.json();
            const dataVotes = await responseVotes.json();
            const dataViews = await responseViews.json();

            const responseProfileImage = await fetch(`http://localhost:5001/get_profile_image_path?username=${dataUsername}`);
            const dataProfileImage = await responseProfileImage.json();

            setAdditionalInfo(prev => ({
                ...prev,
                [`${resultIndex}-${docIndex}`]: {
                    username: dataUsername,
                    votes: dataVotes,
                    views: dataViews,
                    profileImage: `http://localhost:5001/static/profile_images_19988/${dataProfileImage}`
                }
            }));
        } catch (error) {
            console.error('Error fetching additional info:', error);
        }
    };

    const handlePreviewClick = async (title, cellIndex, index, initialLoad = false) => {
        console.log('Fetching preview for:', title, cellIndex, index, initialLoad);

        if (!initialLoad && expandedIndexes.has(index)) {
            const newExpandedIndexes = new Set(expandedIndexes);
            newExpandedIndexes.delete(index);
            setExpandedIndexes(newExpandedIndexes);
            return;
        }

        const localStorageKey = `${title}-${cellIndex}`;
        const cachedData = localStorage.getItem(localStorageKey);

        if (cachedData) {
            const data = JSON.parse(cachedData);
            setCellContents(prev => ({ ...prev, [index]: data }));
            setExpandedIndexes(prev => new Set(prev).add(index));
            return;
        }

        setLoadingIndexes(prev => new Set(prev).add(index));

        try {
            const response = await fetch(`http://localhost:5001/get_cell_content?title=${title}&cell_index=${cellIndex}`);
            const data = await response.json();
            console.log('Fetched data:', data);

            if (response.ok) {
                if (data.error) {
                    console.error('Error fetching cell content:', data.error);
                } else {
                    setCellContents(prev => ({ ...prev, [index]: data }));
                    localStorage.setItem(localStorageKey, JSON.stringify(data));
                    setExpandedIndexes(prev => new Set(prev).add(index));
                }
            } else {
                console.error('Error fetching cell content:', data.error);
            }
        } catch (error) {
            console.error('Error fetching cell content:', error);
        } finally {
            setLoadingIndexes(prev => {
                const newSet = new Set(prev);
                newSet.delete(index);
                return newSet;
            });
        }
    };

    const handleContentClick = async (kernelId) => {
        console.log('Fetching URL for kernel:', kernelId);

        try {
            const response = await fetch(`http://localhost:5001/get_kernel_url?kernel_id=${kernelId}`);
            const data = await response.json();
            console.log('Fetched URL:', data);

            if (response.ok) {
                window.open(data.url, '_blank');
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
                editorRefs.current[cellId].dispose();
            }
            const editor = monaco.editor.create(container, {
                value,
                language: "python",
                automaticLayout: true,
                theme: "vs",
                readOnly: true,
            });
            editorRefs.current[cellId] = editor;
        }
    }, []);

    const calculateEditorHeight = (value) => {
        const lineHeight = 19;
        const numberOfLines = value.split('\n').length;
        const height = lineHeight * (numberOfLines + 1);
        return height;
    };

    useEffect(() => {
        if (queryBubbleRefs.current.length > 0) {
            const lastBubble = queryBubbleRefs.current[queryBubbleRefs.current.length - 1];
            if (lastBubble) {
                setTimeout(() => {
                    lastBubble.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100); // Add a slight delay to ensure the DOM is fully updated
            }
        }
    }, [results]);

    return (
        <div className="result-display">
            {isLoading ? (
                <div className="loader"></div>
            ) : (
                <>
                    {results.map((result, resultIndex) => (
                        <div key={resultIndex}>
                            <div 
                                className="chat-bubble user-bubble" 
                                ref={(el) => {
                                    queryBubbleRefs.current[resultIndex] = el;
                                    if (resultIndex === results.length - 1 && el) {
                                        setTimeout(() => {
                                            el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                        }, 100); // Add a slight delay to ensure the DOM is fully updated
                                    }
                                }}
                            >
                                {result.query}
                            </div>
                            <div className="chat-bubble model-bubble">
                                <ReactMarkdown>{result.response}</ReactMarkdown>
                                {result.mode === 'rag_with_link' && result.source_documents && result.source_documents.length > 0 && (
                                    <>
                                        <hr className="separator" />
                                        <h2>Source Documents:</h2>
                                        <ul className="source-documents-list">
                                            {result.source_documents.map((doc, docIndex) => (
                                                <li key={docIndex} className="source-document-container">
                                                    <div className="source-document-header">
                                                        <img
                                                            src={additionalInfo[`${resultIndex}-${docIndex}`]?.profileImage || `http://localhost:5001/static/profile_images_19988/default.jpg`}
                                                            alt={`${additionalInfo[`${resultIndex}-${docIndex}`]?.username || 'default'}'s profile`}
                                                            className="profile-image"
                                                        />
                                                        <div className="source-document-info">
                                                            <p><strong>Source {docIndex + 1}</strong></p>
                                                            <p>Author: {additionalInfo[`${resultIndex}-${docIndex}`]?.username || 'Loading...'}</p>
                                                            <p>Views: {additionalInfo[`${resultIndex}-${docIndex}`]?.views || 'Loading...'}</p>
                                                            <p>Votes: {additionalInfo[`${resultIndex}-${docIndex}`]?.votes || 'Loading...'}</p>
                                                        </div>
                                                    </div>
                                                    <div className="source-document-content">
                                                        <button onClick={() => handlePreviewClick(doc.metadata.title, doc.metadata.first_cell_index, `${resultIndex}-${docIndex}`)}>
                                                            {expandedIndexes.has(`${resultIndex}-${docIndex}`) ? 'Hide Preview' : 'Show Preview'}
                                                        </button>
                                                        {expandedIndexes.has(`${resultIndex}-${docIndex}`) && (
                                                            <div
                                                                className="cell-content clickable-content"
                                                                onClick={() => handleContentClick(doc.metadata.title)}
                                                            >
                                                                {loadingIndexes.has(`${resultIndex}-${docIndex}`) ? (
                                                                    <div className="loader"></div>
                                                                ) : (
                                                                    cellContents[`${resultIndex}-${docIndex}`]?.map((cell, cellIdx) => (
                                                                        cell.cell_type === 'code' ? (
                                                                            <div
                                                                                key={`${resultIndex}-${docIndex}-${cellIdx}`}
                                                                                style={{ height: calculateEditorHeight(cell.source), border: '1px solid #ddd', marginBottom: '10px' }}
                                                                                ref={(container) => initializeEditor(container, cell.source, `${resultIndex}-${docIndex}-${cellIdx}`)}
                                                                            />
                                                                        ) : (
                                                                            <div key={`${resultIndex}-${docIndex}-${cellIdx}`} className="markdown-cell">
                                                                                <ReactMarkdown>{cell.source}</ReactMarkdown>
                                                                            </div>
                                                                        )
                                                                    ))
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                </li>
                                            ))}
                                        </ul>
                                    </>
                                )}
                            </div>
                        </div>
                    ))}
                </>
            )}
        </div>
    );
};

export default ResultDisplay;
