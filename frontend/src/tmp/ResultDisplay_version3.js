import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import RAGSourcePanel from './RAGSourcePanel';

const ResultDisplay = ({ results, activeButton, isLoading }) => {
    const queryBubbleRefs = useRef([]);

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
                                        {result.source_documents.map((doc, docIndex) => (
                                            <RAGSourcePanel doc={doc} docIndex={docIndex} resultIndex={resultIndex} key={docIndex}></RAGSourcePanel>
                                        ))}
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