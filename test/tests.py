import doctest
import bioino as bn

if __name__ == '__main__':

    doctest.testmod(bn.gff)
    doctest.testmod(bn.fasta)
    doctest.testmod(bn.table2fasta)