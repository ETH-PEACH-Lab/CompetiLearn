import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';

import '../styles/RAGSourcePanel.css';

const RAGSourcePanel = ({ doc, docIndex }) => {
    const baseUrl = `http://localhost:5001`;

    const [sourceMeta, setSourceMeta] = useState({ username: 'default', votes: 'Loading...', views: 'Loading...', profileImage: `${baseUrl}/static/profile_images_10737/default.jpg`, url: '' });
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
                profileImage: `${baseUrl}/static/profile_images_10737/${responseProfileImage}`
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
        <div>
            <a href={sourceMeta.url} target='_blank' className='source-document-panel'>
                <div className="source-document-header">
                    <img
                        src={sourceMeta.profileImage}
                        alt={`${sourceMeta.username}'s profile`}
                        className="profile-image"
                    />
                    <div className="source-document-info">
                        <p><strong>Source {docIndex + 1}</strong></p>
                        <p>Author: {sourceMeta.username}</p>
                        <p>Views: {sourceMeta.views}</p>
                        <p>Votes: {sourceMeta.votes}</p>
                    </div>
                </div>
            </a>
        </div>
        <div
            className="source-document-content"
        >
            {cellContents.map((cell, index) => (
                <div key={index}>
                    {cell.cell_type === 'code' ?
                        <div className='code-cell'>
                            <p>{cell.source}</p>
                            <Editor 
                                defaultValue={cell.source}
                                defaultLanguage='python'
                                options={{
                                    readOnly: true,
                                    minimap: { enabled: false }
                                }}
                                height="20vh"
                            />
                        </div>
                        : <div className='markdown-cell'>
                            <ReactMarkdown>{cell.source}</ReactMarkdown>
                        </div>
                    }
                </div>
            ))
            }
        </div>
    </>
}

export default RAGSourcePanel;