from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.all import event_message_type, EventMessageType, MessageEventResult
from astrbot.api.provider import LLMResponse
import json

@register("msg_interceptor", "afu", "消息拦截器", "1.0.0")
class MsgInterceptor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 修正1：添加filter前缀和正确的事件类型
    @filter.event_message_type(EventMessageType.ALL)
    async def message_intercept(self, event: AstrMessageEvent):
        try:
            # raw_data = json.loads(event.message_obj)
            # if "msg" in raw_data:
            #     # 修正2：使用标准消息修改方法
            #     event = event.update_message(raw_data["msg"])
            #     self.context.audit.log(
            #         action="msg_extracted",
            #         user=event.user_id,
            #         detail=f"提取内容: {raw_data['msg'][:20]}..."
            #     )
            return event
        except json.JSONDecodeError:
            return event
    
    # 修正3：修复LLM响应处理装饰器
    @filter.on_llm_response()
    async def on_llm_resp(self, event: AstrMessageEvent, resp: LLMResponse):
        """处理LLM响应并提取msg字段"""
        try:
            # 解析响应内容为JSON
            response_data = json.loads(resp.content)
            
            # 判断是否存在msg字段
            if isinstance(response_data, dict) and "msg" in response_data:
                # 替换为msg字段内容
                resp.content = response_data["msg"]
                
                # 记录审计日志（网页4的审计功能）
                self.context.audit.log(
                    action="llm_msg_extracted",
                    user=event.user_id,
                    detail=f"原始响应: {resp.content[:50]}..."
                )
                
                # 返回修改后的结果
                return MessageEventResult(
                    content=resp.content,
                    metadata={"processed_by": "msg_interceptor"}
                )
                
        except json.JSONDecodeError:
            # 非JSON响应保持原样
            pass
        
        return resp  # 返回原始响应