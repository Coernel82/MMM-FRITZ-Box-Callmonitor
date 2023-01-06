import argparse
import os
import fritzconnection
import urllib.request
import sys
import json

def send_file(file, content):
    print(json.dumps({"filename": file, "content": content}))
    sys.stdout.flush()

class FritzAccess:
    """
    Stores the connection and provide convenience functions
    """

    def __init__(self, address, port, user, password):
        self.fc = fritzconnection.FritzConnection(address, port, user, password)

    def download_recent_calls(self, directory="data"):
        result = self.fc.call_action("X_AVM-DE_OnTel", "GetCallList")
        filename = os.path.join(directory, "calls.xml")
        self.forward_file(result["NewCallListURL"], filename)

    def download_phone_book(self, directory="data"):
        result = self.fc.call_action("X_AVM-DE_OnTel", "GetPhonebookList")
        if len(result) == 0:
            raise Exception("Please check if your user has access to \"View and edit FRITZ!Box settings\".")
            sys.exit(1)
        for phonebook_id in result["NewPhonebookList"]:
            result_phonebook = self.fc.call_action(
                "X_AVM-DE_OnTel", "GetPhonebook", NewPhonebookID=phonebook_id
            )
            filename = os.path.join(directory, f"pbook_{phonebook_id}.xml")
            self.forward_file(result_phonebook["NewPhonebookURL"], filename)

    def forward_file(self, url, filename):
        try:
            f = urllib.request.urlopen(url)
            content = f.read()
            f.close()
            # replace newline with space keep clear where the file ends
            content = content.replace(b"\n", b" ")
            send_file(filename, content)
        except urllib.error.HTTPError as e:
            raise Exception(f"Error (HTTP) {e.code} {url}")
            sys.exit(1)
        except urllib.error.URLError as e:
            raise Exception(f"Error (URL) {e.code} {url}")
            sys.exit(1)


def main(args):
    handle = FritzAccess(
        address=args.ip,
        port=args.port,
        user=args.username,
        password=args.password
    )

    if args.contacts_only:
        handle.download_phone_book()
        return

    if args.calls_only:
        handle.download_recent_calls()
        return

    handle.download_phone_book()
    handle.download_recent_calls()
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="command line utility for FRITZ!Box access to download phone books and recent calls"
    )
    parser
