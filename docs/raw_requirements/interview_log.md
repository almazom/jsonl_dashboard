# Interview Log — Artifact Nexus SDD Clarifications

**Project:** Artifact Nexus  
**Date Started:** February 17, 2026  
**Status:** In Progress

---

## Question 1: Где в JSONL файле хранится пользовательский запрос (промпт)?

**Дата:** February 17, 2026

### Исследование: Codex CLI Sessions

**Путь к сессиям:**
```
~/.codex/sessions/2026/{MM}/{DD}/rollout-{timestamp}-{uuid}.jsonl
```

**Пример файла:**
```
~/.codex/sessions/2026/02/17/rollout-2026-02-17T07-43-10-019c69e8-cde3-7881-80ab-bbbd6f17b1c7.jsonl
```

### Структура JSONL

| Тип события | Тип события | Где данные |
|-------------|-------------|------------|
| `session_meta` | Метаданные сессии | `payload.id`, `payload.cwd`, `payload.model_provider` |
| `response_item` (role: user) | **Запрос пользователя** | `payload.content[0].text` |
| `response_item` (role: assistant) | **Ответ агента** | `payload.content[0].text` |
| `turn_context` | Контекст turns | `payload.model`, `payload.cwd`, `payload.user_instructions` |
| `event_msg` (type: token_count) | **Токены** | `payload.info.total_token_usage.total_tokens` |
| `event_msg` (type: task_started/complete) | Статус сессии | `payload.type` |

### Примеры извлечения

```python
# Пользовательский промпт
if event['type'] == 'response_item' and event['payload'].get('role') == 'user':
    user_prompt = event['payload']['content'][0]['text']

# Ответ агента
if event['type'] == 'response_item' and event['payload'].get('role') == 'assistant':
    agent_response = event['payload']['content'][0]['text']

# Токены
if event['type'] == 'event_msg' and event['payload'].get('type') == 'token_count':
    tokens = event['payload']['info']['total_token_usage']['total_tokens']

# Timestamp
timestamp = event['timestamp']  # ISO 8601 формат

# Модель
if event['type'] == 'turn_context':
    model = event['payload']['model']
```

### Определение статуса сессии

| Статус | Критерий |
|--------|----------|
| `success` | Есть `event_msg` с `type: task_completed` без ошибок |
| `failure` | Есть `error` в событиях или `task_completed` с ошибкой |
| `interrupted` | Нет `task_completed` (сессия не завершена) |

### Пример токенов из JSONL

```json
{
  "timestamp": "2026-02-17T04:44:04.743Z",
  "type": "event_msg",
  "payload": {
    "type": "token_count",
    "info": {
      "total_token_usage": {
        "input_tokens": 20012,
        "cached_input_tokens": 17408,
        "output_tokens": 73,
        "reasoning_output_tokens": 40,
        "total_tokens": 20085
      },
      "last_token_usage": {
        "input_tokens": 10018,
        "cached_input_tokens": 9856,
        "output_tokens": 27,
        "reasoning_output_tokens": 11,
        "total_tokens": 10045
      },
      "model_context_window": 258400
    }
  }
}
```

---

## Pending Questions

### Question 2: Cognitive Router — что считать «неуверенностью» модели?

**Статус:** ⏳ Ожидает ответа

**Вопросы:**
- Что считается «неуверенностью»? (низкий confidence score? пустой ответ?)
- Кто определяет, что модель «упала» — таймаут, HTTP-ошибка, или JSON parse error?
- Сколько попыток retry на каждую модель в цепочке?

---

### Question 3: Контекстная стратегия — нет алгоритма

**Статус:** ⏳ Ожидает ответа

**Вопросы:**
- Что считается «взаимодействием»? (пара user+assistant? одно JSON-событие?)
- Как именно извлекаются «ошибки»? (по ключу `error`? по статусу `failed`?)
- Какой лимит токенов по умолчанию, если пользователь не задал в конфиге?

---

### Question 4: Статус сессии — нет логики определения

**Статус:** ✅ Частично решено (см. Question 1)

---

### Question 5: Project Root — нет алгоритма вычисления

**Статус:** ⏳ Ожидает ответа

**Вопросы:**
- Как он вычисляется? (родительская папка файла? поиск `.git/` вверх по дереву?)
- Если файл лежит в `/home/user/projects/foo/bar/baz.json` — что будет `project_root`?

---

### Question 6: Token Estimation — нет формулы

**Статус:** ⏳ Ожидает ответа

---

### Question 7: Watcher — нет деталей

**Статус:** ⏳ Ожидает ответа

---

### Question 8: Fuzzy Search — нет библиотеки

**Статус:** ⏳ Ожидает ответа

---

### Question 9: Стоимость — откуда данные

**Статус:** ⏳ Ожидает ответа

---

## Session Paths (CLI)

| CLI | Session Path | Format |
|-----|--------------|--------|
| **Codex** | `~/.codex/sessions/2026/{MM}/{DD}/rollout-*.jsonl` | JSONL |
| **Qwen** | `~/.qwen/projects/{project}/chats/{session-id}.jsonl` | JSONL |
| **Kimi** | `~/.kimi/sessions/{session-id}/{turn-id}/context.jsonl` | JSONL |
| **Gemini** | `~/.gemini/tmp/{project-hash}/chats/session-*.json` | JSON (не JSONL!) |

**Notes:**
- Qwen: project name — это escaped путь (например, `-home-pets-temp-jsonl-dashboard`)
- Gemini: project hash — SHA256 хеш пути проекта
- Gemini использует `.json` вместо `.jsonl`

---

## Summary

| № | Вопрос | Статус |
|---|--------|--------|
| 1 | JSONL структура (Codex) | ✅ Решено |
| 2 | Cognitive Router fallback | ✅ Решено |
| 3 | Project Root алгоритм | ✅ Решено |
| 4 | Session Summary | ✅ Решено |
| 5 | Token estimation | ✅ Решено (не нужен) |
| 6 | Watcher polling | ✅ Решено (30 сек) |
| 7 | Удаление файлов | ✅ Решено (не актуально) |
| 8 | Fuzzy Search библиотека | ✅ Решено (rapidfuzz) |
| 9 | Стоимость | ✅ Решено (не показываем) |
| 10 | Session paths (Codex, Qwen, Kimi, Gemini) | ✅ Решено |

---

**Interview завершён.** Все критические вопросы решены. Можно переходить к реализации.
