import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import VideoPlayer from './VideoPlayer';

const VideoDetailPage = () => {
  const { videoUrl } = useParams(); // Get route parameter for video URL
  const [subtitleTracks, setSubtitleTracks] = useState([]); // State for subtitle tracks
  const [searchPhrase, setSearchPhrase] = useState(''); // State for search phrase
  const [searchResults, setSearchResults] = useState([]); // State for search results
  const [selectedLanguage, setSelectedLanguage] = useState(''); // State for selected language
  const [defaultSubtitleTrack, setDefaultSubtitleTrack] = useState(null); // State for default subtitle track
  const [message, setMessage] = useState(''); // State for error/success messages
  const videoRef = useRef(null); // Ref for video player

  useEffect(() => {
    // Fetch subtitle tracks from backend
    const fetchSubtitles = async () => {
      try {
        const videoId = videoUrl.split('/').pop().split('.')[0];

        const response = await axios.post('/video-detail/', { video_id: videoId }, {
          headers: { 'Content-Type': 'application/json' },
        });

        let subtitleTracks = [];
        if (Array.isArray(response.data.subtitle_vtt_files)) {
          subtitleTracks = response.data.subtitle_vtt_files.map((filePath) => {
            let lang = 'unknown';

            if (filePath.includes('_subtitles_')) {
              lang = filePath.split('_')[2].replace('.vtt', '');
            } else if (filePath.includes('_translated_')) {
              lang = filePath.split('_translated_')[1].replace('.vtt', '');
            }

            return {
              label: lang === 'def' ? 'Default' : lang.toUpperCase(),
              lang: lang,
              src: filePath.replace(/^\/?media\//, '/media/'),
            };
          }).filter(track => track !== null); // Filter out null tracks
        }

        // Sort tracks to place 'def' (default) first
        subtitleTracks.sort((a, b) => (a.lang === 'def' ? -1 : b.lang === 'def' ? 1 : a.lang.localeCompare(b.lang)));

        setSubtitleTracks(subtitleTracks);
        setDefaultSubtitleTrack(subtitleTracks.find(track => track.lang === 'def'));
      } catch (error) {
        setMessage('Error fetching subtitles.');
        console.error('Error fetching subtitles:', error);
      }
    };

    fetchSubtitles();
  }, [videoUrl]);

  const handleSearch = async () => {
    if (!videoUrl || !searchPhrase.trim() || !selectedLanguage) {
      setMessage('Please enter a search phrase and select a language.');
      return;
    }
  
    const selectedTrack = subtitleTracks.find((track) => track.lang === selectedLanguage);
  
    if (!selectedTrack) {
      setMessage('Selected language subtitles not found.');
      return;
    }
  
    try {
      // Extract video ID from videoUrl
      const videoId = videoUrl.split('/').pop().split('.')[0];
  
      // Search for the phrase in subtitles
      const response = await axios.post('http://localhost:8000/search_subtitles/', {
        video_id: videoId,
        phrase: searchPhrase,
        subtitle_file: selectedTrack.src,
      }, {
        headers: { 'Content-Type': 'application/json' },
      });
      console.log(response.data)
      if (response.data.timestamps) {
        // Remove duplicates from search results
        const uniqueTimestamps = [...new Set(response.data.timestamps)];
        setSearchResults(uniqueTimestamps);
        setMessage('');
      } else if(response.data.message === 'Phrase not found in subtitles'){
        // setSearchResults([]);
        setMessage(response.data.message || 'Phrase not found in subtitles.');
      }
    } catch (error) {
      setSearchResults([]);
      // setMessage('Search failed.');
      console.error('Search failed:', error);
    }
  };
  

  const handleTimestampClick = (timestamp) => {
    const [start] = timestamp.split(' --> ');
    const timeParts = start.split(':');
  
    if (timeParts.length !== 3) {
      console.error('Invalid timestamp format:', timestamp);
      return;
    }
  
    const [hours, minutes, seconds] = timeParts;
    const [secs, millis] = seconds.split(',');
  
    // Parse all the parts into numbers
    const timeInSeconds =
      parseInt(hours) * 3600 +
      parseInt(minutes) * 60 +
      parseInt(secs) +
      (millis ? parseInt(millis) / 1000 : 0);
  
    // Check if timeInSeconds is a valid number
    if (!isNaN(timeInSeconds) && videoRef.current) {
      videoRef.current.currentTime = timeInSeconds;
      videoRef.current.play(); // Optionally play the video
    } else {
      console.error('Failed to set video time. Invalid time or video reference.');
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>Video Player</h2>
      <div style={{ marginTop: '20px' }}>
        <VideoPlayer
          videoPath={videoUrl}
          subtitleTracks={subtitleTracks}
          defaultSubtitleTrack={defaultSubtitleTrack}
          videoRef={videoRef}
          preload='auto'
        />
      </div>

      <div style={{ marginTop: '20px' }}>
        <h3>Search Subtitles</h3>
        <input
          type="text"
          value={searchPhrase}
          onChange={(e) => setSearchPhrase(e.target.value)}
          placeholder="Enter phrase to search"
        />
        <select onChange={(e) => setSelectedLanguage(e.target.value)} value={selectedLanguage}>
          <option value="">Select language</option>
          {subtitleTracks.map((track) => (
            <option key={track.lang} value={track.lang}>
              {track.label}
            </option>
          ))}
        </select>
        <button onClick={handleSearch}>Search</button>

        {message && <p>{message}</p>}
      </div>

      <div style={{ marginTop: '20px' }}>
        {searchResults.length > 0 && (
          <>
            <h3>Search Results</h3>
            <ul>
              {searchResults.map((timestamp, index) => (
                <li key={index}>
                  <button onClick={() => handleTimestampClick(timestamp)}>{timestamp}</button>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
};

export default VideoDetailPage;
