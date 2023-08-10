# Dev Run

`chmod u+x run.sh`
`./run.sh dev <script to execute>`

The repo directory will be mounted into the container, so that there's no need to rebuild the container for every change.

# Production Run

`chmod u+x run.sh`
`./run.sh prod <script to execute>`

The repo directory will not be mounted into the conatiner 'cause of security implications.

# Install requirements for mac:

brew install ffmpeg espeak
