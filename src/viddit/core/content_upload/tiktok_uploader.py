import requests


def upload_to_tiktok(access_token, open_id, video_path):
    url = f"https://open-api.tiktok.com/share/video/upload/?access_token={access_token}&open_id={open_id}"

    with open(video_path, "rb") as video_file:
        files = {"video": video_file}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        json_response = response.json()
        if json_response["data"]["error_code"] == 0:
            print("Video uploaded successfully.")
            return json_response["data"]["share_id"]
        else:
            print("Error uploading video:", json_response["data"]["error_msg"])
            return None
    else:
        print("Request failed with status code:", response.status_code)
        return None
