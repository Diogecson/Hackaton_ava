#!/bin/bash
pip install -r requirements.txt
gunicorn main:demo --bind 0.0.0.0:$PORT
