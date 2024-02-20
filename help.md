`sudo apt-get update`

`sudo apt-get install -y docker.io`

`sudo systemctl enable docker`

`sudo systemctl start docker`

`sudo usermod -aG docker $USER`

`sudo reboot`


**login to remote server again**


`sudo apt install unzip`

`curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"`

`unzip awscliv2.zip && rm awscliv2.zip`

`sudo ./aws/install`

`aws configure --profile default`

`nano ~/.aws/credentials`

**add region just below secret key**

```bash
[default]
aws_access_key_id = YourAccessKey
aws_secret_access_key = YourSecreKey
region = us-west-2
```

`git clone https://github.com/ccir41/intelligent-mutual-fund-prospectus-document-processing.git`

`cd intelligent-mutual-fund-prospectus-document-processing`

`docker build -t pdf-advance-rag-financial:latest .`

```bash
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile default)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile default)
export AWS_REGION=$(aws configure get region --profile default)
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_REGION
```

`docker run --name pdf-advance-rag-financial -p 80:80 -d -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_REGION -v ./cache:/app/cache -v ./:/app pdf-advance-rag-financial:latest`

`docker stop pdf-advance-rag-financial`

`docker rm pdf-advance-rag-financial`

`docker login`

`docker tag pdf-advance-rag-financial:latest shishir41/pdf-advance-rag-financial:latest`

`docker push shishir41/pdf-advance-rag-financial:latest`


**And make image of that EC2 and while creating lunch configuration of auto scale add below ec2-user data**

```bash
#!/bin/bash
docker pull shishir41/pdf-advance-rag-financial:latest
docker volume create app_vol
docker volume create app_cache_vol

docker run --name pdf-advance-rag-financial -p 80:80 -d -e AWS_ACCESS_KEY_ID=YourAccessKey -e AWS_SECRET_ACCESS_KEY=YourSecretKey -e AWS_DEFAULT_REGION=YourAwsRegion -v app_vol:/app/cache -v app_cache_vol:/app shishir41/pdf-advance-rag-financial:latest
```