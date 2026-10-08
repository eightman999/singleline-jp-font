from build_family import portable_build_paths


def test_build_paths_are_relative_to_deliverable_root(tmp_path):
    root=tmp_path/'private-checkout/build/family'
    summary={'fonts':[{'path':str(root/'static/font.ttf')}],
             'bitmaps':[{'binary':str(root/'bitmaps/font.sjpb')}]}
    portable_build_paths(summary,root)
    assert summary['fonts'][0]['path']=='static/font.ttf'
    assert summary['bitmaps'][0]['binary']=='bitmaps/font.sjpb'
    assert 'private-checkout' not in str(summary)
