## Experiment Replication Package

We provide the codes to replicate our experiments, including the scripts to train the t5-large-based UnifiedQA model and the scripts to answer the given test cases with the trained UnifiedQA model.

*All the codes for replicating the evaluation are stored in `replication` directory.*

---

### Data source
* We adopt the pre-processed SQuAD2, BoolQ, and NatQA datasets provided by UnifiedQA, which can be accessed at https://console.cloud.google.com/storage/browser/unifiedqa/data.
* The hybrid training set is the combination of the training set from SQuAD2, BoolQ, and NatQA.

---

### Usage Instruction

1) run `train/cli.py` to train the UnifiedQA model (SUT) on the hybrid training set with the hyper-parameters declared in our paper.
    ```bash
    python train/cli.py \
    --size large \
    --do_train \
    --output_dir path/to/output/dir/to/save/model/file \
    --train_file path/to/the/hybrid/train/tsv/file \
    --predict_file path/to/dev/tsv/file \
    --train_batch_size 3 \
    --predict_batch_size 8 \
    --do_lowercase \
    --eval_period 5000 \
    --learning_rate 2e-5 \
    --gradient_accumulation_steps 5 \
    --wait_step 10
    ```
2) run `test/test_model.py` to get SUT's outputs on the samples from the test set of each dataset, which are used as the source test cases.
    ```bash
    python test/test_model.py \
    --model_name allenai/unifiedqa-t5-large \
    --model_path path/to/model \
    --data_file path/to/dev/tsv/file \
    --output_file path/to/output/tsv/file
    # model_path is the path to the saved best checkpoint (finetuned model) obtained from step 1).
    ```
3) for each dataset, prepare the source test case information (by aggregating each source input and the corresponding source output into one information item) and dump the information into the corresponding `.tsv` file.
    ```bash
    python dataset/SQuAD2.py \
    --data_SQuAD2_dev_tsv path/to/source/input/tsv/file \
    --SQuAD2_output_file path/to/source/output/tsv/file \
    --SQuAD2_tsv path/to/output/combined/tsv/file
    
    python dataset/NatQA.py \
    --data_NatQA_dev_tsv path/to/source/input/tsv/file \
    --NatQA_output_file path/to/source/output/tsv/file \
    --NatQA_tsv path/to/output/combined/tsv/file
    
    python dataset/BoolQ.py \
    --data_BoolQ_dev_tsv path/to/source/input/tsv/file \
    --BoolQ_output_file path/to/source/output/tsv/file \
    --BoolQ_tsv path/to/output/combined/tsv/file
    ```
4) for each dataset, run `QAAskeR` to prepare the follow-up inputs with each MR, which are dumped into some `.tsv` files. *(refer to `1-tool.md` for details)*
5) run `test/test_model.py` to get SUT output for each of the follow-up inputs and dump the follow-up outputs into the corresponding `.tsv` files.
6) run `QAAskeR` to measure the violation and form the test report. *(refer to `1-tool.md` for details)*

---

*Return to [README](README.md)*
