import boto3
import subprocess

with open("ip.txt", "w") as f:
    subprocess.run(["hostname", "-I"], stdout=f)

# Create an S3 client
s3 = boto3.client('s3')

s3.upload_file("./ip.txt", "owengillespie.com", "ip.txt")
