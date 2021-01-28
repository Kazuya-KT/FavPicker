# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ratelimit.decorators import ratelimit
from social_django.models import UserSocialAuth
from django.http import HttpResponse

from .forms import InputCount
from .getimage import dl_main_fanc


@login_required
def main_page(request):
    user = UserSocialAuth.objects.get(user_id=request.user.id)
    count = InputCount
    return render(request,'favpicker/main.html',{'user': user, "count": count})

@login_required
@ratelimit(key="ip", rate="50/m")
def pic_dl(request):
    if request.method == "POST":
        form = InputCount(data=request.POST) #受け取ったPOSTデータを渡す
        if form.is_valid(): #is_validで整合性確認
            user_id_val = request.POST["user_id"]
            auth_time_val = int(request.POST["auth_time"])
            count_val = int(request.POST["count"]) 
            auth_data = UserSocialAuth.objects.get(uid=user_id_val)
            if auth_data.extra_data["auth_time"] == auth_time_val:
                dl_result = dl_main_fanc(
                count_val, 
                auth_data.access_token["oauth_token"], 
                auth_data.access_token["oauth_token_secret"], 
                user_id_val
                )
                #以下はブラウザ上で表示されるように変更予定
                #DL成功したときはページ遷移なしにする
                if dl_result == 200:
                    return HttpResponse("TEST")
                elif dl_result == 404:
                    return HttpResponse(f"Failed:{dl_result}：DL可能なツイートが存在しません")
                elif dl_result == 401:
                    return HttpResponse(f"Failed:{dl_result}：ユーザーが存在しないかAPIの回数制限に抵触しています")
                else:
                    return HttpResponse(f"Failed:{dl_result}：エラーが発生しました")
        else:
            #ここも変更する
            form = InputCount()
        return HttpResponse("エラーが発生しました")
