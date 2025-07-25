import math

import nltk

def split_by_paragraphs(original_text, target_bundle_size, max_bundle_size):
    bundles = []

    paragraphs = original_text.split('\n\n')

    current_bundle = ''

    for paragraph in paragraphs:
        if len(paragraph) >= max_bundle_size:
            return None

        if current_bundle == '':
            current_bundle = paragraph
        else:
            updated_bundle = '%s\n\n%s' % (current_bundle, paragraph)

            if len(updated_bundle) > target_bundle_size:
                bundles.append(current_bundle)

                current_bundle = paragraph
            else:
                current_bundle = updated_bundle

    if len(current_bundle) > 0:
        bundles.append(current_bundle)

    return bundles

def split_by_sentences(original_text, target_bundle_size, max_bundle_size):
    bundles = []

    sentences = nltk.tokenize.sent_tokenize(original_text)

    current_bundle = ''

    for sentence in sentences:
        if len(sentence) >= max_bundle_size:
            return None

        if current_bundle == '':
            current_bundle = sentence
        else:
            updated_bundle = '%s %s' % (current_bundle, sentence)

            if len(updated_bundle) > target_bundle_size:
                bundles.append(current_bundle)

                current_bundle = sentence
            else:
                current_bundle = updated_bundle

    if len(current_bundle) > 0:
        bundles.append(current_bundle)

    return bundles

def split_by_space(original_text, target_bundle_size, max_bundle_size):
    bundles = []

    tokens = original_text.split(' ')

    current_bundle = ''

    for token in tokens:
        if len(token) >= max_bundle_size:
            return None

        if current_bundle == '':
            current_bundle = token
        else:
            updated_bundle = '%s %s' % (current_bundle, token)

            if len(updated_bundle) > target_bundle_size:
                bundles.append(current_bundle)

                current_bundle = token
            else:
                current_bundle = updated_bundle

    if len(current_bundle) > 0:
        bundles.append(current_bundle)

    return bundles

def split_by_character(original_text, target_bundle_size, max_bundle_size):
    bundles = []

    index = 0

    while (index + target_bundle_size) < max_bundle_size:
        bundles.append(original_text[index:(index + target_bundle_size)])

        index += target_bundle_size

    bundles.append(original_text[index:])

    return bundles

def split_into_bundles(original_text, bundle_size):
    if len(original_text) <= bundle_size:
        return [original_text]

    bundle_count = math.ceil(len(original_text) / bundle_size)

    target_bundle_size = math.ceil(bundle_size / bundle_count)

    original_text = original_text.replace('\r', '\n')

    while '\n\n\n' in original_text:
        original_text = original_text.replace('\n\n\n', '\n\n')

    paragraph_bundles = split_by_paragraphs(original_text, target_bundle_size, bundle_size)

    if paragraph_bundles is not None:
        return paragraph_bundles

    sentence_bundles = split_by_sentences(original_text, target_bundle_size, bundle_size)

    if sentence_bundles is not None:
        return sentence_bundles

    space_bundles = split_by_space(original_text, target_bundle_size, bundle_size)

    if space_bundles is not None:
        return space_bundles

    character_bundles = split_by_character(original_text, target_bundle_size, bundle_size)

    if character_bundles is not None:
        return character_bundles

    return [original_text]
