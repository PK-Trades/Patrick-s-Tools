import csv
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def process_csv(file_path, output_file):
    with open(file_path, 'r', encoding='utf-8') as input_file, open(output_file, 'w', newline='', encoding='utf-8') as output_file:
        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)

        # Write header row
        csv_writer.writerow(['URL', 'Domain', 'Page Title', 'Meta Description', 'Header Tags', 'Image Tags', 'Internal Links', 'External Links', 'Social Media Links', 'Canonical URL', 'Robots.txt', 'Sitemap.xml', 'Page Speed', 'Mobile Friendly', 'SSL', 'SSL Expiration', 'SSL Issuer', 'SSL Validity', 'SSL Rating', 'SEO Score', 'SEO Rating', 'SEO Recommendations', 'SEO Score (out of 100)'])

        urls_meeting_criteria = 0  # Counter for URLs meeting all criteria

        for row in csv_reader:
            url = row[0]
            domain = urlparse(url).netloc
            page_title = ''
            meta_description = ''
            header_tags = []
            image_tags = []
            internal_links = []
            external_links = []
            social_media_links = []
            canonical_url = ''
            robots_txt = ''
            sitemap_xml = ''
            page_speed = ''
            mobile_friendly = ''
            ssl = ''
            ssl_expiration = ''
            ssl_issuer = ''
            ssl_validity = ''
            ssl_rating = ''
            seo_score = ''
            seo_rating = ''
            seo_recommendations = ''
            seo_score_out_of_100 = ''

            # Get page title
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                page_title = soup.title.text.strip()
            except Exception as e:
                print(f"Error getting page title for {url}: {e}")

            # Get meta description
            try:
                meta_description_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_description_tag:
                    meta_description = meta_description_tag['content']
            except Exception as e:
                print(f"Error getting meta description for {url}: {e}")

            # Get header tags
            try:
                header_tags = [tag.text.strip() for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            except Exception as e:
                print(f"Error getting header tags for {url}: {e}")

            # Get image tags
            try:
                image_tags = [img['src'] for img in soup.find_all('img', src=True)]
            except Exception as e:
                print(f"Error getting image tags for {url}: {e}")

            # Get internal links
            try:
                internal_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('/')]
            except Exception as e:
                print(f"Error getting internal links for {url}: {e}")

            # Get external links
            try:
                external_links = [a['href'] for a in soup.find_all('a', href=True) if not a['href'].startswith('/') and not a['href'].startswith('#')]
            except Exception as e:
                print(f"Error getting external links for {url}: {e}")

            # Get social media links
            try:
                social_media_links = [a['href'] for a in soup.find_all('a', href=True) if re.search(r'facebook|twitter|instagram|linkedin|youtube', a['href'])]
            except Exception as e:
                print(f"Error getting social media links for {url}: {e}")

            # Get canonical URL
            try:
                canonical_url_tag = soup.find('link', rel='canonical')
                if canonical_url_tag:
                    canonical_url = canonical_url_tag['href']
            except Exception as e:
                print(f"Error getting canonical URL for {url}: {e}")

            # Get robots.txt
            try:
                robots_txt = requests.get(f"{url}/robots.txt").text
            except Exception as e:
                print(f"Error getting robots.txt for {url}: {e}")

            # Get sitemap.xml
            try:
                sitemap_xml = requests.get(f"{url}/sitemap.xml").text
            except Exception as e:
                print(f"Error getting sitemap.xml for {url}: {e}")

            # Get page speed
            try:
                page_speed = requests.get(f"https://gtmetrix.com/api/0.1/test?url={url}").json()['reports']['lighthouse']['data']['score']
            except Exception as e:
                print(f"Error getting page speed for {url}: {e}")

            # Get mobile friendly
            try:
                mobile_friendly = requests.get(f"https://search.google.com/test/mobile-friendly?url={url}").text
            except Exception as e:
                print(f"Error getting mobile friendly for {url}: {e}")

            # Get SSL information
            try:
                ssl_info = requests.get(f"https://api.ssllabs.com/api/v3/analyze?host={domain}").json()
                ssl = ssl_info['status']
                ssl_expiration = ssl_info['cert']['notAfter']
                ssl_issuer = ssl_info['cert']['issuerDN']
                ssl_validity = ssl_info['cert']['validity']
                ssl_rating = ssl_info['rating']
            except Exception as e:
                print(f"Error getting SSL information for {url}: {e}")

            # Get SEO score
            try:
 