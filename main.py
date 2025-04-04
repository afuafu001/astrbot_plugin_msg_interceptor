from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# @register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
# class MyPlugin(Star):
#     def __init__(self, context: Context):
#         super().__init__(context)
    
#     # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
#     @filter.command("helloworld")
#     async def helloworld(self, event: AstrMessageEvent):
#         '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
#         user_name = event.get_sender_name()
#         message_str = event.message_str # 用户发的纯文本消息字符串
#         message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
#         logger.info(message_chain)
#         yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

#     async def terminate(self):
#         '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
import json

@register("msg_interceptor", "消息拦截器", "1.0")
class MsgInterceptor(Star):
    def __init__(self, ctx):
        super().__init__(ctx)
        
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def message_intercept(self, event: AstrMessageEvent):
        try:
            # 解析JSON格式的原始消息
            raw_data = json.loads(event.raw_message)
            if "msg" in raw_data:
                # 替换为提取后的msg字段
                event.message = raw_data["msg"]
                # 记录审计日志（网页4的审计功能延伸）
                self.ctx.audit.log(
                    action="msg_extracted",
                    user=event.user_id,
                    detail=f"提取内容: {raw_data['msg'][:20]}..."
                )
            return event
        except json.JSONDecodeError:
            # 非JSON消息保持原样（网页3的错误处理参考）
            return event