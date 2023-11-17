"""
File: segment.py
Author: Siyuan Chen
Email: chansey97@gmail.com
Created Date: Thursday, November 16 2023
-----
Description:
    This code is specifically designed to segment a user-provided text into tweet-sized segments and add a counter,
    like [3/10], to the end of each segment. The public interface for GPT is segmented_text(user_post).
"""

import re

TWEER_MAX_LENGTH = 280

SEGMENT_LENGTH = TWEER_MAX_LENGTH
SEGMENT_NUM_LENGTH = 8
SEGMENT_VALID_LENGTH = SEGMENT_LENGTH - SEGMENT_NUM_LENGTH

## Note: ROUGH_SEGMENT_THRESHOLD must be < (0.5 * SEGMENT_VALID_LENGTH) - MAX_WORD_SIZE
ROUGH_SEGMENT_THRESHOLD = 120


def segmented_text(user_post):
    return '\n'.join(segment(user_post))


def segment(user_post):
    return suffix_num(fine_segment(rough_segment(extract_sentences(user_post))))


def extract_sentences(text):

    # 1. Replace "..." with a placeholder
    placeholders = []
    def replace_with_placeholder(match):
        placeholders.append(match.group())
        return "__QUOTE_" + str(len(placeholders)-1) + "__"

    text_without_quotes = re.sub(r'"[^"]*"', replace_with_placeholder, text)

    # 2. Extract sentences
    sentences = re.findall(r'(?:[^\n]+?[.!?:]\s+)|(?:[^\n]+\n\s*)', text_without_quotes.lstrip())

    # 3. Restore quotes
    restored_sentences = []
    for sentence in sentences:
        for i, placeholder in enumerate(placeholders):
            sentence = sentence.replace("__QUOTE_"+str(i)+"__", placeholder)
        restored_sentences.append(sentence)

    return restored_sentences

def rough_segment(sentences):

    potential_max_length = SEGMENT_VALID_LENGTH
    threshold_for_new_partition = ROUGH_SEGMENT_THRESHOLD

    partitions = []
    current_partition = ""

    for sentence in sentences:

        if len(current_partition) + len(sentence) > potential_max_length:

            stripped_sentence = sentence.rstrip()
            if len(current_partition) + len(stripped_sentence) > potential_max_length:

                if len(current_partition) > threshold_for_new_partition:
                    partitions.append(current_partition)
                    current_partition = sentence
                else:
                    current_partition += stripped_sentence
                    partitions.append(current_partition)
                    current_partition = ""
            else:
                current_partition += stripped_sentence
        else:
            current_partition += sentence

    if current_partition:
        partitions.append(current_partition)

    return partitions


def fine_segment(partitions):
    partitions = [p.rstrip() for p in partitions]

    segments = []

    for p in partitions:
        if len(p) < SEGMENT_VALID_LENGTH:
            segments.append(p)

        else:
            segments.extend(split_text(p))

    return segments


def split_text(text):
    """
    1. Calculate the max uniform distribution length
    2. Splits the given text into segments where each segment is potentially less than or equal to SEGMENT_VALID_LENGTH.
    It ensures that words are not broken in the middle by moving the cursor forward to the end of the word.
    """
    potential_max_length = SEGMENT_VALID_LENGTH
    potential_max_unidist_length = len(text) // (len(text) // potential_max_length + 1) + 1

    segments = []
    current_segment = ""
    cursor = 0

    while cursor < len(text):

        # Check if the current segment exceeds the max length
        if len(current_segment) + 1 > potential_max_unidist_length:

            # If it's in the middle of a word, eat the whole word
            while not text[cursor].isspace() and cursor < len(text):
                current_segment += text[cursor]
                cursor += 1

            # Eat rest spaces
            while text[cursor].isspace() and cursor < len(text):
                current_segment += text[cursor]
                cursor += 1

            # Add the segment and reset
            segments.append(current_segment.rstrip())
            current_segment = ""
        else:
            current_segment += text[cursor]
            cursor += 1

    # Add the last segment if there is any
    if current_segment:
        segments.append(current_segment.rstrip())

    return segments


def suffix_num(segments):
    den = len(segments)
    for i in range(den):
        segments[i] = segments[i] + " [" + str(i + 1) + "/" + str(den) + "]"

    return segments

