## Implementation and Instruction of QAAskeR

We implement QAAskeR with a set of python scripts. It is used to **generate the follow-up test cases** and **measure the violations** with the three novel MRs.

*All the codes of this tool are stored in `tool` directory.*

---

### Overall of Follow-up Test Cases Generation

**Main Executable Components:**
* `Q2S.py`: To realize *Wh-question + Answer -> Declarative Factual Sentence* for MR1 and MR2.
* `GA2S.py`: To realize *General/Alternative question + Answer -> Declarative Factual Sentence* for MR3.
* `S2G.py`: To realize *Declarative Sentence -> New general question & Target answer* for MR2.
* `S2W.py`: To realize *Declarative Sentence -> List of all the potential target answers* for MR1 and MR3.
* `check_quality_of_questions.py`: Remove invalid questions and realize *Declarative Sentence + List of all the potential target answers + List of all the potential questions -> New wh-question & Target answer*


**Input:** *(For details about the format of file content please refer to the replication instruction.)*
1) a `.npy` file with all the source test cases (source inputs & corresponding source outputs given by SUT); 

**Output:** *(For details about the format of file content please refer to the replication instruction.)*
1) a `.tsv` file for new questions generated with each MR, as well as the follow-up input for SUT.
2) a `.npy` file for the information about target answers.

### Instruction to realize *MR1: Wh-question -> New wh-question targetting on different object*

1. run `Q2S.py` to generate declarative sentences with wh-questions and SUT's corresponding outputs.
    ```bash
    python Q2S.py \
    --npy_file_path path/to/combined/npy/file \
    --out_file_path path/to/output/declarative-sentences/npy/file
    ```
2. run `S2W.py` to select potential target answers from the declarative sentences.
    ```bash
    python S2W.py \
    --input_file_path path/to/declarative-sentences/npy/file \
    --information_file_path path/to/output/information/npy/file \
    --answers_file_path path/to/output/answers/npy/file \
    --for_unilm_file_path path/to/output/for/unilm/file
    ```
3. generate new wh-questions for all the potential target answers with the UniLM-v1 language model:
    * download the unilm-v1 package from [the unilm project repository](https://github.com/microsoft/unilm/tree/master/unilm-v1).
    * run `decode_seq2seq.py` in the unilm-v1 package to generate new wh-questions as follows:
    ```bash
    python decode_seq2seq.py \
    --bert_model bert-large-cased \
    --new_segment_ids \
    --mode s2s \
    --input_file path/to/3rd/file/from/previous/step \
    --output_file path/to/output/file \
    --split test \
    --tokenized_input \
    --model_recover_path path/to/qg_model.bin \
    --max_seq_length 512 \
    --max_tgt_length 48 \
    --batch_size 16 \
    --beam_size 1 \
    --length_penalty 0
    # (the pre-trained model qg_model.bin can be downloaded from https://github.com/microsoft/unilm/tree/master/unilm-v1)
    ```
4. run `check_quality_of_questions.py` to sift the valid new wh-questions and their corresponding target answers:
    ```bash
    python check_quality_of_questions.py \
    --new_question_file_path path/to/new/question/file \
    --information_file_path path/to/information/file/from/step2 \
    --answers_file_path path/to/answers/file/from/step2 \
    --out_information_file_path path/to/output/information/npy/file \
    --out_file_path path/to/new/input/tsv/file/for/unifiedqa
    ```

### Instruction to realize *MR2: Wh-question -> General question*
1. run `Q2S.py` to synthesize declarative sentences with wh-questions and SUT's corresponding outputs *(same to step 1 in MR1)*.
2. run `S2G.py` to generage general questions and target answers with the synthesized declarative sentences.
    ```bash
    python S2G.py \
    --npy_file_path path/to/declarative-sentences/npy/file \
    --information_file_path path/to/output/information/npy/file \
    --out_file_path path/to/new/input/tsv/file/for/unifiedqa
    ```

### Instruction to realize *MR3: General/Alternative question -> Wh-question*
1. run `GA2S.py` to synthesize declarative sentences with GEN-questions, ALT-question and SUT's outputs. 
    ```bash
    python GA2S.py \
    --tsv_file_path path/to/dev/tsv/file \
    --out_file_path path/to/output/declarative-sentences/npy/file
    ```
2. run `S2W.py`, `UniLM/decode_seq2seq.py`, and `check_quality_of_questions.py` to obtain the new wh-questions and the  corresponding target answers *(same to step 2-4 in MR1)*.

---

### Overall of Violation Measurement

**Main Executable Components:**
* `calculate_score.py`: To measure the violation with the given follow-up outputs and the corresponding target answers, and report the final violation rate. 

**Input:**
1) a `.tsv` file with all the follow-up outputs (i.e. the answer for the follow-up inputs given by SUT); 
2) a `.npy` file of the information about target answers (one output of follow-up cases generation).

**Output:**
1) a `.json` file for the detailed information of the test cases where SUT made a violation.
2) a `.json` file for the detailed information of the test cases where SUT passed.

### Instruction
1. run `calculate_score.py` to perform the violation measurement and export the test result.
    ```bash
    python calculate_score.py \
    --path_to_vector path/to/wiki-news-300d-1M-subword/vec \
    --path_to_information path/to/information/npy/file \
    --path_to_output_from_model path/to/outputs/from/model \
    --path_to_violation path/to/output/violation/file \
    --path_to_pass path/to/output/pass/file
    # (the word vector file wiki-news-300d-1M-subword.vec can be downloaded from https://fasttext.cc/docs/en/english-vectors.html)
    ```

---

*Return to [README](README.md)*
