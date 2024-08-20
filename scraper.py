import os
import csv
import json
import random
import logging
import datetime
from time import sleep
import requests
import pytz
import tzlocal
from facebook_scraper import get_posts, get_group_info
from settings import *

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set timezone
local_tz = tzlocal.get_localzone()
set_tz = pytz.timezone(TIMEZONE)

# Prepare output file
filename = datetime.datetime.now().strftime('%Y.%m.%d %H-%M') + '.csv'
output_path = os.path.join('output', filename)
os.makedirs('output', exist_ok=True)

# Open CSV file for writing
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Post URL', 'Date', 'Author Name', 'Author ID', 'Text', 'Images', 'Video', 'Post ID'
    ])

    # Set scraping options
    options = {"allow_extra_requests": False, "posts_per_page": 10}
    after = None

    # Configure date filter
    if FILTER_DATE_AFTER:
        after = datetime.datetime.strptime(FILTER_DATE_AFTER, '%Y.%m.%d %H:%M')
        after = after.replace(tzinfo=set_tz).astimezone(local_tz).replace(tzinfo=None)

    # Enable high-resolution images if required
    if HIGH_RES_IMAGES:
        options['allow_extra_requests'] = True

    # Extract group ID from URL if necessary
    if 'https' in GROUP:
        GROUP = GROUP.strip('/').split('/')[-1]

    # Load cookies
    cookies = {}
    used_filename = ''
    try:
        with open('.used_cookie', encoding='utf-8') as fi:
            used_filename = fi.read().strip()
    except Exception:
        pass

    # Select a random cookie file
    cookies_filename = random.choice(os.listdir(COOKIE_DIR))
    while cookies_filename.strip() == used_filename:
        cookies_filename = random.choice(os.listdir(COOKIE_DIR))
        if len(os.listdir(COOKIE_DIR)) < 2:
            break

    # Save the used cookie filename
    with open('.used_cookie', 'w', encoding='utf-8') as fo:
        fo.write(cookies_filename.strip())

    # Load cookies from the selected file
    with open(os.path.join(COOKIE_DIR, cookies_filename)) as cookies_file:
        for entry in json.loads(cookies_file.read())['cookies']:
            cookies[entry['name']] = entry['value']

    print('Using cookie file:', cookies_filename)

    # Get group information
    info = get_group_info(GROUP, cookies=cookies)
    url = None
    if FILTER_AUTHOR_ID:
        url = f'https://m.facebook.com/profile.php?id={FILTER_AUTHOR_ID}&groupid={info["id"]}'

    # Set up post generator
    generator = get_posts(
        group=GROUP,
        start_url=url,
        options=options,
        cookies=cookies,
        latest_date=after,
        pages=999999
    )

    # Scrape posts
    posts_scraped = 0
    for post in generator:
        sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        if len(post) == 2:
            print("Login required")
            exit(0)

        # Filter posts by author name
        if FILTER_AUTHOR_NAME and FILTER_AUTHOR_NAME.lower() != post['username'].lower():
            continue

        # Filter posts by date
        if FILTER_DATE_AFTER and post['time'] < after:
            continue
        if FILTER_DATE_BEFORE:
            before = datetime.datetime.strptime(FILTER_DATE_BEFORE, '%Y.%m.%d %H:%M')
            before = before.replace(tzinfo=set_tz).astimezone(local_tz).replace(tzinfo=None)
            if post['time'] > before:
                continue

        # Filter posts by keywords
        text = post.get('original_text', post['text'])
        if FILTER_KEYWORDS:
            keywords = FILTER_KEYWORDS.split(',')
            if FILTER_KEYWORDS_MODE == 'OR' and not any(keyword.strip().lower() in text.lower() for keyword in keywords):
                continue
            if FILTER_KEYWORDS_MODE == 'AND' and not all(keyword.strip().lower() in text.lower() for keyword in keywords):
                continue

        # Collect images and video
        images = '; '.join(post.get('images', [])) if HIGH_RES_IMAGES else '; '.join(post.get('images_lowquality', []))
        video = post.get('video', '')

        # Write post data to CSV
        writer.writerow([
            post['post_url'].replace('m.facebook.com', 'facebook.com'),
            post['time'].date(),
            post['username'],
            post['user_id'],
            text,
            images,
            video,
            post['post_id']
        ])
        f.flush()
        posts_scraped += 1
        print(post['text'][:100].replace('\n', ' '))
        print('Posts scraped:', posts_scraped)

# Download images if required
if DOWNLOAD_IMAGES:
    print('Downloading images...')
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            if not line['Images']:
                continue
            for index, image_url in enumerate(line['Images'].split('; ')):
                try:
                    print(image_url)
                    resp = requests.get(image_url)
                    with open(f"output/images/{line['Post ID']}_{index}.jpg", 'wb') as fo:
                        fo.write(resp.content)
                except Exception as e:
                    print(e)

# Download videos if required
if DOWNLOAD_VIDEOS:
    print('Downloading videos...')
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            if not line['Video']:
                continue
            try:
                os.system(f'''yt-dlp -o "output/videos/{line['Post ID']}.mp4" "{line['Video']}"''')
            except Exception as e:
                print(e)

print('Done')
