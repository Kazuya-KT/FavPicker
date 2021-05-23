# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ratelimit.decorators import ratelimit
from social_django.models import UserSocialAuth
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
import boto3
import botocore
import json

from .forms import InputCount
from .getimage import dl_main_fanc
from .lamb_fanc import lambda_invoke

@login_required(login_url="/")
def main_page(request):
    user = UserSocialAuth.objects.get(user_id=request.user.id)
    count = InputCount
    return render(request,'favpicker/main.html',{'user': user, "count": count})


@ratelimit(key="ip", rate="50/m")
def pic_dl(request):
    if request.method == "POST":
        #受け取ったPOSTデータを渡す
        form = InputCount(data=request.POST) 
        #is_validで整合性確認
        if form.is_valid(): 
            #dl_resultで必要な情報を変数に格納
            user_id_val = request.POST["user_id"] 
            auth_time_val = int(request.POST["auth_time"])
            count_val = int(request.POST["count"]) 
            auth_data = UserSocialAuth.objects.get(uid=user_id_val)
            #s3にuser_id_valと同じ名前のバケットを作成
            s3 = boto3.resource("s3")
            bucket = s3.Bucket(user_id_val)
            try: #S3ucketの存在確認
                s3.meta.client.head_bucket(Bucket=user_id_val)
            except botocore.exceptions.ClientError:
                bucket.create(
                    #S3バケットの場所がアジアパシフィック（東京）でないとこの後のlambdaがアクセス出来ない
                    CreateBucketConfiguration={
                        'LocationConstraint':'ap-northeast-1'
                    }
                )
            if auth_data.extra_data["auth_time"] == auth_time_val:
                #dl_list_fancに変更予定
                dl_result = dl_main_fanc(
                count_val, 
                auth_data.access_token["oauth_token"], 
                auth_data.access_token["oauth_token_secret"], 
                user_id_val
                )
                #DL成功したときはページ遷移なしにする
                if dl_result == 200:                    
                    if lambda_invoke(user_id_val)["StatusCode"] == 200:
                        messages.success(request, 'データ取得成功')
                        s3_url = boto3.client("s3").generate_presigned_url(
                            "get_object",
                            Params={
                                "Bucket":"zipdatabucketfavpicker01",
                                "Key":user_id_val + ".zip"
                            }
                        )
                        
                        return render(request, "favpicker/dl_page.html", {
                            "s3_url" : s3_url
                        })
                    else: 
                        messages.error(request, "データ取得エラー")
                        return render(request, "favpicker/dl_page.html", {
                            "s3_url" : None
                        })
                elif dl_result == 404:
                    messages.error(request, "DL可能なツイートが存在しません")
                    return render(request, "favpicker/dl_page.html", {"s3_url" : None})
                elif dl_result == 401:
                    messages.error(request, "ユーザーが存在しないかAPIの回数制限に抵触しています")
                    return render(request, "favpicker/dl_page.html", {"s3_url" : None})
                else:
                    messages.error(request, "不明なエラーが発生しました")
                    return render(request, "favpicker/dl_page.html", {"s3_url" : None})
        else:
            form = InputCount()
            messages.error(request, "エラーが発生しました。入力内容を確認してください。")
            return render(request, "favpicker/main.html", {})



