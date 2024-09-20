import React, { useState } from 'react';
import axios from 'axios';

const SearchBar = ({ videoPath, onTimestampsFound }) => {
  const [phrase, setPhrase] = useState('');
  const [message, setMessage] = useState('');

  const handleSearch = async () => {
    if (!phrase) {
      setMessage('Please enter a phrase.');
      return;
    }

    try {
      const response = await axios.get('/search/', {
        params: {
          video_id: videoPath.split('/').pop().replace('.mp4', ''), // Extract video ID from path
          phrase
        }
      });
      onTimestampsFound(response.data.timestamps);
    } catch (error) {
      setMessage('Search failed. Please try again.');
      console.error(error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <input
        type="text"
        value={phrase}
        onChange={(e) => setPhrase(e.target.value)}
        placeholder="Enter phrase to search"
      />
      <button onClick={handleSearch}>Search</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default SearchBar;
