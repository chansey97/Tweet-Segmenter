"""
File: segment.py
Author: Siyuan Chen
Email: chansey97@gmail.com
Created Date: Thursday, November 16 2023
-----
Description:
    This code is specifically designed to segment a user-provided text into tweet-sized segments and add a counter, like [3/10], to the end of each segment.
    The public interface is segment(user_post).
"""

import re

TWEER_MAX_LENGTH = 280

SEGMENT_LENGTH = TWEER_MAX_LENGTH
SEGMENT_NUM_LENGTH = 8
SEGMENT_VALID_LENGTH = SEGMENT_LENGTH - SEGMENT_NUM_LENGTH

ROUGH_SENGMENT_THRESHOLD = 100

def segment(user_post):
    return suffix_num(fine_segment(rough_segment(user_post)))

def rough_segment(text):

    sentences = re.findall(r'[^.!?]*[.!?:]\s+', text)

    partition_potential_limit = SEGMENT_VALID_LENGTH
    threshold_for_new_partition = ROUGH_SENGMENT_THRESHOLD

    partitions = []
    current_partition = ""
    current_partition_remain = partition_potential_limit

    for sentence in sentences:
        new_remain = current_partition_remain - len(sentence)
        if new_remain < 0:
            stripped_sentence = sentence.rstrip()
            new_remain = current_partition_remain - len(stripped_sentence)
            if new_remain < 0:
                if current_partition_remain <= threshold_for_new_partition:
                    partitions.append(current_partition)
                    current_partition = sentence
                    current_partition_remain = partition_potential_limit - len(sentence)
                else:
                    current_partition +=stripped_sentence
                    partitions.append(current_partition)
                    current_partition = ""
                    current_partition_remain = partition_potential_limit
            else:
                current_partition += stripped_sentence
                current_partition_remain = new_remain
        else:
            current_partition += sentence
            current_partition_remain = new_remain

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
    counter = 0
    cursor = 0

    while cursor < len(text):

        # Check if the current segment exceeds the max length
        if counter + 1 > potential_max_unidist_length:

            # If it's in the middle of a word, eat the whole word
            while not text[cursor].isspace() and cursor < len(text):
                current_segment += text[cursor]
                counter += 1
                cursor += 1

            # Eat rest spaces
            while text[cursor].isspace() and cursor < len(text):
                current_segment += text[cursor]
                counter += 1
                cursor += 1

            # Add the segment and reset
            segments.append(current_segment.rstrip())
            current_segment = ""
            counter = 0
        else:
            current_segment += text[cursor]
            counter += 1
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
