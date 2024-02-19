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

`docker run --name pdf-advance-rag-financial -p 80:80 -d -e AWS_ACCESS_KEY_ID=YourAccessKey -e AWS_SECRET_ACCESS_KEY=YourSecreKey -e AWS_DEFAULT_REGION=YourBedrockEnabledRegion pdf-advance-rag-financial:latest`

`docker stop pdf-advance-rag-financial`

`docker rm pdf-advance-rag-financial`


**And make image of that EC2 and while creating lunch configuration of auto scale add below ec2-user data**

```bash
#!/bin/bash

export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile default)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile default)
export AWS_REGION=$(aws configure get region --profile default)

docker run --name pdf-advance-rag-financial -p 80:80 -d -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$AWS_REGION pdf-advance-rag-financial:latest
```