# coding: utf-8
# 每天定时爬起知乎信息, 发邮件提醒
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from qq_email import send
import auto_dama

# 自动处理cookies
session = requests.session()


header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
}

def get_pic():
    """获取验证图片的json结果"""
    times = str(int(time.time()*1000))
    pic_url = 'https://www.zhihu.com/captcha.gif?r={}&type=login&lang=en'.format(times)
    try:
        r = session.get(pic_url, headers=header)
    except Exception:
        print('获取验证图片发生错误')
    with open('pic.jpg', 'wb') as f:
        f.write(r.content)
    print('传入验证码...')
    verifying = auto_dama.auto_verification()
    print('获取验证码...')
    return verifying

def get_index_content(html):
    """获取初始页面话题回答, 用户, 点赞数, 评论数, session_token"""
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find_all('div', class_="Card TopstoryItem")
    info = []
    comment_nums = 0
    for i in div:
        name = i.find_all('a', class_="UserLink-link")
        if name:
            name = name[-1].string
        else:
            name = '匿名用户'
        title = i.find('h2', class_="ContentItem-title")
        if title:
            # 避免广告
            title_url = 'https://www.zhihu.com' + title.find('a').attrs['href']
            title = title.get_text()
            comment_nums = i.find('button',
                                  class_="Button ContentItem-action Button--plain Button--withIcon Button--withLabel")
            if comment_nums:
                comment_nums = comment_nums.get_text()
            else:
                comment_nums = False
        else:
            title = '广告'
        content = i.find('span', class_="RichText CopyrightRichText-richText")
        if content:
            content = content.get_text()
        agree = i.find('button', class_="Button VoteButton VoteButton--up")
        if agree:
            agree = agree.get_text()
        else:
            agree = i.find('button', class_="Button LikeButton ContentItem-action")
            if agree:
                agree = agree.get_text()
        if title != '广告' and comment_nums:
            info.append({'name': name, 'title': title, 'content': content,
                         'agree': agree, 'comment_nums': comment_nums, 'title_url': title_url})
    with open('content.txt', 'w') as f:
        for i in info:
            f.write('用户:{}\n{}\t{}\n{}\n赞:{}\t{}\n\n'.format(
                i['name'], i['title'], i['title_url'], i['content'],
                i['agree'], i['comment_nums'].replace(' ', '')))

def get_content(html):
    """获取抓包数据"""
    try:
        content_text = json.loads(html)['data']
        with open('content.txt', 'a') as f:
            for i in content_text:
                try:
                    update_time = i['updated_time']
                    timestamp = int(update_time)
                    time_local = time.localtime(timestamp)
                    dt = time.strftime("%Y-%m-%d", time_local)
                    if time.strftime("%Y-%m-%d") == dt:
                        action_name = i['action_name']
                        if 'comment' in i:
                            name = i['target']['author']['name']
                            question = i['target']['question']['title']
                            comment_id = i['comment']['id']
                            question_id = i['target']['question']['id']
                            target_id = i['target']['id']
                            comment_url = 'https://www.zhihu.com/question/{}/answer/{}#comment-{}'.format(question_id, target_id, comment_id)
                            f.write('{}评论了{}\n{}\n\n'.format(name, question, comment_url))
                        elif action_name in ['QUESTION_AUTO_ASK_PEOPLE_ANSWER', 'QUESTION_ZHIHU_ASK_PEOPLE_ANSWER']:
                            name = i['operators'][0]['name']
                            title = i['target']['title']
                            title_url = 'http://www.zhihu.com/question/' + i['target']['url'].split('/')[-1]
                            f.write('{}的提问等你来答{}\n{}\n\n'.format(name, title, title_url))
                        else:
                            name = i['target']['author']['name']
                            title = i['target']['title']
                            title_url = i['target']['url']
                            f.write('{}发布了{} {}\n\n'.format(name, title, title_url))
                except Exception:
                    print('解析数据包发生错误')
    except:
        pass

def start():
    verifying_dic = get_pic()
    postdata = {
        'password': '********',
        'captcha': verifying_dic,
        'captcha_type': 'en',
        'phone_num': '*********'
    }
    # 登录
    res = session.post('https://www.zhihu.com/login/phone_num', data=postdata, headers=header)
    print(json.loads(res.text))

    #获取出页面更新内容
    r = session.get('https://www.zhihu.com/', headers=header)
    # print(r.text)
    get_index_content(r.text)
    #获取提醒情况信息
    remind_url = 'https://www.zhihu.com/api/v4/default-notifications?include=data[?(target.type=roundtable)].question,answer;data[?(target.type=answer)].vote_count,thank_count,target.admin_closed_comment.question;data[?(target.type=question)].answer,target.admin_closed_comment;data[?(target.type=article)].column,target.admin_closed_comment;data[?(target.type=ebook)].target.ebook_type;data[*].operators[*].badge[?(type=best_answerer)].topics;data[?(comment)].target.can_comment,comment_permission,author,relationship.is_author'
    r = session.get(remind_url, headers=header)
    get_content(r.text)
    # 发送邮件
    # send()
    # 测试dev分支,第二次测试
    # 测试dev-issue-01分支

start()
