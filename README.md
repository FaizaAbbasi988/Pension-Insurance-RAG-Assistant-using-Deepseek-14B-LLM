The Service part of code is present inside the Service.

How to run the code:

1) In one terminal create the environment using the below command

"Python -m venv insurance"

2) After the environment is created, activate it using below command

insurance/Scripts/activate

3) First Install all the libraries using below command

"pip install -r requirements.txt"

4) Now open two terminal, activate environment in both terminal and then write following line of command in both terminals

1st terminal: uvicorn main:app --reload
2nd terminal: streamlit run D:\Backend_insurance\Service\frontend\app.py ( change the absolute path according to your own need)