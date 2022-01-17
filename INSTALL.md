## Installation Instructions

### Prepare Environment for QAAskeR

QAAskeR depends on Python 3 and some necessary libraries. So, please first install Python 3 interpreter and execute the following commands to install the following libraries. 
*(We recommend you to use environment management tools (e.g., conda and virtualenv) to prepare a standalone python environment for QAAskeR.)*

```
conda create -n QAAskeR python=3.8
conda activate QAAskeR
pip install spacy==3.2.1
conda install -c conda-forge spacy-model-en_core_web_sm
pip install nltk==3.6.7
pip install benepar==0.2.0
conda install -c conda-forge pattern
pip install boto3==1.20.30
pip install rouge==1.0.1
pip install gensim==4.1.2
```


To facilitate the environment construction, we also provide the full dependency list file `requirements4tool.txt`. You can simply execute the following command to install the needed libraries:

```bash
pip install -r requirements4tool.txt
```

*Once the above installation is ready, you should be able to run QAAskeR by following the usage instruction in `1-tool.md`.*

---

### Prepare Environment for the Evaluation Experiment

At first, please follow the above steps to prepare the python environment for QAAskeR.

Then, you need to prepare *another* Python 3 environment for the SUT, `UnifiedQA`, as the SUT has a dependency requirement *Transformers<4.0.0* that conflicts with the requirement of `QAAskeR`. And please execute the following commands to install the necessary libraries in this new python environment for the SUT.

```bash
conda create -n SUT python=3.8
conda activate SUT
pip install transformers==3.2.0
pip install torch==1.10.1+cu113 torchvision==0.11.2+cu113 torchaudio==0.10.1+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
```
 
You can also directly execute the following command to install all the needed libraries with the provided dependency list file `requirements4replication.txt`.

```bash
pip install -r requirements4replication.txt
```

*Once the above installation is ready, you should be able to replicate our evaluation experiment by following the instruction in `2-replication.md`.*

---

*Return to [README](README.md)*
