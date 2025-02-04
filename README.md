# Code review assistant backend

## Create new conda environment:

conda env create -f `<conda-environment.yml>` -n `<env-name>`

## Run when new package is added:

conda env export -n `<env-name>` > `<conda-environment.yml>`

```conda
conda env export -n ai-code-review-app > conda-requirements.yml
```

## Update local conda environment:

conda env update -n `<env-name>` --file `<conda-environment.yml>`

## Installation of CUDA Nvidia:

[Installation](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/)

Start server:
in app folder run -> fastapi dev main.py

Created docker image

```
docker build -t ai-code-review-backend .

```

Run the Docker Container

```
docker run -d -p 10000:10000 ai-code-review-backend

```

Run backed locally:

In /app folder:

```
fastapi dev main.py
```
