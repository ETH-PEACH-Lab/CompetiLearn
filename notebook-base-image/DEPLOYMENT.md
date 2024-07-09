# Using the GitHub Container Registry for Deployment

1. Create a personal token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

```
docker login ghcr.io --username github-account
[Paste your GitHub token on this prompt]
```
2. Build the image for the notebook base image
```
docker image build --platform linux/amd64 -t competilearn-jupyter-base . 
```

2. Tag and push your Docker image
```
docker tag competilearn-jupyter-base ghcr.io/eth-peach-lab/competilearn/competilearn-jupyter-base:latest
docker push ghcr.io/eth-peach-lab/competilearn/competilearn-jupyter-base:latest
```