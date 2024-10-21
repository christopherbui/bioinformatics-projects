# Next Generation Sequencing Analysis Project

Here we demonstrate automating a traditional next generation sequencing anlaysis pipeline using Python. The steps for NGS analysis are shown in the table below.

| **Step**           | **Description**                            | **Tools**             |
| ------------------ | ------------------------------------------ | --------------------- |
| 1. Download Data   | Fetch raw sequencing data                  | SRA Toolkit, Python   |
| 2. Quality Control | Assess data quality                        | FastQC                |
| 3. Preprocessing   | Trim adapters and filter low-quality reads | Trimmomatic, Cutadapt |
| 4. Alignment       | Align reads to a reference genome          | BWA, Bowtie2          |
| 5. BAM Processing  | Convert, sort, and index BAM files         | Samtools              |
| 6. Variant Calling | Identify SNPs and indels                   | FreeBayes, GATK       |
| 7. Annotation      | Add biological context to variants         | ANNOVAR, SnpEff       |
| 8. Visualization   | Visualize and generate reports             | Pandas, Matplotlib    |



# Data

Sequence Read Achve (SRA) is the largest publicly available respository of high throughput sequencing data.

Sequence data can be downlaoded from:

https://www.ncbi.nlm.nih.gov/sra



# Tools

SRA Toolkit Download: https://github.com/ncbi/sra-tools/wiki/01.-Downloading-SRA-Toolkit



# Background

In NGS, the original genome or transcript is randomly fragmented into small pieces, and these pieces are sequenced. The sequence and its accompanying base quality score encompasses a single read, and multiple reads are in a single FASTQ file.

**Note**: Reads do not represent contiguous segments of the original sequence, since they are randomly fragmented. 

To mitigate gaps in sequence coverage, NGS workflows utilize high coverage and overlapping reads to recover missing information.



There are two types of accession numbers that one might see on NCBI's SRA database: *SRR* and *SRX*.

**SRR (SRA Run)**:

- Example: SRR098283 is the **run** accession.
- It represents the sequencing data generated from a specific sequencing experiment. A single run corresponds to a single sequencing run, which could be a paired-end or single-end dataset
- **Paired-end reads**: Sequencing approach where both ends of DNA/RNA fragment are sequenced, providing 2 complementary reads: one 5' to 3' **(read 1)** and the other 3' to 5' **(read 2)** direction.
  - Tools use both reads to determine correct alignment of fragment to repetitive regions or complex genomes
  - Helps detect insertions, deletions, inversions, or mutations by comparing discrepancies between reads
  - For RNA-seq, helps detect alternative splicing events
  - reads are stored in 2 .fastq file
  - Tools: *BWA*, *Bowtie2*, or *STAR* can align paired-end reads by taking in both FASTQ files

**SRX (SRA Experiment)**:

- Example: SRX040724
- It represens the full experiment, which usually includes multiple runs (multiple SRR accessions).



## Interpreting FASTQ Files

It is common to see file extensions such as FASTQ or FASTA. Both contain nucleotide sequences, but FASTQ contains quality score for each base in the same file.

**Quality score** represented certain ASCII characters:

`!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~

More on Bioinformatics file formats:

- https://bioinformaticsworkbook.org/introduction/fileFormats.html#gsc.tab=0

Traditionally, long sequences are split into multiple reads (each read is 4 lines) within the same file, with "+" or "@" used as seperators. This gets confusing to account for, more so in FASTQ with quality score ASCII characters.

Today, Illumina's software than can do high quality short-reads (~100 base pairs), so every 4 lines in a FASTQ file is a read with information for a 100 fragment of the larger sequence.

Example for 1 read iin FASTQ file

> ```
> @HISEQ:402:H147CADXX:1:1101:1250:2208 1:N:0:CGATGT TGATGCTGCNAATTTTATTCAGTCAGCGGAGGGGGCTTACGTGTATTTTCTGCAACCTTT
> +
> CCCFFFFFH#4AFIJJJJJJJJIJJJJJJJJJJJJJJJJJJHHHHHHFFFFFFFEEEEED
> ```



## Adapter Contamination

**Adapters**: Short DNA sequences ligated to ends of DNA/RNA fragments during library preparation.

Adapters allow for fragments to bind to sequencing flow cell and serve as priming sites for sequencing.

- Sequence flow cell preparation -> Library Preparation Process (bind adapters) -> sequencing -> analysis
- The fragments of Adapters that have ligated to sequence undergo PCR amplification to create enough material for sequencing.

Adapter contamination occurs when adapater sequences are not removed during the sequencing reads. This causes adapter sequences to appear in the raw data and affects analysis including alignment, assembly, and variant calling.

**Causes**:

1. **Short DNA Fragments**: If fragment (i.e. 50bp) is shorter than read length (i.e. 100bp), then sequencer will read into the adapter sequence.
2. **Incomplete Trimming**: Adapter trimming software may miss some adapter sequences, leaving them in the FASTQ reads.
3. **Over-amplification in PCR**: If PCR runs for too many cycles, the adapter-ligand sequences are replicated too many times in sequence, causing multiple adapter copies in single read.
   - Need to apply correct number of PCR cycles (8-12)
   - If over-amplifiication as occurred in reads, use software like `Trimmomatic` or `Cutadapt` to remove them.

# End-To-End NGS Analysis Pipeline

Below are the steps that make up an NGS analysis pipeline:

1. Download Sequencing Data

2. Quality Control

   - **FastQC** is one of the most widely used tools for assesing the quality of NGS data
   - FatsQC generates report for each FASTQ file including: per-base sequence quality, GC content, adapter contamination, duplicated reads
   - `fastqc` command outputs an HTML format

   **Notes**:

   - *Sanger / Illumina 1.9 / Phred+33* refers to the quality score encoding method
     - Q = -10 * log~10~(probability of correct base call)
     - Q's value is mapepd to an ASCII character
   - *%GC* refers to GC content across entire sequence
   - *Per base sequence quality*
     - Observe that base calling quality drops more downstream the sequence we are
     - This plot shows average base call quality (i.e. box and whisker plots) for each base position across all reads

3. Data Preprocessing

   - `trimmomatic` or `cutadapt` removes low quality reads or remaining adapters.
   - The output of remaining good quality reads 
   - `Trimmomatic` download:
     - http://www.usadellab.org/cms/index.php?page=trimmomatic
     - https://github.com/usadellab/Trimmomatic

4. Read Alignment

   - We need to index the reference genome so that the alignment software can perform alignment with the trimmed, paired reads faster. If not, then it would have to linearly scan entire reference genome for every read.
   - Indexing Steps:
     1. Break reference genome into subsequences
     2. Create hash table for the positions of these fragments
     3. Compress & store auxiliary data to optimize searching

   Index files allow alignment software to perform fast lookups and avoid linear searching for every read.

   

   **Common Indexing Tools**:

   - BWA, Bowtie2, SAMtools (short reads)

     - BWA Download: https://github.com/lh3/bwa?tab=readme-ov-file

   - minimap2 (PacBio / Oxford Nanopore long reads)

     


   After BWA indexing, several files are generated:

   | **File**                        | **Description**                                              |
   | ------------------------------- | ------------------------------------------------------------ |
   | **`ref.fa.bwt`**                | The **Burrows-Wheeler Transform (BWT)** of the reference genome. This allows BWA to efficiently search for sequences. |
   | **`ref.fa.pac`**                | **Packed sequence**: Stores the reference genome in a compressed format. |
   | **`ref.fa.ann`**                | **Annotations**: Contains metadata, such as the length of the genome and number of sequences. |
   | **`ref.fa.amb`**                | **Ambiguity information**: Identifies positions with ambiguous bases (e.g., N’s in the reference genome). |
   | **`ref.fa.sa`**                 | **Suffix array**: Speeds up alignment by allowing fast lookups of substrings within the reference genome. |
   | **`ref.fa.fai`** (if generated) | **FASTA index file**: Used by other tools (like **SAMtools**) to quickly access specific regions in the reference. |

   The **BWT (`.bwt`)**, **suffix array (`.sa`)**, and **packed sequence (`.pac`)** are key components of the **BWA-MEM algorithm**. They allow BWA to:

   - **Quickly find potential matches** between the reads and the genome.
   - **Perform alignments efficiently**, even with large genomes.

   **Annotation (`.ann`)** and **ambiguity (`.amb`)** files contain auxiliary information, such as regions in the reference that contain ambiguous bases.

   

​	During alignment, **BWA** uses these index files to:

   1. **Search the genome quickly**: The **BWT** and **suffix array** help BWA search through the reference without scanning every base.

   2. **Identify regions to align reads**: The **packed sequence** and **ambiguity information** ensure that all bases in the genome (including ambiguous ones) are handled correctly.

   3. **Ensure fast access to specific sequences**: Tools like **SAMtools** can use the `.fai` index to quickly access specific parts of the genome.

      Alignment output: **Sequence Alignment Map** (SAM)

      Usuallly convert SAM to BAM (binary alignment map) for faster storage and lookup.



5. Convert SAM to BAM and Sort

6. Variant Calling

   - Identifies genomic variants (SNPs, insertions, deletions) by comparing aligned reads to reference genome.

   **Tools**: 

   - GATK: large, complex genomes (i.e. humans, mammals)
     - BaseRecalibrator, HaplotypeCaller
   - FreeBayes: small genomes; diploi & non-diploid organisms
   - bcftools: lightweight and fast, ideal for bacterial genomes
     - Integrates well with SAMtools for variant calling and filtering

7. Annotation

   Some background: https://www.futurelearn.com/info/courses/making-sense-of-genomic-data-covid-19-web-based-bioinformatics/0/steps/319530

8. Visualization & reporting
