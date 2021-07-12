import json
import spacy
import string
import csv
import nltk
import argparse
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from pattern.en import conjugate, lemma, lexeme, PRESENT, INFINITIVE, PAST, FUTURE, SG, PLURAL, PROGRESSIVE

nlp = spacy.load('en_core_web_sm')

def tense(word):
    word_ = nlp(word)
    word_lemma = word_[0].lemma_
    word_doing = conjugate(word_lemma, tense=PRESENT, aspect=PROGRESSIVE)
    word_did = conjugate(word_lemma, tense=PAST)
    word_done = conjugate(word_lemma, tense=PAST, aspect=PROGRESSIVE)
    if word == word_doing:
        return 1
    elif word == word_did or word == word_done:
        return 2
    elif word == word_lemma:
        return 3
    else:
        return 4


def list_to_str(a_list):
    punc = string.punctuation
    special = ["-", "/"]
    this_special = ["$"]
    front_special = False
    str_out = ""
    num = -1
    for i in a_list:
        num += 1
        if num == 0:
            if i not in punc:
                str_out = str_out + i
            else:
                str_out = str_out + i
        else:
            if i in this_special:
                str_out = str_out + " " + i
            elif i == "'s":
                str_out = str_out + i
            elif i not in punc:
                if front_special:
                    str_out = str_out + i
                    front_special = False
                else:
                    str_out = str_out + " " + i
            else:
                if i in special:
                    front_special = True
                str_out = str_out + i
    return str_out


def S2I(a_question):
    question = str(a_question)
    question = question.replace("  ", " ")
    if question[-1] == " ":
        question = question[:-1]
    if "?" in question:
        question = question.replace("?", "")
    doc_question = nlp(question)
    tokens_question = [token for token in doc_question if token.string.strip() != ""]
    str_tokens_question = [token.string.strip() for token in tokens_question if token.string.strip() != ""]
    dep_tokens_question = [token.dep_ for token in doc_question if token.string.strip() != ""]
    pos_tokens_question = [token.pos_ for token in doc_question if token.string.strip() != ""]
    lemma_tokens_question = [token.lemma_ for token in doc_question if token.string.strip() != ""]
    root = str_tokens_question[dep_tokens_question.index("ROOT")]
    root_plc = dep_tokens_question.index("ROOT")
    punct_plc = len(tokens_question)
    if "," in str_tokens_question:
        punct_plc = str_tokens_question.index(",")
    nsubj_plc = -1
    if "nsubj" in dep_tokens_question:
        nsubj_plc = dep_tokens_question.index("nsubj")
    elif "nsubjpass" in dep_tokens_question:
        nsubj_plc = dep_tokens_question.index("nsubjpass")
    elif "conj" in dep_tokens_question:
        nsubj_plc = dep_tokens_question.index("conj")
    have_comma = False
    have_comma_do = False
    final_add = ""
    if nsubj_plc > punct_plc or root_plc > punct_plc or (lemma_tokens_question[0] in ["when", "if", "after", "before", "while"] and punct_plc != len(tokens_question)):
        all_comma = []
        num = 0
        for token in tokens_question:
            if token.string.strip() == ",":
                if pos_tokens_question[num-1] != "NUM" and pos_tokens_question[num+1] != "NUM":
                    all_comma.append(num)
                    have_comma = True
            num += 1
        small_question_start = 0
        if lemma_tokens_question[0] in ["when", "if", "after", "before", "while"]:
            small_question_start = punct_plc
            have_comma_do = True
        else:
            if have_comma:
                for comma in all_comma:
                    if nsubj_plc > comma:
                        small_question_start = comma
                        have_comma_do = True
        if have_comma_do:
            new_question = list_to_str(str_tokens_question[small_question_start + 1:])
            final_add = list_to_str(str_tokens_question[:small_question_start])
        else:
            new_question = question
        doc_new_question = nlp(new_question)
        tokens_question = [token for token in doc_new_question if token.string.strip() != ""]
        str_tokens_question = [token.string.strip() for token in doc_new_question if token.string.strip() != ""]
        pos_tokens_question = [token.pos_ for token in doc_new_question if token.string.strip() != ""]
        dep_tokens_question = [token.dep_ for token in doc_new_question if token.string.strip() != ""]
        lemma_tokens_question = [token.lemma_ for token in doc_new_question if token.string.strip() != ""]
        root = str_tokens_question[dep_tokens_question.index("ROOT")]
        root_plc = dep_tokens_question.index("ROOT")
    if root in ["be", "is", "are", "was", "were", "am"]:
        final = []
        str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
        final.extend([root])
        final.extend(str_tokens_question[:root_plc])
        final.extend(str_tokens_question[root_plc+1:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "?"
        else:
            final_out = final_out[0].upper() + final_out[1:] + "?"
        return final_out
    elif str_tokens_question[root_plc-1] in ["have", "has", "had", "be", "is", "are", "was", "were", "am", "would", "will", "could", "can", "may", "might", "should", "shall"]:
        final = []
        str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
        final.extend([str_tokens_question[root_plc-1]])
        final.extend(str_tokens_question[:root_plc-1])
        final.extend(str_tokens_question[root_plc:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "?"
        else:
            final_out = final_out[0].upper() + final_out[1:] + "?"
        return final_out
    elif str_tokens_question[root_plc-2] in ["have", "has", "had", "be", "is", "are", "was", "were", "am", "would", "will", "could", "can", "may", "might", "should", "shall"]\
            and pos_tokens_question[root_plc-1] in ["ADJ", "ADV", "ADJP"]:
        final = []
        str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
        final.extend([str_tokens_question[root_plc-2]])
        final.extend(str_tokens_question[:root_plc-2])
        final.extend(str_tokens_question[root_plc:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "?"
        else:
            final_out = final_out[0].upper() + final_out[1:] + "?"
        return final_out
    elif pos_tokens_question[root_plc-1] in ["ADJ", "ADV", "ADJP"]\
            and pos_tokens_question[root_plc-2] in ["ADJ", "ADV", "ADJP"]\
            and str_tokens_question[root_plc-3] in ["have", "has", "had", "be", "is", "are", "was", "were", "am", "would", "will", "could", "can", "may", "might", "should", "shall"]:
        final = []
        str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
        final.extend([str_tokens_question[root_plc-3]])
        final.extend(str_tokens_question[:root_plc-3])
        final.extend(str_tokens_question[root_plc:])
        final.pop()
        final_out = list_to_str(final)
        if have_comma_do:
            final_out = final_add + ", " + final_out + "?"
        else:
            final_out = final_out[0].upper() + final_out[1:] + "?"
        return final_out
    else:
        this_tense = tense(root)
        if this_tense == 1:
            if "be" not in lemma_tokens_question:
                doc_question = nlp(question)
                tokens_question = [token for token in doc_question if token.string.strip() != ""]
                str_tokens_question = [token.string.strip() for token in tokens_question if token.string.strip() != ""]
                dep_tokens_question = [token.dep_ for token in doc_question if token.string.strip() != ""]
                pos_tokens_question = [token.pos_ for token in doc_question if token.string.strip() != ""]
                lemma_tokens_question = [token.lemma_ for token in doc_question if token.string.strip() != ""]
                first_vb = []
                num = -1
                for i in pos_tokens_question:
                    num += 1
                    if i == "VERB":
                        first_vb.append(num)
                if first_vb == []:
                    final = []
                    final.extend(["Do"])
                    str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
                    final.extend(str_tokens_question[:])
                    final.pop()
                    final_out = list_to_str(final)
                    if have_comma_do:
                        final_out = final_add + ", " + final_out + "?"
                    else:
                        final_out = final_out[0].upper() + final_out[1:] + "?"
                    return final_out
                else:
                    if str_tokens_question[first_vb[0]] in ["did", "was", "were", "had"]:
                        final = []
                        final.extend([str_tokens_question[first_vb[0]]])
                        str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
                        final.extend(str_tokens_question[:first_vb[0]])
                        final.extend(str_tokens_question[first_vb[0]+1:])
                        final.pop()
                        final_out = list_to_str(final)
                        if have_comma_do:
                            final_out = final_add + ", " + final_out + "?"
                        else:
                            final_out = final_out[0].upper() + final_out[1:] + "?"
                        return final_out
                    else:
                        this_tense = tense(str_tokens_question[first_vb[0]])
                        if this_tense == 2:
                            final = []
                            final.extend(["Did"])
                            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
                            final.extend(str_tokens_question[:first_vb[0]])
                            final.extend([tokens_question[first_vb[0]].lemma_])
                            final.extend(str_tokens_question[first_vb[0] + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "?"
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "?"
                            return final_out
                        elif this_tense == 3:
                            final = []
                            final.extend(["Do"])
                            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
                            final.extend(str_tokens_question[:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "?"
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "?"
                            return final_out
                        elif this_tense == 4:
                            final = []
                            final.extend(["Does"])
                            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
                            final.extend(str_tokens_question[:first_vb[0]])
                            final.extend([tokens_question[first_vb[0]].lemma_])
                            final.extend(str_tokens_question[first_vb[0] + 1:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "?"
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "?"
                            return final_out
                        else:
                            final = []
                            final.extend(["Did"])
                            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
                            final.extend(str_tokens_question[:])
                            final.pop()
                            final_out = list_to_str(final)
                            if have_comma_do:
                                final_out = final_add + ", " + final_out + "?"
                            else:
                                final_out = final_out[0].upper() + final_out[1:] + "?"
                            return final_out
            be_plc = lemma_tokens_question.index("be")
            final = []
            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
            final.extend([str_tokens_question[be_plc]])
            final.extend(str_tokens_question[:be_plc])
            final.extend(str_tokens_question[be_plc + 1:])
            final.pop()
            final_out = list_to_str(final)
            if have_comma_do:
                final_out = final_add + ", " + final_out + "?"
            else:
                final_out = final_out[0].upper() + final_out[1:] + "?"
            return final_out
        elif this_tense == 2:
            final = []
            final.extend(["Did"])
            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
            final.extend(str_tokens_question[:root_plc])
            final.extend([tokens_question[root_plc].lemma_])
            final.extend(str_tokens_question[root_plc + 1:])
            final.pop()
            final_out = list_to_str(final)
            if have_comma_do:
                final_out = final_add + ", " + final_out + "?"
            else:
                final_out = final_out[0].upper() + final_out[1:] + "?"
            return final_out
        elif this_tense == 3:
            final = []
            final.extend(["Do"])
            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
            final.extend(str_tokens_question[:])
            final.pop()
            final_out = list_to_str(final)
            if have_comma_do:
                final_out = final_add + ", " + final_out + "?"
            else:
                final_out = final_out[0].upper() + final_out[1:] + "?"
            return final_out
        elif this_tense == 4:
            final = []
            final.extend(["Does"])
            str_tokens_question[0] = str_tokens_question[0][0].lower() + str_tokens_question[0][1:]
            final.extend(str_tokens_question[:root_plc])
            final.extend([tokens_question[root_plc].lemma_])
            final.extend(str_tokens_question[root_plc + 1:])
            final.pop()
            final_out = list_to_str(final)
            if have_comma_do:
                final_out = final_add + ", " + final_out + "?"
            else:
                final_out = final_out[0].upper() + final_out[1:] + "?"
            return final_out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--information_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    parser.add_argument(
        "--out_file_path",
        default=None,
        type=str,
        required=True,
        help=""
    )
    args = parser.parse_args()
    file_path = args.json_file_path
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    statements = []
    for line in lines:
        i = json.loads(line.strip("\n"))
        statement = i["statement"]
        GT = i["GT"]
        answer = i["answer"]
        article = i["article"]
        question = i["question"]
        index = i["index"]
        this_dataset = i["dataset"]
        statements.append([statement, answer, article, question, GT, index, this_dataset])

    data_jinacha = open(args.information_file_path, 'w', encoding='utf-8')
    new_questions = []
    all_question_article = []
    all_jiancha = []
    all_answer = []
    for a_num in tqdm(range(len(statements))):
        one = statements[a_num]
        if one[0] == "None":
            continue
        new_question = S2I(one[0])
        new_questions.append(new_question)
        all_question_article.append(str(new_question) + " \\n " + str(one[2]))
        all_jiancha.append("{\"primary_question\": \"" + one[3]
                           + "\", \"GT\": \"" + one[4]
                           + "\", \"primary_answer\": \"" + one[1]
                           + "\", \"statement\": \"" + statements[a_num][0]
                           + "\", \"target_answer\": \"" + "yes"
                           + "\", \"new_question\": \"" + new_question
                           + "\", \"article\": \"" + one[2]
                           + "\", \"rouge_1_p\": \"" + str(1)
                           + "\", \"rouge_1_r\": \"" + str(1)
                           + "\", \"index\": \"" + str(one[5])
                           + "\", \"dataset\": \"" + str(one[6]) + "\"}")
        all_answer.append("yes")

    for i in all_jiancha:
        print(i, file=data_jinacha)

    with open(args.out_file_path, 'w', encoding='utf-8') as f:
        tsv_w = csv.writer(f, delimiter='\t', lineterminator='\n')
        num = -1
        for this_sample in new_questions:
            num += 1
            tsv_w.writerow([all_question_article[num], all_answer[num]])

if __name__ == "__main__":
    main()