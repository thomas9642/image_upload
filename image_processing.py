from google.cloud import storage
import os
import google.generativeai as genai
from datetime import datetime
from store_db import insert_image
import logging

gemini_api_key = os.getenv("GEMINI_API_KEY")
bucket = os.getenv("BUCKET_NAME")


cnad_image_uploads_bucket = storage.Client().bucket(bucket)
genai.configure(api_key=gemini_api_key)
text_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def image_processing(image_file):
    logging.info(f"Starting image processing for file: {image_file.filename}")

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    bucket_path = f"{timestamp}/{image_file.filename}"
    logging.info(f"Bucket path for upload: {bucket_path}")

    blob = cnad_image_uploads_bucket.blob(bucket_path)

    try:
        with open(image_file.filename, 'rb') as file:
            logging.info(f"Uploading image file to bucket: {bucket_path}")
            blob.upload_from_file(file)
            logging.info(f"Image file uploaded successfully: {blob.public_url}")
    except Exception as e:
        logging.error(f"Error uploading image file: {e}")
        return

    try:
        genai_img = genai.upload_file(image_file.filename)
        logging.info("Image processed by GenAI.")

        response = text_model.generate_content([genai_img, "describe the image"])
        logging.info("Content generated successfully.")
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return

    insert_image(blob.public_url, response.text)

    base_filename = os.path.splitext(image_file.filename)[0]
    txt_file_name = f"{base_filename}.txt"

    try:
        with open(txt_file_name, 'w') as txt_file:
            txt_file.write(response.text)
            logging.info(f"Text content written to file: {txt_file_name}")

        with open(txt_file_name, 'rb') as txt_file:
            blob = cnad_image_uploads_bucket.blob(f"{timestamp}/{txt_file_name}")
            logging.info(f"Uploading text file to bucket: {txt_file_name}")
            blob.upload_from_file(txt_file)
            logging.info(f"Text file uploaded successfully: {blob.public_url}")
    except Exception as e:
        logging.error(f"Error during text file processing: {e}")
    finally:
        if os.path.exists(image_file.filename):
            os.remove(image_file.filename)
            logging.info(f"Removed local image file: {image_file.filename}")

        if os.path.exists(txt_file_name):
            os.remove(txt_file_name)
            logging.info(f"Removed local text file: {txt_file_name}")

    logging.info("Image processing completed.")


