# Setting Up and Running the Project

Follow the steps below to set up the virtual environment, manage dependencies, and run the Streamlit application.

1. Create a Virtual Environment
Run the following command to create a virtual environment named venv:

python -m venv venv  

2. Activate the Virtual Environment
For Windows:

venv\Scripts\activate  

3. Fixing Activation Restrictions (if needed)
If the virtual environment doesn’t activate due to execution policy restrictions, use the following command to resolve it:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser  

4. Install Project Dependencies
To install all required dependencies specified in the requirements.txt file, run:

pip install -r requirements.txt  

5. Run the Streamlit Application
Launch the Streamlit application with the following command:

streamlit run "file_name.py"  