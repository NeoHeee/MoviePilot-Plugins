# MoviePilot V2 MagicPush 消息通知插件

本插件监听 MoviePilot V2 的 `NoticeMessage` 通知事件，并通过 MagicPush 的 Token 推送接口发送消息。

## 功能

- 支持 MagicPush 自建地址和接口 Token
- 支持纯文本、Markdown、HTML
- 支持按 MoviePilot 通知类型筛选
- 支持在正文中附加海报
- 支持传递 MoviePilot 消息跳转链接
- 支持一键发送测试通知
- 自动跳过指定原生渠道的交互回复，减少重复消息

## MagicPush 端准备

1. 登录 MagicPush。
2. 新建一个“接口”。
3. 将需要使用的通知渠道绑定到该接口。
4. 复制该接口的 Token。
5. 先用以下命令测试 MagicPush 本身：

```bash
curl -X POST "http://你的MagicPush地址:端口/api/push/你的Token" \
  -H "Content-Type: application/json" \
  -d '{"title":"MagicPush测试","content":"接口工作正常","type":"markdown"}'
```

## 推荐安装方式：添加第三方插件仓库

1. 在 MoviePilot V2 的插件市场设置中添加该 GitHub 仓库地址。
2. 刷新插件市场，搜索“MagicPush消息通知”并安装。
3. 安装后进入插件配置页面填写参数。


## 插件配置

- **MagicPush地址**：例如 `http://192.168.1.10:3000`
- **接口Token**：MagicPush 接口页面生成的 Token
- **消息格式**：建议选择 Markdown
- **接收的通知类型**：留空代表全部接收
- **正文附加海报**：开启后将 MoviePilot 海报地址附加到正文
- **标题前缀**：例如 `[MoviePilot]`

填写完成后：

1. 开启“启用插件”。
2. 开启“发送测试通知”。
3. 保存配置。
4. MagicPush 收到测试消息后，再关闭“发送测试通知”并保存。

## 注意事项

- MoviePilot 原生通知渠道和本插件同时启用时，同一事件可能收到两次。
- 海报是否能显示取决于 MagicPush 下游通知渠道是否支持 Markdown 或 HTML 图片。
- MagicPush 和 MoviePilot 位于不同 Docker 网络时，请使用双方均可访问的 LAN 地址，不要填写 `localhost` 或 `127.0.0.1`。
- 如果填写的是完整地址 `/api/push/Token`，插件也能识别；通常只需填写 MagicPush 根地址和 Token。



# MoviePilot V2 MagicPush 控制中心

这是一个不依赖 MoviePilot 系统微信、Telegram 等通知客户端的插件。

## 工作方式

```text
MoviePilot普通通知 ─┐
MoviePilot命令结果 ─┼→ MagicPush入站Webhook → 已绑定的通知渠道
手机控制页/API ────→ MoviePilot命令执行
```

## 功能

- 监听 MoviePilot `NoticeMessage`，把下载、整理、订阅、站点和插件通知发送到 MagicPush。
- 使用 MagicPush 入站 Webhook，不需要 MoviePilot 原生通知客户端。
- 提供适合手机浏览器的独立控制页面。
- 可选择控制页允许执行的 MoviePilot 命令。
- 可修改命令显示名称、分类和显示状态。
- 危险命令二次确认。
- 提供安全令牌、调用频率限制和三秒重复通知抑制。
- 普通命令结果自动推送到 MagicPush。
- 媒体/种子选择列表会转换为只读文字摘要。

## 一、MagicPush端配置

1. 打开 MagicPush → 接口管理。
2. 新建或编辑接口，并绑定需要使用的通知渠道。
3. 开启“入站 Webhook”。
4. 数据来源选择“通用/Generic”。
5. 字段映射建议设置：

```text
标题：$.title
正文：$.content
类型：$.type
```

6. 保存后复制完整地址：

```text
http://MagicPush地址:端口/api/inbound/接口Token
```

MagicPush也支持标准字段直接提取，但当前入站接口要求先开启入站配置。

## 二、推荐安装方式：添加第三方插件仓库

1. 在 MoviePilot V2 的插件市场设置中添加该 GitHub 仓库地址。
2. 刷新插件市场，搜索“MagicPush控制中心”并安装。
3. 安装后进入插件配置页面填写参数。


## 三、插件配置

必须填写：

- 启用插件
- MagicPush入站Webhook完整地址

建议保持：

- 消息格式：Markdown
- 转发系统通知：开启
- 转发命令结果：开启
- 推送命令已提交：开启

“控制页/API安全令牌”留空保存后会自动生成。

## 四、打开手机控制页

安装并保存配置后，进入插件详情页，点击“打开控制页”。

地址格式：

```text
http://MoviePilot地址:3001/api/v1/plugin/MagicPushControl/console?token=控制令牌
```

可将该页面添加到手机桌面。

## 五、命令API

```http
POST /api/v1/plugin/MagicPushControl/execute
Content-Type: application/json
X-MagicPush-Control-Token: 控制令牌

{
  "command": "/version",
  "args": "",
  "confirm": false
}
```

危险命令必须传入：

```json
{
  "command": "/restart",
  "args": "",
  "confirm": true
}
```

## 六、命令显示设置

配置中的JSON只控制按钮显示，不改变命令实际功能：

```json
{
  "/version": {
    "title": "查看版本",
    "category": "系统管理",
    "show": true
  },
  "/restart": {
    "title": "重启MoviePilot",
    "category": "系统管理",
    "show": false
  }
}
```

## 限制

- MagicPush仍然是单向通知工具，命令由插件控制页或API发起。
- 依赖按钮二次交互的复杂命令会被转换为文字摘要，不能在MagicPush通知里继续点击操作。
- `/restart` 在系统重启前只能推送“命令已提交”，重启完成后的通知取决于MoviePilot自身的重启恢复逻辑。
- 建议仅在局域网或HTTPS反向代理下使用控制页。
- 不要把带控制令牌的控制页地址公开到互联网。
