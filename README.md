# MCCA  
**Minecraft Command Assistant**  

用人话描述指令，它可以帮你生成指令并输入到MC里

---

## 使用方式  
在运行前，需自行创建一个 `config.json` 文件，内容如下：  
```json
{
    "api_key": "*********************",
    "context_length": 3,
    "log_file": "log.txt",
    "model": "Qwen/Qwen3-32B"
}
```

### 参数说明  
- **`api_key`**  
  需前往 [硅基流动平台](https://cloud.siliconflow.cn/i/mVqMyTZk) 申请 API Key，替换上面的 `*********************`。  
- **`context_length`**  
  对话上下文记忆长度（默认保留最近 3 条记录）。  
- **`log_file`**  
  日志文件路径（默认为 `log.txt`）。  
- **`model`**  
  指定使用的 AI 模型（默认 `Qwen/Qwen3-32B`）。  

---

## 扩展用途  
通过修改 **提示词（Prompt）**，可适配更多场景，比如cmd指令生成
