@echo off
REM Script to set environment variables for Flask application

REM Set environment variables for development
SET FLASK_ENV=development
SET DATABASE_URL=
SET SECRET_KEY=your-secret-key-for-dev


REM Display the set environment variables
echo FLASK_ENV is set to %FLASK_ENV%
echo DATABASE_URL is set to %DATABASE_URL%
echo SECRET_KEY is set

