### TLDR

This repo details code for a web app providing automated updates on applications for the
[Inisiatif Pendapatan Rakyat](https://ipr.epu.gov.my/about) portal.

### Getting Started
Please ask admin for credential access (the `secrets.toml` file) before you get started.  

Next, set up a virtual environment using the `requirements.txt`. The below 
instructions are for Git Bash on WSL/Linux; amend accordingly for your Operating System/CLI.

```
cd <local_dev_folder>
git clone https://github.com/dev-ipr/ipr-automated-updates

cd <local_venv_folder>
python -m venv venv
source venv/bin/activate

cd <local_dev_folder>/ipr-weekly-updates
pip install -r requirements.txt
streamlit run web_app/main.py
```

### Repo Structure

```
├── README.md
├── requirements.txt
├── .streamlit
│   └── config.toml
├── images
│   ├── ipr-logo.png
│   └── logo_kementerian_ekonomi.png
├── notebooks
│   └── update_applications.ipynb
└── web_app
    ├── __init__.py
    ├── load_data_utils.py
    ├── main.py
    └── security_utils.py
```
