from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from unsloth import FastLanguageModel
import torch
from langchain_core.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline

template = """根据以下上下文信息回答问题。如果上下文不包含答案，请回答"根据提供的信息无法回答该问题"。

上下文:

问题: {question}
答案: """

class InsuranceModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(r"D:\Backend_insurance\Algorithm\Fine_tuning\merged_16bit", 
                                                  trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            r"D:\Backend_insurance\Algorithm\Fine_tuning\merged_16bit", 
            trust_remote_code=True,
            torch_dtype= torch.float16,device_map="cuda",
            load_in_4bit=True)
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, max_new_tokens=200)
        self.llm = HuggingFacePipeline(pipeline=self.pipe)

    def transcribe(self, question: str):
        self.prompt = PromptTemplate.from_template(template)
        self.chain = self.prompt | self.llm
        res = self.chain.invoke({"question": question})

        return str(res.split('答案:')[1])