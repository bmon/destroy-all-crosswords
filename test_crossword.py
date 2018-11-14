from crossword import Crossword, Word, WordLengthDictionary


def test_medium_crossword():
    w = [
        Word(6),  # 1 Across
        Word(6),  # 1 Down
        Word(3),  # 2d
        Word(3),  # 3d
        Word(6),  # 4d
        Word(7),  # 5a
        Word(3),  # 6d
        Word(7),  # 7a
        Word(3),  # 8d
        Word(3),  # 9d
        Word(6),  # 10a
    ]
    w[0].addCollision(w[1], 0, 0)
    w[0].addCollision(w[2], 2, 0)
    w[0].addCollision(w[3], 4, 0)
    w[1].addCollision(w[5], 2, 0)
    w[1].addCollision(w[7], 4, 0)
    w[2].addCollision(w[5], 2, 2)
    w[3].addCollision(w[5], 2, 4)
    w[4].addCollision(w[5], 1, 6)
    w[4].addCollision(w[7], 3, 6)
    w[4].addCollision(w[10], 5, 5)
    w[5].addCollision(w[6], 3, 1)
    w[6].addCollision(w[7], 2, 3)
    w[7].addCollision(w[8], 2, 0)
    w[7].addCollision(w[9], 4, 0)
    w[8].addCollision(w[10], 2, 1)
    w[9].addCollision(w[10], 2, 3)

    dictionary = WordLengthDictionary()
    dictionary.loadFromFile("/usr/share/dict/words")
    xw = Crossword(w, dictionary)
    res = xw.solve()
    print(res)
    assert(res > 0)


if __name__ == "__main__":
    test_medium_crossword()
