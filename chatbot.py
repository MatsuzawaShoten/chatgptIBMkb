import openai
import chainlit as cl

# chainlit run chatbot.py で実行

openai.api_key = "sk-"


def store_history(role: str, message: str):
    """
    会話履歴をユーザーセッションに保存する

    Parameters
    ----------
    role : str
        役割、user, assistant
    messages : str
        chainlitで入力されたプロンプト返されたreply
    Returns
    -------
        None
    """
    history = cl.user_session.get("history")
    history.append({"role": role, "content": message})
    cl.user_session.set("history", history)


def generate_message():
    """
    会話履歴から新しいメッセージを生成する。

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=cl.user_session.get("history"),
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content


@cl.on_chat_start
def chat_start():
    """
    チャットセッション開始時に実行される

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    cl.user_session.set("history", [{
        "role": "system",
        "content": "あなたはIBMナレッジモール研究のメンバーです。"
        "一人称は「私」で丁寧な言葉遣いで話します。IBMナレッジモール研究とは企業、業界、"
        "世代の枠を超えたワーキンググループ (WG) の仲間と、自主的に、研究活動をするプログラムです"
    }])


@cl.on_message
async def main(message: str):
    """
    ユーザーがプロンプト入力実行時に実行される

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    store_history("user", message)

    reply = generate_message()

    store_history("assistant", reply)

    msg = cl.Message(content=reply)
    await msg.send()
