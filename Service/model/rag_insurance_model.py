from langchain.document_loaders import HuggingFaceDatasetLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline
from langchain import HuggingFacePipeline
from langchain.chains import RetrievalQA
import torch
from langchain_community.document_loaders import PyPDFLoader
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import UnstructuredExcelLoader


from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_ollama.llms import OllamaLLM

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class InsuranceModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_models()
    
    def load_models(self):
        self.model = OllamaLLM(model="deepseek-r1:14b", base_url="http://localhost:11434")
        self.embeddings = self.text_embedding()
        self.vector_store = self.vector_search()
        self.prompt = self.format_prompt()
        self.all_splits = self.doc_splitting()
        _ = self.vector_store.add_documents(documents=self.all_splits)
        self.graph = self.load() 
    def doc_splitting(self):
        loader = UnstructuredExcelLoader(r"D:\jincheng_project\RAG\pension_complaints_rewritten.xlsx", mode="elements")
        do = loader.load()

        all_splits  = RecursiveCharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=200,
                add_start_index=True
            ).split_documents(do)
        return all_splits
    def text_embedding(self):
        return HuggingFaceEmbeddings(model_name=r"D:\Backend_insurance\Algorithm\Fine_tuning\Models\all-mpnet-base-v2")
    def vector_search(self):
        embedding_dim = len(self.embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(embedding_dim)

        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        return vector_store
    
    def retrieve(self, state: State):
        retrieved_docs = self.vector_store.similarity_search(state["question"], k=1)
        if not retrieved_docs:
            return {"context": [Document(page_content="无相关信息")]}
        return {"context": retrieved_docs}

    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        formatted_prompt = self.prompt.format(question=state["question"], context=docs_content)
        
        # Get just the generated text without the prompt
        response = self.model(formatted_prompt)
        
        # Extract just the answer part (you may need to adjust this based on your model's output format)
        if isinstance(response, dict):
            answer = response.get("generated_text", "").replace(formatted_prompt, "").strip()
        else:
            answer = response.strip()
        
        return {"answer": answer}

    def format_prompt(self):
        Template = """
            你是一个专业的退休金索赔助理。 请根据您的专业知识直接回应用户的询问. 
            答案必须准确并使用专业语言（避免第一人称代词）。

            回应架构指引:
            1. 总是以适当的问候开始
            2. 提供最准确的资料
            3. 在已知时包括相关部门名称
            4. 概述必要的步骤（如适用）
            5. 在讨论法规时解释政策和要求采取的行动

            特殊情况:
            -如果要求提供电话号码：如果知道，请提供，否则说明信息不可用
            -如果被问及有关部门：命名部门并概述解决问题的步骤
            -如果被问及有关政策：解释政策及其规定的行动
            -如果信息不可用：清楚地说明你不知道什么

            上下文环境:
            {context}

            问题:
            {question}

            回应格式:
            [适当的问候][主要答案][如果需要，额外的指导][如果适当，关闭]

            示例结构:
            "日安。 关于您关于[主题]的问题，[明确答案]。 对于这个问题，你需要[步骤]。 这方面的相关部门是[部门]。 请让我知道，如果你需要任何澄清。"

            现在生成响应:
            """

        prompt = PromptTemplate.from_template(Template)
        return prompt
    def load(self):
        # Compile application and test
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        return graph

    def transcribe(self, question: str):
        response = self.graph.invoke({"question": question})    
        return str(response['answer']).split("</think>")[-1]