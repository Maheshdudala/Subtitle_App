# Video Subtitle Extraction and Generation App

This project is a web application for video upload and subtitle management. It automatically extracts existing subtitles from videos using FFmpeg or generates new subtitles with Whisper AI if none are found. Subtitles are translated into multiple languages, and users can search within subtitles for specific phrases.

## Features

* **Video Upload:** Upload videos with real-time progress tracking.
* **Subtitle Extraction:** Extracts existing subtitle streams with FFmpeg.
* **Subtitle Generation:** Generates subtitles using Whisper if none exist.
* **Multi-language Translation:** Translates subtitles into multiple languages.
* **Subtitle Formats:** Supports both SRT and VTT formats.
* **Searchable Subtitles:** Search within subtitles and jump to the timestamp.
* **Dynamic Subtitle Selection:** Automatically selects the default subtitle language with an option to switch.
* **Database Storage:** Subtitles are stored in PostgreSQL for easy access and management.
* **Progressive Enhancements:** Handles already existing videos

## Tech Stack

* **Backend:** Django (Django Rest Framework)
* **Frontend:** React.js (For video playback)
* **Subtitle Processing:** FFmpeg and Whisper AI
* **Database:** PostgreSQL
* **Containerization:** Docker

## Installation

### 1. Docker Setup

**Step 1:** Pull the latest PostgreSQL Docker image and set up the database
Run the following command to pull the latest PostgreSQL image:

`docker pull postgres:latest`

Step 2: Create necessary roles and permissions
Create a PostgreSQL container and set up roles and permissions:

`docker run --name postgres-container -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -d postgres`

Access the running container and create any additional roles or permissions:
docker exec -it postgres-container psql -U myuser
### Inside psql prompt

`CREATE DATABASE subtitle_app;`

`CREATE ROLE appuser WITH LOGIN PASSWORD 'apppassword';`

`GRANT ALL PRIVILEGES ON DATABASE subtitle_app TO appuser;`

**Please Update docker-compose.yml file with Above username and password**

### Step 3: Build the backend container

Run the following command to build the Docker image for the Django app:

go to subtitle_app and execute below commands:

`docker-compose up --build`


### Step 4:Check for conatiners running

`docker ps`

**Check backend and frontend logs for any errors**

`docker logs <container id >`

## 2]Cloning the Repository and Setting Up the Environment
Step 1: Clone the Git repository

`git clone https://github.com/Maheshdudala/Subtitle_App.git`

`cd Subtitle_App/backend/`

Step 2: Create a virtual environment

`python3 -m venv venv`

`venv\Scripts\activate`

`pip install -r requirements.txt`

`python manage.py migrate`

`python manage.py runserver`



2. Frontend Validation:
go to Frontend folder and run:

`npm start`

Once the server is running, you can access the frontend at:

`http://localhost:3000`

Home page we should able to see Video upload page

Here’s an explanation of the two cases for your Video Subtitle Extraction and Generation App:

### Case 1: Video Subtitle Extraction (with FFmpeg)

When a video is uploaded, the system first checks for existing subtitles within the video file. This is done using FFmpeg, which scans the video to see if it contains embedded subtitle streams (like .srt, .vtt formats).

**Steps:**
1. **Upload Video:** The user uploads a video file through the interface.
2. **Subtitle Extraction:** FFmpeg processes the uploaded video, checking for embedded subtitle streams.
3. **Subtitles Found:** If subtitles are found, they are extracted and saved in both .srt and .vtt formats.
4. **Language Selection:** The extracted subtitles are made available for selection on the video player page. The user can select from the available subtitle languages when they play the video.
5. **Automatic Selection:** A default subtitle language is selected (if specified, such as English), but users can switch to any available language.
6. **Result:** The user can view the video with subtitles in the extracted languages.
### Case 2: Subtitle Generation with Whisper AI and Translation

If no subtitles are found in the video during Case 1, Whisper AI is used to transcribe the audio and generate new subtitles. Whisper provides accurate speech-to-text capabilities, generating subtitles in the default language (usually the video’s spoken language). These subtitles can then be translated into multiple languages for a global audience.

Steps:
1. **Upload Video:** The user uploads a video file through the interface.
2. **Subtitle Check:** FFmpeg checks for subtitles. If none are found, Whisper AI is triggered to transcribe the video.
3. **Subtitle Generation:** Whisper generates subtitles in the original language of the video (e.g., English).
4. **Subtitle Translation:** The generated subtitles are then translated into multiple languages, such as Spanish, German, French, Korean, Urdu, etc.
5. **Multiple Formats:** Subtitles are saved in both .srt and .vtt formats for each translated language.
6. **Language Selection:** On the video player page, the user is presented with options to select subtitles in various languages. The user can choose to watch the video with subtitles in any of the translated languages.
7. **Automatic Selection:** A default subtitle language is pre-selected (e.g., English), but users can switch between the available translations.
8. **Result:** The user can watch the video with Whisper-generated subtitles, choosing from multiple languages for their preferred viewing experience.

Below the API End points links:
Backend:

http://localhost:8000/upload/

http://localhost:8000/upload/

http://localhost:8000/upload/

http://localhost:8000/upload/

frontend:

http://localhost:3000/

http://localhost:3000/VideosList








