#!/bin/bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 