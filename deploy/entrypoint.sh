#!/bin/bash

echo "Starting Chainlit app from entrypoint.sh..."
PYTHONPATH=$PYTHONPATH:$(pwd)/restchat python -m chainlit run app.py --host 0.0.0.0 --port ${PORT:-5500}
