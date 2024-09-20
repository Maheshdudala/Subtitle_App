import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import UploadVideo from './UploadVideo';
import VideoDetailPage from './VideoDetailPage';
import VideosListPage from './VideosListPage';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadVideo />} />
        <Route path="/VideosList" element={<VideosListPage />} />
        <Route path="/video/:videoUrl" element={<VideoDetailPage />} />
      </Routes>
    </Router>
  );
};

export default App;
