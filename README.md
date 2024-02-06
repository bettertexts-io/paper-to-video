# Paper2Video

## Dev Run

`chmod u+x run.sh`
`./run.sh dev <script to execute>`

The repo directory will be mounted into the container, so that there's no need to rebuild the container for every change.

# Production Run

`chmod u+x run.sh`
`./run.sh prod <script to execute>`

The repo directory will not be mounted into the conatiner 'cause of security implications.

# Install requirements for mac:

brew install ffmpeg espeak

# How it works

Fetch the paper by its ID.
Vectorize the paper's LaTeX content.
Summarize the paper.
Convert the summary into a barebone script.
Enrich the barebone script with scenes.
Convert the enriched script into audio pieces.
Generate stock footage based on the script.
Generate captions for the video.
Render the video using the audio pieces, stock footage, and captions.
