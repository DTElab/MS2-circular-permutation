#!/bin/bash
MS2_CP='GCGTCGAACTTTACGCAATTCGTGCTCGTAGACAACGGAGGGACAGGTGACGTAACTGTGGCCCCGAGTAACTTCGCGAATGGCGTCGCCGAGTGGATCTCCAGCAATTCTCGCAGCCAAGCTTATAAAGTTACCTGTAGTGTGCGGCAGAGCTCAGCGCAGAACCGTAAATACACGATTAAAGTTGAAGTACCAAAAGTGGCAACCCAGACCGTGGGCGGCGTCGAACTGCCGGTCGCAGCCTGGCGCAGCTATCTGAACATGGAATTAACCATTCCGATCTTTGCGACGAATTCCGATTGCGAGCTGATTGTTAAAGCTATGCAGGGTTTGCTGAAGGATGGCAATCCCATTCCTTCGGCGATAGCCGCAAACTCAGGTATCTACGCGTCGAACTTTACGCAATTCGTGCTCGTAGACAACGGAGGGACAGGTGACGTAACTGTGGCCCCGAGTAACTTCGCGAATGGCGTCGCCGAGTGGATCTCCAGCAATTCTCGCAGCCAAGCTTATAAAGTTACCTGTAGTGTGCGGCAGAGCTCAGCGCAGAACCGTAAATACACGATTAAAGTTGAAGTACCAAAAGTGGCAACCCAGACCGTGGGCGGCGTCGAACTGCCGGTCGCAGCCTGGCGCAGCTATCTGAACATGGAATTAACCATTCCGATCTTTGCGACGAATTCCGATTGCGAGCTGATTGTTAAAGCTATGCAGGGTTTGCTGAAGGATGGCAATCCCATTCCTTCGGCGATAGCCGCAAACTCAGGTATCTAC'
FWD='GCTCTTAAAGAGGAGAAAGGTCATG'
REV='TAAAAGCTTGGCTGTTTTGGC'
termin='\n'
op='>'
for i in {0..128}
do
	a=$((3*i))
	b=$((i+1))
	echo $op$b >> ref.fasta
	echo ${FWD}${MS2_CP:$a:387}${REV} >> ref.fasta
done
