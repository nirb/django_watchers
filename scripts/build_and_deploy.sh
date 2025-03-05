#!/bin/bash
echo "Building watchers_aws image....."
#docker build --no-cache --platform=linux/amd64/v4 -t watchers_aws .
docker build --no-cache --platform=linux/amd64 -t watchers_aws .
echo "Saving watchers_aws image....."
docker save watchers_aws -o watchers_aws.tar
echo "Copying watchers_aws image to ec2....."
scp -i ../aws/ec2-tlv-general.pem watchers_aws.tar ec2-user@51.17.183.233:/home/ec2-user/docker_images
echo "Removing watchers_aws image....."
rm watchers_aws.tar
echo "Deploying on ec2....."
ssh -i ../aws/ec2-tlv-general.pem ec2-user@51.17.183.233 'bash -s' < scripts/deploy_on_aws.sh
