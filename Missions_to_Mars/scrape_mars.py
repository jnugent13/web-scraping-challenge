from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    # Visit NASA Mars News
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    # Get news_title and news_article
    titles = soup.find_all('div', class_="content_title")
    news_title = titles[1].text
    news_title.replace("\n", "")

    paragraphs = soup.find_all('div', class_="article_teaser_body")
    news_article = paragraphs[0].text

    # Visit JPL Mars Space Images
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    # Get the featured image link
    featured_image = soup.find('article', class_="carousel_item")
    featured_image_link = featured_image.find('a', class_="button")['data-fancybox-href']
    featured_image_url = f'http://www.jpl.nasa.gov{featured_image_link}'

    # Visit the Mars Weather Twitter Page
    mars_weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(mars_weather_url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, "html.parser")

    # Get the latest weather tweet
    tweets = browser.find_by_tag('span')
    weather = []
    for tweet in tweets:
        weather.append(tweet.value)
    
    weather_tweets = []
    for x in weather:
        if "sol" in x:
            weather_tweets.append(x)
    
    mars_weather = weather_tweets[0]

    # Visit the Mars Facts website
    mars_facts_url = "https://space-facts.com/mars/"

    tables = pd.read_html(mars_facts_url)
    df = tables[0]
    df.columns = ['0', 'value']
    df.set_index('0', inplace = True)
    html_table = df.to_html("table.html")

    # Visit the Mars Facts website
    hemispheres_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemispheres_url)
    
    time.sleep(1)

    html = browser.html
    soup = bs(html, 'html.parser')
    
    # Retrieve all elements that contain hemisphere images/links
    pictures = soup.find_all('div', class_='item')

    page_links = []
    titles = []
    for picture in pictures:
        title = picture.find('h3').text
        titles.append(title)
        pic_link = picture.find('a')['href']
        page_links.append(f'https://astrogeology.usgs.gov{pic_link}')

    img_urls = []
    for link in page_links:
        browser.visit(link)
        image = soup.find_all('ul')[0]
        urls = image.find_all('a')
        pic_url = urls[0]['href']
        img_urls.append(pic_url)
    
    hemisphere_image_urls = []
    for x in range(4):
        image_dict = {}
        image_dict["title"] = titles[x]
        image_dict["img_url"] = img_urls[x]
    
    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_article": news_article,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "mars_facts": html_table,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
