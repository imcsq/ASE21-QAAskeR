import json
import gensim
import spacy
import argparse
import numpy as np
from numpy import *
from rouge import Rouge
from scipy import spatial
from nltk.corpus import stopwords
from gensim.models import FastText

stop_words = set(stopwords.words('english'))

rouge = Rouge()

nlp = spacy.load('en_core_web_sm')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path_to_vector",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--path_to_information",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--path_to_output_from_model",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--path_to_violation",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--path_to_pass",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    with open(args.path_to_output_from_model, "r", encoding="utf-8") as g:
        lines_g = g.readlines()

    model_answer = []
    for line in lines_g:
        this_answer = line.strip()
        model_answer.append(this_answer)

    all_info = np.load(args.path_to_information, allow_pickle=True)
    all_info = all_info.tolist()
    new_question = []
    GT = []
    target_answer = []
    statement = []
    yuananswer = []
    yuanquestion = []
    rouge_1_p = []
    rouge_1_r = []
    index = []
    this_dataset = []
    article = []
    for i in all_info:
        article.append(i["article"])
        new_question.append(i["new_question"])
        GT.append(i["GT"])
        target_answer.append(i["target_answer"].lower())
        statement.append(i["statement"])
        yuananswer.append(i["primary_answer"])
        yuanquestion.append(i["primary_question"])
        rouge_1_p.append(i["rouge_1_p"])
        rouge_1_r.append(i["rouge_1_r"])
        index.append(i["index"])
        this_dataset.append(i["dataset"])

    model = gensim.models.KeyedVectors.load_word2vec_format(args.path_to_vector)

    all_scores = []
    for i in range(len(target_answer)):
        doc_target_answer = nlp(target_answer[i])
        str_tokens_question = [token.text for token in doc_target_answer if token.text != ""]
        doc_model_answer = nlp(model_answer[i])
        str_model_answer = [token.text for token in doc_model_answer if token.text != ""]
        list1_0 = str_tokens_question
        list2_0 = str_model_answer
        list1 = [w for w in list1_0 if not w in stop_words]
        list2 = [w for w in list2_0 if not w in stop_words]
        score = []
        word_vectors = model.word_vec
        if list2 == [] or list1 == []:
            score = [0.0]
            average = 0.0
            all_scores.append([average, score])
            continue
        for word1 in list1:
            if word1 in model.key_to_index:
                a_list_score = []
                for word2 in list2:
                    if word2 in model.key_to_index:
                        similar = model.similarity(word1, word2)
                    else:
                        if word1 in word2:
                            similar = 1.0
                        else:
                            similar = int(word1 == word2)
                    a_list_score.append(similar)
                score.append(max(a_list_score))
            else:
                a_list_score = []
                for word2 in list2:
                    if word1 in word2:
                        similar = 1.0
                    else:
                        similar = int(word1 == word2)
                    a_list_score.append(similar)
                score.append(max(a_list_score))
        average = mean(score)
        all_scores.append([average, score])

    assert len(all_scores) == len(model_answer)
    assert len(model_answer) == len(target_answer)
    assert len(target_answer) == len(yuanquestion)
    assert len(yuanquestion) == len(yuananswer)
    assert len(yuananswer) == len(statement)
    assert len(statement) == len(new_question)

    violations = []
    pass_samples = []
    num = -1
    for i in all_scores:
        num += 1
        if i[0] > 0.6:
            pass_samples.append(num)
        else:
            violations.append(num)

    data_violation = open(args.path_to_violation, 'w', encoding='utf-8')
    data_pass = open(args.path_to_pass, 'w', encoding='utf-8')

    for i in violations:
        print("{\"source_question\": \"" + str(yuanquestion[i])
              + "\", \"ground_truth\": \"" + str(GT[i])
              + "\", \"source_answer\": \"" + str(yuananswer[i])
              + "\", \"article\": \"" + str(article[i])
              + "\", \"declarative_sentence\": \"" + str(statement[i])
              + "\", \"target_answer\": \"" + str(target_answer[i])
              + "\", \"new_question\": \"" + str(new_question[i])
              + "\", \"new_answer\": \"" + str(model_answer[i])
              + "\", \"rouge_1_p\": \"" + str(rouge_1_p[i])
              + "\", \"rouge_1_r\": \"" + str(rouge_1_r[i])
              + "\", \"index\": \"" + str(index[i])
              + "\", \"dataset\": \"" + str(this_dataset[i])
              + "\", \"similar_average\": \"" + str(all_scores[i][0])
              + "\", \"similar_scores\": \"" + str(all_scores[i][1]) + "\"}",
              file=data_violation)

    for i in pass_samples:
        print("{\"source_question\": \"" + str(yuanquestion[i])
              + "\", \"ground_truth\": \"" + str(GT[i])
              + "\", \"source_answer\": \"" + str(yuananswer[i])
              + "\", \"article\": \"" + str(article[i])
              + "\", \"declarative_sentence\": \"" + str(statement[i])
              + "\", \"target_answer\": \"" + str(target_answer[i])
              + "\", \"new_question\": \"" + str(new_question[i])
              + "\", \"new_answer\": \"" + str(model_answer[i])
              + "\", \"rouge_1_p\": \"" + str(rouge_1_p[i])
              + "\", \"rouge_1_r\": \"" + str(rouge_1_r[i])
              + "\", \"index\": \"" + str(index[i])
              + "\", \"dataset\": \"" + str(this_dataset[i])
              + "\", \"similar_average\": \"" + str(all_scores[i][0])
              + "\", \"similar_scores\": \"" + str(all_scores[i][1]) + "\"}",
              file=data_pass)

    print("violations number: ", len(violations))
    print("pass number: ", len(pass_samples))

    data_violation.close()
    data_pass.close()


if __name__ == "__main__":
    main()
