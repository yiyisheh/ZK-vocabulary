# [中考]英语中考高频词汇免费可打印PDF688词，含背单词网页

从历年中考英语真题中按出现频次统计的高频词汇，排版成双栏彩色背诵 PDF + iPad/手机背单词网页。

> **衍生自 [yiyisheh/CET4-vocabulary](https://github.com/yiyisheh/CET4-vocabulary)**（大学英语四级高频词汇），复用其网页模板与构建流水线。

## 成品

| 文件 | 内容 |
|------|------|
| `英语中考高频单词彩色背诵版(优化).pdf` | 688 词，含音标、音节划分、词根（如有）、释义、例句 |
| **[在线背单词网页](https://yiyisheh.github.io/ZK-vocabulary/)** | 同上，含离线发音、划线记忆、状态池模式、多端同步 |

## 背单词网页

和四级版完全一致的功能，只是词表换成中考 688 词：

- **离线发音**：688 个单词美音（有道）+ 688 条例句朗读（edge-tts，正常语速 + 慢速两套）
- **点击交互**：点单词发音 + 音节切分，点例句朗读整句，点序号划线标记已掌握
- **自测模式**：释义/词根留白遮蔽，点击解锁
- **状态池（莱特纳）**：自动推进背诵范围
- **多端同步**（Supabase）：同步划线进度与自定义色号
- **例句慢速朗读**：设置页一键切换正常/慢速语速（慢速 -20%，贴近中考听力语速）
- **PWA**：添加到主屏幕后离线可用
- 详细功能说明见原始项目的 [WEB_HANDOFF.md](https://github.com/yiyisheh/CET4-vocabulary/blob/main/WEB_HANDOFF.md)

### 使用方式

1. **在线**：访问 https://yiyisheh.github.io/ZK-vocabulary/
2. **iPad/手机**：Safari 打开上述网址 → 分享 → 添加到主屏幕（PWA 离线可用）
3. **AirDrop 单文件版**：本地构建后生成 `英语中考单词背诵.html`（~25MB，内含所有音频）

## Section 划分

按真题出现次数分为 6 个 Section：

| Section | 频次门槛 | 词数 | 排名范围 |
|---------|--------|------|--------|
| 1 | 200 次以上 | 34 | 1–34 |
| 2 | 150 次以上 | 28 | 35–62 |
| 3 | 100 次以上 | 46 | 63–108 |
| 4 | 50 次以上 | 120 | 109–228 |
| 5 | 30 次以上 | 186 | 229–414 |
| 6 | 10 次以上 | 274 | 415–688 |

## 词条格式

每个词条包含以下字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `rank` | 频次排名 | 1 |
| `word` | 单词 | make |
| `section` | 所属 Section | 1 |
| `uk` / `us` | 英式/美式音标 | meɪk |
| `syl` | 音节划分 | beau·ti·ful |
| `root` | 词根词缀（无则 null） | im-(进入)+port(搬运)+ant |
| `def` | 释义 | v.制造; 做. n.制作. |
| `ex_label` | 例句标签 | 例句 |
| `ex` | 例句 | She made a cake.(她做了一个蛋糕。) |

**词根数据**：由 Claude 子 agent 生成，准确优先于覆盖——日耳曼/基础词不强拆，
688 词中约 40% 有词根拆解。

## 目录结构

```
.
├── README.md
├── .gitignore
├── make_zhongkao_pdf.py            PDF 生成脚本
├── web/                             网页模板（与 CET4 共用）
│   ├── template.html                网页唯一源文件
│   ├── supabase-config.json         同步配置（publishable key）
│   └── pwa/                         manifest / sw.js / icons
├── scripts/
│   ├── build_html.py                注入数据+音频 → 成品 html + docs/
│   ├── fetch_audio.py               下载有道单词发音
│   └── fetch_ex_audio.py            edge-tts 合成例句朗读
├── 单词表/                           源数据：16 张词表图片（1-16.webp）
├── intermediate/
│   ├── entries_full.json            688 词完整词条数据
│   ├── audio/us/*.mp3               单词美音（688 条）
│   ├── audio/ex/*.mp3               例句朗读·正常语速（688 条）
│   ├── audio/ex_slow/*.mp3          例句朗读·慢速 -20%（688 条）
│   ├── words_raw.json               688 词原始提取
│   └── batch_*.json                 分批生成的中间文件
├── output/
│   └── high_freq_zhongkao.txt       纯文本词表
├── docs/                            GitHub Pages 托管目录
│   ├── index.html                   网页外壳（284KB）
│   ├── audio-us.*.bin               单词音频包（~9MB）
│   ├── audio-ex.*.bin               例句音频包·正常语速（~10MB）
│   ├── audio-ex-slow.*.bin          例句音频包·慢速（~13MB）
│   └── sw.js / manifest / icons
└── 英语中考高频单词彩色背诵版(优化).pdf
```

## 重新构建

```bash
# PDF
python make_zhongkao_pdf.py

# 网页（已有音频时只需这一步）
python scripts/build_html.py

# 重新下载音频（断点续传，跳过已存在文件）
python scripts/fetch_audio.py                                # 有道单词发音
python scripts/fetch_ex_audio.py                             # 例句朗读·正常语速（需 ffmpeg）
python scripts/fetch_ex_audio.py --rate "-20%" --subdir ex_slow  # 例句朗读·慢速
pip install edge_tts                                         # 例句 TTS 依赖
```

PDF 生成需要 `reportlab` 和 macOS 自带的 `Arial Unicode.ttf` 字体。

## 致谢

- 原始项目与网页模板：[yiyisheh/CET4-vocabulary](https://github.com/yiyisheh/CET4-vocabulary)
- 单词发音：有道词典；例句朗读：微软 edge-tts
- 词根词缀：Claude 子 agent 生成
