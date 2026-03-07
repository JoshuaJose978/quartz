---
title: Cloud Provider CLI Configuration Guide
---

This guide summarizes the main configuration file locations, example content, and essential commands for viewing and updating account/profile settings using the CLI for AWS, GCP, and Azure.

---

## Table of Contents

1. [AWS CLI](#aws-cli)
   - [Config File Locations & Example](#aws-locations)
   - [Viewing & Updating Configuration (Commands)](#aws-commands)
2. [Google Cloud CLI (gcloud)](#gcloud)
   - [Config File Locations & Example](#gcloud-locations)
   - [Viewing & Updating Configuration (Commands)](#gcloud-commands)
3. [Azure CLI (az)](#azure-cli)
   - [Config File Locations & Example](#azure-locations)
   - [Viewing & Updating Configuration (Commands)](#azure-commands)
4. [Summary Table](#summary)
5. [Notes](#notes)
6. [References](#references)

---

## AWS CLI<a name="aws-cli"></a>

### Config File Locations & Example<a name="aws-locations"></a>

- **Config file:**  
  - Location: `~/.aws/config` (Windows: `%USERPROFILE%\.aws\config`)
  - Stores profile settings like region, output format.

- **Credentials file:**  
  - Location: `~/.aws/credentials` (Windows: `%USERPROFILE%\.aws\credentials`)
  - Stores access keys per profile.

**Example:**

`~/.aws/config`  
```ini
[default]
region = us-east-1
output = json

[profile myprofile]
region = eu-west-1
```

`~/.aws/credentials`  
```ini
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = ...

[myprofile]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
```

---

### Viewing & Updating Configuration (AWS CLI Commands)<a name="aws-commands"></a>

**Viewing Config/Profiles**
```bash
aws configure list                   # Show current config settings
aws configure list-profiles          # List all available profiles
aws configure get region             # Get the default profile's region
aws configure get aws_access_key_id --profile myprofile  # Get myprofile's access key

cat ~/.aws/config                    # Raw config file
cat ~/.aws/credentials               # Raw credentials file
```

**Updating Config/Profiles**
```bash
aws configure                            # Set config for default profile (interactive)
aws configure --profile myprofile        # Set config for a named profile (interactive)

aws configure set region us-west-2 --profile myprofile           # Set region
aws configure set output yaml --profile myprofile                # Set output format
aws configure set aws_access_key_id AKIA.. --profile myprofile   # Set access key
aws configure set aws_secret_access_key <your_secret> --profile myprofile  # Set secret
```

---

## Google Cloud CLI (gcloud)<a name="gcloud"></a>

### Config File Locations & Example<a name="gcloud-locations"></a>

- **Configuration directory:**  
  - Location: `~/.config/gcloud/` (Windows: `%APPDATA%\gcloud\`)
- **Main config file:**  
  - Location: `~/.config/gcloud/configurations/config_default`
- **Service account credentials:**  
  - Typically specified directly via `--key-file=/path/to/key.json`  
- **Other files:**  
  - `~/.config/gcloud/active_config` – Tracks active named config
  - `~/.config/gcloud/credentials.db` – Stores OAuth tokens

**Example:**

`~/.config/gcloud/configurations/config_default`  
```ini
[core]
account = user@gmail.com
project = my-gcp-project
```

---

### Viewing & Updating Configuration (gcloud Commands)<a name="gcloud-commands"></a>

**Viewing Configuration**
```bash
gcloud config list                       # Show current config (project, account, etc.)
gcloud config configurations list        # List all configurations
gcloud config configurations describe MYCONFIG       # Describe named config
gcloud auth list                         # List logged-in accounts

cat ~/.config/gcloud/configurations/config_default   # Raw config file
```

**Updating Configuration**
```bash
gcloud config set project my-gcp-project         # Set active project
gcloud config set account user@example.com       # Set active account
gcloud config set compute/region us-central1     # Set default region

gcloud config configurations activate MYCONFIG   # Activate named config
gcloud config configurations create NEWCONFIG    # Create a new config

gcloud auth login                                # Login with interactive browser
gcloud auth activate-service-account --key-file /path/key.json   # Use service account
```

---

## Azure CLI (az)<a name="azure-cli"></a>

### Config File Locations & Example<a name="azure-locations"></a>

- **Azure Profile:**  
  - Location: `~/.azure/azureProfile.json` (Windows: `%USERPROFILE%\.azure\azureProfile.json`)
  - Stores account/subscription/tenant info.
- **Access Token Cache:**  
  - Location: `~/.azure/accessTokens.json`
- **Cloud Configuration:**  
  - Location: `~/.azure/clouds.config`
- **CLI Settings:**  
  - Location: `~/.azure/config`

**Example:**

`~/.azure/azureProfile.json`
```json
{
  "subscriptions": [
    {
      "id": "subscription-id",
      "name": "My Subscription",
      "user": {
        "name": "user@domain.com",
        "type": "user"
      }
    }
  ],
  "isCloudShell": false
}
```

---

### Viewing & Updating Configuration (az Commands)<a name="azure-commands"></a>

**Viewing Configuration and Accounts**
```bash
az account list                   # Show all subscriptions/accounts
az account show                   # Details on active subscription
az account list --output table    # Table format output

cat ~/.azure/azureProfile.json    # Raw profile file
cat ~/.azure/accessTokens.json    # Raw token file
cat ~/.azure/config               # Raw CLI config
```

**Updating Configuration**
```bash
az account set --subscription <SUBSCRIPTION_ID_OR_NAME>     # Switch active subscription
az login                                                    # Login (browser)
az login --service-principal -u <APP_ID> -p <PASSWORD> --tenant <TENANT_ID>   # Service principal login

az config set core.output=table         # Set default output format
az config set core.collect_telemetry=no # Disable telemetry
```

---

## Summary Table<a name="summary"></a>

| CLI      | Config Location                     | Credentials File                | View Config             | List Profiles/Accounts   | Update Config/Account    |
|----------|-------------------------------------|---------------------------------|-------------------------|-------------------------|-------------------------|
| AWS CLI  | `~/.aws/config`                     | `~/.aws/credentials`            | `aws configure list`<br>`cat ~/.aws/config`     | `aws configure list-profiles` | `aws configure`<br>`aws configure set KEY VALUE --profile NAME` |
| gcloud   | `~/.config/gcloud/configurations/`  | usually via `key-file.json`     | `gcloud config list`<br>`cat ~/.config/gcloud/configurations/config_default` | `gcloud config configurations list`<br>`gcloud auth list` | `gcloud config set KEY VALUE`<br>`gcloud config configurations activate NAME`<br>`gcloud auth login` |
| Azure CLI| `~/.azure/azureProfile.json`        | `~/.azure/accessTokens.json`    | `az account show`<br>`cat ~/.azure/azureProfile.json`    | `az account list`               | `az account set --subscription ID`<br>`az login`<br>`az config set KEY=VALUE` |

---

## Notes<a name="notes"></a>

- All CLI tools also support *environment variables* for config overrides (`AWS_PROFILE`, `GOOGLE_APPLICATION_CREDENTIALS`, etc.).
- Paths starting with `~` are for Linux/macOS. On Windows use `%USERPROFILE%` or `%APPDATA%` as indicated.
- Manual edits to config files are possible, but CLI commands are preferred for correctness.
- For advanced authentication (service accounts, etc.), consult each provider’s documentation.

---

## References<a name="references"></a>

- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [Google Cloud CLI Configuration](https://cloud.google.com/sdk/docs/configurations)
- [Azure CLI Configuration](https://learn.microsoft.com/en-us/cli/azure/azure-cli-configuration)

---

Let me know if you want more details on advanced configuration, automation or other CLI tools!
