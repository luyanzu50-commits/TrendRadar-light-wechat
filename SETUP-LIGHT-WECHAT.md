# TrendRadar 轻量个人微信推送部署说明

本目录已经按“GitHub Actions + 个人微信 + 关键词筛选 + 不接 AI API”的方案配置好。

## 1. 创建 GitHub 仓库

官方推荐从模板创建仓库：

1. 打开 `https://github.com/sansan0/TrendRadar`
2. 点击 `Use this template`
3. 选择 `Create a new repository`
4. 仓库名建议使用 `TrendRadar-light-wechat`

如果你想使用本地这份已改好的配置，把本目录推送到你新建的空仓库：

```bash
cd /Users/030cheems/Desktop/codex/Projects/TrendRadar-light-wechat
git remote add origin https://github.com/<你的用户名>/TrendRadar-light-wechat.git
git push -u origin main
```

## 2. 配置个人微信推送

在企业微信创建机器人 Webhook，然后在 GitHub 仓库里添加 Actions Secrets：

路径：`Settings -> Secrets and variables -> Actions -> New repository secret`

必填：

```text
WEWORK_WEBHOOK_URL=<你的企业微信 Webhook 地址>
WEWORK_MSG_TYPE=text
```

说明：个人微信推送必须用 `text`，所以消息是纯文本；企业微信群机器人可以用 Markdown，但这不是本方案。

## 3. 配置 Cloudflare R2 远程存储

GitHub Actions 每次运行后环境会销毁，建议配置 R2 保存历史数据和去重记录。

在 Cloudflare 创建 R2 bucket 和访问密钥后，添加这些 GitHub Secrets：

```text
S3_BUCKET_NAME=<你的 bucket 名称>
S3_ACCESS_KEY_ID=<R2 Access Key ID>
S3_SECRET_ACCESS_KEY=<R2 Secret Access Key>
S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
S3_REGION=auto
```

## 4. 当前配置摘要

- `.github/workflows/crawler.yml`
  - 北京时间 08:15 到 22:15，每 2 小时运行一次。
- `config/config.yaml`
  - `schedule.preset: "custom"`
  - `filter.method: "keyword"`
  - `ai_analysis.enabled: false`
  - `ai_translation.enabled: false`
  - `notification.channels.wework.msg_type: "text"`
- `config/timeline.yaml`
  - 默认只采集，不推送。
  - 08:00-10:00 推送早间速览。
  - 19:00-21:00 推送晚间汇总。
- `config/frequency_words.txt`
  - 只监控 AI工具/效率、医疗器械出海、海外营销/LinkedIn、竞品/行业动态。

## 5. 测试

添加 Secrets 后，在 GitHub 仓库：

1. 进入 `Actions`
2. 选择 `Get Hot News`
3. 点击 `Run workflow`
4. 等运行结束后查看 `Run crawler` 日志
5. 手机微信确认是否收到 TrendRadar 推送

如果 7 天后 workflow 自动停用，进入 `Actions -> Check In -> Run workflow` 续期。
