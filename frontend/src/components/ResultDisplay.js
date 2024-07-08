import React, { useEffect, useRef } from 'react';
import Markdown from 'react-markdown';
import RAGSourcePanel from './RAGSourcePanel';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { faRobot } from '@fortawesome/free-solid-svg-icons';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'


const ResultDisplay = ({ results }) => {
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
                            <div className="chat-user">
                                <FontAwesomeIcon icon={faUser} />
                            </div>
                            <div className='chat-content'>
                                <Markdown
                                    children={result.query}
                                    components={{
                                        code(props) {
                                            const { children, className, node, ...rest } = props
                                            const match = /language-(\w+)/.exec(className || '')
                                            return match ? (
                                                <SyntaxHighlighter
                                                    {...rest}
                                                    PreTag="div"
                                                    children={String(children).replace(/\n$/, '')}
                                                    language={match[1]}
                                                    style={vscDarkPlus}
                                                />
                                            ) : (
                                                <code {...rest} className={className}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                />
                            </div>
                        </div>

                        <div className="chat-bubble model-bubble">
                            <div className="chat-user chat-bot">
                                <FontAwesomeIcon icon={faRobot} />
                            </div>
                            <div className='chat-content'>
                                {!result.response && <div className="loader"></div>}
                                <Markdown
                                    children={result.response}
                                    components={{
                                        code(props) {
                                            const { children, className, node, ...rest } = props
                                            const match = /language-(\w+)/.exec(className || '')
                                            return match ? (
                                                <SyntaxHighlighter
                                                    {...rest}
                                                    PreTag="div"
                                                    children={String(children).replace(/\n$/, '')}
                                                    language={match[1]}
                                                    style={vscDarkPlus}
                                                />
                                            ) : (
                                                <code {...rest} className={className}>
                                                    {children}
                                                </code>
                                            )
                                        }
                                    }}
                                />
                                {result.mode === 'rag_with_link' && result.source_documents && result.source_documents.length > 0 && (
                                    <div className='source-display-container'>
                                        <hr className="separator" />
                                        <h2 className="source">Based on the following Kaggle posts:</h2>
                                        {result.source_documents.map((doc, docIndex) => (
                                            <RAGSourcePanel doc={doc} docIndex={docIndex} resultIndex={resultIndex} key={docIndex}></RAGSourcePanel>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </>
        </div>
    );
};

export default ResultDisplay;
