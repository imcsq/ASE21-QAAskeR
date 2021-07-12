import json
import csv
import argparse


def main():
    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument(
        "--data_BoolQ_dev_tsv",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--BoolQ_output_file",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--BoolQ_tsv",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    with open(args.BoolQ_output_file) as fdata:
        lines = fdata.readlines()
    output = []
    for line in lines:
        output.append(line.strip("\n"))

    all_question = []
    all_answer = []
    all_article = []
    all_index = []
    with open(args.data_BoolQ_dev_tsv, "r", encoding='utf-8', errors='ignore') as f:
        num = -1
        for line in f:
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
    with open(args.BoolQ_tsv, 'w', encoding='utf-8') as f:
        tsv_w = csv.writer(f, delimiter='\t', lineterminator='\n')
        num = -1
        for answer in output:
            num += 1
            if answer in ["yes", "no"]:
                tsv_w.writerow(
                    [all_question[num], output[num], all_article[num], all_index[num], "boolq", all_answer[num]])


if __name__ == "__main__":
    main()

