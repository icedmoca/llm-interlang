from bridge.bridge_protocol import InterlangBridge
from runners.batch_optimizer import BatchOptimizer

class ModelRouter:
    def __init__(self):
        self.models = {
            "chatgpt": InterlangBridge(mode="cdp"),
            "fast": InterlangBridge(mode="xdotool"),
        }
        self.optimizer = BatchOptimizer()

    def route(self, message: str):
        if message.startswith(". ?"):
            return self.models["chatgpt"]

        if "comp" in message:
            return self.models["fast"]

        return self.models["chatgpt"]

    def send(self, message: str):
        model = self.route(message)
        return model.send(message)

    def send_batch(self, messages):
        if not self.optimizer.should_batch(messages, self.models["chatgpt"].scorer):
            return [self.send(m) for m in messages]

        batch = ". " + " ; ".join([m[2:] if m.startswith(". ") else m for m in messages])
        return self.send(batch)
