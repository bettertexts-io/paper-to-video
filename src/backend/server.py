import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline.tmp import tmp_path
from pipeline.app import paper_2_video

app = FastAPI()


class PaperRequest(BaseModel):
    paper_id: str


@app.post("/paper2video")
async def create_paper_video(paper_request: PaperRequest):
    try:
        logging.info(f"paper_request: {paper_request}")
        video_file_id = paper_2_video(paper_request.paper_id)
        video_url = f"http://127.0.0.1:8000/video/{video_file_id}"

        return {"video_url": video_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/video/{video_id}")
async def read_video(video_id: str):
    file_path = tmp_path(paper_id=video_id, kind="output")
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Video not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
