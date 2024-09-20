import React, { useState, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for redirection

const UploadVideo = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState('');
  const [videoPath, setVideoPath] = useState('');
  const [subtitleTracks, setSubtitleTracks] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const videoRef = useRef(null); // Define videoRef to reference the video element
  const navigate = useNavigate(); // Initialize navigate for redirection

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a video file.');
      return;
    }

    const formData = new FormData();
    formData.append('video', selectedFile);

    setUploading(true); // Set uploading to true
    setProgress(0); // Reset progress

    try {
      const response = await axios.post('/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(percent); // Update progress
          }
        }
      });

      setMessage(response.data.message);
      console.log('Full response data:', response.data);

      if (response.data.video) {
        const videoPath = response.data.video.replace(/^\/?media\//, '/media/');
        setVideoPath(videoPath);

        // If subtitles exist, set the subtitle tracks
        if (response.data.subtitle_vtt_files) {
          const subtitleVttFiles = response.data.subtitle_vtt_files.map((filePath) => {
            const lang = filePath.split('_translated_')[1]?.replace('.vtt', '');
            return {
              label: lang ? lang.toUpperCase() : 'Default',
              lang: lang || 'default',
              src: filePath.replace(/^\/?media\//, '/media/')
            };
          });
          setSubtitleTracks(subtitleVttFiles);
        }

        // Check if the video already exists and display the message accordingly
        if (response.data.message === 'Video already exists') {
          setMessage('Video and Subtitles already exists.');
        }
        
        // Handle subtitles processing or generation messages
        if (response.data.subtitles_extracted) {
          setMessage('Subtitles processed successfully with FFmpeg.');
        } else if (response.data.subtitles_generated) {
          setMessage('Subtitles generated successfully with Whisper.');
        } else if (!response.data.message.includes('already exists')) {
          setMessage('No subtitles were processed.');
        }
      }

      // Wait for 3 seconds before redirecting (if needed)
      setTimeout(() => {
        navigate('/VideosList');
      }, 5000);

    } catch (error) {
      setMessage('Video upload failed.');
      console.error(error);
    } finally {
      setUploading(false); // Reset uploading state
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>Upload Video</h2>
      <input type="file" onChange={handleFileChange} accept="video/mp4" />
      <button onClick={handleUpload} disabled={uploading}>Upload</button>
      {uploading && <p style={{ color: 'green' }}>Uploading... {progress}%</p>}
      {message && <p>{message}</p>}
    </div>
  );
};

export default UploadVideo;
