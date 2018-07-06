#!/usr/bin/env python

"""
Python script to download a release from github release page.
"""

import os
import sys
import json
import time

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

try:
    input = raw_input
except NameError:
    pass


__version__ = "0.0.1"
__author__ = "Xan xan"
__email__ = "xan.xan@gmail.com"
__license__ = "MIT"

class ConnectionError(Exception):
    """
    Raised on connection error.
    """

    def __init__(self, reason=None):
        """
        :param reason: Connection error reason.
        """
        self.reason = reason if reason else "Unknown reason."

    def __str__(self):
        return str(self.reason)


class GithubError(Exception):
    """
    Generic exception raised on GitHub API HTTP error.
    """

    def __init__(self, code, message=None):
        """
        :param code: HTTP error code.
        :param message: Exception message text.
        """
        self.code = code
        self.message = message

    def __str__(self):
        return "GitHub API HTTP {0}{1}".format(self.code, (": " + self.message) if self.message else "")

def resolve_last_release_tag(account=None, repo=None, quiet=False):
    """
    request the last version published in github
    :param account: GitHub repository owner
    :param repo: GitHub repository name
    :param quiet: It True, print nothing
    """
    url = "https://api.github.com/repos/{0}/{1}/releases/latest".format(account, repo)
    headers = {}
    request = urllib2.Request(url, headers=headers)
    start = time.time()
    try:
        response = urllib2.urlopen(request).read().decode("utf-8")
    except urllib2.HTTPError as e:
        raise GithubError(e.code)  # Generic GitHub API exception.
    except urllib2.URLError as e:
        raise ConnectionError(e.reason)
    stats = json.loads(response)
    if not quiet:
        end = time.time()
        print("Downloaded in {0:.3f}s".format(end - start))
    return stats

def get_tag_name(release, quiet=False):
    """
    get the tag name from the information
    :param release: information about the release
    :return: the tagName
    """
    tagName = release["tag_name"]
    return tagName

def get_asset_url(release, quiet=False):
    """
    get the assets url from the release information
    :return: the assets_url
    """
    return release["assets_url"]

def dlfile(url, path):
    """
    download the file and save it into the provided path
    :param url: url to download
    :param path: where to save the file
    """
    # Open the url
    try:
        f = urllib2.urlopen(url)
        print "downloading " + url

        # Open our local file for writing
        with open(path, "wb") as local_file:
            local_file.write(f.read())

    #handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url

def download_asset(release, assetName, quiet=False):
    """"
    extract the asset list and download the asset using the provided name
    :param release: information of the release
    :param assetName: name of the asset to download and name of the file to be generated
    :param quiet: if True, print information
    """
    url = get_asset_url(release)
    headers = {}
    request = urllib2.Request(url, headers=headers)
    start = time.time()
    try:
        response = urllib2.urlopen(request).read().decode("utf-8")
    except urllib2.HTTPError as e:
        raise GithubError(e.code)  # Generic GitHub API exception.
    except urllib2.URLError as e:
        raise ConnectionError(e.reason)
    stats = json.loads(response)
    if not quiet:
        end = time.time()
        print("Downloaded in {0:.3f}s".format(end - start))
    for asset in stats:
        if asset["name"] == assetName:
            artifact_url = asset["browser_download_url"]
            dlfile(artifact_url, assetName)


def main(account=None, repo=None, tag=None, artifact=None, latest=False, quiet=False):
    """
    Get number of downloads for GitHub release(s).
    :param account: GitHub repository owner username. If empty, user will be prompted for input.
    :param repo: GitHub repository name. If empty, user will be prompted for input.
    :param tag: Release tag name. If empty, get stats for all releases.
    :param artifact: Artifact to download
    :param latest: If True, ignore "tag" parameter and get stats for the latest release.
    :param quiet: If True, print nothing.
    """
    stat = resolve_last_release_tag(account, repo, quiet)
    download_asset(stat, "servantV3-0.0.1-SNAPSHOT-fat.jar", True)
#    print stat
#    print get_tag_name(stat)
#    print get_asset_url(stat)
#    if not quiet:
#        print_greeting()
#    try:
#        stats = download(account, repo, tag, artifact, latest, quiet)
#    except GithubError as e:
#        error(e.message)
#    except ConnectionError as e:
#        error(str(e))
#    else:
#        total = get_stats_downloads(stats, quiet or not detail)
#        print_total(total, quiet, tag or (stats["tag_name"] if latest else None))
#        return total



def main_cli(args=None):
    """
    Parse the command line and call the main function.
    """
    account = None           # GitHub account
    repo = None              # GitHub repository
    tag = None               # GitHub release tag
    latest = False           # Latest release
    quiet = False            # Quiet output
    artifact = None          # Artifact to download
    if args is None:
        args = sys.argv[1:]
    for arg in args:
        if arg == "-q" or arg == "--quiet":
            quiet = True
        elif arg == "-l" or arg == "--latest":
            latest = True
        elif arg == "-h" or arg == "--help" or arg == "-?":
            print_help()
        else:
            if not account:
                if "/" not in arg:
                    account = arg
                else:
                    userrepo = arg.split("/")
                    account = userrepo[0]
                    repo = userrepo[1]
            elif not repo:
                repo = arg
            elif not artifact:
                artifact = arg
            elif quiet and latest:
                break
            elif not tag:
                tag = arg
    return main(account, repo, tag, artifact, latest, quiet)


if __name__ == "__main__":  # pragma: no cover
    try:
        main_cli(sys.argv[1:])
    except KeyboardInterrupt:
        pass
