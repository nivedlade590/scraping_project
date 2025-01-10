import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import pymongo
import requests
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

# MongoDB connection setup
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "twitter_trends"
COLLECTION_NAME = "trending_topics"

# ProxyMesh configuration
PROXY_URL = "http://cs18b024:Niv$45D5*de@https://proxymesh.com/account/proxy_status/us-ca/"

def get_public_ip():
    """Fetch the public IP address."""
    response = requests.get("http://api.ipify.org?format=json")
    return response.json()["ip"]

def configure_driver(proxy_url):
    """Configure Selenium WebDriver to use ProxyMesh."""
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = proxy_url
    proxy.ssl_proxy = proxy_url

    edge_options = Options()
    edge_options.Proxy = proxy
    edge_options.add_argument('--ignore-certificate-errors')

    service = Service("msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

def fetch_trending_topics(driver):
    """Fetch top 5 trending topics."""
    driver.get("https://x.com/home")
    time.sleep(5)

    trending_topics = []
    trending_section = driver.find_element(By.XPATH, "//div[@aria-label='Timeline: Trending now']")
    trending_elements = trending_section.find_elements(By.XPATH, ".//span")

    trending_topics = [topic.text for topic in trending_elements[:5]]
    driver.quit()
    return trending_topics

def store_results_in_mongodb(unique_id, topics, ip_address):
    """Store data in MongoDB."""
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    document = {
        "unique_id": unique_id,
        "trend1": trending_topics[0] if len(trending_topics) > 0 else None,
        "trend2": trending_topics[1] if len(trending_topics) > 1 else None,
        "trend3": trending_topics[2] if len(trending_topics) > 2 else None,
        "trend4": trending_topics[3] if len(trending_topics) > 3 else None,
        "trend5": trending_topics[4] if len(trending_topics) > 4 else None,
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address": ip_address
    }
    

    collection.insert_one(document)
    return document

@app.route("/run-script", methods=["GET"])
def run_script():
    """Run the Selenium script and return results as JSON."""
    print("hello!!  I'm under the water")
    unique_id = str(uuid.uuid4())
    ip_address = get_public_ip()
    driver = configure_driver(PROXY_URL)
    trending_topics = fetch_trending_topics(driver)
    result = store_results_in_mongodb(unique_id, trending_topics, ip_address)
    #result = store_results_in_mongodb(1,2,3)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
