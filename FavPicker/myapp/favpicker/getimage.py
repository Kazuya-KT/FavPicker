import json
import sys
import pprint
import ssl
import urllib.request
import requests
from requests_oauthlib import OAuth1Session  # OAuthのライブラリの読み込み
from . import api_settings  # 認証情報
import boto3

CK = api_settings.CON_KEY
CS = api_settings.CON_SECRET

max_id_value = None
twitter = None
ssl._create_default_https_context = ssl._create_unverified_context

#お気に入り一覧を取得してJSONで返す。返された値はmedia_url()にて処理
#params内の値max_idに指定されたツイートID以降のお気に入りを取得する
def fav_list(count_value, user_id, max_id_value = None):
    url = "https://api.twitter.com/1.1/favorites/list.json?tweet_mode=extended"
    params = {"user_id": user_id, "count": count_value, "max_id": max_id_value}
    get_fav = twitter.get(url, params=params)
    #剪定
    if get_fav.status_code != 200: 
        return get_fav
    else:
        return get_fav

#fav_listにて取得したJSONからメディアURLを含むツイートを抽出する。
#変数"media_info_temp"にリスト形式でURLを追加。
#URLを含まないツイートの場合はリストにHogeを追加。追加せずにスルーする方法があればそちらに変更した方がスマート。
def media_url(res_json):
    r = json.loads(res_json.text)
    media_info_temp = []
    for t in r:
        if "extended_entities" in t:
            media_info = [t["extended_entities"]["media"]]
            media_info_temp.append(media_info)
        else:
            media_info_temp.append("Hoge")
    return media_info_temp

#関数fav_listにて取得したJSONを関数media_urlにてURLを抜き出し、この関数でURLから画像と動画をDLする。
def movie_or_photo(dl_value, user_id, max_id):
    fl_result = fav_list(dl_value, user_id, max_id)
    if fl_result.status_code == 401:
        fl_result_error = 401
        return fl_result_error
    elif fl_result.text == "[]":
        fl_result_error = 404
        return fl_result_error
    urls = []
    get_media_info = media_url(fl_result)
    #ここでループをまわして画像と動画URLを出力
    for m in get_media_info:
        if "Hoge" in m:
            continue
        else:
            if "video_info" in m[0][0]:
                for video in m[0][0]["video_info"]["variants"]:
                    if "bitrate" in video and video["bitrate"] == 2176000:
                        urls.append(video["url"])
                    else:
                        continue
            else:
                for n in m[0]:
                    urls.append(n["media_url_https"])
    if urls == []:
        urls_val = 404
        return urls_val
    id_json = json.loads(fl_result.text)
    print("取得数は", len(id_json), "です", sep="")
    global max_id_value
    max_id_value = id_json[len(id_json) - 1]["id_str"]
    print(max_id_value)
    #pprint.pprint(list(set(urls)))
    return urls

#現在は上部階層の「image」「movie」に保存されるようになっているがS3へバケットを自動生成して保存するように変更する
def dl_images(dl_url, bucket_path):
    try:
        session = boto3.Session()
        s3 = session.resource('s3')
        bucket = s3.Bucket(bucket_path)
        for url in dl_url:
            name = url.split("/")
            image_file_path = "./image/" + name[-1]
            movie_file_path = "./movie/" + name[-1]
            if url.endswith(('jpg', 'png')):
                res = requests.get(url + ":orig", stream=True)
                bucket.upload_fileobj(res.raw, image_file_path)
                print(image_file_path)
            elif url.endswith("mp4"):
                res = requests.get(url, stream=True)
                bucket.upload_fileobj(res.raw, movie_file_path)
                print(movie_file_path)
            else: #ここに来るのはmp4?tag=10みたいなファイル
                re_name = movie_file_path.split(".")
                rename_movie_file_path = "." + re_name[-2] + ".mp4"
                bucket.upload_fileobj(res.raw, rename_movie_file_path)
                print(rename_movie_file_path)
    except TypeError as e:
        print("TypeError:", e)
        sys.exit()

#DLが成功すれば200,画像/で動画が存在しなければ404,APIのLimitに抵触orユーザーが存在しなければ401をView.pyに返す
def dl_main_fanc(count_value, access_token, access_token_seclet, user_id):
    global twitter
    twitter = OAuth1Session(CK, CS, access_token, access_token_seclet, user_id)
    dl_lists = []
    while count_value > 200:
        media_lists = movie_or_photo(200, user_id, max_id_value)
        if media_lists == 404 or media_lists == 401:
            return media_lists
        for l in media_lists:
            dl_lists.append(l)
        count_value -= 200
    else:
        media_lists = movie_or_photo(count_value, user_id, max_id_value)
        if media_lists == 404 or media_lists == 401:
            return media_lists
        for l in media_lists:
            dl_lists.append(l)
    print(dl_lists)
    dl_images(list(set(dl_lists)), user_id)
    media_lists_val = 200
    return media_lists_val
