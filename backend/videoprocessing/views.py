import os
import re
import subprocess
import whisper
from django.shortcuts import get_object_or_404
from moviepy.editor import VideoFileClip
import pysrt
from deep_translator import GoogleTranslator
from tqdm import tqdm
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from rest_framework.views import APIView

from videoprocessing.models import Subtitle


class UploadVideoView(APIView):
    def post(self, request):
        # Check if the file is present in the request
        if 'video' not in request.FILES:
            return HttpResponseBadRequest("No video file provided")

        # Get the uploaded file
        uploaded_file = request.FILES['video']
        fs = FileSystemStorage()

        video_filename = os.path.splitext(uploaded_file.name)[0]

        # Check if the video already exists
        existing_video_path = os.path.join(fs.location, f'{video_filename}.mp4')
        print(f"Checking for existing video at: {existing_video_path}")
        if os.path.exists(existing_video_path):
            print("Video already exists")

            # Generate URLs for existing subtitles
            language_vtt_files = []
            for file in os.listdir(fs.location):
                if file.startswith(video_filename) and file.endswith('.vtt'):
                    # Create URL for each VTT file
                    language_vtt_files.append(fs.url(file))

            # Generate media URL for the existing video
            video_url = fs.url(f'{video_filename}.mp4')

            return JsonResponse({
                'message': 'Video already exists',
                'video': video_url,
                'subtitle_vtt_files': language_vtt_files
            })

        try:
            # Save the file and retrieve its path
            print("Video does not exist, uploading new video")
            video_path = fs.save(uploaded_file.name, uploaded_file)
            video_full_path = fs.path(video_path)

            # Define subtitle paths
            subtitle_path = os.path.splitext(video_full_path)[0] + ".srt"
            subtitle_path_vtt = os.path.splitext(video_full_path)[0] + ".vtt"

            # Try to extract subtitles with FFmpeg
            subtitles_found = self.extract_subtitles_with_ffmpeg(video_full_path, fs.location)

            if not subtitles_found:
                print("No subtitles were extracted, generating them with Whisper")

                # Extract audio from video and generate subtitles
                audio_path = self.extract_audio_from_video(video_full_path)
                self.generate_subtitles_with_whisper(audio_path, subtitle_path)

                # Translate the generated SRT into multiple languages
                self.translate_srt_file(subtitle_path, {
                    'Spanish': 'es',
                    'German': 'de',
                    'Korean': 'ko',
                    'Urdu': 'ur'
                })

                # Check which VTT files were created
                language_vtt_files = []
                video_name_a = os.path.splitext(os.path.basename(video_path))[0]
                for file in os.listdir(fs.location):
                    if file.startswith(video_name_a) and file.endswith('.vtt'):
                        language_code = file.split('_translated_')[-1].split('.')[0]
                        language_vtt_files.append(fs.url(file))

                # Generate media URLs
                subtitle_url = fs.url(os.path.basename(subtitle_path))
                video_url = fs.url(uploaded_file.name)

                return JsonResponse({
                    'message': 'Subtitles generated successfully',
                    'subtitle_file': subtitle_url,
                    'video': video_url,
                    'subtitles_generated': language_vtt_files  # Return generated VTT file URLs
                })

            else:
                print("Subtitles were found with FFmpeg")
                # Collect all files generated with the video base name
                generated_files = []
                video_name_b = os.path.splitext(os.path.basename(video_path))[0]
                for file in os.listdir(fs.location):
                    if file.startswith(video_name_b) and file.endswith('.vtt'):
                        generated_files.append(fs.url(file))

                # Generate media URL for the video
                video_url = fs.url(uploaded_file.name)

                return JsonResponse({
                    'message': 'Subtitles were found and extracted successfully with FFmpeg',
                    'video': video_url,
                    'subtitles_extracted': generated_files  # Return existing subtitle file URLs
                })

        except Exception as e:
            print(f"Error during subtitle extraction: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    def extract_subtitles_with_ffmpeg(self, video_path, output_subtitle_dir):

        video_name = os.path.splitext(os.path.basename(video_path))[0]
        # Run FFmpeg to get the list of streams
        command = ['ffmpeg', '-i', video_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Extract stream details from the FFmpeg output
        streams = re.findall(r'Stream #0:(\d+)(?:\((.*?)\))?: (.*?)\n', result.stderr)

        if not streams:
            print("No streams detected.")
            return False

        # Create output directory if it does not exist
        if not os.path.exists(output_subtitle_dir):
            os.makedirs(output_subtitle_dir)

        # Initialize a variable to track the correct subtitle stream index
        subtitle_index = 0
        extracted_any_subtitle = False

        for index, lang, stream_type in streams:
            if "Subtitle" in stream_type:
                map_string = f"0:s:{subtitle_index}"
                print(f"Attempting to extract: {map_string}")

                lang_code = lang if lang else f"sub{subtitle_index}"
                print(f"Attempting to extract: 0:s:{subtitle_index} (Language: {lang_code})")

                # Extract subtitle stream
                output_subtitle_path = os.path.join(output_subtitle_dir, f'{video_name}_subtitles_{lang_code}.srt')
                print("output_subtitle_path:",output_subtitle_path)
                command = [
                    'ffmpeg',
                    '-i', video_path,
                    '-map', f'0:s:{subtitle_index}',
                    output_subtitle_path
                ]
                try:
                    print(f"Extracting subtitle stream {subtitle_index}...")
                    result = subprocess.run(command, capture_output=True, text=True)

                    # Check if the subtitle file was created and is non-empty
                    if os.path.exists(output_subtitle_path) and os.path.getsize(output_subtitle_path) > 0:
                        print(f"Subtitle stream {subtitle_index} extracted successfully.")
                        extracted_any_subtitle = True
                        # Convert the generated .srt file to .vtt
                        output_vtt_path = os.path.join(output_subtitle_dir,f'{video_name}_subtitles_{lang_code}.vtt')
                        print("output_vtt_path:",output_vtt_path)
                        self.convert_srt_to_vtt(output_subtitle_path, output_vtt_path)
                        self.save_subtitle_to_db(video_name, lang_code, 'extracted', output_subtitle_path,output_subtitle_path, 'srt')
                        self.save_subtitle_to_db(video_name, lang_code, 'extracted', output_vtt_path,output_vtt_path, 'vtt')
                    else:
                        print(f"No subtitles found for stream {subtitle_index} or file is empty.")

                except subprocess.CalledProcessError as e:
                    print(f"Error extracting subtitles for stream {subtitle_index}: {e}")
                    print("Error Output:", e.stderr)
                except Exception as e:
                    print(f"Unexpected error for stream {subtitle_index}: {e}")

                # Increment the subtitle index for the next subtitle stream
                subtitle_index += 1

        print("Extraction complete. Any subtitles extracted:", extracted_any_subtitle)
        return extracted_any_subtitle

    def generate_subtitles_with_whisper(self, audio_path, output_subtitle_path):
        print("Generating subtitles using Whisper...")
        model = whisper.load_model("base")

        # Transcribe the audio to generate subtitles
        result = model.transcribe(audio_path)

        # Get segments and timestamps
        segments = result["segments"]
        subtitles = []

        for segment in segments:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            # Convert time from seconds to SRT format (hours:minutes:seconds,milliseconds)
            start_time_str = "{:02}:{:02}:{:02},{:03}".format(int(start_time // 3600), int((start_time % 3600) // 60),
                                                              int(start_time % 60), int(start_time * 1000 % 1000))
            end_time_str = "{:02}:{:02}:{:02},{:03}".format(int(end_time // 3600), int((end_time % 3600) // 60),
                                                            int(end_time % 60), int(end_time * 1000 % 1000))

            subtitles.append({
                "index": len(subtitles) + 1,
                "start": start_time_str,
                "end": end_time_str,
                "text": text
            })

        self.save_subtitles_to_srt(subtitles, output_subtitle_path)

        # Extract directory and base filename from the SRT path
        subtitle_dir = os.path.dirname(output_subtitle_path)
        base_filename = os.path.splitext(os.path.basename(output_subtitle_path))[0]

        # Create VTT file path
        output_vtt_path = os.path.join(subtitle_dir, f'{base_filename}_translated_def.vtt')

        # Convert SRT to VTT
        self.convert_srt_to_vtt(output_subtitle_path, output_vtt_path)

        print("Subtitles generated successfully with Whisper.")

    def save_subtitle_to_db(self, video_file, language_code, subtitle_type, file_path,subtitle_name_ext, file_format):
        with open(file_path, 'rb') as f:
            file_content = f.read()
        Subtitle.objects.create(
            video_file_name=video_file,
            language_code=language_code,
            subtitle_type=subtitle_type,
            subtitle_file=file_content,
            subtitle_name_ext = subtitle_name_ext,
            file_format=file_format
        )


    def save_subtitles_to_srt(self, subtitles, output_path):
        with open(output_path, 'w', encoding='utf-8') as file:
            for sub in subtitles:
                file.write(f"{sub['index']}\n")
                file.write(f"{sub['start']} --> {sub['end']}\n")
                file.write(f"{sub['text']}\n")
                file.write("\n")

    def extract_audio_from_video(self, video_path):
        clip = VideoFileClip(video_path)
        audio = clip.audio
        audio_path = video_path.replace('.mp4', '.wav')
        audio.write_audiofile(audio_path)
        return audio_path

    def translate_text(self, text, target_language):
        translator = GoogleTranslator(target=target_language)
        return translator.translate(text)

    def read_srt_file(self, file_path):
        subs = pysrt.open(file_path)
        text_to_translate = "\n".join([sub.text for sub in subs])
        return subs, text_to_translate

    def write_srt_file(self, subs, translated_text, output_srt_path):
        translated_lines = translated_text.split("\n")
        for i, sub in enumerate(subs):
            sub.text = translated_lines[i]
        subs.save(output_srt_path, encoding='utf-8')

    def translate_srt_file(self, input_srt_path, target_languages):
        # Extract the directory and base name of the input file
        subtitle_dir = os.path.dirname(input_srt_path)
        base_filename = os.path.splitext(os.path.basename(input_srt_path))[0]

        # Read the original .srt file
        subs, text_to_translate = self.read_srt_file(input_srt_path)

        for language, lang_code in target_languages.items():
            print(f"Translating to {language}...")

            translated_text = ""
            for line in tqdm(text_to_translate.split("\n"), desc=f"Translating to {language}"):
                translated_text += self.translate_text(line, lang_code) + "\n"

            # Save the translated .srt file in the media directory
            output_srt_path = os.path.join(subtitle_dir, f'{base_filename}_translated_{lang_code}.srt')
            output_vtt_path = os.path.join(subtitle_dir, f'{base_filename}_translated_{lang_code}.vtt')

            # Write the translated text into a new .srt file
            self.write_srt_file(subs, translated_text.strip(), output_srt_path)

            # Convert the translated .srt to .vtt
            self.convert_srt_to_vtt(output_srt_path, output_vtt_path)

            print(f"Translation for {language} completed: {output_srt_path}, {output_vtt_path}")

    def convert_srt_to_vtt(self, srt_path, vtt_path):
        """
        Converts SRT subtitle file to VTT format.
        """
        with open(srt_path, 'r', encoding='utf-8') as srt_f, open(vtt_path, 'w', encoding='utf-8') as vtt_f:
            # Write WEBVTT header required for .vtt files
            vtt_f.write("WEBVTT\n\n")
            vtt_f.write(srt_f.read().replace(',', '.'))  # Replace commas with dots for VTT format


# from django.http import JsonResponse
# from django.views import View
# import os
# import re
# from django.conf import settings

# class UploadVideoView(APIView):
#     def post(self, request):
class SearchSubtitlesView(APIView):
    def post(self, request):
        # import pdb
        # pdb.set_trace()
        # Extract data from the request
        video_id = request.data.get('video_id')
        # print(video_id)
        phrase = request.data.get('phrase', '').strip()
        language = request.data.get('language')  # Get selected language
        subtitle_file = request.data.get('subtitle_file', '').strip()
        # print("subtitle_file:",subtitle_file)

        if not video_id or not phrase:
            return JsonResponse({'error': 'Missing video_id or phrase'}, status=400)

        if subtitle_file.startswith('/media/'):
            subtitle_file = subtitle_file[len('/media/'):]

        subtitle_path = os.path.join(settings.MEDIA_ROOT, f'{subtitle_file}')


        if not os.path.exists(subtitle_path):
            return JsonResponse({'error': 'Subtitle file not found'}, status=404)

        with open(subtitle_path, 'r', encoding='utf-8') as file:
            srt_content = file.read()

        timestamps = self.extract_timestamp(srt_content, phrase)

        if not timestamps:
            print('Phrase not found in subtitles')
            return JsonResponse({'message': 'Phrase not found in subtitles'}, status=200)

        response_data = {'timestamps': timestamps}
        return JsonResponse(response_data)

    def extract_timestamp(self, srt_content, phrase):
        timestamps = []
        entries = re.split(r'\n\n', srt_content.strip())

        for entry in entries:
            lines = entry.split('\n')
            if len(lines) >= 3:
                timestamp_line = lines[1]
                subtitle_text = '\n'.join(lines[2:])
                if phrase.lower() in subtitle_text.lower():
                    timestamps.append(timestamp_line)

        return timestamps



class ListVideosView(APIView):
    def get(self, request):
        # Get the directory where media files are stored
        media_root = settings.MEDIA_ROOT

        try:
            # List all video files in the media root directory
            video_files = [f for f in os.listdir(media_root)
                           if os.path.isfile(os.path.join(media_root, f))
                           and f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

            # Sort video files by their last modification time (latest first)
            video_files.sort(key=lambda f: os.path.getmtime(os.path.join(media_root, f)), reverse=True)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        # Return the list of video files with their URLs
        video_urls = [settings.MEDIA_URL + video_file for video_file in video_files]

        return JsonResponse({'videos': video_urls})

class VideoDetailView(APIView):
    def post(self, request):
        video_id = request.data.get('video_id')
        print("video_id:",video_id)
        if not video_id:
            return JsonResponse({'error': 'Missing video_id'}, status=400)

        # if video_id.startswith('/media/'):
        #     video_id = video_id[len('/media/'):]

        video_path = os.path.join(settings.MEDIA_ROOT, video_id)+".mp4"
        print("video_path:",video_path)

        # Check if the video file exists
        if not os.path.exists(video_path):
            return JsonResponse({'error': 'Video file not found'}, status=404)

        # Generate URLs for subtitles
        language_vtt_files = []
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        for file in os.listdir(settings.MEDIA_ROOT):
            if file.startswith(video_name) and file.endswith('.vtt'):
                # Create URL for each VTT file
                language_vtt_files.append(settings.MEDIA_URL + file)

        # Generate media URL for the video
        video_url = settings.MEDIA_URL + os.path.basename(video_path)

        return JsonResponse({
            'message': 'Video details retrieved successfully',
            'video': video_url,
            'subtitle_vtt_files': language_vtt_files  # Return generated VTT file URLs
        })


class GetSubtitleView(APIView):
    def get(self, request, subtitle_id):
        # Retrieve the subtitle object
        subtitle = get_object_or_404(Subtitle, id=subtitle_id)

        # Convert the memoryview (binary content) to bytes
        binary_content = bytes(subtitle.subtitle_file)

        # Prepare the response with appropriate content type and headers
        response = HttpResponse(binary_content, content_type=f"text/{subtitle.file_format}")

        # Set the filename for the download using the subtitle file name and extension
        subtitle_name_ext = f"{subtitle.video_file_name}_subtitles_{subtitle.language_code}.{subtitle.file_format}"
        response['Content-Disposition'] = f'attachment; filename="{subtitle_name_ext}"'

        return response