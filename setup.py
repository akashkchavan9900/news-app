from setuptools import setup, find_packages
from typing import List

HYPHEN_E_DOT='-e .'
def get_requirements(file_path:str)->List[str]:

    ''' Function to return the list of requirements'''

    requirements=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]

        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)

    return requirements

setup(
    name="news-summazrization-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),
    python_requires=">=3.10",
    author="Akash Chavan",
    author_email="akashkchavan9900@gmail.com",
    description="A web-based application for news summarization and sentiment analysis with TTS in Hindi",
)