from pmresearch.stage3.reliability import cohen_kappa, krippendorff_alpha_ordinal
def test_perfect_agreement():
 assert cohen_kappa(['0','1','2'],['0','1','2']) == 1.0
 assert krippendorff_alpha_ordinal([['0','0'],['1','1'],['2','2']]) == 1.0
def test_kappa_disagreement():
 assert cohen_kappa(['0','0','1','1'],['0','1','0','1']) == 0.0
