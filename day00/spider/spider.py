# from bs4 import BeautifulSoup
import requests
import os
import sys 
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_images_from_page(url, save_path="./data/"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')

    os.makedirs(save_path, exist_ok=True)

    for img in images:
        img_url = urljoin(url, img.get('src'))
        print(f"Found image: {img_url}")



def start_spider(args): 
    scrape_images_from_page(args['url'], args['path'])




def parse_args():
    if len(sys.argv) < 2:
        print("Usage: python spider.py [-r -l -p [PATH]] <url>")
    i = 1
    args = {
        'valid': False,
        'depth': 5,
        'path': "./data/",
        'url': None
    }
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith('-'):
            if arg == '-r':
                i += 1
            elif arg == '-l' and i + 1 < len(sys.argv) and sys.argv[i + 1].isnumeric():
                args['depth'] = int(sys.argv[i + 1])
                i += 2
            elif arg == '-p' and i + 1 < len(sys.argv):
                args['path'] = sys.argv[i + 1]
                i += 2  
            else:
                print(f"Unknown option or missing argument for {arg}.\nUsage: python spider.py [-r -l <depth> -p <path>] <url>")
                sys.exit(1)
        
        elif arg.startswith('http') or arg.startswith('https'):
            if i != len(sys.argv) - 1:
                print("Usage: python spider.py [-r -l <depth> -p <path>] <url>")
                return args
            args['url'] = arg
            args['valid'] = True
            return args
        else:
            print(f"Unknown option or missing argument for {arg}.\nUsage: python spider.py [-r -l <depth> -p <path>] <url>")
            return args
    print("No URL provided.\nUsage: python spider.py [-r -l <depth> -p <path>] <url>") 
    return args


if __name__ == "__main__":
    args = parse_args()
    if args['valid']:
        start_spider(args)
    else:
       sys.exit(1)


