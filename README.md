# 🚀 Streamlit Project Setup Guide
Welcome to your Streamlit project! Follow these simple steps to get everything up and running in no time. 💻✨

## 1️⃣ Create a Virtual Environment
First, let’s create a virtual environment to isolate your project dependencies:

```python
python -m venv venv
```  
🎉 Your environment is ready to go!

## 2️⃣ Activate the Virtual Environment
Activate the virtual environment based on your operating system:

Windows:
```bash
venv\Scripts\activate  
```

💡 You should now see (venv) in your terminal prompt!

## 3️⃣ Fix Activation Issues (If Any)
If you’re unable to activate the virtual environment due to execution policy restrictions, use this command to fix it:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser 
```
🔒 Problem solved!

## 4️⃣ Install Dependencies
Install all required libraries and dependencies from the requirements.txt file:
```python
pip install -r requirements.txt  
```
📦 Dependencies are now installed!

## 5️⃣ Run the Streamlit Application
Start your Streamlit app with the following command:
```bash
streamlit run "file_name.py"  
```
👉 Replace file_name.py with the actual name of your Python file.

## 💡 Pro Tips
Keep your requirements.txt file up to date by running:
```python
pip freeze > requirements.txt  
```
Use streamlit hello to explore the default Streamlit demo and test your setup.
## 🎯 You’re all set to build amazing things with Streamlit! If you face any issues, don’t hesitate to ask for help. Let’s make something awesome! 🚀