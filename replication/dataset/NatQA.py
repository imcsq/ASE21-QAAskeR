import json
import csv
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
        "--NatQA_tsv",
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
            question = question.replace("\\", "")
            question = question.replace('"', "'")
            answer = answer.replace("\\", "")
            answer = answer.replace('"', "'")
            article = article.replace("\\", "")
            article = article.replace('"', "'")
            all_question.append(question)
            all_answer.append(answer.strip())
            all_article.append(article)
            all_index.append(num)

    with open(args.NatQA_tsv, 'w', encoding='utf-8') as f:
        tsv_w = csv.writer(f, delimiter='\t', lineterminator='\n')
        num = -1
        for answer in output:
            num += 1
            if "no answer" not in answer:
                tsv_w.writerow(
                    [all_question[num], output[num], all_article[num], all_index[num], "NatQA", all_answer[num]])


if __name__ == "__main__":
    main()
