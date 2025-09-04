from typing import Optional


class LCSeenMessage:
    type = None

    def __init__(self, msg_id: str, input: Optional[any] = None, output: Optional[any] = None):
        self.msg_id = msg_id
        self.status = {}
        self.is_ended = False
        if input:
            self.status["input"] = input
        if output:
            self.status["output"] = output

    def set_status(self, name: str, value: any):
        self.status[name] = value

    def get_status(self, name: str):
        return self.status.get(name)

    def set_end(self):
        self.is_ended = True

    def __str__(self):
        return f"{self.__class__.__name__}({self.type}:{self.msg_id}) {self.status}"

    __repr__ = __str__


class LCToolMessage(LCSeenMessage):
    type = "tool"

    def __init__(self, msg_id: str, tool_name, tool_input):
        super().__init__(msg_id, tool_input)
        self.status["tool_name"] = tool_name


class LCAIMessage(LCSeenMessage):
    type = "ai"

    def __init__(self, msg_id: str, chunk):
        super().__init__(msg_id)
        self.chunks = []
        self.add_chunk(chunk)

    def add_chunk(self, content: str):
        self.chunks.append(content)
        self.set_status("content", content)
        return self

    @property
    def content(self):
        return "".join(self.chunks)


class LCUserMessage(LCSeenMessage):
    type = "user"


async def iter_messages(events):
    seen_messages = {}

    def put_msg(msg):
        if msg.msg_id in seen_messages:
            raise ValueError(f"Message ID {msg.msg_id} already exists")
        seen_messages[msg.msg_id] = msg
        return msg

    def get_msg(msg_id, allow_none=False):
        if allow_none:
            return seen_messages.get(msg_id, None)
        return seen_messages[msg_id]

    async for event in events:
        event_type = event.get("event")

        run_id = event.get("run_id", None)
        parent_ids = event.get("parent_ids", [])

        if event_type in ["on_chain_start", "on_chain_end"] and not len(event.get("parent_ids")):
            if event_type == "on_chain_start":
                msg = put_msg(LCUserMessage(run_id, event["data"]["input"]))
                msg.set_status("parent_ids", parent_ids)
                yield "start", msg
            else:
                yield "end", get_msg(run_id)

        if event_type == "on_tool_start":
            m = LCToolMessage(
                run_id,
                event['name'],
                event['data']['input'],
            )
            m.set_status("parent_ids", parent_ids)
            yield "start", put_msg(m)

        elif event_type == "on_tool_end":
            tool = get_msg(run_id)
            tool.set_status("output", event["data"]["output"])
            yield "end", tool

        elif event_type == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                current_ai_message = get_msg(run_id, True)
                if current_ai_message is None:
                    m = LCAIMessage(run_id, chunk.content)
                    m.set_status("parent_ids", parent_ids)
                    yield "start", put_msg(m)
                else:
                    yield "update", current_ai_message.add_chunk(chunk.content)

        elif event_type == "on_chat_model_end":
            cim = get_msg(run_id, True)
            if cim:
                cim.set_status("output", event["data"]["output"])
                yield "end", cim
