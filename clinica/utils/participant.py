# coding: utf8
from clinica.utils.filemanip import read_participant_tsv


def get_unique_subjects(in_subject_list, in_session_list):
    """Get unique participant IDs

    The function to read the .tsv file returns the following
    participant_id and session_id lists:
    participant1, participant1, ..., participant2, participant2, ...
    session1    , session2    , ..., session1    , session2    , ...
    This function returns a list where all participants are only selected
    once:
    participant1, participant2, ..., participant_n
    and for each participant, the list of corresponding session id
    eg.:
    participant1 -> [session1, session2]
    participant2 -> [session1]
    ...
    participant_n -> [session1, session2, session3]

    Args:
        in_subject_list (list of strings): list of participant_id
        in_session_list (list of strings): list of session_id

    Returns:
        out_unique_subject_list (list of strings): list of
            participant_id, where each participant appears only once
        out_persubject_session_list2 (list of list): list of list
            (list2) of session_id associated to any single participant
    """

    import numpy as np

    subject_array = np.array(in_subject_list)
    session_array = np.array(in_session_list)

    # The second returned element indicates for each participant_id the
    # element they correspond to in the 'unique' list. We will use this
    # to link each session_id in the repeated list of session_id to
    # their corresponding unique participant_id

    unique_subject_array, out_inverse_positions = np.unique(
        subject_array, return_inverse=True)
    out_unique_subject_list = unique_subject_array.tolist()

    subject_number = len(out_unique_subject_list)
    out_persubject_session_list2 = [
        session_array[
            out_inverse_positions == subject_index
            ].tolist() for subject_index in range(subject_number)]

    return out_unique_subject_list, out_persubject_session_list2


def get_subject_session_list(input_dir, ss_file=None, is_bids_dir=True, use_session_tsv=False, tsv_dir=None):
    """Parse a BIDS or CAPS directory to get the subjects and sessions.

    This function lists all the subjects and sessions based on the content of
    the BIDS or CAPS directory or (if specified) on the provided
    subject-sessions TSV file.

    Args:
        input_dir: A BIDS or CAPS directory path.
        ss_file: A subjects-sessions file (.tsv format).
        is_bids_dir: Indicates if input_dir is a BIDS or CAPS directory
        use_session_tsv (boolean): Specify if the list uses the sessions listed in the sessions.tsv files
        tsv_dir (str): if TSV file does not exist, it will be created in output_dir. If
            not specified, output_dir will be in <tmp> folder

    Returns:
        subjects: A subjects list.
        sessions: A sessions list.

    Notes:
        This is a generic method based on folder names. If your <BIDS> dataset contains e.g.:
        - sub-CLNC01/ses-M00/anat/sub-CLNC01_ses-M00_T1w.nii
        - sub-CLNC02/ses-M00/dwi/sub-CLNC02_ses-M00_dwi.{bval|bvec|json|nii}
        - sub-CLNC02/ses-M00/anat/sub-CLNC02_ses-M00_T1w.nii
        get_subject_session_list(<BIDS>, None, True) will return
        ['ses-M00', 'ses-M00'], ['sub-CLNC01', 'sub-CLNC02'].

        However, if your pipeline needs both T1w and DWI files, you will need to check
        with e.g. clinica_file_reader_function.
    """
    import os
    import tempfile
    from time import time, strftime, localtime
    import clinica.iotools.utils.data_handling as cdh

    if not ss_file:
        if tsv_dir:
            output_dir = tsv_dir
        else:
            output_dir = tempfile.mkdtemp()
        timestamp = strftime('%Y%m%d_%H%M%S', localtime(time()))
        tsv_file = 'subjects_sessions_list_%s.tsv' % timestamp
        ss_file = os.path.join(output_dir, tsv_file)

        cdh.create_subs_sess_list(
            input_dir=input_dir,
            output_dir=output_dir,
            file_name=tsv_file,
            is_bids_dir=is_bids_dir,
            use_session_tsv=use_session_tsv)

    participant_ids, session_ids = read_participant_tsv(ss_file)
    return session_ids, participant_ids