from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


class InsuranceModel:
    def __init__(self):
        self.model = None
        self.load_model()
        self.templete = self.format_prompt()
        self.chain = self.load()
    
    def load_model(self):
        self.model = OllamaLLM(model="deepseek-r1:8b", base_url="http://localhost:11434")
    def format_prompt(self):
        Template="""
            你是一个专业的分类器，严格判断问题是否与养老保险有关。请遵守：
            1. 只回答"是"或"否"（不带引号）
            2. "是"仅适用于直接涉及养老保险索赔，资格和流程的问题。
            3. "否"适用于以下情况：
            -问候/问候（你好/天气等。)
            -无关主题（餐饮/体育等)
            -模糊和无法判断意图的问题

            典型保险问题的例子：
            【是】养老金认证不合格怎么办？
            [是]索赔需要哪些材料
            [不]你好
            【不】今天天气怎么样
            [No]推荐附近的餐馆

            当前问题：
            {question}

            回答：
            """
        return Template
    def load(self):
        prompt = ChatPromptTemplate.from_template(self.templete)

        chain = prompt | self.model
        return chain
         


    def transcribe(self, question: str):
            return self.chain.invoke({"question": question})
