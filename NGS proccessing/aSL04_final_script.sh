#!/bin/bash
java -jar /usr/share/java/trimmomatic-0.39.jar PE 004_S4_L001_R1_001.fastq.gz 004_S4_L001_R2_001.fastq.gz s1_pe s1_se s2_pe s2_se SLIDINGWINDOW:6:15 MINLEN:30
cat s1_pe s1_se >> FWD_reads
bwa index Reference/ref.fasta
bwa mem -p -k 30 -O 300 -L 500 -H -M Reference/ref.fasta FWD_reads > slHTS.sam
samtools view -bT Reference/ref.fasta slHTS.sam -o slHTS.bam
samtools sort -o slHTS_sort.bam slHTS.bam
samtools index slHTS_sort.bam
java -jar /home/sl/Documents/picard.jar CleanSam I=slHTS_sort.bam O=slHTS_filt.bam
java -jar /home/sl/Documents/picard.jar CollectAlignmentSummaryMetrics R=Reference/ref.fasta I=slHTS_filt.bam O=aSL04_ex.txt
samtools view -b -F 4 slHTS_filt.bam > slHTS_map.bam
samtools view slHTS_map.bam |sort|less -S > asl04.txt
