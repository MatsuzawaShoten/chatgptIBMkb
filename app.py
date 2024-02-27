import chainlit as cl


# chainlit run app.py で実行
@cl.on_message
async def main(message: str):
    await cl.Message(content="こんにちは").send()
