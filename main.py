from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.all import event_message_type, EventMessageType, MessageEventResult
from astrbot.api.provider import LLMResponse
from astrbot.core.message.message_event_result import (
    MessageEventResult,
    MessageChain,
    CommandResult,
    EventResultType,
)
from astrbot.core.message.component import Comp
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
    @filter.on_llm_response()
    async def on_llm_resp(self, event: AstrMessageEvent, resp: LLMResponse):
        try:
            # 获取消息链中的纯文本内容（网页1的响应处理方案）
            response_str = resp.completion_text
            
            # 解析JSON并验证msg字段（网页5的字段验证逻辑）
            if response_data := json.loads(response_str):
                if isinstance(response_data, dict) and (msg := response_data.get("msg")):
                    # 重构消息链（网页3的组件管理方案）
                    resp.result_chain = MessageChain([Comp.Plain(str(msg))])
                    return MessageEventResult(
                        content=str(msg),
                        metadata={"processor": "msg_interceptor"}
                    )
                    
            # 处理工具调用结果（网页2的异步处理特性）
            if resp.tools_call_args:
                for tool_arg in resp.tools_call_args:
                    if isinstance(tool_arg, dict) and "msg" in tool_arg:
                        return MessageEventResult(
                            content=str(tool_arg["msg"]),
                            metadata={"source": "tool_call"}
                        )
        
        except json.JSONDecodeError:
            # 非JSON响应保持原样（网页3的错误处理规范）
            pass
        
        return resp