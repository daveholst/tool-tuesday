import json
from get_tool_music_videos import *


def handler(event, context):
    video_result = get_random_tool_video
    if video_result:
        return {"statusCode": 200, "body": json.dumps(video_result)}
    else:
        return {"statusCode": 500, "body": json.dumps("Something Went Wrong")}
