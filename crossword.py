class WordLengthDictionary:
    def __init__(self, wordlist=[]):
        self.sets = dict()
        for word in wordlist:
            self.set(word)

    def loadFromFile(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.set(line.strip())

    def set(self, word):
        length = len(word)
        if length not in self.sets:
            self.sets[length] = list()
        self.sets[length].append(word.lower())


class Word:
    def __init__(self, length):
        self.length = length
        self.collisions = {}
        self.letters = [None] * self.length

    def addCollision(self, rhs, selfIndex, rhsIndex):
        if selfIndex < 0:
            selfIndex = self.length + selfIndex
        if rhsIndex < 0:
            rhsIndex = rhs.length + rhsIndex
        assert selfIndex < self.length and rhsIndex < rhs.length and selfIndex >= 0 and rhsIndex >= 0
        self.collisions[selfIndex] = (rhs, rhsIndex)
        rhs.collisions[rhsIndex] = (self, selfIndex)

    def solutions(self, worddict):
        wordset = worddict.sets[self.length]
        solutions = []
        for word in wordset:
            if self.fits(word):
                solutions.append(word)

        return solutions

    def fits(self, word):
        if len(word) != self.length:
            return False
        for index, collision in self.collisions.items():
            letter = collision[0].letters[collision[1]]
            if letter is not None and word[index] != letter:
                return False

        return True

    def set(self, word):
        assert self.fits(word), "oh no!"
        self.letters = list(word)

    def clear(self):
        self.letters = [None] * self.length

    def __bool__(self):
        return self.letters != [None] * self.length

    def __len__(self):
        return self.length

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "".join([i if i is not None else "_" for i in self.letters])


class Crossword:
    def __init__(self, words, dictionary=WordLengthDictionary()):
        self.words = words
        self.dictionary = dictionary

    def assertConnected(self):
        words = [self.words[0]]
        seen = []
        while words:
            w = words.pop()
            seen.append(w)
            for target, idx in w.collisions.values():
                if target not in seen:
                    words.append(target)

        for w in self.words:
            assert w in seen, f"{self.words.index(w)} is not connected!"
        for w in seen:
            assert w in self.words


    def solve(self):
        self.assertConnected()
        return self.solveByHand()
        return self.solveLongestFirst()

    def solveByHand(self):
        unsolvedWords = [w for w in self.words if not w]
        solutions = []
        skipped = []
        while unsolvedWords + skipped:
            sortedWords = sorted(unsolvedWords, key=lambda w: len(w.solutions(self.dictionary))) + skipped
            word = sortedWords[0]
            word.letters = ['☐'] * word.length
            self.render()
            word.clear()
            print(self.words.index(word) + 1, ":", word)
            print(word.solutions(self.dictionary))
            ans = ""

            while ans not in word.solutions(self.dictionary):
                blank = False
                ans = input("Please enter a solution: ")
                if not ans:
                    ans = input("Please enter a solution (leave blank to skip):")
                    if not ans:
                        blank = True
                        break
                        print("skipping.")

            if word in unsolvedWords:
                unsolvedWords.remove(word)
            if word in skipped:
                skipped.remove(word)

            if blank:
                skipped.append(word)
                continue

            word.set(ans)
            solutions.append(word)

        print("Your answers:")
        for sol in solutions:
            #print(self.words.index(sol), ":", sol)
            print(f"w[{self.words.index(sol)}].set(\"{sol}\")")

        self.render()


    def solveLongestFirst(self):
        unsolvedWords = [w for w in self.words if not w]
        sortedWords = sorted(unsolvedWords, key=len, reverse=True)
        return self.solveSubset(sortedWords)

    def solveSubset(self, subset):
        if len(subset) == 0:
            print("SOLVED!")
            self.render()
            exit()
            return 1

        word = subset.pop(0)
        count = 0
        for solution in word.solutions(self.dictionary):
            word.set(solution)
            count += self.solveSubset(subset[:])
            word.clear()

        return count

    def render(self):
        # last word will be 0,0
        w = self.words[-1]
        coords = {w: (0,0)}
        isAcross = {w: True}
        unmappedWords = [w]

        # build coordinates and orientations for all words
        while unmappedWords:
            w = unmappedWords.pop(0)
            for wordIndex, (target, targetIndex) in w.collisions.items():
                if isAcross[w]:
                    delta = (wordIndex, targetIndex)
                else:
                    delta = (-targetIndex, -wordIndex)
                newCoords = (coords[w][0] + delta[0], coords[w][1] + delta[1])

                if target in coords:
                    assert coords[target] == newCoords
                    assert isAcross[target] != isAcross[w]
                else:
                    isAcross[target] = not isAcross[w]
                    coords[target] = newCoords
                    unmappedWords.append(target)

        for w in self.words:
            assert w in coords
            if w not in coords:
                breakpoint()

        # update coords to help in drawing
        minx = min([i[0] for i in coords.values()])
        miny = min([i[1] for i in coords.values()])

        maxx = max([i[0] for i in coords.values()])
        maxy = max([i[1] for i in coords.values()])


        for k in coords.keys():
            v = coords[k]
            coords[k] = (v[0] - minx, (maxy - (v[1] - miny)))

        maxlen = max([w.length for w in self.words])

        x_size = maxx + maxlen
        y_size = maxy + maxlen

        canvas = [[' '] * y_size for i in range(x_size)]

        # number the words, helps when debugging
        #for idx in range(len(self.words)):
        #    num = str(idx + 1)
        #    for idxWord in range(len(num)):
        #        self.words[idx].letters[idxWord] = num[idxWord]

        for word, coord in coords.items():
            for i in range(word.length):
                letter = word.letters[i]
                if not letter and i in word.collisions:
                    col = word.collisions[i]
                    letter = col[0].letters[col[1]]

                if isAcross[word]:
                    canvas[coord[1]][coord[0] + i] = letter
                else:
                    canvas[coord[1] + i][coord[0]] = letter


        for line in canvas:
            line = [i if i else '_' for i in line]
            strline = ''.join(line).rstrip()
            if strline:
                print(strline)

        return canvas




