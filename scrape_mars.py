from bs4 import BeautifulSoup
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import pandas as pd

def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()
    data = {}

    # parsing mars news
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find_all("li", class_="slide")
    latest_title = results[0].find('h3').text
    latest_para = results[0].find("div", class_="rollover_description_inner").text
    data["latest_title"] = latest_title
    data["latest_para"] = latest_para

    # parsing main image
    url_JPL_Mars = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_JPL_Mars)
    html_JPL_Mars = browser.html
    soup_JPL_Mars = BeautifulSoup(html_JPL_Mars, 'html.parser')
    featured_image_text = soup_JPL_Mars.find('div', class_="carousel_items").find('article')['style']
    featured_image_url = featured_image_text[featured_image_text.find('url')+5:-3]
    featured_image_url = "https://www.jpl.nasa.gov"+featured_image_url
    data["featured_image_url"] = featured_image_url

    #parsing latest tweet
    url_twit_Mars = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url_twit_Mars)
    html_twit_Mars = browser.html
    soup_twit_Mars = BeautifulSoup(html_twit_Mars, 'html.parser')
    mars_weather = soup_twit_Mars.find_all("div", class_="tweet")[0].find('p', class_="TweetTextSize").text
    data["mars_weather"] = mars_weather

    #parsing hemisphere images
    url_mars_hemi = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_mars_hemi)
    html_mars_hemi = browser.html
    soup_mars_hemi = BeautifulSoup(html_mars_hemi, 'html.parser')
    images_link = soup_mars_hemi.find_all('a', class_="itemLink")
    images_text = []
    for image_link in images_link:
        if image_link.find('h3') != None:
            images_text.append(image_link.find('h3').text)

    hemisphere_image_urls = []
    try:
        for text in images_text:
            image_dict = {}
            print(text)
            browser.find_by_text(text).click()
            inner_page = browser.html
            soup_inner_page = BeautifulSoup(inner_page, 'html.parser')
            image_dict['title'] = text.replace("Enhanced", "")
            image_dict['img_url'] = soup_inner_page.find('div', class_="downloads").find('a')['href']
            hemisphere_image_urls.append(image_dict)
            browser.find_by_text("Back").click()
    except ElementDoesNotExist:
        print("Scraping Complete")
    data["hemisphere_image_urls"] = hemisphere_image_urls

    # Mars facts
    url_mars_facts = "https://space-facts.com/mars/"
    tables = pd.read_html(url_mars_facts)
    mars_df = tables[0]
    mars_df = mars_df.rename(columns={0: "Description", 1:"Value"})
    mars_df_html = mars_df.to_html(index=False, justify="justify-all", border=2)
    data["facts"] = mars_df_html
    
    return data
