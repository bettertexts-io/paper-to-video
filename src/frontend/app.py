import streamlit as st
import time
import requests


def main():
    st.title("Paper2Video")

    paper_url = st.text_input(
        "Please enter the URL to an arXiv paper:",
        placeholder="e.g. https://arxiv.org/abs/1706.03762",
    )

    if st.button("Submit"):
        if paper_url:
            submit_url(paper_url)
        else:
            st.write("Please enter a valid URL")
    else:
        st.write("Enter a URL and press submit")


def submit_url(paper_url):
    # Introducing a status progress bar while the request is being processed
    with st.spinner("Videorizing the paper. This can take up to 5 minutes..."):
        progress_bar = st.progress(0)

        for i in range(4):
            # Update the progress bar with each iteration.
            progress_bar.progress((i + 1) * 25)

            # Simulating some process with a sleep
            time.sleep(0.1)

        # You would replace 'YOUR_BACKEND_ENDPOINT' with the endpoint of your backend service
        response = requests.post(
            "http://127.0.0.1:8000/paper2video",
            json={"paper_id": paper_url.split("/")[-1]},
        )

        if response.status_code == 200:
            st.success("The URL has been submitted successfully!")
        else:
            st.error(f"Failed to submit the URL. Error: {response.text}")


if __name__ == "__main__":
    main()
