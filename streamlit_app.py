import streamlit as st
from openai import OpenAI
import spacy
import nltk
from PIL import Image
import requests
from io import BytesIO
import json

# Download NLTK datasets (words and stopwords)
try:
    nltk.data.find('corpora/words.zip')
except:
    nltk.download("words")

try:
    nltk.data.find('corpora/stopwords.zip')
except:
    nltk.download("stopwords")

# Show title and description.
st.title("🧠 Turn your resume into pure brainrot")
st.markdown(
    "Upload your resume below and we will get cooking right away!"
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets["api_key"]

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md or .pdf)", type=("txt", "md", "pdf")
)



if uploaded_file is not None:
    import tempfile
    from pydparser import ResumeParser
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        # Write the uploaded file content to the temporary file
        tmp_file.write(uploaded_file.read())
        temp_file_path = tmp_file.name  # Get the temporary file path
    
    try:
        # Pass the temporary file path to ResumeParser
        data = ResumeParser(temp_file_path).get_extracted_data()
        # Display the extracted data
        #st.write(data)
    finally:
        # Ensure the temporary file is deleted after processing
        import os
        os.remove(temp_file_path)
    
    del data["name"]
    del data["email"]
    del data["mobile_number"]

    filtered_data = {key: value for key, value in data.items() if value is not None}

    # Convert the dictionary to a JSON string for easy reading
    resume_data = json.dumps(filtered_data, indent=4)

    # Define your prompt
    prompt = (
        "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: "
        "Later I will input a resume of a person and your task will be to generate a brainrot meme "
        "that ridicules who this person will become in the future. The meme should have a "
        "a line of text. The meme should ridicule the person and be pure brainrot. The person should "
        "not feel honored but laughed at (in a funny way). You should imagine the person "
        "as a whole and ridicule his resume so far and smartly ridicule hypocrisy. "
        "In the following is his parsed resume in a json format, use all information available. It "
        "is very important that you first fully imagine the person and then create the meme. "
        "His parsed resume: "
        + resume_data  # Append the formatted resume to the prompt
    )
    #st.write(prompt)


    # Generate an answer using the OpenAI API.
    response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )
    image_url = response.data[0].url

        # Fetch the image
    response = requests.get(image_url)
    if response.status_code == 200:
        # Open the image from the response content
        img = Image.open(BytesIO(response.content))
        
        # Display the image in Streamlit
        st.image(img, caption="Academic weapon", use_container_width =True)
    else:
        st.error("Failed to fetch the image.")