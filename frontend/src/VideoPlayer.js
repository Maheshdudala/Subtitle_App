import React, { useEffect } from 'react';

const VideoPlayer = ({ videoPath, subtitleTracks, timestamps, videoRef }) => {
  useEffect(() => {
    const videoElement = videoRef.current;

    const handleLoadedMetadata = () => {
      console.log('Video metadata loaded');
    };

    if (videoElement) {
      videoElement.addEventListener('loadedmetadata', handleLoadedMetadata);

      // Log subtitle tracks to verify they are being passed correctly
      console.log('Subtitle tracks:', subtitleTracks);

      return () => videoElement.removeEventListener('loadedmetadata', handleLoadedMetadata);
    }
  }, [videoPath, subtitleTracks, videoRef]);

  const handleTimestampClick = (timestamp) => {
    console.log('Timestamp clicked:', timestamp);

    const [start] = timestamp.split(' --> '); // Assuming the timestamp follows the SRT format
    if (!start) {
      console.error('Invalid timestamp:', timestamp);
      return;
    }

    // Split the time into hours, minutes, seconds, and milliseconds
    const [hours, minutes, seconds] = start.split(':');
    const [secs, millis = '0'] = seconds.split(',');

    // Convert time into seconds
    const timeInSeconds =
      parseInt(hours, 10) * 3600 +
      parseInt(minutes, 10) * 60 +
      parseInt(secs, 10) +
      parseInt(millis, 10) / 1000;

    console.log('Parsed time in seconds:', timeInSeconds);

    // Ensure videoRef is valid
    if (videoRef.current) {
      videoRef.current.currentTime = timeInSeconds;
      videoRef.current.play(); // Optionally play the video after seeking
      console.log('Video should jump to:', timeInSeconds);
    } else {
      console.error('Video reference is null');
    }
  };

  return (
    <div>
      <video ref={videoRef} width="800" controls preload='metadata'>
        <source src={videoPath} type="video/mp4" />
        {subtitleTracks &&
          subtitleTracks.length > 0 &&
          subtitleTracks.map((track, index) => (
            <track
              key={index}
              label={track.label}
              kind="subtitles"
              srcLang={track.lang}
              src={track.src}
              default={index === 0}
            />
          ))}
        Your browser does not support the video tag.
      </video>
      <div style={{ marginTop: '10px' }}>
        {timestamps &&
          timestamps.length > 0 &&
          timestamps.map((timestamp, index) => (
            <div key={index}>
              <button onClick={() => handleTimestampClick(timestamp)}>
                Jump to {timestamp}
              </button>
            </div>
          ))}
      </div>
    </div>
  );
};

export default VideoPlayer;
