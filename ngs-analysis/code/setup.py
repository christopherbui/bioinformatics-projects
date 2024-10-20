import subprocess

def download_sra_data(sra_id, output_dir):
    """
    Download SRA data using SRA Toolkit

    Parameters:
        sra_id (str): Accession id of sequence
        output_dir: Output directory
    """
    try:
        print(f'Downloading {sra_id}...')
        # use 'prefetch' command to download .sra file
        subprocess.run(f'prefetch {sra_id} -0 {output_dir}', shell=True, check=True)

        # convert .sra to .fastq using fastq-dump
        sra_file = f'{output_dir}/{sra_id}/{sra_id}.sra'
        subprocess.run(f'fastq-dump --split-files {sra_file} -0 {output_dir}', shell=True, check=True)

        print(f'Downloaded and converted {sra_id} to FASTQ format.')
    except subprocess.CalledProcessError as e:
        print(f'Error during dowload or conversion: {e}')