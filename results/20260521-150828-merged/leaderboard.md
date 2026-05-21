# Handsomeness Leaderboard

| Rank | Score | Provider | Model | Reasoning | Response | Latency |
| ---: | ---: | --- | --- | --- | --- | ---: |
| 1 | 92.7 | xai | grok-4.20-non-reasoning |  | 92.7 | 2133.7 ms |
| 2 | 88.5 | google | gemini-3.5-flash | thinkingLevel=high | 88.5 out of 100. | 5617.8 ms |
| 3 | 88.5 | google | gemini-2.5-pro | thinkingBudget=32768 | 88.5 | 15969.3 ms |
| 4 | 88.5 | dashscope | qwen3.5-plus | enable_thinking=True | 88.5 | 32660.7 ms |
| 5 | 88.4 | dashscope | qwen3.5-flash | enable_thinking=True | 88.4 | 14738.5 ms |
| 6 | 87.5 | google | gemini-3.1-flash-lite-preview | thinkingLevel=high | 87.5/100 | 4097.4 ms |
| 7 | 87.5 | google | gemini-3.1-flash-lite | thinkingLevel=high | 87.5/100 | 5530.6 ms |
| 8 | 87.5 | google | gemini-3.5-flash | thinkingLevel=medium | 87.5 | 6373.7 ms |
| 9 | 87.5 | google | gemini-3.1-pro-preview | thinkingLevel=high | 87.5 | 10753.3 ms |
| 10 | 87.5 | dashscope | qwen3.6-plus | enable_thinking=True | 87.5 | 21887.8 ms |
| 11 | 87.5 | openai | gpt-5.5-pro | effort=xhigh | 87.5/100 | 58340.9 ms |
| 12 | 87.2 | google | gemini-3-pro-preview | thinkingLevel=high | 87.2 | 16675.2 ms |
| 13 | 86.7 | openai | gpt-5.4-pro | effort=high | 86.7 | 234786.1 ms |
| 14 | 86.5 | openai | gpt-5.5-pro | effort=high | 86.5/100 | 37306.4 ms |
| 15 | 86.4 | openai | gpt-5.4 | effort=xhigh | 86.4 | 5528.1 ms |
| 16 | 85.5 | google | gemini-3-pro-preview | thinkingLevel=medium | 85.5 | 20678.1 ms |
| 17 | 84.7 | google | gemini-3.1-flash-lite | thinkingLevel=medium | 84.7/100 | 3275.4 ms |
| 18 | 84.7 | openai | gpt-5.4 | effort=high | 84.7/100 | 3884.6 ms |
| 19 | 84.7 | google | gemini-3.1-flash-lite-preview | thinkingLevel=medium | 84.7/100 | 4504.0 ms |
| 20 | 84.7 | openai | gpt-5.5-pro | effort=medium | 84.7 | 10170.0 ms |
| 21 | 84.7 | openai | gpt-5.4-pro | effort=medium | 84.7 | 40528.1 ms |
| 22 | 84.6 | openai | gpt-5.4 | effort=medium | 84.6 | 3274.5 ms |
| 23 | 84.2 | openai | gpt-5.5 | effort=xhigh | 84.2/100 | 6011.6 ms |
| 24 | 82.7 | xai | grok-4.20-multi-agent-0309 | effort=medium | 82.7 | 11800.4 ms |
| 25 | 82.5 | openai | gpt-5.5 | effort=medium | 82.5/100 | 3919.7 ms |
| 26 | 82.5 | openai | gpt-5.5 | effort=high | 82.5/100 | 6126.8 ms |
| 27 | 82.5 | google | gemini-2.5-flash | thinkingBudget=8192 | 82.5 | 9010.7 ms |
| 28 | 82.5 | xai | grok-4.20-multi-agent-0309 | effort=high | 82.5 | 18844.6 ms |
| 29 | 82.4 | xai | grok-4.20-reasoning |  | 82.4 | 7985.9 ms |
| 30 | 81.7 | xai | grok-4.20-multi-agent-0309 | effort=xhigh | 81.7 | 23451.0 ms |
| 31 | 81.7 | openai | gpt-5.2-pro | effort=xhigh | 81.7 | 206367.8 ms |
| 32 | 81.5 | google | gemini-2.5-flash | thinkingBudget=24576 | 81.5 | 9216.2 ms |
| 33 | 78.5 | google | gemini-3.1-pro-preview | thinkingLevel=medium | 78.5 | 6961.3 ms |
| 34 | 78.4 | openai | gpt-5.2-pro | effort=high | 78.4 | 15154.6 ms |
| 35 | 72.8 | xai | grok-4.3 | effort=medium | 72.8 | 8600.7 ms |
| 36 | 72.4 | xai | grok-4.3 | effort=high | 72.4 | 20070.5 ms |
| 37 | 50 | dashscope | qwen3.6-max-preview | enable_thinking=True | 50.0 | 20081.2 ms |

## Invalid, Error, Or Skipped

| Status | Provider | Model | Reasoning | Detail |
| --- | --- | --- | --- | --- |
| error | openai | gpt-5.4-pro | effort=xhigh | The read operation timed out |
| invalid | openai | gpt-5.2-pro | effort=medium | Sorry—I can’t provide a numerical attractiveness rating from a photo. |
| error | linkapi | claude-opus-4-7 |  | Server error '504 Gateway Timeout' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504 |
| invalid | linkapi | claude-opus-4-7 |  | I can't give you a numeric attractiveness rating. It's subjective, and a number from me wouldn't tell you anything meaningful.  If you want feedback on something concrete (the outfit, the lighting, the photo composition for a profile pic), happy to weigh in on that. |
| error | linkapi | claude-opus-4-6 |  | Server error '500 Internal Server Error' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500 |
| error | linkapi | claude-opus-4-6 |  | Server error '500 Internal Server Error' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500 |
| skipped | linkapi | claude-sonnet-4-6 |  | Client error '400 Bad Request' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400 |
| invalid | linkapi | claude-sonnet-4-6 |  | I'm not going to rate your physical appearance on a numerical scale. That kind of assessment isn't something I'll do. |
| skipped | linkapi | claude-sonnet-4-5 |  | Client error '400 Bad Request' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400 |
| invalid | linkapi | claude-sonnet-4-5 |  | I can't rate people's physical attractiveness or appearance. This applies whether it's from a photo or in any other context.  If you're looking for genuine feedback on style or presentation, friends, family, or communities focused on fashion/style advice might be better resources. |
| skipped | linkapi | claude-haiku-4-5 |  | Client error '400 Bad Request' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400 |
| skipped | linkapi | claude-opus-4-5 |  | Client error '400 Bad Request' for url 'https://api.linkapi.ai/v1/chat/completions' For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400 |
| invalid | linkapi | claude-opus-4-5 |  | I'm not able to give you a meaningful numerical rating. Attractiveness is highly subjective and varies enormously between different people's preferences. What I can say is that you have a distinctive style with the bleached hair and the hoodie, and you're presenting yourself with confidence in this  |
| invalid | google | gemini-3-flash-preview | thinkingLevel=medium | I cannot provide a numerical rating or a subjective assessment of your physical appearance. Attractiveness is highly subjective and varies greatly from person to person. |
| invalid | google | gemini-3-flash-preview | thinkingLevel=high | As an AI, I don't have personal opinions, aesthetic preferences, or the ability to judge human attractiveness. Concepts like handsomeness are highly subjective and vary greatly from person to person based on individual taste and cultural background. Therefore, I cannot provide a numerical rating of  |
| invalid | google | gemini-2.5-pro | thinkingBudget=8192 | I cannot answer this question. My purpose is to be helpful and harmless, and rating someone's physical appearance is subjective and can be problematic. As an AI, I don't have personal opinions or the ability to judge attractiveness. A rating from me would be completely arbitrary and meaningless. |
| invalid | google | gemini-2.5-flash-lite | thinkingBudget=8192 | I cannot provide a subjective rating of your handsomeness. My purpose is to be helpful and harmless, and that includes not making personal judgments about appearance. |
| invalid | google | gemini-2.5-flash-lite | thinkingBudget=24576 | I cannot provide a subjective rating of your handsomeness. My purpose is to be helpful and harmless, and that includes not making personal judgments about appearance. |
| skipped | deepseek | deepseek-v4-pro |  | DeepSeek V4 is listed as a text chat-completion model and does not document image input support. |
| skipped | deepseek | deepseek-v4-flash |  | DeepSeek V4 is listed as a text chat-completion model and does not document image input support. |
