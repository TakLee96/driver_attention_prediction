# -*- coding: utf-8 -*-
"""
@author: Ye Xia
"""

import os
import pickle
#import pdb



#data_dir = data/
#training set directory: data/training/
#validation set directory: data/validation/
#camera_images/
#gazemap_images/
#10_342.jpg

def read_datasets(data_dir, in_sequences=False, keep_prediction_rate=True, \
                    longest_seq=None, sample_rate=3):
    if in_sequences:
        if keep_prediction_rate:
            pickle_filename = "data_point_names_in_sequences.pickle"
        else:
            pickle_filename = "data_point_names_in_sequences_for_visualization.pickle"
    else:
        pickle_filename = "data_point_names.pickle"

    pickle_filepath = os.path.join(data_dir, pickle_filename)
    if not os.path.exists(pickle_filepath):
        directories = ['training', 'validation', 'application']
        data_point_names = {}
        for directory in directories:
            data_point_names[directory] = get_data_point_names(data_dir+directory+'/', \
                    in_sequences, keep_prediction_rate, longest_seq=longest_seq, \
                    sample_rate=sample_rate)
        print ("Pickling ...")
        with open(pickle_filepath, 'wb') as f:
            pickle.dump(data_point_names, f, pickle.HIGHEST_PROTOCOL)
    else:
        print ("Found pickle file!")
        with open(pickle_filepath, 'rb') as f:
            data_point_names = pickle.load(f)

    return data_point_names['training'], data_point_names['validation'], data_point_names['application']


def get_data_point_names(directory, in_sequences=False, keep_prediction_rate=True, \
                            predictionRate=3, longest_seq=None, sampleRate=3):
    if not os.path.isdir(directory):
        print("Data directory '" + directory + "' not found.")
        return None

    image_path = os.path.join(directory, 'camera_images')
    data_points = [f[:-4] for f in os.listdir(image_path) if f.endswith('.jpg')]
    data_points.sort()

    # Our model was trained at 3 Hz, so it only supports prediction at 3 frames/second.
    # If a different sample rate is desired, we will sample more frames
    # than needed, split them into groups of 3 frames per second,
    # and train multiple times. (See group_num below)
    if sampleRate % 3 == 0:
        numGroups = sampleRate / 3
    else:
        numGroups = sampleRate

    if in_sequences:
        data_point_dict = {}

        # Assign each frame a group number indicating which set it will be
        # trained in. For example, if the desired rate is 4 Hz, we would sample
        # 4x3=12 frames, then train 4 different groups at the default 3 Hz
        # to get data for each frame.
        group_num = 0

        for data_point in data_points:
            video_id = data_point.split('_')[0]
            if keep_prediction_rate:
                group_key = group_num
                group_num = (group_num + 1) % numGroups
            else:
                group_key = video_id

            group = data_point_dict.setdefault(group_key, [])
            group.append(data_point)

        data_point_names = \
            list(data_point_dict.values())
    else:
        data_point_names = list(data_points)

    if longest_seq is not None:
        #avoid sequences that are too long to avoid memory error
        size_threshold = longest_seq
        data_point_names = crop_long_seqs(data_point_names, size_threshold)

    no_of_videos = len(data_point_names)
    print ('No. of %s videos: %d' % (directory, no_of_videos))

    return data_point_names



def crop_long_seqs(data_point_names, size_threshold):
    sizes = [len(seq) for seq in data_point_names]
    long_indices = [i for i,size in enumerate(sizes) if size>size_threshold]
    if len(long_indices) == 0:
        return data_point_names

    for i in long_indices:
        seq = data_point_names[i]
        data_point_names.append(seq[size_threshold:])
        data_point_names[i] = seq[:size_threshold]
    return crop_long_seqs(data_point_names, size_threshold)
