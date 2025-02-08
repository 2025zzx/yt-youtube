import browsercookie
import browser_cookie3
#
#
cookies = browser_cookie3.chrome(domain_name='.youtube.com')

# 打印 YouTube cookies
for cookie in cookies:
    if "youtube.com" in cookie.domain:
        print(f'{cookie.name}={cookie.value}')
# import browsercookie
#
# # 获取 Chrome 的 cookies
# cookies = browsercookie.chrome()
#
# # 打印 YouTube cookies
# for cookie in cookies:
#     if "youtube.com" in cookie.domain:
#         print(f'{cookie.name}={cookie.value}')