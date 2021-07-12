## Installation Instructions

### Prepare Environment for QAAskeR

QAAskeR depends on Python 3 and some necessary libraries. So, please first install Python 3 interpreter and the following libraries. 
*(We recommend you to use environment management tools (e.g., conda and virtualenv) to prepare a standalone python environment for QAAskeR.)*

```
benepar==0.2.0
gensim==3.1.0
nltk==3.6.2
Pattern==3.6
rouge==1.0.0
spacy==2.0.13
transformers==4.8.2
en-core-web-sm==2.0.0
torch==1.7.1+cu110
```

To facilitate the environment construction, we also provide the full dependency list file `requirements4tool.txt`. You can simply execute the following command to install the needed libraries:

```bash
pip install -r requirements4tool.txt
```

*Once the above installation is ready, you should be able to run QAAskeR by following the usage instruction in `1-tool.md`.*

---

### Prepare Environment for the Evaluation Experiment

At first, please follow the above steps to prepare the python environment for QAAskeR.

Then, you need to prepare *another* Python 3 environment for the SUT, `UnifiedQA`, as the SUT has a dependency requirement *Transformers<4.0.0* that conflicts with the requirement of `QAAskeR`. And please install the following necessary libraries in this new python environment for the SUT.

```bash
transformers==3.2.0
torch==1.7.1+cu110
```
 
You can also directly execute the following command to install all the needed libraries with the provided dependency list file `requirements4replication.txt`.

```bash
pip install -r requirements4replication.txt
```

*Once the above installation is ready, you should be able to replicate our evaluation experiment by following the instruction in `2-replication.md`.*

---

*Return to [README](README.md)*
