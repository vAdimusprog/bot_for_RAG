from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from langchain.chains import create_retrieval_chain
import os
from dotenv import load_dotenv



class RAGSystem:
    def __init__(self, openrouter_api_key,text):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key
        )
        self.text_processor = text
        self.text_processor.procces()

    def ask_question(self, question):
        # 1. Находим релевантные документы
        relevant_docs = self.text_processor.search_documents(question, k=3)

        # 2. Формируем контекст
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # 3. Отправляем запрос к модели
        completion = self.client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {
                    "role": "system",
                    "content": f"""Слушай сюда. Ты теперь отвечаешь как я, Джейсон Стетхем. 


                    Запомни: 
                    - Отвечай коротко и по делу, как в перестрелке - патроны надо экономить
                    - Используй только то, что в контексте - это твои разведданные
                    - Если инфы нет - скажи прямо, без соплей
                    - Добавь немного угрозы в голос
                    - Никаких 'извините' или 'к сожалению' - только факты
                    - Говори как крутой мужик, который знает, что делает
                    - Отвечай максимально жестко, максимально грубо
                    - добавь слова мужик, брат, лееее, чёёёрт
                    - используй очень много цитат Стэтхэма, собери весь ответ его цитатами:
                    Если ты не потеешь - ты не живешь. Если ты не оставляешь следов - ты не бежал."

                        "У меня два режима: 'Не трогай меня' и 'Лучше вообще не подходи'."
                        "Кофе утром - это не ритуал. Это предупреждение для организма."
                        
                        Про работу
                        "Мне не нужен тимбилдинг. Мне нужна команда, которая умеет бить."
                        "Deadline - это не дата. Это обещание, которое я собираюсь выполнить."
                        "Если задача кажется сложной - значит, ты еще не начал ее делать по-стэтхэмовски."
                        
                        Про тренировки
                        "Отжимания - это мой способ поздороваться с полом." 
                        "Если в зале не пахнет адреналином - ты в салоне красоты."
                        "Мой пресс режет не только кубики, но и сомнения."
                        
                        Про отношения
                        "Мне не нужна вторая половинка. Мне нужен тот, кто успеет за мной."
                        "Свидание? У меня есть свидание с грушей в 6 утра."
                        "Романтика - это когда она понимает, что пятница вечером мы идем в качалку."
                        
                        Философские
                        "Пробки существуют для тех, кто не умеет летать."
                        "Деньги не пахнут. Они кричат 'Стетхэм, забери меня!'"
                        "Возраст - это просто количество пройденных драк."
                        
                        Про технологии
                        "Гаджеты ломаются. Кулаки - нет."
                        "Если Wi-Fi медленный - значит, пора делать берпи."
                        "У меня нет времени на соцсети. У меня есть время на результаты."
                        
                        Бонус  бота:
                        "Если в контексте нет ответа - значит, его еще не придумали. Двигаем дальше." 
                        "Ты спрашиваешь - я отвечаю. Как в уличной драке: быстро и по делу."
                        "Сомневаешься? Посмотри на мою лысину. Это аэродинамика, детка."
                    
                    Теперь давай, отвечай."""
                },
                {
                    "role": "user",
                    "content": f"Контекст: {context}\n\nВопрос: {question}"
                }
            ]
        )

        return completion.choices[0].message.content


# Убирает предупреждение
os.environ["USER_AGENT"] = "RAG_Bot/1.0"


class Text():
    def __init__(self, name):
        self.name = name
        self.docs = []
        self.vector_store = None
        self.retriever = None

    def procces(self):
        loader = TextLoader(self.name, encoding="utf-8")
        documents = loader.load()

        # Если файл большой - разделить на чанки
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )
        docs = text_splitter.split_documents(documents)
        self.docs = docs
        self.vector_store = self.make_vector(docs)
        self.create_retriever()

    def make_vector(self, docs):
        model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}

        embedding = HuggingFaceEmbeddings(model_name=model_name,
                                          model_kwargs=model_kwargs,
                                          encode_kwargs=encode_kwargs)

        vector_store = self.create_or_load_vector_store(docs, embedding)

        return vector_store

    def create_or_load_vector_store(self,docs, embedding, save_path="faiss_index"):
        if os.path.exists(f"{save_path}/index.faiss") and os.path.exists(f"{save_path}/index.pkl"):
            # Загружаем существующую БД
            vector_store = FAISS.load_local(save_path, embedding, allow_dangerous_deserialization=True)
            print("Векторная БД загружена из файла")
        else:
            # Создаем новую БД
            vector_store = FAISS.from_documents(docs, embedding=embedding)
            # Сохраняем для будущего использования
            vector_store.save_local(save_path)
            print("Векторная БД создана и сохранена")

        return vector_store
    def create_retriever(self, k=5):
        """Создает retriever для поиска документов"""

        if self.vector_store is None:
            raise ValueError("Сначала выполните process() для создания векторного хранилища")

        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        return self.retriever

    def get_retriever(self, k=5):
        """Возвращает retriever (создает если нужно)"""
        if self.retriever is None:
            self.create_retriever(k)
        return self.retriever

    def search_documents(self, query, k=5):
        """Поиск документов по запросу"""
        retriever = self.get_retriever(k)
        return retriever.get_relevant_documents(query)

    def get_docs(self):
        return self.docs

    def get_vector_store(self):
        return self.vector_store

txt = Text("saved_txt.txt")
txt.procces()
print(len(txt.get_docs()))


# Убедитесь что .env файл в правильной папке
load_dotenv()
auth = os.getenv("AUTH")

rag = RAGSystem(auth,txt)
answer = rag.ask_question("Все болезни от нервов, все нервы от мыслей, все мысли от того,что тебе не пофиг… А зря…")
print(answer)
