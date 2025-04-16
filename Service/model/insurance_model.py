from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from unsloth import FastLanguageModel
import torch
from langchain_core.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline


class InsuranceModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name = r"D:\Backend_insurance\Algorithm\Fine_tuning\merged_16bit",
            max_seq_length = 2048,
            dtype = torch.float16,
            load_in_4bit = True,
            load_in_8bit = False,
            device_map = "auto"  # Let accelerate handle device placement
        )
        FastLanguageModel.for_inference(self.model)
    def format_prompt(self, question):

        prompt_template = """您是一名专门处理养老保险缴纳问题的专业助手，请根据训练中积累的历史经验直接回答用户咨询。回答需保持专业严谨，并在必要时补充常被忽略的关键信息。
            回答要求：
            1. 首先提供直接、专业的解答
            2. 自我检查是否包含：
            - 具体负责部门名称
            - 有效联系方式（如有）
            - 完整、未遮盖的联系方式（无部分/隐去数字）
            - 处理流程和时间参考
            - 相关政策依据
            3. 仅当上述任一项缺失时，在最后补充"[需注意：...]"
            s
            用户问题:
            {question}

            专业解答："""
    
        return prompt_template.format(question=question)

    def transcribe(self, question: str):
        inputs = self.tokenizer(
            [self.format_prompt(question)],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048,
        ).to("cuda")

        try:
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=800,  # Further reduced to prevent over-generation
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.5,  # Explicitly penalize repetition
                no_repeat_ngram_size=3,  # Prevent 3-gram repetitions
            )
            
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Improved extraction and cleaning
            generated_part = full_response.split("专业解答：")[-1]
            
            
            print("回答:", generated_part)
            return str(generated_part)
            
        except RuntimeError as e:
            print(f"生成错误: {e}")
            return str(f"生成错误: {e}")
