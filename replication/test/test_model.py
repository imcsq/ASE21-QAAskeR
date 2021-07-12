from transformers import AutoTokenizer, T5ForConditionalGeneration
import torch
import argparse
from tqdm import tqdm
from torch.utils.data import DataLoader
from t5 import MyT5
import os

device = torch.device("cuda")


def run_model(data, model, tokenizer, all_question, **generator_args):
    all_ids = []
    for question in all_question:
        this_question = question.lower()
        input_ids = tokenizer.encode(this_question, return_tensors="pt")
        all_ids.append(input_ids)
    all_ids = tuple(t.to(device) for t in all_ids)
    for ids in tqdm(all_ids, desc="Evaluating"):
        res = model.generate(ids, **generator_args)
        out = tokenizer.batch_decode(res, skip_special_tokens=True)
        this_out = out[0]
        print(this_out, file=data)


def main():
    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument(
        "--model_name",
        default="allenai/unifiedqa-t5-large",
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--model_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--data_file",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--output_file",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    model_name = args.model_name
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    checkpoint = os.path.join(args.model_path)
    model = MyT5.from_pretrained(model_name, state_dict=torch.load(checkpoint))
    model.to(device)
    print("Loading checkpoint")

    all_question = []
    all_answer = []

    with open(args.data_file, "r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            question, answer = line.split("\t")
            all_question.append(question)
            all_answer.append(answer)
    data = open(args.output_file, 'w', encoding='utf-8')
    run_model(data, model, tokenizer, all_question)
    data.close()


if __name__ == "__main__":
    main()



