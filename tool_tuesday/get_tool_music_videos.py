import urllib.request
import re
import requests
import random
from bs4 import BeautifulSoup

# Helper function to strip innerText from html element
def unwrapper(element):
    inner_text = element.getText(strip=True)
    return inner_text[1:-1]


def get_random_tool_video():

    # Get the released song list from wikipedia
    html = requests.get(
        "https://en.wikipedia.org/wiki/List_of_songs_recorded_by_Tool"
    ).text
    soup = BeautifulSoup(html, "html.parser")
    song_elements = soup.find_all(
        "th", attrs={"scope": "row", "class": "", "style": ""}
    )
    songs = list(map(unwrapper, song_elements))

    # Pick a random song
    random_song = random.choice(songs)
    print(random_song)

    # Search for that song on youtube and get a random video
    video_link_regex = r"watch\?v=(\S{11})"
    html = (
        urllib.request.urlopen(
            "https://www.youtube.com/results?search_query=TOOL+"
            + random_song.replace(" ", "+")
        )
        .read()
        .decode()
    )
    video_ids = re.findall(video_link_regex, html)
    random_video = "https://www.youtube.com/watch?v=" + random.choice(video_ids)
    video_result = {"title": random_song, "video": random_video}
    print(video_result)

    return video_result


get_random_tool_video()
