import os
import requests
import json
#from db_handler import Database


def get_slack_hook_url(value):
    query = f"""
        select [Value]
        from key_collection
        where [Key] = 'slackLogger'
    """

    urls = eval(Database.execute_list(query=query, name='ml_live_select')[0]['Value'])
    return urls[f"{value}"]


def slack(channel_name, msg, detail, **kargs):
    cwd = os.getcwd().replace('\\', '/')
    slack_webhook_url = get_slack_hook_url(f"{channel_name}")
    data = {"blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"At project \"midi-deamon/youtube-playlist\", error has occurred."
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Args: {kargs}\n*Error Message*\n{msg}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Detail*\n```{detail}```"
            }
        }
    ]}
    requests.post(slack_webhook_url, data=json.dumps(data))

def slack_result(channel_name:str, msg:str, p_fail_list:list):
    cwd = os.getcwd().replace('\\', '/')
    slack_webhook_url = get_slack_hook_url(channel_name)
    data = {"blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"\"midi-deamon/{cwd.split('/')[-1]}\" 실행 결과"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*검색 실패 UPC*\n```{str(p_fail_list)}```"
            }
        }
    ]}
    requests.post(slack_webhook_url, data=json.dumps(data))