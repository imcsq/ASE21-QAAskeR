import json
import spacy
import string
import nltk
import argparse
from tqdm import tqdm
from nltk.tokenize import word_tokenize
from pattern.en import conjugate, lemma, lexeme, PRESENT, INFINITIVE, PAST, FUTURE, SG, PLURAL, PROGRESSIVE
from wh_rules.howmany import howmany
from wh_rules.what import what
from wh_rules.how import how
from wh_rules.why import why
from wh_rules.who import who
from wh_rules.whose import whose
from wh_rules.where import where
from wh_rules.when import when
from wh_rules.which import which


nlp = spacy.load('en_core_web_sm')


this_what = what()
this_how = how()
this_howmany = howmany()
this_why = why()
this_who = who()
this_whose = whose()
this_where = where()
this_when = when()
this_which = which()


def change(question, answer):
    if "can't " in question:
        question = question.replace("can't ", "can not ")
    elif "won't " in question:
        question = question.replace("won't ", "will not ")
    elif "couldn't " in question:
        question = question.replace("couldn't ", "could not ")
    elif "shouldn't " in question:
        question = question.replace("shouldn't ", "should not ")
    elif "haven't " in question:
        question = question.replace("haven't ", "have not ")
    elif "hasn't " in question:
        question = question.replace("hasn't ", "has not ")
    elif "mustn't " in question:
        question = question.replace("mustn't ", "must not ")
    elif "aren't " in question:
        question = question.replace("aren't ", "are not ")
    elif "isn't " in question:
        question = question.replace("isn't ", "is not ")
    elif "weren't " in question:
        question = question.replace("weren't ", "were not ")
    elif "wasn't " in question:
        question = question.replace("wasn't ", "was not ")
    elif "don't " in question:
        question = question.replace("don't ", "do not ")
    elif "doesn't " in question:
        question = question.replace("doesn't ", "does not ")
    elif "didn't " in question:
        question = question.replace("didn't ", "did not ")
    if "dont " in question:
        question = question.replace("dont ", "do not ")
    if "How man " in question:
        question = question.replace("How man ", "How many ")
    if "How maney " in question:
        question = question.replace("How maney ", "How many ")
    doc_question = nlp(question)
    tokens_question = [token for token in doc_question if token.string.strip() != ""]
    str_tokens_question = [token.string.strip() for token in doc_question if token.string.strip() != ""]
    boolean_start = ["be", "do", "will", "can", "should", "may", "have", "must", "would", "am", "could", "shell", "might"]
    if tokens_question[0].lemma_ in ["how", "what", "who", "why", "whose", "where", "when", "which"]:
        if "How many " in question or "how many " in question or "How much " in question or "how much " in question or "How long " in question or "how long " in question or "How old " in question or "how old " in question or "How far " in question or "how far " in question:
            statement = this_howmany.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "what" or ("what" in question and tokens_question[0].lemma_ != "who"):
            statement = this_what.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "who":
            statement = this_who.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "why" or ", why " in question:
            statement = this_why.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "whose":
            statement = this_whose.generate(question, answer)
            return statement
        elif "When and where" in question or "Where and when" in question:
            if "When and where" in question:
                question = question.replace("When and where", "Where")
            if "Where and when" in question:
                question = question.replace("Where and when", "Where")
            statement = this_where.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "where":
            statement = this_where.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "when":
            statement = this_when.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "how":
            statement = this_how.generate(question, answer)
            return statement
        elif tokens_question[0].lemma_ == "which":
            statement = this_which.generate(question, answer)
            return statement
    if tokens_question[0].lemma_ in boolean_start:
        return
    elif "How many " in question or "how many " in question or "How much " in question or "how much " in question or "How long " in question or "how long " in question or "How old " in question or "how old " in question or "How far " in question or "how far " in question:
        statement = this_howmany.generate(question, answer)
        return statement
    elif "what" in str_tokens_question or "What" in str_tokens_question:
        statement = this_what.generate(question, answer)
        return statement
    elif "how" in str_tokens_question or "How" in str_tokens_question:
        statement = this_how.generate(question, answer)
        return statement
    elif "who" in str_tokens_question or "Who" in str_tokens_question or "whom" in str_tokens_question:
        statement = this_who.generate(question, answer)
        return statement
    elif "why" in str_tokens_question or "Why" in str_tokens_question:
        statement = this_why.generate(question, answer)
        return statement
    elif "whose" in str_tokens_question or "Whose" in str_tokens_question:
        statement = this_whose.generate(question, answer)
        return statement
    elif "where" in str_tokens_question or "Where" in str_tokens_question or "in which" in str_tokens_question or "In which" in str_tokens_question:
        statement = this_where.generate(question, answer)
        return statement
    elif "when" in str_tokens_question or "When" in str_tokens_question:
        statement = this_when.generate(question, answer)
        return statement
    elif "which" in str_tokens_question or "Which" in str_tokens_question:
        statement = this_which.generate(question, answer)
        return statement


def this_main(tsv_file_path, out_file_path):
    print_out_data = []
    output = []
    with open(tsv_file_path, "r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            question, answer, article, index, this_dataset, GT = line.split("\t")
            output.append([question.strip("\n"), answer.strip("\n"), article.strip("\n"), GT.strip("\n"), index.strip("\n"), this_dataset.strip("\n")])
    data = open(out_file_path, 'w', encoding='utf-8')
    for a_num in tqdm(range(len(output))):
        i = output[a_num]
        question = i[0]
        if "can't " in question:
            question = question.replace("can't ", "can not ")
        elif "won't " in question:
            question = question.replace("won't ", "will not ")
        elif "couldn't " in question:
            question = question.replace("couldn't ", "could not ")
        elif "shouldn't " in question:
            question = question.replace("shouldn't ", "should not ")
        elif "haven't " in question:
            question = question.replace("haven't ", "have not ")
        elif "hasn't " in question:
            question = question.replace("hasn't ", "has not ")
        elif "mustn't " in question:
            question = question.replace("mustn't ", "must not ")
        elif "aren't " in question:
            question = question.replace("aren't ", "are not ")
        elif "isn't " in question:
            question = question.replace("isn't ", "is not ")
        elif "weren't " in question:
            question = question.replace("weren't ", "were not ")
        elif "wasn't " in question:
            question = question.replace("wasn't ", "was not ")
        elif "don't " in question:
            question = question.replace("don't ", "do not ")
        elif "doesn't " in question:
            question = question.replace("doesn't ", "does not ")
        elif "didn't " in question:
            question = question.replace("didn't ", "did not ")
        if "dont " in question:
            question = question.replace("dont ", "do not ")
        if "How man " in question:
            question = question.replace("How man ", "How many ")
        if "How maney " in question:
            question = question.replace("How maney ", "How many ")
        doc_question = nlp(question)
        tokens_question = [token for token in doc_question if token.string.strip() != ""]
        str_tokens_question = [token.string.strip() for token in doc_question]
        boolean_start = ["be", "do", "will", "can", "should", "may", "have", "must", "would", "am", "could", "shell", "might"]
        if tokens_question[0].lemma_ in ["how", "what", "who", "why", "whose", "where", "when", "which"]:
            if "How many " in question or "how many " in question or "How much " in question or "how much " in question or "How long " in question or "how long " in question or "How old " in question or "how old " in question or "How far " in question or "how far " in question:
                statement = this_howmany.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                      + "\", \"answer\": \"" + i[1]
                      + "\", \"article\": \"" + i[2]
                      + "\", \"question\": \"" + question
                      + "\", \"GT\": \"" + i[3]
                      + "\", \"index\": \"" + i[4]
                      + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "what" or ("what" in str_tokens_question and tokens_question[0].lemma_ != "who"):
                statement = this_what.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "who":
                statement = this_who.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "why" or ", why " in question:
                statement = this_why.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "whose":
                statement = this_whose.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif "When and where" in question or "Where and when" in question:
                if "When and where" in question:
                    new_question = question.replace("When and where", "Where")
                if "Where and when" in question:
                    new_question = question.replace("Where and when", "Where")
                statement = this_where.generate(new_question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "where":
                statement = this_where.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "when":
                statement = this_when.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "how":
                statement = this_how.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
            elif tokens_question[0].lemma_ == "which":
                statement = this_which.generate(question, i[1])
                if statement == None:
                    continue
                if "?" in statement:
                    statement.replace("?", "")
                if "?" in statement:
                    statement.replace("?", "")
                print_out_data.append("{\"statement\": \"" + str(statement)
                                       + "\", \"answer\": \"" + i[1]
                                       + "\", \"article\": \"" + i[2]
                                       + "\", \"question\": \"" + question
                                       + "\", \"GT\": \"" + i[3]
                                       + "\", \"index\": \"" + i[4]
                                       + "\", \"dataset\": \"" + i[5] + "\"}")
                continue
        if tokens_question[0].lemma_ in boolean_start:
            continue
        elif "How many " in question or "how many " in question or "How much " in question or "how much " in question or "How long " in question or "how long " in question or "How old " in question or "how old " in question or "How far " in question or "how far " in question:
            statement = this_howmany.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "what" in str_tokens_question or "What" in str_tokens_question:
            statement = this_what.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "how" in str_tokens_question or "How" in str_tokens_question:
            statement = this_how.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "who" in str_tokens_question or "Who" in str_tokens_question or "whom" in str_tokens_question:
            statement = this_who.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "why" in str_tokens_question or "Why" in str_tokens_question:
            statement = this_why.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "whose" in str_tokens_question or "Whose" in str_tokens_question:
            statement = this_whose.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "where" in str_tokens_question or "Where" in str_tokens_question or "in which" in str_tokens_question or "In which" in str_tokens_question:
            statement = this_where.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "when" in str_tokens_question or "When" in str_tokens_question:
            statement = this_when.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
        elif "which" in str_tokens_question or "Which" in str_tokens_question:
            statement = this_which.generate(question, i[1])
            if statement == None:
                continue
            if "?" in statement:
                statement.replace("?", "")
            if "?" in statement:
                statement.replace("?", "")
            print_out_data.append("{\"statement\": \"" + str(statement)
                                   + "\", \"answer\": \"" + i[1]
                                   + "\", \"article\": \"" + i[2]
                                   + "\", \"question\": \"" + question
                                   + "\", \"GT\": \"" + i[3]
                                   + "\", \"index\": \"" + i[4]
                                   + "\", \"dataset\": \"" + i[5] + "\"}")
            continue
    for i in print_out_data:
        print(i, file=data)
    data.close()


def main():
    parser = argparse.ArgumentParser()
    # Required parameters
    parser.add_argument(
        "--tsv_file_path",
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
    this_main(args.tsv_file_path, args.out_file_path)


if __name__ == "__main__":
    main()
