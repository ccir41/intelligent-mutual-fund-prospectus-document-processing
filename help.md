`sudo apt-get update`

`git clone https://github.com/ccir41/intelligent-mutual-fund-prospectus-document-processing.git`

`sudo apt-get install -y docker.io`

`sudo systemctl enable docker`

`sudo systemctl start docker`

`sudo usermod -aG docker $USER`

`sudo reboot`

`cd intelligent-mutual-fund-prospectus-document-processing`

`docker build -t pdf-advance-rag-financial:latest .`

`docker run --name pdf-advance-rag-financial -p 80:80 -d -e AWS_ACCESS_KEY_ID=YourAccessKey -e AWS_SECRET_ACCESS_KEY=YourSecreKey -e AWS_DEFAULT_REGION=YourBedrockEnabledRegion pdf-advance-rag-financial:latest`