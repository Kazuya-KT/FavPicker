import boto3
import requests

def dl_images(dl_lists, bucket_path):
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_path)
        for url in dl_url:
            name = url.split("/")
            image_file_path = "./image/" + name[-1]
            movie_file_path = "./movie/" + name[-1]
            if url.endswith(('jpg', 'png')):
                res = requests.get(url + ":orig", stream=True)
                bucket.upload_fileobj(res.raw, image_file_path)
                #print(image_file_path)
            elif url.endswith("mp4"):
                res = requests.get(url, stream=True)
                bucket.upload_fileobj(res.raw, movie_file_path)
                #print(movie_file_path)
            else: #ここに来るのはmp4?tag=10みたいなファイル
                re_name = movie_file_path.split(".")
                rename_movie_file_path = "." + re_name[-2] + ".mp4"
                res = requests.get(url, stream=True)
                bucket.upload_fileobj(res.raw, rename_movie_file_path)
                #print(rename_movie_file_path)
        return 200
    except TypeError as e:
        print("TypeError:", e)
        sys.exit()
        return 401