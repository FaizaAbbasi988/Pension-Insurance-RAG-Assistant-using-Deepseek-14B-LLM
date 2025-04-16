# 如何运行项目（中文说明）
创建虚拟环境：
在终端中运行以下命令创建虚拟环境：
python -m venv insurance

激活虚拟环境：
在终端中运行以下命令激活虚拟环境：
insurance/Scripts/activate

安装依赖库：
在虚拟环境中运行以下命令安装项目依赖：
pip install -r requirements.txt

启动项目：
打开两个终端窗口，并在每个终端中激活虚拟环境。然后分别执行以下命令：

终端一（运行后端服务）：
uvicorn main:app --reload

终端二（运行前端 Streamlit 应用）：
streamlit run D:\Backend_insurance\Service\frontend\app.py
请根据你的本地路径修改上面的绝对路径。

# How to Run the Project (English Instructions)
Create a Virtual Environment:
Run the following command in your terminal:
python -m venv insurance

Activate the Virtual Environment:
Use the following command to activate it:
insurance/Scripts/activate

Install Dependencies:
Install all required libraries:
pip install -r requirements.txt

Start the Project:
Open two terminal windows and activate the virtual environment in both. Then run the following commands:

First Terminal (Run Backend API):
uvicorn main:app --reload

Second Terminal (Run Frontend using Streamlit):
streamlit run D:\Backend_insurance\Service\frontend\app.py
Make sure to change the absolute path according to your local setup.

