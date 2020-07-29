# awsip: Update the IP of a Route 53 record if it's been changed.

My ISP can change my public IP anytime unless I shell out $$$ for a business connection...qq
This script is meant to run periodically, keeping a Route53 record consistent with my home router's public IP.

To use it, just run the file with no arguments.

```
python3 awsip.py
```

**Note**: The script expects to be able to read `~/.aws/config` for a profile named `awsip`.
To set that up, follow these steps:

1. In the AWS management console, go to IAM.
1. Create a group named something like `Route53Applications` with the `AmazonRoute53FullAccess` permission.
1. Create a user named something like `awsip` with `Programmatic access` and add him to your new group (`Route53Applications`).
1. Copy the access key and secret.
1. Place them into your `~/.aws/config` under the profile name `awsip`.
1. Done! `boto3` will be able to access the access key from your config file.

Here's what my `~/.aws/config` looks like:

```
[profile awsip]
aws_access_key_id = Y0U41NTG3TT1NGMYK3YS
aws_secret_access_key = OrMyS3cret3ithe+rWh4tD0YouT1hink1mStup1d
```
