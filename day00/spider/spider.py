import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes

VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

def has_valid_image_extension(url):
    filename = os.path.basename(url.split('?')[0])
    _, ext = os.path.splitext(filename)
    return ext.lower() in VALID_IMAGE_EXTENSIONS

def scrape_images_from_page(url, seen, save_path="./data/", depth=5, index=[0], base_domain=None):
    if depth < 0 or url in seen:
        return
    seen.add(url)

    print(f"\n--- Crawling: {url} | Depth: {depth} ---")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')
    links = soup.find_all('a', href=True)

    os.makedirs(save_path, exist_ok=True)

    for img in images:
        img_url = img.get('src')
        if not img_url:
            continue

        img_url = urljoin(url, img_url)

        try:
            img_response = requests.get(img_url, timeout=10)
            img_response.raise_for_status()

            content_type = img_response.headers.get('Content-Type', '')
            extension = mimetypes.guess_extension(content_type.split(";")[0].strip()) or '.jpg'

            if has_valid_image_extension(img_url):
                filename = os.path.basename(img_url.split('?')[0])
            else:
                filename = f"image_{index[0]}{extension}"
                index[0] += 1

            file_path = os.path.join(save_path, filename)
            if os.path.exists(file_path):
                print(f"File {file_path} already exists, skipping.")
                continue
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
            print(f"Saved image to {file_path}")

        except requests.RequestException as e:
            print(f"Error downloading image {img_url}: {e}")

    # Extract base domain if not already set
    if not base_domain:
        base_domain = urlparse(url).netloc

    for link in links:
        href = link['href']
        next_url = urljoin(url, href)
        parsed = urlparse(next_url)

        # Stay within the same domain
        if parsed.netloc == base_domain:
            scrape_images_from_page(next_url, seen, save_path, depth - 1, index, base_domain)

def start_spider(args):
    seen = set()
    scrape_images_from_page(args['url'], seen, args['path'], args['depth'])

def parse_args():
    args = {
        'valid': False,
        'depth': 5,
        'path': "./data/",
        'url': None
    }

    if len(sys.argv) < 2:
        return args

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '-r':
            i += 1
        elif arg == '-l' and i + 1 < len(sys.argv) and sys.argv[i + 1].isnumeric():
            args['depth'] = int(sys.argv[i + 1])
            i += 2
        elif arg == '-p' and i + 1 < len(sys.argv):
            args['path'] = sys.argv[i + 1]
            i += 2
        elif arg.startswith('http'):
            if i != len(sys.argv) - 1:
                return args
            args['url'] = arg
            args['valid'] = True
            return args
        else:
            return args
    return args

if __name__ == "__main__":
    args = parse_args()
    if args['valid']:
        start_spider(args)
    else:
        print("Usage: python spider.py [-r -l <depth> -p <path>] <url>")
        sys.exit(1)
