import re, requests
from collections import namedtuple
from HTMLParser import HTMLParser

REGEX_PATTERN = '\.[A-z]+\("/[A-z/]+"'
CODE_SPLIT_NAME_REGEX_PATTERN = '([0-9]+:"[A-z\.-]+")+'
CODE_SPLIT_HASH_REGEX_PATTERN = '([0-9]+:"[a-z0-9]{20}")+'
SCRIPT_URLS = set()

Endpoint = namedtuple("Endpoint", "method url")

class MyHTMLParser(HTMLParser):
  def handle_starttag(self, tag, attrs):
    if tag == 'script':
      for attr in attrs:
        if attr[0] == 'src':
          SCRIPT_URLS.add(attr[1])

def get_method(s):
  return s.split('(')[0].replace('.', '')

def get_url(s):
  return re.findall('".*"', s)[0].replace('"', '')

def remove_last_slash(s):
  return re.sub('/"', '"', s)

def remove_double_quote(s):
  return re.sub('"', '', s)

def is_api_call(method):
  return method == 'get' or method == 'put' or method == 'delete' or method == 'post'

def get_scripts_from_html(url):
  r = requests.get(url)
  parser = MyHTMLParser()
  parser.feed(r.text)

def extract_endpoints_from_js(code, api_root):
  endpoints = []

  substrings = [remove_last_slash(s) for s in re.findall(REGEX_PATTERN, code)]
  substrings = set(substrings)
  for s in substrings:
    method = get_method(s)
    url = get_url(s)
    if is_api_call(method):
      url = api_root + url
    else:
      # Change the method to GET for react-router methods
      method = 'get'
    endpoints.append(Endpoint(method, url))

  return endpoints

def search_for_more_bundled_js_files(code):
  bundled_files = {}
  hashes = [remove_double_quote(s) for s in re.findall(CODE_SPLIT_HASH_REGEX_PATTERN, code)]
  if len(hashes) != 0:
    names = [remove_double_quote(s) for s in re.findall(CODE_SPLIT_NAME_REGEX_PATTERN, code)]
    for name in names:
      c = name.split(':') 
      bundled_files[c[0]] = '/assets/' + c[1]
    for hashstring in hashes:
      c = hashstring.split(':') 
      if c[0] in bundled_files:
        bundled_files[c[0]] = bundled_files[c[0]] + '-' + c[1] + '.js'
    
  return bundled_files

def scan_js_files(domain, path, api_root):
  # Inspect given js file for endpoints
  all_endpoints = set()
  r = requests.get(domain + path)
  endpoints = extract_endpoints_from_js(r.text, api_root)
  for endpoint in endpoints:
    endpoint = endpoint._replace(url=domain+endpoint.url)
    all_endpoints.add(endpoint)

  # Get more endpoints by recursively searching for more bundled js files
  d = search_for_more_bundled_js_files(r.text)
  for key, value in d.iteritems():
    all_endpoints = all_endpoints.union(scan_js_files(domain, value, api_root))
  
  return all_endpoints

def get_endpoints(domain, path_to_scan, api_root='/api'):
  global SCRIPT_URLS
  SCRIPT_URLS = set()

  # Get the URLs of all bundled js files
  get_scripts_from_html(path_to_scan)

  # Scan through each js file for endpoints
  all_endpoints = set()
  for script_url in SCRIPT_URLS:
    all_endpoints = all_endpoints.union(scan_js_files(domain, script_url, api_root))

  return all_endpoints
