#!/bin/bash

python -m pip install -r "./stocksExtract/requirements.txt" --no-warn-script-location
python "./stocksExtract/stocksExtract/bot.py"