# Tool Tuesday Random Video Generator

Basic python app that grabs the most recent track/song listings off wikipedia, picks one at random, searches youtube with it and then grabs a random video.

## Getting Started

1. Make sure you have poetry installed https://python-poetry.org/docs/
2. Install venv and dependencies: `poetry install`
3. Run the handler locally: `poetry run local_dev`

## Deploy to lambda

1. Make sure pulumi is installed
2. Build and bundle the app: `./build-bundle.sh`
3. Deploy: `pulumi up`


## TODO
- [ ] Put an API gateway in front of it
- [ ] Rewrite infra in python. Currently no m1 support for grpcio (dependency of pulumi via python). Due for release Jan 23'
- [ ] ?Keep a record of previous results - dynamo table?
- [ ] ?Add a live/tool-archives flag on requests?