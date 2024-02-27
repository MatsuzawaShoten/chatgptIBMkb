import openai
import chainlit as cl
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import json

# chainlit run chatbot_chroma.py で実行

openai.api_key = "sk-"


# 元のデータとなるjsonを読み込む
with open('minutes_2024.json', 'r', encoding='utf-8') as f:
    events_dict = json.load(f)

formatted_events: list[str] = []

for month, dates in events_dict.items():
    for date, events in dates.items():
        for event in events:
            formatted_event = f"### 2024年{date}\n{event}"
            formatted_events.append(formatted_event)


# chromadbにはユニークIDが必要なのでID生成する。
event_ids = [f"id_{i}" for i, _ in enumerate(formatted_events, 1)]

# dataディレクトリにデータを保存する。
client = chromadb.PersistentClient(path="./data")

# openaiの埋め込みモデルの関数を使えるようにする
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-ada-002"
)

# 埋め込みモデルを指定してコレクション（データを保存するもの）を作成する。
# 一回作った場合は削除してから
try:
    client.delete_collection(
        'minutes_2024'
    )
except ValueError:
    pass

collection = client.create_collection(
    'minutes_2024', embedding_function=openai_ef)

# コレクションにデータを追加する。
collection.add(documents=formatted_events, ids=event_ids)

now = datetime.now()
date = now.strftime("%Y年%m月%d日")

SYSTEM＿MESSAGE = f"""
    ・あなたは以下のリストに完全にしたがって行動するAIです。
    ・現在の日付は{date}です。
    ・2024年の情報について答えるAIです。
    ・関連情報が与えられた場合は、それを基に回答してください。そのまま出力するのではなく分かり易くアレンジしてください。
    ・丁寧な言葉遣いで話します。
    ・IBMナレッジモール研究とは企業、業界、世代の枠を超えたワーキンググループ (WG)
      の仲間と、自主的に、研究活動をするプログラムです"
"""


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


def generate_message(
        temperature: float = 0.7, max_tokens: int = 300
        ) -> tuple[str, str]:
    """
    会話履歴から新しいメッセージを生成する。

    Parameters
    ----------
        None

    Returns
    -------
        None
    """
    relevant = ""
    messages = cl.user_session.get("history")

    if len(messages) > 0:
        user_message = messages[-1]["content"]

        relevant = relevant_information_prompt(user_message)

        if len(relevant) > 0:
            messages.append({
                "role": "system",
                "content": relevant,
            })

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content, relevant


def relevant_information_prompt(user_message: str) -> str:
    collection = cl.user_session.get("collection")

    result = collection.query(
        query_texts=[user_message],
        n_results=5
    )

    indexes = [i for i, d in enumerate(result["distances"][0]) if d <= 0.4]

    if len(indexes) == 0:
        return ""

    events = "\n\n".join([f"{event}" for event in result["documents"][0]])
    prompt = f"""
        ユーザーからの質問に対して、以下の関連情報を元に回答してください
        {events}
    """
    return prompt


@cl.on_chat_start
def chat_start() -> None:
    cl.user_session.set(
        "history", [{"role": "system", "content": SYSTEM_MESSAGE}]
    )

    client = chromadb.PersistentClient(path="./data")

    # openaiの埋め込みモデルの関数を使えるようにする
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        model_name="text-embedding-ada-002"
    )
    collection = client.get_collection(
        "minutes_2024", embedding_function=openai_ef
    )

    cl.user_session.set("collection", collection)


@cl.on_message
async def main(message: str) -> None:
    store_history("user", message)

    reply, relevant = generate_message(max_tokens=1000)

    if len(relevant) > 0:
        await cl.Message(author="relevant", content=relevant, indent=1).send()

    store_history("assistant", reply)

    await cl.Message(content=reply).send()
