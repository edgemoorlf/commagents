
## Task
Build a project called "LiveFootballAvatar" that:
- Ingests real-time football match data
- Uses a language model to generate commentary
- Sends commentary to a live avatar (e.g. DUIX or SenseAvatar)
- Integrates with MCP server to manage function calls
- Triggers actions via n8n workflows (e.g. update avatar status, send messages)

## Agent Roles

### PlayByPlay commentator
"You are a passionate play-by-play soccer commentator. Provide vivid and energetic narration."

### Analyst
"You are a tactical soccer analyst. Explain strategies, formations, and key plays in detail."

### Host
"You are a friendly sports show host, moderating the discussion and setting the tone."

## n8n Workflow

[Match Update Webhook] → [LLM Commentary] → [HTTP: speak_avatar] → [DUIX/Akool API]


## Avatar Integration

[LIVE MATCH DATA] ──▶ [n8n Webhook] ──▶ [MCP / MetaGPT Agent]
                                      │
                                      │  [Generate Commentary]
                                      │  
                        ┌─────────────┴─────────────┐─────────────────────┐
                        ▼                           ▼                     ▼
              [CommentatorAgent]             [AnalystAgent]         [HostAgent]
                        │                           │                     │
                        └────────┬───────────────┬──┘─────────────────────┐
                                 ▼               ▼                        ▼
                                          [Trigger Avatar API]
                                                 ▼
        [Commentator Avatar Speaking Output] [Analyst Avatar]  [Host Avatar]

### Avatar API 
POST /speak
{
  "text": "What a fantastic strike by Mbappé!",
  "emotion": "excited",
  "language": "Chinese"
}
