# You-re-So-Special

你好特别——一个自动化微博监控机器人

使用[钉钉机器人](https://github.com/zhuifengshen/DingtalkChatbot)webhook实现自动信息推送

## 使用方法

1.   `git clone https://github.com/b3nguang/You-re-So-Special.git`
2.   `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
3.   修改`main.py`里的webhook和secret，在`inc/WeiboMonitor.py`里添加uid
4.   `python3 main.py`
5.   自行添加宝塔定时任务
