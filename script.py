from playwright.sync_api import sync_playwright
import json
import re
import requests
import os

#url = "https://www.threads.net/t/CuXFPIeLLod"

url= input("Insert here the url of the thread: ")
link_pattern = re.compile(r"https://www\.threads\.net/api/graphql")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    graph_responses = []

    def capture_response(response):
        if link_pattern.match(response.url):
            print( response.status, response.url)
            graph_responses.append({
                "status": response.status,
                "url": response.url,
                "content": response.text(),
            })

    page.on("response", capture_response)
    page.goto(url, wait_until="networkidle", timeout=90000)
    page.context.close()
    browser.close()
    content = json.loads(graph_responses[0]['content'])
    #print(content)
    with open("content.json", "w", encoding='utf8') as file:
        json.dump(content, file, indent=4, ensure_ascii=False)


links = []
links_video = []
thread_items = content["data"]["data"]["containing_thread"]["thread_items"]
for item in thread_items:
    post = item["post"]
    if "image_versions2" in post:
        candidates = post["image_versions2"]["candidates"]
        candidate= max(candidates, key=lambda x: x["width"])
        url = candidate["url"]
        links.append(url)

for item in thread_items:
    post = item["post"]
    if "video_versions" in post:
        video_candidates = post["video_versions"]
        video_candidate= min(video_candidates, key=lambda y: y["type"])
        url = video_candidate["url"]
        links_video.append(url)

#get for images links
for i, link in enumerate(links, start=1):
    response = requests.get(link)
    if response.status_code == 200: 
        file_name = f"image_{i}.jpg"
        file_path = os.path.join("./", file_name)
        with open(file_path, "wb") as file:
                file.write(response.content)
        print(f"Downloaded {file_name} and saved to {file_path}")
    else:
        print(f"Failed to download image: {link}")

#get for video links
for i, link in enumerate(links_video, start=1):
    response = requests.get(link)
    if response.status_code == 200: 
        file_name = f"video_{i}.mp4"
        file_path = os.path.join("./", file_name)
        with open(file_path, "wb") as file:
                file.write(response.content)
        print(f"Downloaded {file_name} and saved to {file_path}")
    else:
        print(f"Failed to download video: {link}")
