from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
import json

@register("msg_interceptor", "afu", "消息拦截器", "1.0.0")
class MsgInterceptor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 修正1：添加filter前缀和正确的事件类型
    @filter.event_message_type(EventMessageType.PRIVATE)
    async def message_intercept(self, event: AstrMessageEvent):
        try:
            raw_data = json.loads(event.raw_message)
            if "msg" in raw_data:
                # 修正2：使用标准消息修改方法
                event = event.update_message(raw_data["msg"])
                self.context.audit.log(
                    action="msg_extracted",
                    user=event.user_id,
                    detail=f"提取内容: {raw_data['msg'][:20]}..."
                )
            return event
        except json.JSONDecodeError:
            return event
    
    # 修正3：修复LLM响应处理装饰器
    @filter.on_llm_response()
    async def on_llm_resp(self, event: AstrMessageEvent, resp: LLMResponse):
        print(resp)  # 确保冒号结尾