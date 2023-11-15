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

    max_length = SEGMENT_VALID_LENGTH

    words = text.split()
    segments = []
    current_segment = ""

    for word in words:
        if len(current_segment) + len(word) + 1 > max_length:
            segments.append(current_segment)
            current_segment = word
        else:
            if current_segment:
                current_segment += " "
            current_segment += word

    if current_segment:
        segments.append(current_segment)

    return segments

def suffix_num(segments):

    den = len(segments)
    for i in range(den):
        segments[i] = segments[i] + " [" + str(i + 1) + "/" + str(den) + "]"

    return segments
