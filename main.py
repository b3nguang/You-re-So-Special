import logging
import os
from typing import Dict, Optional

from dingtalkchatbot.chatbot import DingtalkChatbot
from inc import WeiboMonitor, output

# 设置日志配置
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 钉钉机器人Webhook地址和加签密钥
webhook: str = os.environ["webhook"]
secret: str = os.environ["secret"]

def dingding(content: str, webhook: Optional[str] = webhook, secret: Optional[str] = secret) -> None:
    """
    发送钉钉通知的函数。
    
    参数:
    - content: 要发送的内容（str类型）
    - webhook: 钉钉机器人的Webhook地址（可选，默认为全局变量webhook，str类型）
    - secret: 钉钉机器人加签密钥（可选，默认为全局变量secret，str类型）
    
    返回值:
    无
    """
    try:
        xiaoding = DingtalkChatbot(webhook, secret=secret)
        xiaoding.send_text(msg=content)
    except Exception as e:
        logging.info(f"发送钉钉通知失败: {e}")

def weiboSender(dicts: Dict[str, any]) -> bool:
    """
    处理微博信息并发送通知的函数。
    
    参数:
    - dicts: 包含微博信息的字典
    
    返回值:
    - flag: 布尔值，表示处理微博信息并发送通知是否成功
    """
    flag: bool = True
    try:
        logging.debug(dicts)
        content: str = f"{dicts['nick_name']}发布新微博！\n发送时间：{dicts['created_at']}\n发送内容：{dicts['text']}\n"
        dingding(content)
    except Exception as e:
        logging.debug(f"处理微博信息失败: {e}")
        flag = False
    return flag

def read_file(file_path: str) -> Optional[str]:
    """
    安全读取文件的函数。
    
    参数:
    - file_path: 文件路径（str类型）
    
    返回值:
    - 文件内容（字符串），如果读取失败则返回None
    """
    if not os.path.exists(file_path):
        open(file_path, 'w').close()  # 创建并关闭文件以确保存在

    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logging.debug(f"文件 {file_path} 未找到。")
        return None
    except IOError as e:
        logging.debug(f"读取文件 {file_path} 失败: {e}")
        return None

def main() -> None:
    # 输出logo
    logging.info(output.logo())
    # 初始化微博监控
    weibo = WeiboMonitor.WeiboMonitor()
    weibo.get_weibo_info()
    # 读取微博ID文件
    text = read_file('weiboID.txt')
    if text is None:
        return
    # 如果文件为空，则获取新的微博ID
    if text == '':
        weibo.get_wb_queue()
    # 开始监控微博
    newWB: Optional[Dict[str, any]] = weibo.start_monitor()
    # logging.debug(newWB)
    if newWB is not None:
        if weiboSender(newWB):  # 发送钉钉通知成功则输出True
            logging.info('微博信息已发送')
        else:
            logging.info('微博信息发送失败')

if __name__ == '__main__':
    main()