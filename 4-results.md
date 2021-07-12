## Detailed Test Results and Manual Inspection Record

We provide the raw test result files given by QAAskeR and the manual inspection records.

*All the data are stored in `results` directory.*

---

### Content Structure
```
results
┝━━ 1-test_result_of_original_model
│   ┝━━ SQuAD2_MR1
│   │      followup_input.tsv: follow-up inputs of the eligible test cases for original UnifiedQA model with MR1 on SQuAD2 test set.
│   │      pass.json: detail information of the passed cases.
│   │      violation.json: detail information of the violated cases.
│   ┝━━ SQuAD2_MR2: (content structure is similar to above.)
│   ┝━━ SQuAD2_MR3: (content structure is similar to above.)
│   ┝━━ BoolQ_MR3: (content structure is similar to above.)
│   ┝━━ NatQA_MR1: (content structure is similar to above.)
│   ┝━━ NatQA_MR2: (content structure is similar to above.)
│   ┕━━ NatQA_MR3: (content structure is similar to above.)
┝━━ 2-human_inspectation_result
│       SQuAD2_MR1.csv: the manual inspectation result on the revealed violations with MR1 on SQuAD2 test set.
│       ...(7 files in total)...
│       NatQA_MR3.csv: the manual inspectation result on the revealed violations with MR3 on NatQA test set.
┝━━ 3-test_result_of_new_retrained_model: (content structure is similar to `1-test_result_of_original_model`.)
┕━━ 4-test_result_of_google_search
        GoogleSearch.csv: the test result on Google Search service with 20 samples from MKQA dataset.
```

---

*Return to [README](README.md)*
