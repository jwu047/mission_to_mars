# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

# From Jupyter notebook
def scrape_all():

    # Initiate headless driver for deployment, change chromedriver path as needed
    browser = Browser("chrome", executable_path="C:/bin/chromedriver", headless=True)
    # Run mars_news(browser) to return the title and paragraph
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store in dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # local url
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Get first list item and wait if not present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    # Get site's html and parse with bs4
    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        # Find container for information
        list_element = news_soup.find('li', class_='slide')
        # Find title and paragraph
        list_element_title = list_element.find('div', class_='content_title').get_text()
        list_element_paragraph = list_element.find('div', class_='article_teaser_body').get_text()

    # Return None for both variables
    except AttributeError:
        return None, None

    return list_element_title, list_element_paragraph


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    
    # Find and click the full image button
    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()
    # Find and click the more info button
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_button = browser.find_link_by_partial_text("more info")
    more_info_button.click()

    # Get the html and parse
    html = browser.html
    img_soup = BeautifulSoup(html, "html.parser")

    # Find the image url
    img_fig = img_soup.find('figure', class_='lede')
    img = img_fig.find('a').get('href')

    # Get relative link 
    try:
        img_url_rel = img.get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    return img_url


def hemispheres(browser):
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)

    # List to contain image urls
    image_urls = []
    # How many elements are in the page that contain what we want
    links = browser.find_by_css("a.product-item h3")

    # Click the link, find the sample anchor, return the href
    for i in range(len(links)):
        data = {}

        # Index and click
        browser.find_by_css("a.product-item h3")[i].click()

        # Retrieve and append img_url and title
        sample = browser.find_link_by_text('Sample').first
        data['img_url'] = sample['href']
        data['title'] = browser.find_by_css('h2.title').text

        # Append each dictionary data to list
        image_urls.append(data)

        # Goes back and repeats for the loop
        browser.back()

    return image_urls


def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    # Using twitter's tweet attributes, locate tweets made by the user 'MarsWxReport'
    tweet_attrs = {'class': 'tweet', 'data-screen-name': 'MarsWxReport'}
    tweet = weather_soup.find("div", attrs=tweet_attrs)

    # Get tweet content contained in paragraph element
    tweet_text = tweet.find("p", "tweet-text").get_text()

    return tweet_text


def mars_facts():
    try:
        # Currently(12/12/2019), we need the first table, change if necessary
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["Description", "Value"]
    df.set_index("Description", inplace=True)

    # Returns table with bootstrap class styles
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # Print to console for scripts
    print(scrape_all())
