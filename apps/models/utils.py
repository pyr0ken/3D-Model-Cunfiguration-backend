import os
from image_to_3d.run import convert_to_3d
from django.core.files.base import ContentFile
from django.conf import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

def ai_note_description(title):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(contents=title)
    return response.text

def convert_2d_to_3d(image):
    # Set up CUDA memory settings
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

    # Assuming convert_to_3d returns the output file path
    output_file_path = convert_to_3d(image)
    # /home/username/3d-model-configuration/backend/media/images3d/name.glb

    # Read the local file
    with open(output_file_path, 'rb') as output_file:
        file_data = output_file.read()

    # Create a Django ContentFile object
    django_file = ContentFile(file_data, name=output_file_path.split('/')[-1])

    return django_file