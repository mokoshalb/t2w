import requests
import json
import re
import urllib.parse
import os

GUEST_TOKEN_ENDPOINT = "https://api.twitter.com/1.1/guest/activate.json"
STATUS_ENDPOINT = "https://twitter.com/i/api/graphql/"
QUOTED_VALUE = re.compile("[\"']([^\"']+)[\"']")
MP4_PART = re.compile("/.+\.mp4|/.+m4s$")
VIDEO_BASE = "https://video.twimg.com"
CONTAINER_PATTERN = re.compile("['\"](http[^'\"]+&container=fmp4)")
MISSING_VARIABLE_PATTERN = re.compile("Query violation: Variable '([^']+)'")
MISSING_FEATURE_PATTERN = re.compile("The following features cannot be null: ([a-zA-Z_0-9, ]+)")
RETRY_COUNT = 5

def send_request(url, session_method, headers):
    response = session_method(url, headers=headers, stream=True)
    response_json = ""
    try:
        response_json = response.json()
    except:
        response_json = "Failed to parse json from response."
    assert response.status_code == 200, f"Failed request to {url}.  {response.status_code} {response_json}.  Please submit an issue including this information."
    result = [line.decode("utf-8") for line in response.iter_lines()]
    return "".join(result)


def exploratory_request(url, method, headers, video_id):
    folder = os.path.dirname(__file__)
    request_details_file = os.path.join(folder, "RequestDetails.json")
    with open(request_details_file, "r") as f:
        request_details = json.load(f)
    json_features = request_details["features"]
    json_variables = request_details["variables"]
    features = urllib.parse.quote_plus(json.dumps(json_features, separators=(',', ':')))
    json_variables["focalTweetId"] = video_id
    variables = urllib.parse.quote_plus(json.dumps(json_variables, separators=(',', ':')))
    status_params = f"TweetDetail?variables={variables}&features={features}"
    response = method(url + status_params, headers=headers)
    result = "".join([line.decode("utf-8") for line in response.iter_lines()])
    if response.status_code == 200:
        return result
    for _ in range(RETRY_COUNT):
        missing_vaiables = MISSING_VARIABLE_PATTERN.findall(result)
        missing_features = MISSING_FEATURE_PATTERN.findall(result)
        if missing_features:
            missing_features = missing_features[0].split(", ")
        if missing_vaiables or missing_features:
            for variable in missing_vaiables:
                json_variables[variable] = True
            for feature in missing_features:
                json_features[feature] = True
            features = urllib.parse.quote_plus(json.dumps(json_features, separators=(',', ':')))
            variables = urllib.parse.quote_plus(json.dumps(json_variables, separators=(',', ':')))
            status_params = f"TweetDetail?variables={variables}&features={features}"
            response = method(url + status_params, headers=headers)
            result = "".join([line.decode("utf-8") for line in response.iter_lines()])
            if response.status_code == 200:
                # save the updated variables and features
                with open(request_details_file, "w") as f:
                    del json_variables["focalTweetId"]
                    json.dump({"features": json_features, "variables": json_variables}, f, indent=4)
                print(f"Success on {_} try")
                break
    return result

def search_json(j, target_key, result):
    if type(j) == dict:
        for key, value in j.items():
            if key == target_key:
                if type(value) == list:
                    result.extend(value)
                else:
                    result.append(value)
            search_json(value, target_key, result)
    if type(j) == list:
        for item in j:
            search_json(item, target_key, result)
    return result

def get_video(video_url):
    video_ids = re.findall("status/([0-9]+)", video_url)
    assert len(video_ids) == 1, f"Did not understand your twitter URL.  Example: https://twitter.com/james_a_rob/status/1451958941886435329"
    video_id = video_ids[0]
    with requests.Session() as session:
        headers = {}
        container = send_request(video_url, session.get, headers)
        js_files = re.findall("src=['\"]([^'\"()]*js)['\"]", container)
        bearer_token = None
        query_id = None
        for f in js_files:
            file_content = send_request(f, session.get, headers)
            bt = re.search(
                '["\'](AAA[a-zA-Z0-9%-]+%[a-zA-Z0-9%-]+)["\']', file_content)
            ops = re.findall('\{queryId:"[a-zA-Z0-9_]+[^\}]+"', file_content)
            query_op = [op for op in ops if "TweetDetail" in op]
            if len(query_op) == 1:
                query_id = re.findall('queryId:"([^"]+)"', query_op[0])[0]
            if bt:
                bearer_token = bt.group(1)
        assert bearer_token, f"Did not find bearer token.  Are you sure you used the right URL? {video_url}"
        assert query_id, f"Did not find query id.  Are you sure you used the right twitter URL? {video_url}"
        headers['authorization'] = f"Bearer {bearer_token}"
        guest_token_resp = send_request(GUEST_TOKEN_ENDPOINT, session.post, headers)
        guest_token = json.loads(guest_token_resp)['guest_token']
        assert guest_token, f"Did not find guest token. Probably means the script is broken. Please submit an issue. Include this message in your issue: {video_url}"
        headers['x-guest-token'] = guest_token
        status_resp = exploratory_request(f"{STATUS_ENDPOINT}{query_id}/", session.get, headers, video_id)
        status_json = json.loads(status_resp)
        legacies = search_json(status_json, "legacy", [])
        legacy = [l for l in legacies if "id_str" in l and l["id_str"] == video_id]
        assert legacy and len(legacy) == 1, f"Did not find video. Please confirm you are using the correct link. If your link is correct please report this as an issue including this message. {video_url}"
        legacy = legacy[0]
        variants = search_json(legacy, "variants", [])
        variants = [v for v in variants if 'bitrate' in v]
        if variants:
            variants.sort(key=lambda x: x['bitrate'], reverse=True)
            variant = variants[0]
            return variant["url"]
        else:
            print("Some tweets have a legacy format that this handles")
            return ""
