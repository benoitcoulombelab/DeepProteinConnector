import os.path
from io import TextIOWrapper
from unittest.mock import MagicMock, ANY

import pytest

from afpairs import InteractionScore, MultiInteractionScore


@pytest.fixture
def mock_testclass():
    _file_path = MultiInteractionScore.file_path
    _multi_interaction_score = MultiInteractionScore.multi_interaction_score
    _parse_mapping = MultiInteractionScore.parse_mapping
    _interaction_score = InteractionScore.interaction_score
    yield
    MultiInteractionScore.file_path = _file_path
    MultiInteractionScore.multi_interaction_score = _multi_interaction_score
    MultiInteractionScore.parse_mapping = _parse_mapping
    InteractionScore.interaction_score = _interaction_score


def test_main(testdir, mock_testclass):
    pdbs = ["1.pdb", "2.pdb", "3.pdb"]
    [open(f, 'w').close() for f in pdbs]
    MultiInteractionScore.multi_interaction_score = MagicMock()
    MultiInteractionScore.main(pdbs)
    MultiInteractionScore.multi_interaction_score.assert_called_once_with(
        input_files=pdbs, name=r"(\w+)__(\w+)", radius=6.0, weight=False,
        first_chains=["A"], second_chains=["B"], output_file=ANY,
        mapping_file=None, source_column=0, converted_column=1)
    output_file = MultiInteractionScore.multi_interaction_score.call_args.kwargs["output_file"]
    assert isinstance(output_file, TextIOWrapper)
    assert output_file.mode in ["r+", "w"]


def test_main_parameters(testdir, mock_testclass):
    pdbs = ["1.pdb", "2.pdb", "3.pdb"]
    [open(f, 'w').close() for f in pdbs]
    mapping_file = "mappings.txt"
    open(mapping_file, 'w').close()
    output_file = "output.txt"
    MultiInteractionScore.multi_interaction_score = MagicMock()
    MultiInteractionScore.main(
        ["-n", r"(\w+)____(\w+)", "-a", "A,B", "-b", "C,D", "-r", "9", "-w", "-o", output_file,
         "-M", mapping_file, "-S", "2", "-C", "3"] + pdbs)
    MultiInteractionScore.multi_interaction_score.assert_called_once_with(
        input_files=pdbs, name=r"(\w+)____(\w+)", radius=9.0, weight=True,
        first_chains=["A", "B"], second_chains=["C", "D"], output_file=ANY,
        mapping_file=ANY, source_column=1, converted_column=2)
    mapping_in = MultiInteractionScore.multi_interaction_score.call_args.kwargs["mapping_file"]
    assert mapping_in.name == mapping_file
    assert mapping_in.mode == "r"
    output_out = MultiInteractionScore.multi_interaction_score.call_args.kwargs["output_file"]
    assert output_out.name == output_file
    assert output_out.mode == "w"


def test_main_long_parameters(testdir, mock_testclass):
    pdbs = ["1.pdb", "2.pdb", "3.pdb"]
    [open(f, 'w').close() for f in pdbs]
    mapping_file = "mappings.txt"
    open(mapping_file, 'w').close()
    output_file = "output.txt"
    MultiInteractionScore.multi_interaction_score = MagicMock()
    MultiInteractionScore.main(
        ["--name", r"(\w+)____(\w+)", "--first", "A,B", "--second", "C,D", "--radius", "9", "--weight",
         "--output", output_file, "--mapping", mapping_file, "--source_column", "2", "--converted_column", "3"] + pdbs)
    MultiInteractionScore.multi_interaction_score.assert_called_once_with(
        input_files=pdbs, name=r"(\w+)____(\w+)", radius=9.0, weight=True,
        first_chains=["A", "B"], second_chains=["C", "D"], output_file=ANY,
        mapping_file=ANY, source_column=1, converted_column=2)
    mapping_in = MultiInteractionScore.multi_interaction_score.call_args.kwargs["mapping_file"]
    assert mapping_in.name == mapping_file
    assert mapping_in.mode == "r"
    output_out = MultiInteractionScore.multi_interaction_score.call_args.kwargs["output_file"]
    assert output_out.name == output_file
    assert output_out.mode == "w"


def test_multi_interaction_score(testdir, mock_testclass):
    pdbs = ["POLR2A__POLR2B.pdb", "POLR2C__POLR2J.pdb", "POLR2D__POLR2G.pdb"]
    [open(f, 'w').close() for f in pdbs]
    output_file = "output.txt"
    InteractionScore.interaction_score = MagicMock(side_effect=[2.3, 4.5, 8.2])
    with open(output_file, 'w') as output_out:
        MultiInteractionScore.multi_interaction_score(input_files=pdbs, output_file=output_out)
    InteractionScore.interaction_score.assert_any_call(pdb=ANY, radius=6.0, weight=False,
                                                       first_chains=["A"], second_chains=["B"])
    for i in range(0, len(pdbs)):
        assert InteractionScore.interaction_score.call_args_list[i].kwargs["pdb"].name == pdbs[i]
    assert os.path.isfile(output_file)
    with open(output_file, 'r') as output_in:
        assert output_in.readline() == "Bait\tTarget\tScore\n"
        assert output_in.readline() == "POLR2A\tPOLR2B\t2.3\n"
        assert output_in.readline() == "POLR2C\tPOLR2J\t4.5\n"
        assert output_in.readline() == "POLR2D\tPOLR2G\t8.2\n"


def test_multi_interaction_score_mapping(testdir, mock_testclass):
    pdbs = ["RPB1_HUMAN__RPB2_HUMAN.pdb", "RPB3_HUMAN__RPB11_HUMAN.pdb", "RPB4_HUMAN__RPB7_HUMAN.pdb"]
    [open(f, 'w').close() for f in pdbs]
    mapping_file = "mapping_file.txt"
    open(mapping_file, 'w').close()
    mappings = {"RPB1_HUMAN": "POLR2A", "RPB2_HUMAN": "POLR2B", "RPB3_HUMAN": "POLR2C", "RPB7_HUMAN": "POLR2G"}
    MultiInteractionScore.parse_mapping = MagicMock(return_value=mappings)
    output_file = "output.txt"
    InteractionScore.interaction_score = MagicMock(side_effect=[2.3, 4.5, 8.2])
    with open(output_file, 'w') as output_out, open(mapping_file, 'r') as mapping_in:
        MultiInteractionScore.multi_interaction_score(input_files=pdbs, output_file=output_out, mapping_file=mapping_in)
        MultiInteractionScore.parse_mapping.assert_called_once_with(mapping_in, 0, 1)
    InteractionScore.interaction_score.assert_any_call(pdb=ANY, radius=6.0, weight=False,
                                                       first_chains=["A"], second_chains=["B"])
    for i in range(0, len(pdbs)):
        assert InteractionScore.interaction_score.call_args_list[i].kwargs["pdb"].name == pdbs[i]
    assert os.path.isfile(output_file)
    with open(output_file, 'r') as output_in:
        assert output_in.readline() == "Bait\tTarget\tScore\n"
        assert output_in.readline() == "POLR2A\tPOLR2B\t2.3\n"
        assert output_in.readline() == "POLR2C\tRPB11_HUMAN\t4.5\n"
        assert output_in.readline() == "RPB4_HUMAN\tPOLR2G\t8.2\n"


def test_multi_interaction_score_invalid_name(testdir, mock_testclass):
    pdbs = ["POLR2A__POLR2B.pdb", "POLR2C__POLR2J.pdb", "POLR2D__POLR2G.pdb"]
    [open(f, 'w').close() for f in pdbs]
    output_file = "output.txt"
    InteractionScore.interaction_score = MagicMock(side_effect=[2.3, 4.5, 8.2])
    try:
        with open(output_file, 'w') as output_out:
            MultiInteractionScore.multi_interaction_score(input_files=pdbs, name=r"(\w+)", output_file=output_out)
    except (AssertionError, IndexError):
        assert True
    else:
        assert False, "Expected AssertionError"


def test_multi_interaction_score_invalid_filename(testdir, mock_testclass):
    pdbs = ["POLR2A.pdb", "POLR2C__POLR2J.pdb", "POLR2D__POLR2G.pdb"]
    [open(f, 'w').close() for f in pdbs]
    output_file = "output.txt"
    InteractionScore.interaction_score = MagicMock(side_effect=[2.3, 4.5, 8.2])
    try:
        with open(output_file, 'w') as output_out:
            MultiInteractionScore.multi_interaction_score(input_files=pdbs, output_file=output_out)
    except (AssertionError, IndexError):
        assert True
    else:
        assert False, "Expected AssertionError"


def test_parse_mapping(testdir, mock_testclass):
    mapping_file = "mapping_file.txt"
    with open(mapping_file, 'w') as mapping_out:
        mapping_out.write("RPB1_HUMAN\tPOLR2A\n")
        mapping_out.write("NOGENE_HUMAN\t\n")
        mapping_out.write("RPB2_HUMAN\tPOLR2B\n")
    with open(mapping_file, 'r') as mapping_in:
        mappings = MultiInteractionScore.parse_mapping(mapping_file=mapping_in)
    assert "RPB1_HUMAN" in mappings
    assert mappings["RPB1_HUMAN"] == "POLR2A"
    assert "RPB2_HUMAN" in mappings
    assert mappings["RPB2_HUMAN"] == "POLR2B"
    assert "NOGENE_HUMAN" not in mappings
