#!/usr/bin/env python2
"""
Logpuzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Google's Python Class
http://code.google.com/edu/languages/google-python-class/

Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg
HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US;
rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6"

"""

import os
import re
import sys
import urllib.request
import argparse
import shutil


def read_urls(filename):
    """Returns a list of the puzzle urls from the given log file,
    extracting the hostname from the filename itself.
    Screens out duplicate urls and returns the urls sorted into
    increasing order."""

    # get base url out of filename
    base_url = ''
    reg_base_url = re.match(r'.*(_)(.*)', filename)
    if reg_base_url:
        base_url = reg_base_url.group(2)

    reg = re.compile(r'((GET )(.*(puzzle).*(.jpg))( ))')
    url_list = []

    # get url out of file
    with open(filename) as f:
        for line in f.readlines():
            matched = reg.search(line)
            if matched:
                url = 'http://' + base_url + matched.group(3)
                if url not in url_list:
                    url_list.append(url)

    # sorts list based on wheither it needs to be descrabled
    scrabled_reg = re.compile(r'(puzzle).*(-).*(-)(.*)(.jpg)')
    if url_list:
        if scrabled_reg.search(url_list[0]):
            url_list = sorted(url_list, key=lambda x: x.split('-')[-1])
        else:
            url_list.sort()
    return(url_list)


def download_images(img_urls, dest_dir):
    """Given the urls already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory
    with an img tag to show each local image file.
    Creates the directory if necessary.
    """
    # clear directory if exists and add fresh directory
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.mkdir(dest_dir)
    # clear index.html if it has content
    open(dest_dir+'/index.html', 'w').close()
    # write to index.html
    with open(dest_dir+'/index.html', 'a') as f:
        f.write('<html>\n<body>\n')
        # download images from list to dest_dir
        for i in range(len(img_urls)):
            filename = 'img' + str(i)
            fullfilename = os.path.join(dest_dir, filename)
            urllib.request.urlretrieve(img_urls[i], fullfilename)
            f.write('<img src="' + filename + '">')
        f.write('</body>\n</html>\n')


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--todir',  help='destination directory for downloaded images'
        )
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser


def main(args):
    """Parse args, scan for urls, get images from urls"""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)

    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
