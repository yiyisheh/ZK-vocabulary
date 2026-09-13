# -*- coding: utf-8 -*-
"""按四级同义辨析 JSON 的格式，生成中考高频词同义辨析.json。
分组、note 与辨析文字为人工撰写；rank/pos/gloss/音标/例句等字段
自动取自 intermediate/entries_full.json。"""
import json, re, sys

ENTRIES = json.load(open('intermediate/entries_full.json', encoding='utf-8'))
BY_WORD = {}
for e in ENTRIES:
    BY_WORD.setdefault(e['word'], []).append(e)

SECTION_FREQ = {1: "真题出现 200 次以上", 2: "真题出现 150 次以上", 3: "真题出现 100 次以上",
                4: "真题出现 50 次以上", 5: "真题出现 30 次以上", 6: "真题出现 10 次以上"}
POS_CN = {"n.": "名词", "v.": "动词", "adj.": "形容词", "adv.": "副词", "vt.": "及物动词",
          "vi.": "不及物动词", "conj.": "连词", "prep.": "介词", "pron.": "代词",
          "aux.": "助动词", "n./v.": "名词/动词"}

def extract_pos(defi):
    tags = re.findall(r'(?:^|(?<=\. ))([a-z]+\.|n\./v\.)', defi)
    out = []
    for t in tags:
        if t not in out:
            out.append(t)
    return out

GROUPS = []  # (topic, [(word, rank_or_None, note)], usage, colloc, summary)
def G(topic, members, usage, colloc, summary):
    GROUPS.append((topic, members, usage, colloc, summary))

# ---------- 分组数据 ----------
G("制作与创造", [("make",None,""),("create",None,""),("produce",None,""),("invent",None,""),("invention",None,"invent 的名词"),("discovery",None,""),("pioneer",None,"")],
  "make 最通用，指制造、做；create 强调从无到有的创造；produce 侧重生产、制造（尤指批量或自然产生）；invent 指发明前所未有的东西，invention 是其名词；discovery 指发现已存在的事物；pioneer 指开拓新领域的先驱。",
  "make sth.；create/produce sth.；invent a machine；make a discovery；a pioneer in/of",
  "泛指制作用 make；文学艺术创作用 create；生产用 produce；发明用 invent；发现用 discovery。")

G("知道与理解", [("know",None,""),("learn",None,""),("understand",None,""),("realize",None,""),("recognize",None,""),("knowledge",None,"")],
  "know 指知道、认识的状态；learn 指通过学习获得；understand 强调理解含义或道理；realize 指突然意识到；recognize 指认出、辨认出曾见过的人或物；knowledge 是名词，指知识。",
  "know/learn about；understand the meaning；realize that…；recognize sb.'s voice；knowledge of",
  "知道用 know；学会用 learn；理解用 understand；意识到用 realize；认出用 recognize。")

G("需要与要求", [("need",None,""),("require",None,""),("request",None,"")],
  "need 最通用，指需要；require 较正式，指（规则、条件）要求、需要；request 指礼貌地请求，语气客气。",
  "need to do / need doing；require sb. to do；request sth. from sb.",
  "日常需要用 need；正式规定要求用 require；客气请求用 request。")

G("玩耍与表演", [("play",None,""),("show",None,""),("act",None,""),("perform",None,"")],
  "play 指玩耍、打球、演奏乐器；show 指展示、演出（也可作名词）；act 指行动或在戏剧中扮演角色；perform 指正式表演、演出，也可指执行、表现。",
  "play basketball/the piano；on show；act as；perform on stage",
  "玩耍打球用 play；给人看用 show；扮演角色用 act；登台演出用 perform。")

G("仅仅与正好", [("just",None,""),("simply",None,"")],
  "just 表示正好、仅仅、刚才；simply 表示仅仅、只不过，还可表示简单地。",
  "just now；just right；simply because",
  "刚才、恰好用 just；只不过用 simply。")

G("不同与相同", [("different",None,""),("difference",None,"different 的名词"),("same",None,""),("similar",None,""),("opposite",None,""),("compare",None,"")],
  "different 指不同的；difference 是其名词；same 指相同的，常与 the 连用；similar 指相似但不完全相同；opposite 指相反的、对面的；compare 指通过比较找出异同。",
  "be different from；the same as；be similar to；the opposite of；compare A with/to B",
  "不同用 different(from)；相同用 the same(as)；相似用 similar(to)；对比用 compare。")

G("保持与继续", [("keep",None,""),("stay",None,""),("remain",None,""),("continue",None,"")],
  "keep 指保持某种状态或继续做；stay 指停留、保持（某种状态不变）；remain 较正式，指仍然是、留下；continue 指中断后或不中断地继续。",
  "keep doing；keep + adj.；stay healthy；remain silent；continue doing/to do",
  "保持状态用 keep/stay；书面语“仍然是”用 remain；继续做用 keep/continue doing。")

G("开始与结束", [("start",None,""),("begin",None,""),("finish",None,""),("complete",None,"")],
  "start 与 begin 几乎通用，start 还可指启动、出发；finish 指做完某事；complete 较正式，强调完整地完成，也可作形容词“完整的”。",
  "start/begin doing/to do；finish doing；complete sth.",
  "开始用 start/begin；做完用 finish(doing)；圆满完成用 complete。")

G("极好与完美", [("great",None,""),("wonderful",None,""),("excellent",None,""),("perfect",None,""),("fine",None,"")],
  "great 泛指伟大的、极好的；wonderful 指令人惊喜的、精彩的；excellent 指优秀的、杰出的，常用于正式评价；perfect 指完美无缺的；fine 指好的、健康的、晴朗的（How are you? —Fine.）。",
  "a great success；a wonderful trip；an excellent student；a perfect day",
  "口语叫好说 great/wonderful；正式称赞优秀用 excellent；毫无缺点用 perfect。")

G("大与小", [("little",None,""),("tiny",None,""),("huge",None,"")],
  "little 指小的、少的；tiny 比 little 更小，指极小的；huge 指巨大的。",
  "a little boy；a tiny insect；a huge building",
  "小用 little；极小到微小用 tiny；巨大用 huge。")

G("正确与真实", [("right",None,""),("correct",None,""),("true",None,""),("truth",None,"true 的名词"),("exact",None,""),("proper",None,"恰当的"),("mistake",None,"")],
  "right 最通用，指对的、正确的；correct 较正式，指答案、做法正确，作动词指纠正；proper 指恰当的、合适的；true 指真实的、符合事实的；truth 是名词“真相”；exact 指精确的、丝毫不差的；mistake 指错误，是这组词的反义对照。",
  "a right/correct answer；a true story；tell the truth；the exact time；make a mistake",
  "对错用 right/correct；真假用 true/truth；精确用 exact；错误用 mistake。")

G("变得", [("become",None,""),("grow",None,""),("turn",None,"")],
  "become 最通用，后接名词或形容词；grow 强调逐渐变化；turn 常指颜色、性质的改变，后多接形容词。",
  "become a doctor；grow taller；turn yellow/green",
  "成为用 become；渐渐变用 grow；颜色、性质转变用 turn。")

G("重要与必要", [("important",None,""),("necessary",None,"")],
  "important 指重要的、有重大意义的；necessary 指必要的、不可缺少的。",
  "It is important/necessary (for sb.) to do sth.",
  "意义重大用 important；必不可少用 necessary。")

G("参观与游览", [("visit",None,""),("visitor",None,"visit 的名词"),("sightseeing",None,"")],
  "visit 指参观、拜访（人或地方）；visitor 指游客、来访者；sightseeing 是名词，专指观光、游览。",
  "visit a museum；a foreign visitor；go sightseeing",
  "参观某地用 visit；游客用 visitor；观光活动用 sightseeing。")

G("问题与麻烦", [("problem",None,""),("trouble",None,""),("matter",None,""),("disturb",None,"")],
  "problem 指需要解决的难题；trouble 指麻烦、困境，常不可数；matter 指事情、问题，常用于“怎么了”；disturb 是动词，指打扰、使不安。",
  "solve a problem；in trouble；What's the matter?；disturb sb.",
  "难题用 problem；麻烦用 trouble；“怎么回事”用 matter；打扰别人用 disturb。")

G("国家与民族", [("country",None,""),("nation",None,""),("national",None,"nation 的形容词"),("international",None,"")],
  "country 最常用，指国家（也可指乡村）；nation 较正式，侧重民族、国民；national 是形容词“国家的、民族的”；international 指国际的。",
  "a developing country；the whole nation；national flag；international trade",
  "日常说国家用 country；正式文体用 nation；国际的用 international。")

G("停止与阻止", [("stop",None,""),("prevent",None,""),("avoid",None,"")],
  "stop 指使停止或停止做；prevent 指阻止某事发生；avoid 指主动避开、避免。",
  "stop doing / stop to do；prevent sb. (from) doing；avoid doing",
  "停下用 stop；阻止发生用 prevent(from)；主动避开用 avoid(doing)。")

G("改变与交换", [("change",None,""),("exchange",None,"")],
  "change 指改变、变化（也可作名词“零钱”）；exchange 指互换、交换或兑换货币。",
  "change one's mind；change into；exchange A for B；exchange gifts",
  "变化用 change；互相交换用 exchange。")

G("种类", [("kind",None,""),("sort",None,"")],
  "kind 指种类，也可作形容词“善良的”；sort 与 kind 同义，口语中更常用，也可作动词“分类”。",
  "a kind/sort of；all kinds of；what kind of",
  "种类用 kind/sort；“善良”义只用 kind。")

G("听", [("hear",None,""),("listen",None,""),("sound",None,"听起来")],
  "hear 强调听到的结果；listen 强调听的动作，后接 to；sound 作系动词表示听起来。",
  "hear sb. do/doing；listen to music；sound great",
  "听见用 hear；去听听用 listen(to)；听起来用 sound。")

G("年轻与年长", [("young",None,""),("teenager",None,""),("junior",None,""),("senior",None,""),("primary",None,"初级的")],
  "young 指年轻的；teenager 指 13 至 19 岁的青少年；junior 指年少的、初级的；senior 指年长的、高年级的；primary 指初级的、小学的（primary school 小学）。",
  "a young man；junior high school；senior high school；primary school",
  "年轻用 young；青少年用 teenager；初中用 junior high；高中用 senior high；小学用 primary。")

G("应该与必须", [("should",None,""),("must",None,"")],
  "should 指应该，表建议或责任，语气较弱；must 指必须，语气强，还可表肯定推测“一定”。",
  "should do；must do；must be（一定是）",
  "劝告用 should；强制或肯定推测用 must。")

G("因为与当…时", [("because",None,""),("since",None,""),("while",None,"")],
  "because 直接表原因，语气最强；since 表已知的原因“既然”，也可指“自从”；while 引导时间“当…时”，也可表对比“然而”。",
  "because of + n.；since then；while doing",
  "表原因首选 because；既用 since；正当…时用 while。")

G("喜欢与偏爱", [("enjoy",None,""),("prefer",None,""),("favorite",None,""),("interest",None,""),("attract",None,"")],
  "enjoy 指享受、喜欢做某事；prefer 指两者中更喜欢；favorite 指最喜爱的（人或物）；interest 指兴趣，或作动词“使感兴趣”；attract 指吸引。",
  "enjoy doing；prefer A to B / prefer to do；one's favorite；be interested in；attract visitors",
  "喜欢做用 enjoy(doing)；更偏爱用 prefer；最喜欢的人或物用 favorite。")

G("移动与携带", [("move",None,""),("carry",None,""),("bring",None,"")],
  "move 指移动、搬家，也可指感动；carry 指随身携带、搬运（无方向性）；bring 指从别处带来（朝向说话人）。",
  "move to；carry a bag；bring sth. to sb.",
  "移动搬家用 move；扛带用 carry；带来用 bring。")

G("确定与可能", [("sure",None,""),("certain",None,""),("possible",None,""),("likely",None,""),("probably",None,""),("maybe",None,""),("perhaps",None,"")],
  "sure 指确信的，口语常用；certain 与 sure 同义，更正式，也可指“某些”；possible 指客观上可能的；likely 指很可能的（主语可是人或事）；probably、maybe、perhaps 都是副词“可能”，probably 可能性最大，maybe 多用于句首。",
  "be sure/certain (that)/to do；It is possible that…；be likely to do；probably/maybe/perhaps + 句子",
  "确信用 sure/certain；可能的事用 possible/likely；可能地用 probably，句首用 maybe。")

G("说与谈", [("speak",None,""),("shout",None,""),("chat",None,""),("conversation",None,""),("discuss",None,""),("argue",None,""),("explain",None,""),("describe",None,"")],
  "speak 指说（语言）、发言；shout 指大喊；chat 指闲聊；conversation 是名词“谈话”；discuss 指正式讨论；argue 指争论、争吵；explain 指解释原因道理；describe 指描述情形细节。",
  "speak English；shout at/to；chat with；have a conversation；discuss sth. with sb.；argue with；explain sth. to sb.；describe sth.",
  "讲话用 speak；大喊用 shout；闲聊用 chat；讨论用 discuss；争吵用 argue；解释用 explain；描述用 describe。")

G("花费", [("pay",None,""),("spend",None,""),("cost",None,""),("afford",None,"")],
  "pay 主语是人，指付款（pay for）；spend 主语是人，指花时间或金钱（spend on/doing）；cost 主语是物，指某物值多少钱；afford 指负担得起，常与 can 连用。",
  "pay for；spend…on/(in) doing；sth. costs sb.…；can/can't afford (to do)",
  "人付款用 pay；人花时间金钱用 spend；物花多少钱用 cost；买得起用 afford。")

G("记得与忘记", [("remember",None,""),("forget",None,""),("memory",None,"")],
  "remember 指记得（remember doing 记得做过，remember to do 记得要做）；forget 是其反义；memory 是名词，指记忆力、回忆。",
  "remember/forget to do / doing；in memory of",
  "记得要做用 remember to do；记得做过用 remember doing；反义用 forget。")

G("植物与种植", [("plant",None,""),("leaf",None,""),("vegetable",None,"")],
  "plant 作名词指植物，作动词指种植；leaf 指树叶，复数 leaves；vegetable 指蔬菜。",
  "plant trees；green leaves；fresh vegetables",
  "种植用 plant；叶子用 leaf（复数 leaves）；蔬菜用 vegetable。")
G("旅行与票务", [("travel",None,""),("ticket",None,""),("passport",None,"")],
  "travel 指旅行（可泛指也可指具体行程）；ticket 指车票、门票、机票；passport 指出国必备的护照。",
  "travel around the world；book a ticket；show one's passport",
  "旅行用 travel；票用 ticket；护照用 passport。")

G("困难", [("hard",None,""),("difficult",None,"")],
  "hard 指困难的，也可指硬的、努力地；difficult 只指困难的，稍正式，不与“努力”义混淆。",
  "a hard/difficult problem；work hard；It is difficult for sb. to do",
  "困难用 hard/difficult；“努力地”只能是 hard（hardly 意为“几乎不”）。")

G("通常与一般", [("usually",None,""),("common",None,""),("ordinary",None,""),("normal",None,""),("regular",None,""),("standard",None,""),("typical",None,"")],
  "usually 是副词“通常”；common 指常见的、普遍的；ordinary 指普通的、平凡的；normal 指正常的；regular 指有规律的、定期的；standard 指标准的；typical 指典型的、有代表性的。",
  "as usual；common sense；an ordinary day；normal temperature；regular exercise；standard English；a typical example",
  "频率“通常”用 usually；常见用 common；平凡用 ordinary；正常用 normal；规律用 regular；标准用 standard；典型用 typical。")

G("拿握与抓住", [("hold",None,""),("catch",None,"")],
  "hold 指拿着、握住（持续状态），还可指举办（会议）；catch 指抓住（瞬间动作）、赶上（车）、接住。",
  "hold on；hold a meeting；catch the bus；catch up with",
  "握着用 hold；一把抓住、赶车用 catch。")

G("特别与奇怪", [("special",None,""),("unusual",None,""),("strange",None,"")],
  "special 指特别的、特殊的（褒义）；unusual 指不寻常的（中性）；strange 指奇怪的、陌生的。",
  "a special gift；an unusual experience；a strange man",
  "特别的用 special；不寻常的用 unusual；奇怪陌生用 strange。")

G("关心与介意", [("care",None,""),("mind",None,"")],
  "care 指关心、在意（care about/for）；mind 指介意，常用于疑问句“你介意吗”，也可作名词“头脑、想法”。",
  "care about；take care of；Would you mind doing…?；Never mind.",
  "关心照顾用 care(of/about)；介意用 mind。")

G("美丽", [("beautiful",None,""),("lovely",None,"")],
  "beautiful 指美丽的，语气最强，可形容人、景、物；lovely 指可爱的、令人愉快的，语气亲切。",
  "a beautiful park；a lovely girl",
  "美丽用 beautiful；可爱怡人用 lovely。")

G("流行", [("popular",None,""),("pop",None,"")],
  "popular 指流行的、受欢迎的（be popular with/among）；pop 指流行音乐（pop music），是 popular 的缩略。",
  "be popular with；pop music",
  "受欢迎用 popular；流行音乐用 pop。")

G("相信、猜想与怀疑", [("believe",None,""),("trust",None,""),("suppose",None,""),("guess",None,""),("doubt",None,""),("imagine",None,"")],
  "believe 指相信某事为真；trust 指信任某人（人品）；suppose 指猜想、认为（be supposed to 应该）；guess 指无把握的猜测；doubt 指怀疑、不信；imagine 指想象。",
  "believe in；trust sb.；be supposed to do；guess the answer；doubt whether…；imagine doing",
  "相信用 believe；信任人用 trust；认为用 suppose；瞎猜用 guess；怀疑用 doubt；想象用 imagine。")

G("计划与准备", [("plan",None,""),("prepare",None,""),("aim",None,"")],
  "plan 指计划、打算；prepare 指为…做准备；aim 指目标，作动词指旨在、瞄准。",
  "plan to do；prepare for；aim to do / aim at；the aim of",
  "打算用 plan(to do)；备考用 prepare(for)；目标用 aim。")

G("担心与紧张", [("worry",None,""),("afraid",None,""),("nervous",None,"")],
  "worry 指担心（worry about）；afraid 指害怕（be afraid of/to do）；nervous 指（考试、演讲前）紧张不安。",
  "worry about；be afraid of；feel nervous",
  "担心用 worry(about)；害怕用 afraid；紧张用 nervous。")

G("寄与收", [("send",None,""),("receive",None,""),("envelope",None,"")],
  "send 指寄出、发送；receive 指（客观）收到；envelope 指信封。",
  "send sth. to sb. / send sb. sth.；receive a letter；an envelope",
  "寄发用 send；收到用 receive；信封装信封 envelope。")

G("接受与应允", [("accept",None,""),("agree",None,""),("refuse",None,""),("allow",None,"")],
  "accept 指（主观愿意）接受，与 receive（客观收到）相对；agree 指同意（agree with/to do）；refuse 指拒绝；allow 指允许。",
  "accept an invitation；agree with sb. / agree to do；refuse to do；allow sb. to do",
  "接受用 accept；同意用 agree；拒绝用 refuse(to do)；允许用 allow(sb. to do)。")

G("等待与期望", [("wait",None,""),("expect",None,""),("hope",None,""),("wish",None,"")],
  "wait 指等待（wait for）；expect 指预期某事会发生；hope 指希望（hope to do/that，不接 sb. to do）；wish 指难以实现的愿望或祝愿（wish sb. sth.）。",
  "wait for；expect sb. to do；hope to do / hope that…；wish sb. good luck",
  "等待用 wait(for)；预料用 expect；希望用 hope（不能说 hope sb. to do）；祝愿用 wish。")

G("决定", [("decide",None,""),("decision",None,"decide 的名词")],
  "decide 是动词，指决定（decide to do）；decision 是名词（make a decision）。",
  "decide to do / decide on；make a decision",
  "动词决定用 decide；名词用 decision。")

G("选择", [("choose",None,""),("pick",None,"")],
  "choose 指选择、挑选（choose from/between），较正式；pick 口语中更常用，还可指捡起、采摘。",
  "choose…from/between；pick up；pick apples",
  "挑选用 choose/pick；“捡起、摘”用 pick up/pick。")

G("失去与失败", [("lose",None,""),("miss",None,""),("fail",None,"")],
  "lose 指丢失、输掉（比赛）；miss 指错过（车、机会）、想念；fail 指失败、考试不及格（fail to do 未能做到）。",
  "lose one's way；lose the game；miss the bus；fail the exam；fail to do",
  "丢失、输用 lose；错过想念用 miss；失败不及格用 fail。")

G("程度与语气副词", [("quite",None,""),("enough",None,""),("really",None,"")],
  "quite 指相当、十分（quite + adj.）；enough 指足够，修饰形容词副词时后置（big enough）；really 指真正地、确实（加强语气）。",
  "quite good；good enough；enough time",
  "相当用 quite 前置；足够用 enough，形副后置、名词前置。")

G("离开与返回", [("leave",None,""),("return",None,"")],
  "leave 指离开（leave for 动身去）、留下、遗忘（把某物落在某处）；return 指返回、归还（return to / return sth. to sb.）。",
  "leave for Beijing；leave sth. at home；return to；return sth. to sb.",
  "离开、落下用 leave；回来、归还用 return。")

G("节省与浪费", [("save",None,""),("waste",None,""),("spare",None,"")],
  "save 指节省、储蓄、拯救；waste 指浪费（时间、金钱）；spare 指备用的、空闲的，作动词指抽出（时间）。",
  "save money/water/lives；a waste of time；waste time doing；spare time；spare no effort",
  "节省救人用 save；浪费用 waste；空闲抽出用 spare。")

G("然而与总之", [("however",None,""),("anyway",None,"")],
  "however 指然而，表转折，位置灵活；anyway 指无论如何、总之，常用于转换话题或收尾。",
  "However, …；anyway, …",
  "转折用 however；不管怎么说用 anyway。")

G("时间与迟早", [("later",None,""),("late",None,""),("already",None,""),("recently",None,""),("nowadays",None,""),("immediately",None,""),("suddenly",None,""),("sudden",None,"suddenly 的形容词")],
  "later 指后来、稍后；late 指迟、晚（be late for）；already 指已经（肯定句）；recently 指最近（常与完成时连用）；nowadays 指现今；immediately 指立刻；suddenly 指突然地，sudden 是其形容词。",
  "later on；be late for；have already done；in recent years；right now/immediately；all of a sudden",
  "稍后 later、迟到 late、已经 already、最近 recently、如今 nowadays、立刻 immediately、突然 suddenly。")

G("建造与修理", [("build",None,""),("building",None,"build 的名词"),("repair",None,""),("fix",None,""),("mend",None,"")],
  "build 指建造（大型建筑），building 指建筑物；repair 指修理（较大物件，较正式）；fix 指修理、安装、固定（口语常用）；mend 指修补（衣物、小物件）。",
  "build a bridge；a tall building；repair a car；fix the computer；mend shoes",
  "建造用 build；修理用 repair/fix（口语）；缝补用 mend。")

G("活动与行为", [("activity",None,""),("behavior",None,"")],
  "activity 指（有组织的）活动；behavior 指行为、举止（品行）。",
  "after-school activities；good/bad behavior",
  "课外活动用 activity；行为举止用 behavior。")

G("发生与似乎", [("happen",None,""),("appear",None,""),("seem",None,"")],
  "happen 指（偶然）发生（happen to do 碰巧）；appear 指出现、显得；seem 指似乎（seem to do / It seems that…）。",
  "What happened?；happen to do；appear/seem to be；It seems that…",
  "发生用 happen；出现用 appear；似乎用 seem。")

G("打破与破坏", [("break",None,""),("damage",None,""),("destroy",None,"")],
  "break 指打破、弄坏（也可作名词“休息”）；damage 指局部损坏，可修复；destroy 指彻底毁坏，无法修复。",
  "break the window；break down；damage the crops；destroy the village",
  "打碎用 break；损坏用 damage；毁灭用 destroy。")

G("节日与庆祝", [("festival",None,""),("celebrate",None,""),("birth",None,"")],
  "festival 指节日；celebrate 指庆祝；birth 指出生（birthday 生日）。",
  "the Spring Festival；celebrate one's birthday；date of birth",
  "节日用 festival；庆祝用 celebrate；出生用 birth。")

G("语言与表达", [("language",None,""),("mean",None,""),("express",None,""),("expression",None,"express 的名词"),("pronounce",None,""),("communication",None,"")],
  "language 指语言；mean 指意思是、意味着；express 指表达（感情、观点），expression 是其名词，也可指“表情、词语”；pronounce 指发音；communication 指交流、通讯。",
  "foreign languages；mean doing/to do；express oneself；facial expression；pronounce the word；communicate/communication with",
  "语言用 language；“意思是”用 mean；表达用 express；发音用 pronounce；交流用 communication。")

G("例子与情况", [("example",None,""),("case",None,"")],
  "example 指例子、榜样（for example 例如）；case 指具体情况、案例、案件，也可指箱子。",
  "for example；set an example；in this case；in case of",
  "举例用 example；“具体情况、案例”用 case。")
G("健康与疾病", [("healthy",None,""),("illness",None,""),("disease",None,""),("patient",None,""),("medical",None,""),("drug",None,""),("fever",None,""),("cough",None,""),("toothache",None,""),("ache",None,""),("cancer",None,""),("clinic",None,""),("dentist",None,"")],
  "healthy 指健康的；illness 泛指疾病（状态）；disease 指（具体的）疾病、病症；patient 指病人（作形容词指耐心的）；medical 指医疗的；drug 指药（也可指毒品）；fever 发烧、cough 咳嗽、toothache 牙痛、ache 疼痛、cancer 癌症，都是具体病症；clinic 指诊所；dentist 指牙医。",
  "keep healthy；a serious illness/disease；see a doctor/patient；medical care；take medicine/drugs；have a fever/cough/toothache；go to the clinic/dentist",
  "健康用 healthy；生病状态用 illness；具体疾病用 disease；病人用 patient；“头痛/牙痛”用 -ache 合成词。")

G("分享与分开", [("share",None,""),("divide",None,""),("separate",None,""),("mix",None,"")],
  "share 指分享、共用（share sth. with sb.）；divide 指把整体分成若干份（divide…into）；separate 指把连在一起的东西分开（separate…from）；mix 是其反义“混合”。",
  "share…with；divide…into；separate…from；mix…with",
  "分享用 share(with)；划分用 divide(into)；分离用 separate(from)；混合用 mix。")

G("味道与气味", [("taste",None,""),("smell",None,""),("sour",None,""),("bitter",None,"")],
  "taste 指品尝、尝起来；smell 指闻、闻起来、气味；sour 指酸的；bitter 指苦的（也可指痛苦的）。",
  "taste good/delicious；smell nice；sour grapes；bitter medicine",
  "尝用 taste；闻用 smell；酸用 sour；苦用 bitter。")

G("公司与商业", [("company",None,""),("business",None,""),("factory",None,""),("industry",None,""),("trade",None,""),("trader",None,"trade 的名词"),("market",None,""),("sale",None,""),("product",None,""),("item",None,""),("fair",None,"集市；展会")],
  "company 指公司（也可指陪伴）；business 指商业、生意、事务；factory 指工厂；industry 指（整个）工业、产业；trade 指贸易，trader 指商人；market 指市场；sale 指出售、促销（on sale）；product 指产品；item 指一件商品、一个项目；fair 指集市、展览会。",
  "run a company；do business；work in a factory；the car industry；international trade；on the market；on sale；produce products",
  "公司用 company；生意用 business；工厂用 factory；产业用 industry；贸易用 trade；市场用 market；出售促销用 sale。")

G("关闭", [("close",None,""),("shut",None,"")],
  "close 指关闭（也可作形容词“近的、亲密的”）；shut 与 close 同义，口气更强，过去式过去分词仍为 shut。",
  "close/shut the door；close down；shut up",
  "关门用 close/shut；“闭嘴”用 shut up；“亲近的”用 close。")

G("光与亮", [("light",None,""),("bright",None,""),("shine",None,""),("flash",None,"")],
  "light 指光、灯（作形容词指轻的、明亮的）；bright 指明亮的（也可指聪明的）；shine 指照耀、发光；flash 指闪光、一闪而过。",
  "turn on the light；bright sunshine；The sun shines.；a flash of lightning",
  "灯光用 light；明亮用 bright；照耀用 shine；闪光用 flash。")

G("站立与忍受", [("stand",None,""),("suffer",None,"")],
  "stand 指站立，口语中也指忍受（can't stand doing）；suffer 指遭受（痛苦、损失），常接 from（患病）。",
  "stand up；can't stand doing；suffer from；suffer a loss",
  "站立用 stand；“受不了”用 can't stand；遭罪患病用 suffer(from)。")

G("兴奋与惊讶", [("excite",None,""),("amaze",None,"")],
  "excite 指使兴奋（excited 感到兴奋的，exciting 令人兴奋的）；amaze 指使大为惊奇。",
  "be excited about；be amazed at/by",
  "兴奋用 excite(-ed/-ing)；惊叹用 amaze(-d)。")

G("想法与观点", [("opinion",None,""),("view",None,""),("attitude",None,""),("spirit",None,"")],
  "mind（见“关心与介意”组）也指头脑、想法（make up one's mind 下定决心）；opinion 指意见、看法（in one's opinion）；view 指观点，也可指风景、视野；attitude 指态度（attitude to/towards）；spirit 指精神、心灵。",
  "change one's mind；in one's opinion；point of view；attitude to/towards；team spirit",
  "想法心思用 mind；看法用 opinion/view；态度用 attitude；精神用 spirit。")

G("命令与指示", [("order",None,""),("instruction",None,"")],
  "order 指命令、点餐、订单（in order to 为了）；instruction 指（常用复数）操作说明、指示。",
  "order a meal；follow the instructions；in order to",
  "命令、点菜用 order；说明书、指示用 instructions。")

G("位置变化", [("fall",None,""),("lie",None,"躺"),("lay",None,""),("hang",None,"")],
  "fall 指落下、跌倒（fell, fallen）；lie 指躺、位于（lay, lain），也可指说谎（lied）；lay 指放置、下蛋（laid, laid），是 lie(躺) 的过去式同形词；hang 指悬挂（hung, hung）。",
  "fall down/off；lie down；lay the table；lay eggs；hang up",
  "落下用 fall；躺用 lie(lay, lain)；放置下蛋用 lay(laid)；悬挂用 hang(hung)。")

G("收集与储存", [("collect",None,""),("store",None,"储存")],
  "collect 指收集、收藏（爱好性）；store 指储存、储备（作名词指商店）。",
  "collect stamps；store food/information",
  "收藏爱好品用 collect；储存物资信息用 store。")

G("天气", [("weather",None,""),("sunny",None,""),("rainy",None,""),("cloudy",None,""),("wet",None,""),("shower",None,"阵雨")],
  "weather 是不可数名词“天气”；sunny 晴朗的、rainy 多雨的、cloudy 多云的、wet 潮湿多雨的，均为形容词；shower 指阵雨（也可指淋浴）。",
  "fine weather；a sunny/rainy/cloudy day；get wet；a heavy shower",
  "天气用 weather；晴/雨/阴分别用 sunny/rainy/cloudy；阵雨用 shower。")

G("保护与守卫", [("protect",None,""),("guard",None,"")],
  "protect 指保护（protect…from/against）；guard 指守卫、警卫（也可作名词指卫兵）。",
  "protect the environment；guard the gate；a security guard",
  "保护环境用 protect(from)；站岗守卫用 guard。")

G("机会与挑战", [("chance",None,""),("challenge",None,"")],
  "chance 指机会、可能性（by chance 偶然）；challenge 指挑战（也可作动词）。",
  "a good chance；by chance；face/meet a challenge",
  "机会用 chance；挑战用 challenge。")

G("改善与发展", [("improve",None,""),("develop",None,""),("increase",None,""),("reduce",None,"")],
  "improve 指改善、提高（质量）；develop 指发展、开发、培养；increase 指增加；reduce 指减少。",
  "improve English；develop a habit；increase/reduce the price",
  "提高质量用 improve；发展培养用 develop；增加用 increase；减少用 reduce。")

G("文化与传统", [("culture",None,""),("traditional",None,""),("custom",None,""),("history",None,""),("society",None,"")],
  "culture 指文化；traditional 指传统的；custom 指风俗、习惯（社会群体的）；history 指历史；society 指社会。",
  "Chinese culture；traditional festivals；local customs；modern society",
  "文化用 culture；传统的用 traditional；风俗用 custom；社会用 society。")

G("穿戴", [("wear",None,""),("dress",None,""),("suit",None,"适合"),("match",None,"相配")],
  "wear 指穿着、戴着（状态）；dress 指给…穿衣（dress sb./oneself），作名词指连衣裙；suit 指（颜色、款式）适合某人；match 指（衣物之间）相配。",
  "wear a coat/glasses；get dressed；suit sb. well；match your shoes",
  "穿着状态用 wear；穿衣动作用 dress；适合用 suit；搭配用 match。")

G("环境与自然", [("environment",None,""),("natural",None,""),("pollution",None,""),("pollute",None,"pollution 的动词")],
  "environment 指环境；natural 指自然的、天然的；pollution 是名词“污染”；pollute 是其动词。",
  "protect the environment；natural resources；air/water pollution；pollute the river",
  "环境用 environment；自然的用 natural；污染名词 pollution、动词 pollute。")

G("到达与进入", [("arrive",None,""),("reach",None,""),("enter",None,"")],
  "arrive 是不及物动词，接 at（小地点）/in（大地点）；reach 是及物动词，直接接地点；enter 指进入（房间、比赛、大学），直接接宾语。",
  "arrive at/in；reach Beijing；enter the room",
  "到达：arrive at/in 或 reach（及物）；进入用 enter（不加 into）。")

G("力量与虚弱", [("strong",None,""),("weak",None,""),("power",None,""),("force",None,"")],
  "strong 指强壮的、强烈的；weak 是其反义；power 指力量、权力、电力；force 指武力、作用力，作动词指强迫。",
  "a strong man；be weak in；electric power；by force；force sb. to do",
  "强壮用 strong；虚弱用 weak；电力权力用 power；武力强迫用 force。")

G("身体部位", [("head",None,""),("heart",None,""),("shoulder",None,""),("wing",None,""),("blood",None,""),("physical",None,"身体的")],
  "head 指头；heart 指心脏、内心；shoulder 指肩膀（作动词指肩负）；wing 指翅膀；blood 指血液；physical 指身体的（也可指物理的）。",
  "use one's head；learn by heart；shoulder to shoulder；physical examination",
  "身体部位各归其词；体检用 physical examination。")

G("伤害与烧伤", [("hurt",None,""),("burn",None,"")],
  "hurt 指弄伤、疼痛（hurt-hurt-hurt）；burn 指烧伤、燃烧。",
  "hurt one's leg；get burned/burnt；burn down",
  "受伤疼痛用 hurt；烧伤燃烧用 burn。")

G("邀请与接待", [("invite",None,""),("invitation",None,"invite 的名词"),("treat",None,""),("greet",None,""),("introduce",None,""),("regard",None,"问候")],
  "invite 指邀请，invitation 是其名词；treat 指款待、对待、治疗；greet 指打招呼、迎接；introduce 指介绍（introduce A to B）；regard 作名词复数 regards 表问候，作动词指把…看作（regard…as）。",
  "invite sb. to do；accept an invitation；treat sb. to dinner；greet sb. with a smile；introduce oneself；regard…as；give my regards to",
  "邀请用 invite/invitation；请客用 treat；问候迎接用 greet；介绍用 introduce；‘看作’用 regard…as。")

G("声音与安静", [("voice",None,""),("noise",None,""),("silence",None,""),("quiet",None,""),("quietly",None,"quiet 的副词"),("loudly",None,"")],
  "voice 指人的嗓音；noise 指（令人不快的）噪音；silence 是名词“寂静”；quiet 指安静的，quietly 是其副词；loudly 指大声地。",
  "in a low/loud voice；make noise；in silence；keep quiet；talk loudly",
  "嗓音用 voice；噪音用 noise；安静用 quiet/silence；大声地用 loudly。")

G("原谅与道歉", [("excuse",None,""),("apologize",None,"")],
  "excuse 指原谅（Excuse me 劳驾），作名词指借口；apologize 指道歉（apologize to sb. for sth.）。",
  "Excuse me；make an excuse；apologize to sb. for (doing) sth.",
  "借口、劳驾用 excuse；正式道歉用 apologize(to…for…)。")

G("影视与演出场所", [("film",None,""),("cinema",None,""),("theater",497,""),("theater",560,"与前一词条重复收录"),("opera",None,""),("concert",None,""),("screen",None,"")],
  "film 指电影；cinema 指电影院（go to the cinema）；theater 指剧院、戏院（两个词条重复收录）；opera 指歌剧；concert 指音乐会；screen 指银幕、屏幕。",
  "see/watch a film；go to the cinema/theater；Beijing Opera；go to a concert；on the screen",
  "电影用 film；电影院用 cinema；剧院用 theater；音乐会用 concert；屏幕用 screen。")

G("报刊与新闻", [("news",None,""),("newspaper",None,""),("magazine",None,""),("report",None,""),("reporter",None,"report 的名词"),("advertisement",None,""),("headline",None,""),("message",None,""),("press",None,"报刊；新闻界")],
  "news 是不可数名词“新闻”；newspaper 指报纸；magazine 指杂志；report 指报道（动词/名词），reporter 指记者；advertisement 指广告；headline 指头条标题；message 指消息、留言；press 作名词可指报刊、新闻界。",
  "a piece of news；read a newspaper/magazine；a news report；leave a message；make headlines",
  "新闻用 news（不可数）；报纸 newspaper、杂志 magazine；记者 reporter；广告 advertisement；留言 message。")

G("音乐与广播", [("radio",None,""),("band",None,""),("piano",None,"")],
  "radio 指收音机、无线电广播；band 指乐队；piano 指钢琴（play the piano）。",
  "listen to the radio；a jazz band；play the piano",
  "广播用 radio；乐队用 band；钢琴用 piano（乐器前加 the）。")
G("人群与成员", [("crowd",None,""),("human",None,""),("member",None,""),("partner",None,"")],
  "crowd 指人群（也可作动词“拥挤”）；human 指人、人类；member 指（团体）成员；partner 指伙伴、搭档。",
  "a crowd of；human beings；a member of；business partners",
  "人群用 crowd；人类用 human；成员用 member；搭档用 partner。")

G("不定代词", [("anything",None,""),("everybody",None,"")],
  "anything 指任何事物，多用于疑问、否定句；everybody 指每个人，作主语时谓语用单数。",
  "anything else；everybody knows",
  "任何事物用 anything；人人用 everybody（谓语单数）。")

G("有用与可用", [("useful",None,""),("available",None,"")],
  "useful 指有用的；available 指可用的、可获得的、有空的。",
  "be useful for/to；tickets available；be available to do",
  "有用用 useful；弄得到、有空用 available。")

G("检查与考试", [("check",None,""),("examination",None,""),("review",None,""),("grade",None,""),("score",None,""),("degree",None,"学位；程度"),("monitor",None,"监视")],
  "check 指检查、核对；examination 指正式考试（= exam），也可指检查；review 指复习、回顾、评论；grade 指年级、成绩；score 指分数、得分；degree 指学位、程度；monitor 作动词指监视，作名词指班长、显示器。",
  "check the answers；take an examination；review lessons；get good grades/scores；a college degree",
  "核对用 check；考试用 examination；复习用 review；成绩用 grade/score；学位用 degree。")

G("聪明与迟钝", [("clever",None,""),("wise",None,""),("dull",None,"")],
  "clever 指聪明的、机灵的；wise 指明智的、有智慧的（阅历深）；dull 指迟钝的、乏味的（反义对照）。",
  "a clever boy；a wise choice；a dull book",
  "机灵用 clever；睿智用 wise；迟钝乏味用 dull。")

G("连接与关系", [("connect",None,""),("relation",None,"")],
  "connect 指连接、联系（connect…with/to）；relation 指关系、联系，也可指亲属。",
  "connect A with/to B；the relation between A and B",
  "连接用 connect；关系用 relation。")

G("诚信与违法", [("honest",None,"反义对照"),("cheat",None,""),("steal",None,""),("murder",None,""),("prisoner",None,""),("punish",None,"")],
  "honest 指诚实的（反义对照）；cheat 指欺骗、作弊；说谎用 lie（lied, lied，见“位置变化”组）；steal 指偷（steal sth. from）；murder 指谋杀；prisoner 指囚犯；punish 指惩罚（punish sb. for）。",
  "an honest boy；cheat in the exam；tell a lie；steal money；be punished for",
  "诚实 honest；作弊欺骗 cheat；说谎 lie；偷 steal；谋杀 murder；囚犯 prisoner；惩罚 punish。")

G("古代与现代", [("ancient",None,""),("modern",None,"")],
  "ancient 指古代的、古老的；modern 指现代的、新式的。",
  "ancient China；modern technology",
  "古代用 ancient；现代用 modern。")

G("水域", [("ocean",None,""),("stream",None,""),("coast",None,"")],
  "ocean 指海洋；stream 指小溪（作动词指流出）；coast 指海岸。",
  "the Pacific Ocean；a small stream；on the coast",
  "大洋用 ocean；小溪用 stream；海岸用 coast。")

G("愉快与糟糕", [("pleasure",None,""),("pleasant",None,""),("comfortable",None,""),("funny",None,""),("terrible",None,""),("awful",None,"")],
  "pleasure 是名词“愉快、乐事”（with pleasure 乐意效劳）；pleasant 指令人愉快的；comfortable 指舒适的；funny 指有趣的、好笑的；terrible 与 awful 指糟糕的、可怕的。",
  "with pleasure；a pleasant trip；a comfortable chair；a funny story；terrible weather",
  "乐事用 pleasure；令人愉快用 pleasant；舒适用 comfortable；好笑用 funny；糟糕用 terrible/awful。")

G("遗憾与懊悔", [("pity",None,""),("shame",None,""),("regret",None,"")],
  "pity 指遗憾、怜悯（What a pity!）；shame 指羞耻、遗憾的事；regret 指后悔（regret doing 后悔做过）。",
  "What a pity!；It's a shame that…；regret doing",
  "真可惜用 pity/shame；后悔用 regret(doing)。")

G("骄傲", [("proud",None,""),("pride",None,"proud 的名词")],
  "proud 是形容词“自豪的”（be proud of）；pride 是名词（take pride in）。",
  "be proud of；take pride in",
  "为…自豪：be proud of = take pride in。")

G("服务", [("service",None,""),("servant",None,""),("waiter",None,"")],
  "service 指服务（作动词指维修保养）；servant 指仆人；waiter 指（餐厅）服务员。",
  "good service；public service；ask the waiter",
  "服务用 service；仆人用 servant；餐厅服务员用 waiter。")

G("成功与胜利", [("success",None,""),("successful",None,"success 的形容词"),("succeed",None,"success 的动词"),("achieve",None,""),("achievement",None,"achieve 的名词"),("victory",None,"")],
  "success 是名词；successful 是形容词（be successful in）；succeed 是动词（succeed in doing）；achieve 指（经努力）实现目标，achievement 是其名词“成就”；victory 指（比赛、战争的）胜利。",
  "achieve success；be successful in；succeed in doing；achieve one's dream；a great achievement；win a victory",
  "成功：名词 success、形容词 successful、动词 succeed(in doing)；实现梦想用 achieve；比赛胜利用 victory。")

G("结果与影响", [("result",None,""),("effect",None,""),("influence",None,"")],
  "result 指结果（as a result 因此）；effect 指效果、作用（have an effect on）；influence 指（深远的、潜移默化的）影响。",
  "as a result；have an effect/influence on",
  "结果用 result；效果用 effect；深远影响用 influence。")

G("练习与训练", [("practice",None,""),("exercise",None,""),("coach",None,"")],
  "practice 指练习（practice doing）；exercise 指运动、体操、习题；coach 指教练，作动词指训练指导。",
  "practice speaking English；do exercise/morning exercises；a football coach",
  "练技能用 practice(doing)；锻炼做操用 exercise；教练用 coach。")

G("技能与才能", [("skill",None,""),("ability",None,""),("talent",None,""),("able",None,"")],
  "skill 指（后天练成的）技能；ability 指能力（the ability to do）；talent 指天赋；able 是形容词（be able to do 能够）。",
  "learn a skill；the ability to do；have a talent for；be able to do",
  "技能用 skill；能力用 ability（be able to）；天赋用 talent。")

G("休息与醒来", [("rest",None,""),("wake",None,"")],
  "rest 指休息（have a rest），也可指“其余的部分”；wake 指醒来、唤醒（wake up）。",
  "have/take a rest；the rest of；wake up",
  "休息用 rest；醒来用 wake(up)。")

G("友善与无礼", [("friendly",None,""),("polite",None,""),("rude",None,""),("gentle",None,""),("cruel",None,"")],
  "friendly 指友好的（be friendly to）；kind（见“种类”组）作形容词指善良的、和蔼的；polite 指有礼貌的；rude 指粗鲁的；gentle 指温和的、轻柔的；cruel 指残忍的。",
  "be friendly/kind/polite/rude to sb.；a gentle voice；be cruel to",
  "友好 friendly；善良 kind；礼貌 polite；粗鲁 rude；温和 gentle；残忍 cruel。")

G("处理与解决", [("deal",None,""),("solve",None,""),("solution",None,"solve 的名词"),("overcome",None,"")],
  "deal 指处理（deal with）；solve 指解决（问题、谜题）；solution 是其名词（the solution to）；overcome 指克服（困难、恐惧）。",
  "deal with；solve the problem；the solution to；overcome difficulties",
  "处理用 deal with；解题解决用 solve(solution to)；克服困难用 overcome。")

G("死亡", [("die",None,""),("dead",None,"die 的形容词"),("death",None,"die 的名词")],
  "die 是动词（die of/from）；dead 是形容词（可表持续状态）；death 是名词。",
  "die of illness；has been dead for years；the death of",
  "动词死用 die；状态用 dead（与时间段连用）；名词用 death。")

G("富有与价值", [("rich",None,""),("wealth",None,""),("expensive",None,""),("cheap",None,""),("valuable",None,""),("value",None,""),("treasure",None,"")],
  "rich 指富有的、丰富的；wealth 是名词“财富”；expensive 指昂贵的；cheap 是其反义；valuable 指有价值的、贵重的；value 是名词“价值”（作动词指重视）；treasure 指财宝，作动词指珍惜。",
  "be rich in；a man of wealth；too expensive/cheap；valuable advice；the value of；treasure our friendship",
  "富有 rich、财富 wealth；贵贱 expensive/cheap；有价值 valuable/value；珍宝珍惜 treasure。")

G("价格与奖励", [("price",None,""),("award",None,""),("reward",None,""),("medal",None,""),("honor",None,"")],
  "price 指价格（价格高低用 high/low，不用 expensive）；award 指奖品，作动词指正式授予；reward 指报酬、酬谢；medal 指奖牌；honor 指荣誉。",
  "the price of；win an award；a reward for；a gold medal；in honor of",
  "价格用 price；获奖用 award；酬谢用 reward；奖牌用 medal；荣誉用 honor。")

G("饮食", [("supper",None,""),("menu",None,""),("diet",None,""),("cooker",None,""),("boil",None,""),("hungry",None,""),("thirsty",None,"")],
  "supper 指晚餐；menu 指菜单；diet 指日常饮食、节食；cooker 指炊具（注意：厨师是 cook）；boil 指煮沸；hungry 指饥饿的；thirsty 指口渴的。",
  "have supper；read the menu；on a diet；a rice cooker；boil water；be hungry/thirsty",
  "晚饭 supper；菜单 menu；饮食节食 diet；锅具 cooker；煮沸 boil；饿 hungry；渴 thirsty。")

G("邻居", [("neighbor",None,"美式拼写"),("neighbour",None,"英式拼写")],
  "两词同义，neighbor 是美式拼写，neighbour 是英式拼写。",
  "next-door neighbor/neighbour",
  "美式 neighbor，英式 neighbour，意思完全相同。")

G("两者择一", [("either",None,""),("neither",None,"")],
  "either 指（两者中）任一（either…or… 或者…或者…）；neither 指两者都不（neither…nor…）。",
  "either…or…；neither…nor…",
  "两者之一用 either(or)；两者都不用 neither(nor)。")

G("清洁与脏乱", [("clear",None,"清除"),("tidy",None,""),("sweep",None,""),("brush",None,""),("bath",None,""),("mess",None,""),("rubbish",None,""),("litter",None,"")],
  "clear 作动词指清除（作形容词指清楚的）；tidy 指整洁的、整理；sweep 指打扫（swept）；brush 指刷；bath 指洗澡；mess 指脏乱；rubbish 与 litter 指垃圾，litter 作动词指乱扔。",
  "clear the table；tidy up；sweep the floor；brush teeth；take a bath；in a mess；throw rubbish/litter about",
  "整理用 tidy(up)；扫地 sweep；刷牙 brush；脏乱 mess；垃圾 rubbish/litter。")

G("灾难", [("accident",None,""),("earthquake",None,""),("flood",None,"")],
  "accident 指（交通等）意外事故；earthquake 指地震；flood 指洪水（作动词指淹没）。",
  "a car/traffic accident；by accident；an earthquake；a flood",
  "事故用 accident；地震用 earthquake；洪水用 flood。")

G("孤独", [("alone",None,""),("lonely",None,""),("single",None,"")],
  "alone 指独自一人（客观事实，不强调感情）；lonely 指孤独的（主观感受）；single 指单一的、单身的。",
  "live alone；feel lonely；a single room",
  "独自一人的客观状态用 alone；内心孤独用 lonely；单个单身用 single。")

G("时刻", [("moment",None,""),("minute",None,""),("period",None,"")],
  "moment 指片刻、瞬间（at the moment 此刻）；minute 指分钟；period 指一段时期、课时。",
  "wait a moment；at the moment；in a few minutes；a period of time",
  "片刻用 moment；分钟用 minute；时期用 period。")

G("数量与全部", [("whole",None,""),("most",None,""),("amount",None,""),("several",None,""),("dozen",None,""),("population",None,"")],
  "whole 指整个的（the whole + 名词）；most 指大多数、最；amount 指数量（an amount of + 不可数）；several 指几个；dozen 指一打（十二个）；population 指人口。",
  "the whole day；most of；a large amount of；several times；two dozen eggs；the population of",
  "整个用 whole；大多数用 most；数量用 amount of（不可数）；几个用 several；人口用 population。")

G("绘画与艺术", [("paint",None,""),("draw",None,""),("artist",None,""),("design",None,""),("decorate",None,"")],
  "paint 指用颜料画、刷漆；draw 指用线条画（draw-drawn）；artist 指画家、艺术家；design 指设计；decorate 指装饰。",
  "paint a picture；draw a picture；design a poster；decorate the room",
  "涂颜料用 paint；画线条用 draw；设计用 design；装饰用 decorate。")

G("电话", [("mobile",None,""),("telephone",None,""),("ring",None,"打电话"),("bell",None,"")],
  "mobile 指手机（mobile phone）；telephone 指电话（机）；ring 指（铃）响、打电话（ring sb. up）；bell 指铃、钟。",
  "on the mobile/telephone；ring sb. (up)；The bell rings.",
  "手机用 mobile；电话用 telephone；铃响、打电话用 ring；铃用 bell。")

G("中间与边缘", [("middle",None,""),("center",None,""),("edge",None,""),("bottom",None,"")],
  "middle 指中间（in the middle of）；center 指中心；edge 指边缘；bottom 指底部。",
  "in the middle of；in the center of；on the edge of；at the bottom of",
  "中间用 middle；中心用 center；边缘用 edge；底部用 bottom。")

G("危险与安全", [("dangerous",None,""),("danger",None,"dangerous 的名词"),("safe",None,"")],
  "dangerous 是形容词“危险的”；danger 是名词（in danger 处于危险中）；safe 是其反义“安全的”。",
  "be dangerous；in danger；out of danger；keep safe",
  "危险的用 dangerous；危险（名词）用 danger；安全用 safe。")

G("认真与严格", [("careful",None,""),("carefully",None,"careful 的副词"),("serious",None,""),("strict",None,"")],
  "careful 是形容词“小心的”，carefully 是其副词；serious 指认真的、严肃的、严重的；strict 指严格的（be strict with sb.）。",
  "be careful (with)；listen carefully；take…seriously；be strict with sb.",
  "小心用 careful(-ly)；认真严肃用 serious；对人严格用 strict(with)。")

G("季节", [("spring",None,""),("winter",None,""),("autumn",None,"")],
  "spring 春天、winter 冬天、autumn 秋天（英式）；fall 作名词在美式英语中指秋天（作动词指落下，见“位置变化”组）。",
  "in spring/winter/autumn",
  "秋天英式 autumn、美式 fall；季节前介词用 in。")

G("天地之间", [("earth",None,""),("ground",None,""),("space",None,"")],
  "earth 指地球、泥土；ground 指地面、场地；space 指太空、空间。",
  "on earth；on the ground；in space",
  "地球用 the earth；地面用 ground；太空用 space。")

G("管理与经营", [("control",None,""),("manage",None,""),("manager",None,"manage 的名词"),("operate",None,""),("operation",None,"operate 的名词")],
  "control 指控制；manage 指管理、设法做到（manage to do）；manager 指经理；operate 指操作、运转、动手术；operation 指手术、操作、运转。",
  "under control；manage to do；operate a machine；have an operation",
  "控制用 control；管理设法用 manage(to do)；操作用 operate；手术用 operation。")

G("直接与笔直", [("straight",None,""),("direct",None,""),("director",None,"direct 的名词")],
  "straight 指笔直的（go straight）；direct 指直接的，作动词指指挥、导演；director 指导演、主管。",
  "go straight；a direct flight；a film director",
  "笔直用 straight；直接用 direct；导演主管用 director。")

G("遵循与按照", [("follow",None,""),("according",None,"according to 按照")],
  "follow 指跟随、遵循（规则、建议）；according 不单独用，according to 表示根据、按照。",
  "follow the rules/advice；according to the report",
  "跟随遵循用 follow；“按照…”用 according to。")

G("匆忙与缓慢", [("rush",None,""),("hurry",None,""),("slow",None,"")],
  "rush 指冲、匆忙（rush to do）；hurry 指赶紧（hurry up，in a hurry）；slow 指慢的（反义），作动词指放慢。",
  "rush out；hurry up；in a hurry；slow down",
  "冲忙用 rush；催促用 hurry(up)；放慢用 slow(down)。")

G("建议", [("advise",None,""),("suggest",None,""),("suggestion",None,"suggest 的名词")],
  "advise 指劝告（advise sb. to do / advise doing）；suggest 指建议（suggest doing / suggest that…，不接 sb. to do）；suggestion 是可数名词（注意：advice 不可数）。",
  "advise sb. to do；suggest doing；make a suggestion",
  "劝某人做用 advise sb. to do；建议做用 suggest doing；名词建议用 suggestion。")

G("努力与进步", [("effort",None,""),("progress",None,"")],
  "effort 指努力（make an effort to do）；progress 指进步（不可数，make progress）。",
  "make an effort；spare no effort；make progress",
  "努力用 effort；进步用 progress（不可数）。")

G("最后", [("last",None,""),("final",None,"")],
  "last 指最后的、上一个的（last week），作动词指持续；final 指最终的、决定性的（the final exam 期终考试）。",
  "last week/year；at last；the final exam；in the final",
  "上一个、最后用 last；最终的（结果、考试）用 final。")

G("战争与和平", [("peace",None,""),("war",None,""),("army",None,""),("soldier",None,""),("enemy",None,""),("attack",None,"")],
  "peace 指和平；war 指战争；army 指军队；soldier 指士兵；enemy 指敌人；attack 指攻击（动名兼用）。",
  "in peace；world peace；join the army；attack the city",
  "和平 peace；战争 war；军队 army；士兵 soldier；敌人 enemy；攻击 attack。")

G("包括与排除", [("include",None,""),("except",None,"")],
  "include 指包括、包含；except 指除……之外（不包括）。",
  "including…；everyone except me",
  "包括用 include；除外用 except。")

G("通知与警告", [("warn",None,""),("inform",None,""),("notice",None,""),("note",None,"")],
  "warn 指警告（warn sb. of/against/not to do）；inform 指（正式）通知（inform sb. of）；notice 指注意到、布告；note 指笔记、便条。",
  "warn sb. of danger；inform sb. of sth.；notice sb. doing；take notes",
  "警告用 warn；正式告知用 inform；注意到、布告用 notice；笔记用 note。")

G("基础", [("basic",None,""),("base",None,"")],
  "basic 指基本的、基础的；base 指底部、基地，作动词指以…为基础（be based on）。",
  "basic skills/knowledge；at the base of；be based on",
  "基本的用 basic；以…为基础用 base(be based on)。")

G("软硬与光滑", [("soft",None,""),("smooth",None,""),("rough",None,"")],
  "soft 指柔软的、轻柔的；smooth 指光滑的、平稳的；rough 指粗糙的、粗暴的（反义对照）。",
  "soft music/skin；a smooth road；rough hands",
  "柔软用 soft；光滑用 smooth；粗糙用 rough。")

G("竞赛", [("contest",None,""),("athlete",None,"")],
  "contest 指竞赛、比赛（演讲、歌唱等）；athlete 指运动员。",
  "a speech contest；a top athlete",
  "竞赛用 contest；运动员用 athlete。")

G("科学学科", [("science",None,""),("scientist",None,"science 的名词"),("chemistry",None,""),("physics",None,""),("chemical",None,"chemistry 的形容词"),("geography",None,""),("experiment",None,""),("lab",None,"")],
  "science 指科学；scientist 指科学家；chemistry 化学、physics 物理、geography 地理是学科名；chemical 指化学的（作名词指化学品）；experiment 指实验；lab 指实验室（laboratory 的缩略）。",
  "study science；a famous scientist；do an experiment；in the lab",
  "科学 science、科学家 scientist；学科 chemistry/physics/geography；实验 experiment；实验室 lab。")

G("政策与职务", [("policy",None,""),("official",None,""),("secretary",None,"")],
  "policy 指政策、方针；official 指官方的（作名词指官员）；secretary 指秘书、书记。",
  "government policy；an official visit；a general secretary",
  "政策用 policy；官方的/官员用 official；秘书用 secretary。")

G("方向与地址", [("direction",None,""),("address",None,"")],
  "direction 指方向（in the direction of），复数可指用法说明；address 指地址，也可指演讲。",
  "in all directions；ask the way/direction；home address",
  "方向用 direction；地址用 address。")

G("金属与材料", [("metal",None,""),("iron",None,""),("steel",None,""),("plastic",None,"")],
  "metal 指金属（总称）；iron 指铁（也可指熨斗）；steel 指钢；plastic 指塑料。",
  "made of metal/iron/steel/plastic",
  "金属总称 metal；铁 iron；钢 steel；塑料 plastic。")

G("日期", [("date",None,""),("calendar",None,"")],
  "date 指日期（What's the date today?），也可指约会；calendar 指日历。",
  "the date of birth；look at the calendar",
  "日期用 date；日历用 calendar。")

G("压力", [("pressure",None,""),("stress",None,"")],
  "pressure 指（外界施加的）压力（under pressure）；stress 指（内心的）压力、紧张，也可指重音、强调。",
  "under pressure；reduce stress；lay stress on",
  "外界压力用 pressure；心理紧张用 stress。")

G("失望与心烦", [("disappoint",None,""),("upset",None,"")],
  "disappoint 指使失望（disappointed 感到失望的）；upset 指心烦的、难过的，作动词指使心烦、打翻。",
  "be disappointed with/at；feel upset",
  "失望用 disappoint(-ed)；心烦难过用 upset。")

G("生气", [("angry",None,""),("mad",None,"")],
  "angry 指生气的（be angry with sb.）；mad 口语中指生气的、疯狂的。",
  "be angry with sb./about sth.；be mad at；go mad",
  "生气用 angry(with)；口语用 mad(at)。")

G("残障", [("deaf",None,""),("disable",None,"")],
  "deaf 指聋的（the deaf 聋人）；disable 是动词“使残疾、使失去能力”（disabled 残疾的）。",
  "be deaf in one ear；disabled people",
  "聋的用 deaf；使残疾用 disable（形容词 disabled）。")

G("私人与秘密", [("private",None,""),("secret",None,"")],
  "private 指私人的、私密的（private life/school）；secret 指秘密（keep a secret）。",
  "in private；private information；keep a secret；in secret",
  "私人的用 private；秘密用 secret。")

G("房屋与设施", [("apartment",None,""),("flat",None,"公寓"),("window",None,""),("fence",None,""),("ceiling",None,""),("block",None,"街区")],
  "apartment 指公寓（美式）；flat 指公寓（英式）；window 指窗户；fence 指栅栏；ceiling 指天花板；block 指街区、大楼、大块。",
  "live in an apartment/flat；open the window；garden fence；on the ceiling；a block of flats",
  "公寓美式 apartment、英式 flat；栅栏 fence；天花板 ceiling；街区 block。")

G("度量", [("weigh",None,""),("measure",None,""),("height",None,""),("wide",None,""),("kilometer",None,""),("distance",None,"")],
  "weigh 指称重、重达；measure 指测量；height 指高度、身高；wide 指宽阔的；kilometer 指公里；distance 指距离。",
  "weigh 50 kilos；measure the room；in height；two meters wide；within walking distance",
  "称重用 weigh；测量用 measure；高度 height、宽度 wide；距离用 distance。")

G("机器与设备", [("machine",None,""),("tool",None,""),("digital",None,""),("electric",None,""),("battery",None,"")],
  "machine 指机器；tool 指（手工）工具；digital 指数字的；electric 指电的、电动的；battery 指电池。",
  "a washing machine；garden tools；a digital camera；an electric car；change the battery",
  "机器用 machine；工具用 tool；数码的用 digital；电动的用 electric；电池用 battery。")

G("勇气", [("brave",None,""),("courage",None,"brave 的名词"),("dare",None,"")],
  "brave 是形容词“勇敢的”；courage 是名词“勇气”；dare 指敢（dare (to) do）。",
  "a brave soldier；have the courage to do；dare (to) do",
  "勇敢用 brave；勇气用 courage；“敢”用 dare。")

G("女性", [("female",None,""),("daughter",None,"")],
  "female 指女性的、雌性的（作名词指女性）；daughter 指女儿。",
  "a female teacher；his daughter",
  "女性（性别）用 female；女儿用 daughter。")

G("环与圈", [("circle",None,""),("round",None,""),("around",None,"")],
  "circle 指圆圈（作动词指环绕）；round 指圆的，作介词/副词指围绕；ring（见“电话”组）也可指圆环、戒指；around 指在周围、大约。",
  "draw a circle；a round table；sit around；around the corner",
  "圆圈用 circle；圆的/围绕用 round；指环用 ring；在周围用 around。")

G("绳与链", [("rope",None,""),("chain",None,"")],
  "rope 指绳子；chain 指链条（也可指连锁店）。",
  "jump rope；a gold chain；a chain of shops",
  "绳子用 rope；链条用 chain。")

G("空与倒", [("blank",None,""),("empty",None,""),("pour",None,"")],
  "blank 指空白的（纸、表格）；empty 指空的（容器、房间），作动词指倒空；pour 指倒（液体）、倾泻。",
  "fill in the blank；an empty bottle；pour tea",
  "空白用 blank；空容器用 empty；倒水用 pour。")


G("其他与另一个", [("other",None,""),("another",None,"")],
  "other 指其他的（the other 两者中的另一个，others 别人）；another 指三者以上中的另一个。",
  "the other day；each other；one another；another cup of tea",
  "其他的用 other；再来一个用 another。")

G("航空", [("plane",None,""),("airplane",None,""),("airport",None,""),("pilot",None,""),("flight",None,"")],
  "plane 是 airplane 的口语缩略，都指飞机；airport 指机场；pilot 指飞行员；flight 指航班、飞行。",
  "by plane；take a plane；at the airport；Flight CA938",
  "飞机用 plane(=airplane)；机场用 airport；飞行员用 pilot；航班用 flight。")

G("交通与车辆", [("traffic",None,""),("truck",None,""),("railway",None,""),("transport",None,""),("cycle",None,"自行车")],
  "traffic 指交通（流量，不可数）；truck 指卡车；railway 指铁路；transport 指运输、交通工具；cycle 作名词指自行车，作动词指骑自行车，也可指循环。",
  "heavy traffic；traffic lights；by railway；public transport；cycle to school",
  "交通流量用 traffic；卡车用 truck；铁路用 railway；运输用 transport；骑自行车用 cycle。")

G("加入与出席", [("join",None,""),("attend",None,""),("meeting",None,""),("absent",None,"反义对照")],
  "join 指加入（团体、人群，join sb./the club）；attend 指出席、参加（会议、课程，较正式）；meeting 指会议（attend/hold a meeting）；absent 指缺席的（be absent from，反义对照）。",
  "join the army/club；join in；attend a meeting/school；be absent from school",
  "加入团体用 join；出席会议上课用 attend；缺席用 absent(from)。")

G("鼓励与支持", [("encourage",None,""),("support",None,""),("provide",None,"")],
  "encourage 指鼓励（encourage sb. to do）；support 指支持、支撑；provide 指提供（provide sth. for sb. / provide sb. with sth.）。",
  "encourage sb. to do；support one's family；provide sth. for sb. / provide sb. with sth.",
  "鼓励用 encourage；支持用 support；提供用 provide。")

G("学校与场馆", [("classroom",None,""),("library",None,""),("museum",None,""),("pupil",None,""),("educate",None,"")],
  "classroom 指教室；library 指图书馆；museum 指博物馆；pupil 指（中）小学生；educate 指教育。",
  "in the classroom；borrow books from the library；visit the museum；educate children",
  "教室 classroom；图书馆 library；博物馆 museum；小学生 pupil；教育 educate。")

G("表情与动作", [("laugh",None,""),("gesture",None,"")],
  "laugh 指笑（laugh at 嘲笑）；gesture 指手势、姿态。",
  "laugh at；burst into laughter；make a gesture",
  "笑用 laugh（嘲笑 laugh at）；手势用 gesture。")

G("敲踢与抛扔", [("knock",None,""),("kick",None,""),("blow",None,"打击"),("throw",None,"")],
  "knock 指敲（knock at/on the door）；kick 指踢；blow 作名词指打击，作动词指吹、刮；throw 指扔、投（threw, thrown）。",
  "knock at the door；kick the ball；blow the wind；throw away",
  "敲门 knock；踢 kick；吹刮 blow；扔 throw。")

G("登山", [("climb",None,""),("mountain",None,"")],
  "climb 指攀登、爬；mountain 指山（climb the mountain 爬山）。",
  "climb the mountain/tree；high mountains",
  "爬用 climb；山用 mountain。")

G("职业", [("driver",None,""),("farmer",None,""),("worker",None,"")],
  "driver 指司机；farmer 指农民；worker 指工人。",
  "a bus/taxi driver；work on a farm；factory workers",
  "司机 driver；农民 farmer；工人 worker。")

G("厚重与单薄", [("heavy",None,""),("thin",None,"")],
  "heavy 指重的、大量的（heavy rain/traffic）；thin 指瘦的、薄的、稀的。",
  "a heavy box/rain；thin ice；a thin man",
  "重、大（雨、交通）用 heavy；瘦、薄用 thin。")

G("烟与燃料", [("smoke",None,""),("gas",None,""),("steam",None,""),("fuel",None,""),("coal",None,"")],
  "smoke 指烟（作动词指抽烟）；gas 指气体、煤气、汽油（美式）；steam 指蒸汽；fuel 指燃料（总称）；coal 指煤。",
  "No smoking；cook with gas；steam engines；burn fuel/coal",
  "烟用 smoke；煤气汽油用 gas；蒸汽用 steam；燃料总称 fuel；煤用 coal。")

G("无聊", [("boring",None,""),("bored",None,"")],
  "boring 指（事物）令人无聊的；bored 指（人）感到无聊的。",
  "a boring film；be/feel bored",
  "物令人无聊用 boring；人感到无聊用 bored。")

G("勤奋与懒惰", [("active",None,""),("lazy",None,"")],
  "active 指活跃的、积极的（be active in）；lazy 指懒惰的（反义对照）。",
  "take an active part in；a lazy boy",
  "积极主动用 active；懒惰用 lazy。")

G("情况与位置", [("situation",None,""),("condition",None,""),("position",None,""),("location",None,""),("scene",None,"")],
  "situation 指形势、处境；condition 指条件、状况；position 指位置、职位、立场；location 指（地理）位置、地点；scene 指场景、现场、景色。",
  "in a difficult situation；living conditions；in position；the location of；the scene of the accident",
  "处境用 situation；条件状况用 condition；职位位置用 position；地点用 location；现场场景用 scene。")

G("方式与风格", [("method",None,""),("system",None,""),("pattern",None,""),("style",None,"")],
  "method 指方法（有条理的）；system 指系统、制度；pattern 指模式、图案；style 指风格、款式。",
  "a teaching method；the method of；a system of；behavior patterns；in style；life style",
  "方法用 method；系统制度用 system；模式图案用 pattern；风格款式用 style。")

G("组织", [("organize",None,""),("organization",None,"organize 的名词")],
  "organize 是动词，指组织、安排；organization 是名词，指组织、机构。",
  "organize an activity；an international organization",
  "动词组织用 organize；名词机构用 organization。")

G("尊敬与钦佩", [("respect",None,""),("admire",None,"")],
  "respect 指尊敬、尊重（人、规则）；admire 指钦佩、羡慕（才华、成就）。",
  "respect one's teachers；admire sb. for sth.",
  "尊敬用 respect；钦佩羡慕用 admire。")

G("主要", [("mainly",None,""),("major",None,"")],
  "mainly 是副词“主要地”；major 是形容词“主要的、重大的”（major in 主修）。",
  "mainly because；a major problem；major in English",
  "副词主要用 mainly；形容词主要的用 major。")

G("动物", [("animal",None,""),("butterfly",None,"")],
  "animal 指动物（总称）；butterfly 指蝴蝶。",
  "wild animals；a beautiful butterfly",
  "动物总称用 animal；蝴蝶用 butterfly。")

G("地域", [("village",None,""),("province",None,""),("capital",None,"")],
  "village 指村庄；province 指省；capital 指首都（也可指资本、大写字母）。",
  "a small village；Sichuan Province；the capital of China",
  "村庄用 village；省用 province；首都用 capital。")

G("颜色与气色", [("gray",None,""),("pale",None,"")],
  "gray 指灰色的（英式拼写 grey）；pale 指苍白的（脸色）。",
  "gray hair；turn pale",
  "灰色用 gray；苍白用 pale。")

# ---------- 组装 ----------
def build():
    groups = []
    used = {}  # rank -> topic
    errors = []
    for i, (topic, members, usage, colloc, summary) in enumerate(GROUPS, 1):
        mem_out = []
        pos_parts = []
        for word, rank, note in members:
            cands = BY_WORD.get(word)
            if not cands:
                errors.append(f"未知单词: {word} (组 {topic})")
                continue
            e = cands[0] if rank is None else next((c for c in cands if c['rank'] == rank), None)
            if e is None:
                errors.append(f"找不到词条: {word} rank={rank}")
                continue
            if e['rank'] in used:
                errors.append(f"重复分组: {word}(rank {e['rank']}) 同时在「{used[e['rank']]}」和「{topic}」")
            used[e['rank']] = topic
            poses = extract_pos(e['def'])
            mem_out.append({
                "rank": e['rank'],
                "word": e['word'],
                "pos": poses,
                "gloss": e['def'],
                "note": note,
                "pronunciation": f"英[{e['uk']}]  美[{e['us']}]",
                "frequency": f"Section {e['section']}（{SECTION_FREQ[e['section']]}）",
                "example": e['ex'],
            })
            cn = "、".join(f"{p}（{POS_CN.get(p,p)}）" for p in poses)
            pos_parts.append(f"{e['word']}：{cn}")
        groups.append({
            "id": f"G{i:03d}",
            "topic": topic,
            "member_count": len(mem_out),
            "members": mem_out,
            "analysis": {
                "pos_difference": "；".join(pos_parts) + "。",
                "usage_difference": usage,
                "collocation": colloc,
                "summary": summary,
            },
        })
    uncovered = [e for e in ENTRIES if e['rank'] not in used]
    return groups, uncovered, errors

groups, uncovered, errors = build()
if errors:
    print("!! 错误：")
    for e in errors:
        print("  -", e)
    sys.exit(1)

data = {
    "meta": {
        "title": "中考高频词同义/近义辨析（688 词版）",
        "source_repo": "https://github.com/yiyisheh/ZK-vocabulary",
        "source_file": "中考/output/high_freq_zhongkao.txt",
        "source_order": "按历年中考真题出现频次排序，Section 1 为最高频",
        "generated_at": "2026-09-12",
        "word_list_size": 688,
        "group_count": len(groups),
        "covered_word_count": 688 - len(uncovered),
        "uncovered_word_count": len(uncovered),
        "uncovered_words": [e['word'] for e in uncovered],
        "grouping_policy": "同一词条只进入一个最核心的小组；同根词与近义词合并；跨组关系尽量在辨析文字中说明，不重复占位。",
        "fields": {
            "groups[].topic": "同义/近义或易混主题",
            "groups[].members[].rank": "该词在 688 词表中的频次排名",
            "groups[].members[].pos": "从原词表释义自动提取的词性",
            "groups[].members[].gloss": "原词表释义",
            "groups[].members[].note": "词形变化或组内角色提示",
            "groups[].members[].pronunciation": "英式/美式音标",
            "groups[].members[].frequency": "所属 Section 及对应真题出现次数门槛",
            "groups[].members[].example": "原词表例句及中文译文",
            "groups[].analysis.pos_difference": "成员词词性差异",
            "groups[].analysis.usage_difference": "语境、语义侧重点和语体差异",
            "groups[].analysis.collocation": "常见搭配或句型",
            "groups[].analysis.summary": "一句话选用总结"
        }
    },
    "groups": groups,
}
with open('中考高频词同义辨析.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f"OK: {len(groups)} 组, 覆盖 {688 - len(uncovered)}/688, 未覆盖 {len(uncovered)}: {[e['word'] for e in uncovered]}")