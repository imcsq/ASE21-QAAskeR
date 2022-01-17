import numpy as np
import argparse


def main():
    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument(
        "--data_NatQA_dev_tsv",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--NatQA_output_file",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--NatQA_npy",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    with open(args.NatQA_output_file, "r", encoding='utf-8', errors='ignore') as fdata:
        lines = fdata.readlines()
    output = []
    for line in lines:
        output.append(line.strip("\n"))

    all_question = []
    all_answer = []
    all_article = []
    all_index = []
    with open(args.data_NatQA_dev_tsv, "r", encoding='utf-8', errors='ignore') as f:
        cnt = 0
        invalid_lines = 0
        num = -1
        for line in f:
            num += 1
            question_article, answer = line.split("\t")
            question, article = question_article.split("\\n")
            all_question.append(question)
            all_answer.append(answer.strip())
            all_article.append(article)
            all_index.append(num)
    
    data_save_in_npy = []
    for index in range(len(output)):
        if "no answer" not in output[index]:
            data_save_in_npy.append([all_question[index], output[index], all_article[index], all_index[index], "NatQA", all_answer[index]])
    np.save(args.NatQA_npy, data_save_in_npy)


if __name__ == "__main__":
    main()