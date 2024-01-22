import speech_recognition as sr
import os
import glob
from pydub import AudioSegment
from tqdm import tqdm
from pydub.silence import split_on_silence
from moviepy.editor import *

# Directory paths
input_directory = './data/videos'
output_directory = './data/raw'

# Function to extract audio from MP4 and save as MP3
def extract_audio(input_file, output_file):
    video = VideoFileClip(input_file)
    audio = video.audio
    audio.write_audiofile(output_file)
    audio.close()
    video.close()

# Extract MP3 from MP4 files in the input directory
def extract_mp3_from_videos(input_directory, output_directory):
    import os
    
    # Ensure output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Extract MP3 from each MP4 file in the input directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".mp4"):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_name = os.path.splitext(file_name)[0] + ".mp3"
            output_file_path = os.path.join(output_directory, output_file_name)
            extract_audio(input_file_path, output_file_path)
            print(f"Extracted audio from {input_file_path} and saved as {output_file_path}")

# Call the function to extract MP3 from videos
extract_mp3_from_videos(input_directory, output_directory)



# Path to MP3 files
path_mp3 = './data/raw/*.mp3'

# Path to store text files
path_text = './data/processed/'

# Create the output directory if it doesn't exist
os.makedirs(path_text, exist_ok=True)

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Get a list of MP3 files
filelist = glob.glob(path_mp3)

for file in tqdm(filelist):
    # Load each MP3 file
    audio_mp3 = AudioSegment.from_mp3(file)

    # Split audio on silence
    chunks = split_on_silence(audio_mp3, min_silence_len=500, silence_thresh=audio_mp3.dBFS - 14, keep_silence=500)

    # Initialize full_text for the current audio file
    full_text = ""

    # Process every chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # Save the audio chunk as a temporary WAV file
        temp_wav_file = f"temp_chunk{i}.wav"
        audio_chunk.export(temp_wav_file, format="wav")

        # Recognize speech in the chunk
        with sr.AudioFile(temp_wav_file) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)
            # Inside the loop where speech recognition is performed
            # Inside the loop where speech recognition is performed
            try:
                text = recognizer.recognize_google(audio, language='en-US')
                text = f"{text.capitalize()}. "
                full_text += text
            except sr.UnknownValueError:
                print("Audio not understandable in chunk", i)
            except sr.RequestError as e:
                print(f"No response from Google API: {e}")



        # Delete the temporary WAV file
        os.remove(temp_wav_file)

    # Save the full text to a text file
    filename = os.path.splitext(os.path.basename(file))[0] + ".txt"
    with open(os.path.join(path_text, filename), 'w') as text_file:
        text_file.write(full_text)
