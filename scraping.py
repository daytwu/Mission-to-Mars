# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
    
driver_loc = r'C:\Users\daytw\.wdm\drivers\chromedriver\win32\87.0.4280.88\chromedriver.exe'

def scrape_all():
    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': driver_loc}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'last_modified': dt.datetime.now(),
        'hemispheres': hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    #Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

### JPL Space Images Featured Image

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url


def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    hemi_titles = hemi_soup.find_all('h3')
    hemi_titles = [hemi.text for hemi in hemi_titles]
    site = 'https://astrogeology.usgs.gov'

    hemi_meta = hemi_soup.find_all('div', class_='item')

    for i in range(len(hemi_meta)):
        browser.visit(f"{site}{hemi_meta[i].find('a')['href']}")
        
        html = browser.html
        hem_meta_soup = soup(html, 'html.parser')

        hem_url = hem_meta_soup.find('div', class_='downloads')
        hemi_value = hem_url.find('a')['href']
        hemisphere_image_urls.append({'image_url': hemi_value,
                                    'title': hemi_titles[i]})


    return hemisphere_image_urls


if __name__ == '__main__':

    # If running as script, print scraped data
    print(scrape_all())


