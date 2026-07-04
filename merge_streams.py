import argparse
import sys
import os
import logging
import requests
from P4 import P4, P4Exception

def parse_arguments():
    parser = argparse.ArgumentParser(description="Password should be provided in the P4PASSWD env")
    parser.add_argument("--source", required = True, help = "Source stream path")
    parser.add_argument("--target", required= True, help = "Target stream path")
    parser.add_argument("--port", required = True, help = "Perforce server address/port")
    parser.add_argument("--user", required = True, help = "Perforce username")
    parser.add_argument("--client-name", required = True, help ="P4 client workspace name")
    parser.add_argument("--client-root", required = True, help = "Path to workspace")
    parser.add_argument("--force-sync", action="store_true", help="Forces full workspace sync")

    return parser.parse_args()
    
def set_up_connection(user, port):
    p4 = P4()
    p4.exception_level = 1
    p4.user = user
    p4.port = port

    p4_password = os.environ.get("P4PASSWD")
    if p4_password:
        p4.password = p4_password

    try: 
        p4.connect()
        
        if p4_password:
            p4.run_login()  
        return p4

    except P4Exception as e:
        raise RuntimeError(e)

def set_up_workspace(p4, target_stream, client_name, client_root, force_sync):
    client = p4.fetch_client(client_name)
    client["Root"] = client_root
    client["Stream"] = target_stream
    p4.save_client(client)
    p4.client = client_name  

    if force_sync:
        p4.run_sync("-f")
    else:
        p4.run_sync()

def merge_and_submit(p4, source):
    result = p4.run_merge("--from", source, "//...")
    opened = p4.run_opened()
    if len(opened) == 0:
        message = "No changes between streams to integrate."
        logging.info(message)
        return message
    
    p4.run_resolve("-am")
    unresolved = p4.run_resolve("-n")
    if len(unresolved) > 0:
        p4.run_revert("//...")
        raise RuntimeError("Conflicts preventing automatic merge detected. Manual resolve required.")
    else:
        p4.run_submit("-d", "Automatic merge completed")
        message = f"Successfully merged {len(result)} files from source to target stream."
        logging.info(message)
        return message

def send_discord_alert(message):
    webhook_url = os.environ.get("WEBHOOK_URL")

    if not webhook_url:
        logging.warning("Discord webhook url not set. Skipping Discord notification.")
        return
    
    data = {
        "content": f"Perforce merge alert: \n{message}"
    }

    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        logging.info("Discord alert sent successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Discord alert: {e}")
   


def main(args):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    status_message = ""
    exit_code = 0
    p4 = None

    try:
        p4 = set_up_connection(args.user, args.port)
        set_up_workspace(p4, args.target, args.client_name, args.client_root, args.force_sync)
        status_message = merge_and_submit(p4, args.source)
    except Exception as e:
        logging.error(f"{e}")
        status_message = e
        exit_code = 1
    
    finally:
        if p4 and p4.connected():
            p4.disconnect()
        
        send_discord_alert(status_message)
        sys.exit(exit_code)

if __name__ == "__main__":
    args = parse_arguments()
    main(args)