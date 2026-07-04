# Perforce Stream Merge Automator

## Overview
A Python-based  utility for automating Perforce Helix Core stream integrations. Designed for CI/CD pipelines, it handles workspace setup, stream merging, automatic conflict detection, and sends execution reports via Discord webhooks.

## Features
* **Automated Merging:** Handles `p4 merge`, `p4 resolve (-am)`, and automatic submissions.
* **Conflict Detection:** Safely halts and reverts changes if manual conflict resolution is required.
* **Force Sync:** Optional `--force-sync` flag to ensure the workspace is fully up-to-date before merging.
* **ChatOps Integration:** Sends execution summaries and error reports directly to a Discord channel.

## Prerequisites
* Python 3.x
* Perforce Server (p4d) and Client (p4/p4python)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/RukatM/p4-stream-merge-automator.git
   cd p4-stream-merge-automator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Set the following environment variables before running the script to ensure secrets are not hardcoded:
* `P4PASSWD` - Your Perforce user password.
* `WEBHOOK_URL` - Discord Webhook URL for status notifications.

## Usage
Run the script via CLI:
```bash
python merge_script_DevOps_test.py \
  --source //depot/main \
  --target //depot/dev \
  --port localhost:1666 \
  --user my_user \
  --client-name my_workspace \
  --client-root ./workspace_dir \
  --force-sync
```
