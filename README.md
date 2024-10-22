# I 3D LAB (backend)

[![Django](https://img.shields.io/badge/Django-3.2%2B-brightgreen)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

## Table of Contents
- [I 3D LAB (backend)](#i-3d-lab-backend)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Tech Stack](#tech-stack)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Configuration](#configuration)
    - [Environment Variables](#environment-variables)

## Introduction

A 3d model configuration based on web.

## Tech Stack

- **Framework:** Django 3.2+
- **Programming Language:** Python 3.8+
- **Database:** PostgreSQL
- **Other Libraries/Tools:** Django Rest Framework, 

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- pip
- virtualenv (optional but recommended)
- create a database with 3dmodel name

### Steps

1. **Create and activate a virtual environment**
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

2. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up the database**
    ```sh
    python manage.py migrate
    ```

4. **Create a superuser**
    ```sh
    python manage.py createsuperuser
    ```

5. **Run the development server**
    ```sh
    python manage.py runserver
    ```

6. **Config image to 3d module**
```
# Install g++=9.3.0 in conda environment by
conda install gxx_linux-64=9.3.0
# Install torkit3d
git submodule update --init third_party/torkit3d && 
FORCE_CUDA=1 pip install third_party/torkit3d &&
# Install apex
git submodule update --init third_party/apex &&
pip install -v --disable-pip-version-check --no-cache-dir --no-build-isolation --config-settings "--build-option=--cpp_ext" --config-settings "--build-option=--cuda_ext" third_party/apex
```

## Configuration

### Environment Variables

Create a `.env` file in the project root and configure the following variables:

```env
# ------ Django Setting ------
SECRET_KEY="django-insecure-qbyp^46&#uxpnji#0-u=_g52z%w#1@5^x+1h+q^+egc_a1h5@v"
DEBUG=True
ALLOWED_HOSTS='127.0.0.1 localhost'

# ------ Postgresql Service ------
POSTGRES_DB='3dmodel'
POSTGRES_USER='admin'
POSTGRES_PASSWORD='admin'
POSTGRES_HOST='127.0.0.1'
POSTGRES_PORT='5432'

# ------ Video SDK Service ------
VIDEOSDK_API_KEY="594df1e4-6897-4a11-ace0-af87512578e8"
VIDEOSDK_SECRET_KEY="30fe59bfe2205654ce9079c9d111e462de66614829a1601f659f6237894f9829"
VIDEOSDK_API_ENDPOINT="https://api.videosdk.live/v2"

```

This README was generated with ❤️ by Mohammad Hosein Yaghoubi.

