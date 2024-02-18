sudo apt-get update
git clone https://github.com/ccir41/intelligent-mutual-fund-prospectus-document-processing.git
sudo apt-get install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
sudo reboot

docker build -t pdf-advance-rag-financial:latest .

docker run -p 80:80 -e AWS_ACCESS_KEY_ID= -e AWS_SECRET_ACCESS_KEY= -e AWS_DEFAULT_REGION=us-west-2 pdf-advanced-rag-financial:latest

sudo apt install unzip
sudo apt install awscli -y