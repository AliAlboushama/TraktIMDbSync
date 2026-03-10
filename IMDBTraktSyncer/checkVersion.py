import xml.etree.ElementTree as ET
import urllib.request
import subprocess
import sys


def get_installed_version():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "TraktIMDbSync"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split()[1]
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        print(
            f"Error: Python executable '{sys.executable}' does not have pip installed."
        )

    return None


def get_latest_version():
    try:
        with urllib.request.urlopen(
            "https://pypi.org/rss/project/traktimdbsync/releases.xml"
        ) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        for item in root.findall("./channel/item"):
            title = item.find("title").text
            if title:
                return title
    except Exception:
        return None


def compare_versions(installed, latest):
    def parse_version(v):
        return tuple(map(int, v.split(".")))

    return parse_version(installed) < parse_version(latest)


def checkVersion():
    installed_version = get_installed_version()
    if not installed_version:
        return

    latest_version = get_latest_version()
    if not latest_version:
        return

    if compare_versions(installed_version, latest_version):
        print(
            f"A new version of TraktIMDbSync is available: {latest_version} (installed: {installed_version})."
        )
        print("To update use: python -m pip install TraktIMDbSync --upgrade")
        print("Documentation: https://github.com/AliAlboushama/TraktIMDbSync/releases")
    # else:
    # print(f"IMDBTraktSyncer is up to date (installed: {installed_version})")
