import openai
import json
import logging
import requests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

class GPTMetadata:
    def __init__(self, api_key_path):
        api_key = json.load(open(api_key_path))["key"]
        openai.api_key = api_key
        logging.info("API key successfully loaded")

    def generate_metadata_gpt(self, post_and_comments):
        logging.info("Generating metadata using GPT API")

        # Prepare the prompt
        prompt = (
            "As an AI language model, generate metadata for a YouTube video created from the following Reddit post and comments. "
            "The metadata should include a Title, Description, Tags, and Category optimized for search engine optimization (SEO).\n\n"
        )

        for key, value in post_and_comments.items():
            prompt += f"{key}: {value}\n"

        prompt += (
            "\nPlease provide the metadata in the following format:\n"
            "Title: {title}\n"
            "Description: {description}\n"
            "Tags: {tag1}, {tag2}, {tag3}\n"
            "Category: {category}\n"
            "---\n"
        )

        # Call the GPT API
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=["---"],
            temperature=0.5,
        )

        logging.info("GPT API response received")

        # Extract metadata from response
        metadata_text = response.choices[0].text.strip()

        # Parse the metadata
        metadata_lines = metadata_text.split("\n")
        metadata = {}

        for line in metadata_lines:
            key, value = line.split(": ", 1)
            if key == "Tags":
                metadata[key] = [tag.strip() for tag in value.split(",")]
            else:
                metadata[key] = value

        logging.info("Metadata successfully generated and parsed")
        return metadata
    
    def generate_thumbnail_dalle(self, description, output_filename = "thumbnail.png"):
        logging.info("Generating thumbnail using DALL-E API")

        # Prepare the prompt
        prompt = f"Create a YouTube thumbnail in a Steve Ditko cover art style with high resolution, don't include text. Use this description for reference - description: {description}"

        # Call the DALL-E API
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}",
        }
        data = {
            "model": "image-alpha-001",
            "prompt": prompt,
            "num_images": 1,
            "size": "256x256",
            "response_format": "url",
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]

        # Download the image and save it to the output file
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        with open(output_filename, "wb") as out:
            out.write(image_response.content)

        logging.info(f"Thumbnail successfully generated and saved as {output_filename}")
