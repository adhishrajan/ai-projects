import sys
from copy import deepcopy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        copy = deepcopy(self.domains)

        for x in self.domains:
            length = x.length
            for v in copy[x]:
                if len(v) != length:
                    self.domains[x].remove(v)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revised = False
        overx, overy = self.crossword.overlaps[x, y]

        if overx:

            for a in self.domains[x]:
                found = False

                for b in self.domains[y]:
                    if a[overx] == b[overy]:
                        found = True
            if not found:
                self.domains[x].remove(a)
                revised = True

        return revised

                             
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs == None:
            #  If `arcs` is None, begin with initial list of all arcs in the problem.
            queue = []
            for v1 in self.domains:
                for v2 in self.crossword.neighbors(v1):
                    if self.crossword.overlaps[v1, v2] != None:
                        queue.append((v1, v2))

        while len(queue) > 0:
            # Otherwise, use `arcs` as the initial list of arcs to make consistent.
            # pop first value in queue and apply ac3
            i, j = queue.pop(0)
            if self.revise(i, j):
                if len(self.domains[i]) == 0:
                    return False
                for each in self.crossword.neighbors(i):
                    if each != j:
                        queue.append((each, i))
            return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """


        for a in self.crossword.variables:
            if a not in assignment.keys():
                return False
            if assignment[a] not in self.crossword.words:
                return False

        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """


        # checking correct lengths
        for check1 in assignment:
            if len(assignment[check1]) != check1.length:
                return False

        # checking for distict values
        check2 = [*assignment.values()]
        if len(check2) != len(set(check2)):
            return False

        # checking for conflicts with neighbors
        for check3 in assignment:
            for each in self.crossword.neighbors(check3):
                if each in assignment:
                    i, j = self.crossword.overlaps[check3, each]
                    if assignment[check3][i] != assignment[each][j]:
                        return False

     
        return True
            
        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # nearby = all neighbors of var
        nearby = self.crossword.neighbors(var)
        
        for a in assignment:
            # delete the Variable from nearby if it has already been assigned
            if a in nearby:
                nearby.remove(a)

        # we will sort this array by constraints once filled
        sortedlist = []
        for s in self.domains[var]:
            numruleout = 0  # set the number of values the variable rules out to 0 initially
            for n in nearby:
                for x in self.domains[n]:
                    overlap = self.crossword.overlaps[var, n]


                    if overlap:
                        i, j = overlap
                        # they can be ruled out if overlaps do not equal eachother
                        if s[i] != x[j]:
                            numruleout = numruleout + 1
           
            sortedlist.append([s, numruleout])

        # sorting the list in order by the number of values they rule out for neighboring variables
        sortedlist.sort(key = lambda y: y[1])

        # return sortedlist, but remove numruleout in each instance
        return [final[0] for final in sortedlist] 


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        varss = []
        for c in self.crossword.variables: 
            if c not in assignment:  
               # add all unassigned variables to varss array
                varss.append([c, len(self.domains[c]), len(self.crossword.neighbors(c))])

        # sort potential variables by the number of domain options (ascending) and number of neighbors (descending)
        if len(varss) != 0:
            varss.sort(key = lambda f: (f[1], -f[2]))
            # return first variable after sorting
            return varss[0][0]

       
        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            copy = assignment.copy()
            copy[var] = value
            if self.consistent(copy):
                result = self.backtrack(copy)
                if result is not None:
                    return result
        
        return None
                
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()