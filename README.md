# AWSIP: Update the IP of a Route 53 record if it's been changed.

My ISP can change my public IP anytime unless I shell out $$$ for a business connection...qq
This script is meant to run periodically, keeping a Route53 record consistent with my home router's public IP.

To use it, just run the file with no arguments.
**Note**: The script expects to be able to read `~/.aws/config` for a profile named `awsip`.

```
python3 awsip.py
```