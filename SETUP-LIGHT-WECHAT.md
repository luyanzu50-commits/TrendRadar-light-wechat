# TrendRadar 轻量 ntfy 手机推送部署说明

本目录已经按“GitHub Actions + ntfy 手机推送 + 关键词筛选 + 不接付费 AI API”的方案配置好。

## 1. 创建 GitHub 仓库

官方推荐从模板创建仓库：

1. 打开 `https://github.com/sansan0/TrendRadar`
2. 点击 `Use this template`
3. 选择 `Create a new repository`
4. 仓库名建议使用 `TrendRadar-light-wechat`

如果你想使用本地这份已改好的配置，把本目录推送到你新建的空仓库：

```bash
cd /Users/030cheems/Documents/New\ project
git remote add origin https://github.com/<你的用户名>/TrendRadar-light-wechat.git
git push -u origin master
```

## 2. 配置 ntfy 手机推送

在手机安装 ntfy，订阅一个只有你知道的 topic，然后在 GitHub 仓库里添加 Actions Secrets：

路径：`Settings -> Secrets and variables -> Actions -> New repository secret`

必填：

```text
NTFY_TOPIC=<你的 ntfy topic>
```

可选：

```text
NTFY_SERVER_URL=https://ntfy.sh
NTFY_TOKEN=<私有 topic 才需要>
```

本方案不使用学校企业微信，也不创建企业微信群机器人，避免影响别人。

## 3. 存储策略

不配置 Cloudflare R2，保持轻量免费模式。

为了让“只采集不打扰”的运行结果能被晚间汇总继续使用，`.github/workflows/crawler.yml` 已使用 GitHub Actions cache 保存 `output/` 数据。这样不需要额外云存储，也能在多次 Actions 运行之间保留当天数据和去重记录。

## 4. 当前配置摘要

- `.github/workflows/crawler.yml`
  - 北京时间 08:15 到 22:15，每 2 小时运行一次。
  - 使用 GitHub Actions cache 保存 `output/`，不依赖 R2。
- `config/config.yaml`
  - `schedule.preset: "custom"`
  - `filter.method: "keyword"`
  - `ai_analysis.enabled: false`
  - `ai_translation.enabled: false`
  - `notification.channels.ntfy.server_url: "https://ntfy.sh"`
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
5. 手机 ntfy 确认是否收到 TrendRadar 推送

如果 7 天后 workflow 自动停用，进入 `Actions -> Check In -> Run workflow` 续期。
