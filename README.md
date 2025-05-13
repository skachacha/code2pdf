# code2pdf

Simple Python script that converts source code files in the current directory into syntax-highlighted PDF documents.

It uses **Pygments** for syntax highlighting and **wkhtmltopdf** for PDF generation

## Requirements

* Python 3.x
* Pygments: `pip install Pygments`
* wkhtmltopdf: Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
  * Windows users can `winget install --id=wkhtmltopdf.wkhtmltox  -e`
  * Make sure it's in your system's PATH.

## Usage

1.  Place the script convert.py in the directory containing the code files you want to convert.
2.  Run it.
3.  Yippee!
