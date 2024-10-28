import os
from django.conf import settings
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from TTS.api import TTS
from pydub import AudioSegment

# Load the TTS model once when the server starts
tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)


class GenerateTTSView(APIView):

    def post(self, request, *args, **kwargs):
        # Extract parameters from the request
        text = request.data.get("text")
        language = request.data.get("language")
        print("language" , language)
        reference_speaker_file = request.FILES.get("reference_speaker")

        # Validate input
        if not text or not reference_speaker_file:
            return Response({"error": "Text and reference_speaker file are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Ensure MEDIA_ROOT directory exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        # Define file paths
        temp_file_path = os.path.join(settings.MEDIA_ROOT, "temp_reference_speaker.wav")
        output_file_path = os.path.join(settings.MEDIA_ROOT, "output1.wav")

        try:
            # Handle .mp3 files by converting them to .wav
            if reference_speaker_file.name.endswith('.mp3'):
                temp_mp3_path = os.path.join(settings.MEDIA_ROOT, "temp_reference_speaker.mp3")
                with open(temp_mp3_path, "wb") as temp_file:
                    for chunk in reference_speaker_file.chunks():
                        temp_file.write(chunk)
                # Convert mp3 to wav
                audio = AudioSegment.from_mp3(temp_mp3_path)
                audio.export(temp_file_path, format="wav")
                os.remove(temp_mp3_path)
            else:
                # Save .wav file directly
                with open(temp_file_path, "wb") as temp_file:
                    for chunk in reference_speaker_file.chunks():
                        temp_file.write(chunk)

            # Generate TTS audio file
            tts_model.tts_to_file(
                text=text,
                speaker_wav=temp_file_path,
                language=language,
                file_path=output_file_path
            )

            # Construct relative URL for the output file
            relative_output_path = "/media/output1.wav"  # Modify this to your desired path
            return Response({"output_file_path": relative_output_path}, status=status.HTTP_200_OK)

        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
