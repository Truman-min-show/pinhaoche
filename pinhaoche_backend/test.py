from ride.models import User
user_id = 3  # 替换为 Token 中的 user_id
try:
    user = User.objects.get(id=user_id)
    print(f"用户存在：{user.username}, 状态：{user.status}")
except User.DoesNotExist:
    print("用户不存在！")