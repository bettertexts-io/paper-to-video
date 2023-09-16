from threading import Thread
import streamlit as st
import time
import requests
import websockets
import asyncio
import json


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


async def fetch_progress(paper_id, progress_bar):
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/{paper_id}") as websocket:
        while True:
            data = await websocket.recv()
            progress_data = json.loads(data)
            progress_bar.progress(progress_data["progress"])


def run_fetch_progress(paper_id, progress_bar):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_progress(paper_id, progress_bar))
    loop.close()


def submit_url(paper_url):
    # Introducing a status progress bar while the request is being processed
    with st.spinner(
        "Converting the paper into a video. This can take up to 20 minutes..."
    ):
        progress_bar = st.progress(0)

        paper_id = paper_url.split("/")[-1]
        thread = Thread(target=run_fetch_progress, args=(paper_id, progress_bar))
        thread.start()

        # You would replace 'YOUR_BACKEND_ENDPOINT' with the endpoint of your backend service
        response = requests.post(
            "http://127.0.0.1:8000/paper2video",
            json={"paper_id": paper_id},
        )

        if response.status_code == 200:
            st.success("The video has been generated successfully.")
            video_url = response.json()["video_url"]
            st.video(video_url)
        else:
            st.error(f"Failed to generate the video: {response.text}")


if __name__ == "__main__":
    main()
