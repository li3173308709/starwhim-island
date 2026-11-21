#!/usr/bin/env python3
"""Additional Chinese teaching narration in the exact reference girl's voice.

The 400 character / English word clips remain owned by voice-learning-v22-plan.json.
This plan adds native Chinese meanings and reusable UI dialogue, never Latin
pinyin or device speech.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parent.parent
src=(ROOT/'scripts/learning_v22.js').read_text(encoding='utf-8')
m=re.search(r'\bconst WORDS=(\[.*?\]);',src,re.S)
if not m:raise RuntimeError('English learning dataset missing')
words=json.loads(m.group(1))
assert len(words)==200
rows=[]
used=set()
def add(key,text,context):
    text=text.strip()
    if key in used or not text or not re.search('[\u4e00-\u9fff]',text):return
    used.add(key)
    uid='cn'+hashlib.sha256(key.encode()).hexdigest()[:18]
    rows.append(dict(id=uid,role='narrator',key=key,text=text,context=context,
                     voice_name='活泼女孩参考音色',provider='F5-TTS'))
for w in words:
    add('cn:meaning:'+w['en'],f"中文意思是：{w['zh']}。",'英语图卡中文释义')

for topic in sorted({w['cat'] for w in words}):
    spoken=re.sub(r'[^\u4e00-\u9fff]','',topic)
    add('cn:topic:'+topic, '这里是'+spoken+'主题，一起认识新单词吧！','英语主题名称')

# Simple recorded sentences can be reused on many cards. Variable word meanings
# use their own keyed voice clip, rather than guessing a dynamic TTS voice.
phrases=[
('home','丁一一，我们先认识每个单词的图片、英文和中文。看图理解意思，再听英文发音，然后和小精灵一起闯关。'),
('five','每次认识五个新单词，学完以后再玩小游戏。'),
('choose','选择你喜欢的童话主题。'),
('teaching','今天我们认识一个新的单词朋友。看一看图片，听一听英文，记住中文意思。'),
('learn-more','先学单词，再开启游戏。'),
('unlock','再认识几个单词，就可以解锁新的挑战啦。'),
('learned','你已经认识不少单词朋友了，真棒！'),
('review','我们一起复习刚刚学过的五个单词。'),
('card-next','如果记住这个单词，就点击下一张图卡吧。'),
('practice','刚刚认识的单词，现在可以玩一个轻松的小考验啦。'),
('practice-wrong','再试一次。看一看图片，想想它的中文意思。'),
('practice-right','答对啦！你真是一个聪明的小探险家！'),
('quiz-picture','请仔细看看图片，选出对应的英文单词。'),
('quiz-listen','请听一听英文发音，再找到正确的图片。'),
('quiz-spell','把刚刚学过的单词按顺序拼出来。'),
('quiz-memory','找到英文和图片这一对好朋友。'),
('quiz-next','太棒了，准备挑战下一关！'),
('quiz-end','恭喜你完成了五个关卡，继续探索更多单词吧！'),
('quiz-help','如果不确定，可以再听一次发音，慢慢思考。'),
('quiz-stars','小精灵送来了星星！每一次练习都让你更进步。'),
('quiz-locked','先学会这些单词，才能打开新关卡哦。'),
('review-none','你还没有学过这个主题的单词，我们先从第一张图卡开始吧。'),
('topic-done','这个主题的单词都学过啦，可以换一个主题或者继续复习。'),
('hanzi-home','欢迎来到汉字寻宝乐园，这里有两百个汉字，先认识汉字和例词，再完成有趣的挑战。'),
('hanzi-lesson','看看这个汉字和图画，注意拼音的声调，点听一听学习正确的普通话读音。'),
('hanzi-picture','看看图画，选出对应的汉字。'),
('hanzi-pinyin','观察拼音和声调，找到正确的汉字。'),
('hanzi-word','给词语补上缺少的那个汉字。'),
('hanzi-review','复习之前做错的汉字，一点一点记住它们。'),
('hanzi-right','回答正确，真棒！我们又认识了一个汉字朋友。'),
('hanzi-wrong','没关系，再观察一下汉字和图画，慢慢来。'),
('hanzi-done','本轮识字挑战结束了，继续认识更多汉字吧。'),
('generic-home','点击学习，先认识新知识，然后再进入游戏。'),
('generic-choose','请选一个喜欢的选项。'),
('generic-back','点击返回，回到学习主题。'),
('generic-next','点击下一张，认识新的朋友。'),
('generic-listen','点击喇叭，听活泼女孩给你讲一讲。'),
('generic-reward','完成挑战了！今天你又学到了新本领。'),
('generic-stars','小星星奖励已经送给你了！'),
('generic-progress','这是你当前的学习进度。'),
('generic-card','这是一个学习图卡。先看一看，再点击听一听。'),
('generic-title','你可以选择听这个页面上的中文说明。'),
]
for key,text in phrases:
    add('cn:ui:'+key,text,'学习页面中文说明')

# Include actual static Chinese button labels in the same voice.
def only_hanzi(t):
    return re.sub(r'[^\u4e00-\u9fff]','',t)
for label in re.findall(r"\b(?:b|btn)\(\s*'([^']*)'",src):
    spoken=only_hanzi(label)
    if spoken:
        add('cn:button:'+spoken,spoken+'。','中文按钮标签')
for label in re.findall(r'<h[234][^>]*>([^<]+)</h[234]>',src):
    spoken=only_hanzi(label)
    if len(spoken)>1:
        add('cn:line:'+spoken,spoken+'。','静态中文标题')
assert len(rows)>=200+20+35, len(rows)
p=ROOT/'voice-learning-ui-v23-plan.json'
p.write_text(json.dumps(dict(version=23,count=len(rows),lines=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Prepared {len(rows)} Chinese teaching narration clips:')
print('  200 English meanings,',len({x['cat'] for x in words}),'topic introductions,',len(phrases),'reusable voice instructions')
