import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const VideosListPage = () => {
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch the list of videos from the API
        fetch('/list-videos/')
            .then(response => response.json())
            .then(data => {
                if (data.videos) {
                    setVideos(data.videos);
                } else {
                    setError('No videos found.');
                }
                setLoading(false);
            })
            .catch(_err => {
                setError('Error fetching video list.');
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div style={{ padding: '20px' }}>
            <h1>Uploaded Videos</h1>
            {videos.length > 0 ? (
                <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {videos.map((videoUrl, index) => (
                        <li key={index} style={{ marginBottom: '10px' }}>
                            <Link to={`/video/${encodeURIComponent(videoUrl)}`} style={{ textDecoration: 'none', color: '#007bff' }}>
                                {videoUrl.substring(videoUrl.lastIndexOf('/VideosList') + 1)}
                            </Link>
                        </li>
                    ))}
                </ul>
            ) : (
                <div>No videos available.</div>
            )}
        </div>
    );
};

export default VideosListPage;
