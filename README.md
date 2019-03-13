# bcl2fq-local

A bcl2fastq wrapper

# Usage
```text
usage:  bcl2fq-local -i <seq_dir> -o <ou_dir>
    
optional arguments:
    --sample-sheet Path  Using custom sample sheet file
    --mismatch N         Mismatch for barcode, default: 1
    --process N          Process number for demultiplexing and processing
    --io-process N       Process number for reading and writing
    --binpath   Path     Bcl2fastq binary file path
    --cmd-only           Only print the cmd without running it
```

