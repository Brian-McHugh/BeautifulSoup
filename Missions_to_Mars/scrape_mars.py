from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import requests
import pandas as pd
import pymongo


# Setup connection to mongodb
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)

# Select database
db = client.mars


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    #db.mars.remove()

    news_title, news_paragraph = mars_news()

    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image_url": featured_img(),
        "mars_weather": twitter_weather(),
        "mars_facts": mars_facts(),
        "mars_hemispheres": mars_hems()
    }
    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data


# NASA Mars News
def mars_news():
    browser = init_browser()

    # Visit the NASA Mars news website
    news_url = "https://mars.nasa.gov/news"
    browser.visit(news_url)

    time.sleep(1)

    # Scrape page into Soup
    news_html = browser.html
    news_soup = bs(news_html, "html.parser")

    # Find the title of the latest article
    title = news_soup.find("div", class_="content_title")
    news_title = title.text

    # Find the title of the latest article
    paragraph = news_soup.find("div", class_="article_teaser_body")
    news_p = paragraph.text

    # Close the browser after scraping
    browser.quit()

    # Return results
    return news_title, news_p


# JPL Mars Space Images - Featured Image
def featured_img():
    browser = init_browser()
    
    # Visit the JPL Mars Space Images website
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)

    time.sleep(1)

    # Click through to the featured image
    browser.click_link_by_id("full_image")

    time.sleep(1)

    # Click 'more info' to get to the full size image(s)
    browser.is_element_present_by_text("more info", wait_time=0.5)
    browser.find_link_by_partial_text("more info").click()

    time.sleep(1)

    # Scrape page into Soup
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, "html.parser")

    img = jpl_soup.select_one("figure.lede a img")

    try:
        jpl_img = img["src"]

    except:
        return None

    # Piece together the url for the image with the base url
    featured_image_url = "https://www.jpl.nasa.gov" + jpl_img

    # Close the browser after scraping
    browser.quit()

    # Return results
    return featured_image_url


# Mars Weather
def twitter_weather():
    browser = init_browser()

    # Visit the JPL Mars Space Images website
    weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_url)

    time.sleep(1)

    # Scrape page into Soup
    weather_html = browser.html
    weather_soup = bs(weather_html, "html.parser")

    weather = weather_soup.find('div',{'class':'js-tweet-text-container'}).text.replace("\n"," ").strip()
    mars_weather = weather.split('pic')[0]
    #weather = weather_soup.find("li", {"data-item-type": "tweet"})
    #mars_weather = get_tweet_text(weather)
    #weather = weather_soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
    #mars_weather = weather.text

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_weather


# Mars Facts
def mars_facts():
    browser = init_browser()

    # Visit the Mars Facts website
    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)

    time.sleep(1)

    # Scrape page into Soup
    facts_html = browser.html

    # Read table into Pandas
    df = pd.read_html(facts_html)
    mars_table = df[0]
    mars_table.columns = ["Feature", "Value"]
    mars_table.set_index("Feature", inplace=True)
    mars_table = mars_table.to_html()

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_table


# Mars Hemispheres
def mars_hems():
    browser = init_browser()

    # Visit the USGS Astrogeology website
    hems_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hems_url)

    time.sleep(1)

    # Scrape page into Soup
    hems_html = browser.html
    hems_soup = bs(hems_html, "html.parser")

    # find the hemisphere blurbs
    blurbs = hems_soup.find_all('div', class_='description')[:4]

    mars_hemispheres = []

    for blurb in blurbs:
        img = {}
        href = blurb.h3.text
        browser.click_link_by_partial_text(href)
        hems_html = browser.html
        hems_soup = bs(hems_html, "html.parser")
        img['title'] = href
        img['img_url'] = hems_soup.find('a', target='_blank')['href']
        mars_hemispheres.append(img)
        browser.back()

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_hemispheres







