import React, { useState, useEffect } from 'react';
import Markdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

import '../styles/RAGSourcePanel.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faThumbsUp } from '@fortawesome/free-solid-svg-icons';

const RAGSourcePanel = ({ doc, docIndex }) => {
    const baseUrl = `http://localhost:5001`;

    const [sourceMeta, setSourceMeta] = useState({ username: 'default', votes: 'Loading...', views: 'Loading...', profileImage: `${baseUrl}/static/profile_images_19988/default.jpg`, url: '' });
    const [cellContents, setCellContents] = useState([]);

    async function fetchData(url) {
        const response = await fetch(`${baseUrl}${url}`);
        if (!response.ok) {
            throw new Error(`Error fetching data from ${url}: ${response.statusText}`);
        }
        return response.json();
    }

    const fetchAdditionalInfo = async () => {
        const endpoints = [
            `/get_username?kernel_id=${doc.metadata.title}`,
            `/get_kernel_vote?kernel_id=${doc.metadata.title}`,
            `/get_kernel_view?kernel_id=${doc.metadata.title}`,
            `/get_kernel_url?kernel_id=${doc.metadata.title}`
        ];
        try {
            const [responseUsername, responseVotes, responseViews, responseURL] = await Promise.all(
                endpoints.map(endpoint => fetchData(endpoint))
            );
            const responseProfileImage = await fetchData(`/get_profile_image_path?username=${responseUsername}`)
            const result = {
                username: responseUsername,
                votes: responseVotes,
                views: responseViews,
                url: responseURL.url,
                score: 0.57,
                comment: 20,
                title: 'Moa | Feature Selection | Cp_dose | Cp_time',
                update:'4y ago',
                profileImage: `${baseUrl}/static/profile_images_19988/${responseProfileImage}`
            }
            setSourceMeta(result)
        } catch (error) {
            console.error('Error fetching additional info:', error);
        }
    };

    const fetchCellContents = async () => {
        try {
            const cellContents = await fetchData(`/get_cell_content?title=${doc.metadata.title}&cell_index=${doc.metadata.first_cell_index}`);
            setCellContents(cellContents)
        } catch (error) {
            console.error('Error fetching cell content:', error);
        }
    };

    useEffect(() => {
        fetchAdditionalInfo();
        fetchCellContents();
    }, [doc]);

    return <>
        <div className='source-document-container'>
            <a href={sourceMeta.url} target='_blank' className='source-document-panel'>
                <div className="source-document-header">
                    <img
                        src={sourceMeta.profileImage}
                        alt={`${sourceMeta.username}'s profile`}
                        className="profile-image"
                    />
                    <div className="source-document-info">
                        <p><strong>{sourceMeta.title}</strong></p>
                        <p className='source-secondary'>Author: {sourceMeta.username} · {sourceMeta.update}</p>
                        <p className='source-secondary'>Score: {sourceMeta.score} · {sourceMeta.comment} comments</p>
                    </div>
                    <ul className="source-document-status">
                        <li> <FontAwesomeIcon icon={faEye} /> {sourceMeta.views}</li>
                        <li> <FontAwesomeIcon icon={faThumbsUp} /> {sourceMeta.votes}</li>
                    </ul>
                </div>
                <div
                    className="source-document-content"
                >
                    {cellContents.map((cell, index) => (
                        <div key={index}>
                            {cell.cell_type === 'code' ?
                                <div className='code-cell'>
                                    <div className='code-cell-id'>In [{index + 1}]:</div>
                                    <div className='code-cell-content'>
                                        <Markdown
                                            children={`\`\`\`python 
${cell.source}
\`\`\``}
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
                                                            style={oneLight}
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
                                : <div className='markdown-cell'>
                                    <Markdown>{cell.source}</Markdown>
                                </div>
                            }
                        </div>
                    ))
                    }
                </div>
            </a>
        </div>

    </>
}

export default RAGSourcePanel;