import streamlit as st
import openai
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


# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.pdf)", type=("pdf")
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


    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    def try_generate_image(api_key, prompt):
        try:
            # Create an OpenAI client using the provided API key
            client = OpenAI(api_key=api_key)
            
            # Attempt to generate an image
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response
        except openai.AuthenticationError as e:
            # Return the exception as a string so we can handle it
            return str(e)

    # Get the secret key from Streamlit secrets
    openai_api_key = st.secrets.get("api_key")

    # First try with the secret API key
    response = try_generate_image(openai_api_key, prompt)

    # Check if the API key failed
    if isinstance(response, str):  # If error message is returned
        user_api_key = st.text_input("OpenAI API Key", type="password")
        if not user_api_key:
            st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        else:
            # Try generating the image with the user's API key
            response_second_try = try_generate_image(user_api_key, prompt)
            if isinstance(response_second_try, str):  # If there's still an error with the user's key
                st.error(f"Error with your API key: {response_second_try}")
            else:
                # If successful, display the image
                image_url = response_second_try.data[0].url
                        # Fetch the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Open the image from the response content
                    img = Image.open(BytesIO(response.content))
                    
                    # Display the image in Streamlit
                    st.image(img, caption="Academic weapon", use_container_width =True)
                else:
                    st.error("Failed to fetch the image.")
    else:
        # If the secret key worked, display the image
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