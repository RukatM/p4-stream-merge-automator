import argparse
import sys
import os
import logging
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
        logging.error(f"{e}")
        sys.exit(1)

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
        logging.info("No changes between streams to integrate.")
        sys.exit(0)
    
    p4.run_resolve("-am")
    unresolved = p4.run_resolve("-n")
    if len(unresolved) > 0:
        logging.error("Conflicts preventing automatic merge detected. Manual resolve required.")
        p4.run_revert("//...")
        sys.exit(1)
    else:
        p4.run_submit("-d", "Automatic merge completed")
        logging.info(f"Successfully merged {len(result)} files from source to target stream.")

def main(args):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    p4 = set_up_connection(args.user, args.port)

    try:
        set_up_workspace(p4, args.target, args.client_name, args.client_root, args.force_sync)
        merge_and_submit(p4, args.source)
    except P4Exception as e:
        logging.error(f"{e}")
        sys.exit(1)
    
    finally:
        if p4.connected():
            p4.disconnect()

if __name__ == "__main__":
    args = parse_arguments()
    main(args)