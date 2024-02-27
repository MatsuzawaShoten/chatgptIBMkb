import json
import chromadb
import openai
from chromadb.utils import embedding_functions


openai.api_key = "sk-"

# 元のデータとなるjsonを読み込む
with open('events_2023.json', 'r', encoding='utf-8') as f:
    events_dict = json.load(f)

formatted_events: list[str] = []

for month, dates in events_dict.items():
    for date, events in dates.items():
        for event in events:
            formatted_event = f"### 2023年{date}\n{event}"
            formatted_events.append(formatted_event)


# for event in formatted_events[:5]:
#     print(event)
#     print("----")

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
        'events_2023'
    )
except ValueError:
    pass

collection = client.create_collection(
    'events_2023', embedding_function=openai_ef)

# コレクションにデータを追加する。
collection.add(documents=formatted_events, ids=event_ids)

# ベクトルデータベースで「」を検索する。
result = collection.query(
    query_texts=['デパートに関するできごと'],
    n_results=5
)

# ベクトルが近い順に距離の値が表示
print(result['distances'])
# ベクトルが近い順に結果表示
print(result['documents'])
