import streamlit as st
import nbformat
from nbconvert import WebPDFExporter

pagebreak = r'''<div style="page-break-after: always; visibility: hidden"> 
\pagebreak 
</div>'''

hidestderr = r'''
<style>
    div.output_stderr {
    display: none !important;
    }
</style>
'''

instructions = r'''
Use this page to convert homework notebooks to PDFs for submission to Gradescope. Please check that **all** answers are fully visible in the output before submitting. The instructor and grutors are not reponsible for grading missing or partially obscured answers.

See the troubleshooting guide below for help resolving common issues.
'''

troubleshooting = r'''
### Troubleshooting

#### Answer cell does not appear in output

Cells marked for answers in the original notebook should be included in the generated output, however edits to the notebook could result in missing answers.

If a cell does not appear in the PDF output, you can force it to appear under a particular question by adding the following line at the top of the cell:

```
#! QX
```

Where `X` is the question number. This works with both markdown and Python cells.

#### Cell output does not appear

Make sure to run the full notebook and *save* it before converting. The outputs should be included in the `.ipynb` file.

#### Figures go off the page

Make sure that all figures are fully visible. See [this StackOverflow post](https://stackoverflow.com/questions/332289/how-do-i-change-the-size-of-figures-drawn-with-matplotlib) for how to set figure sizes in Matplotlib.

'''

st.title('CS152 Notebook Converter')
st.markdown(instructions)
uploaded_file = st.file_uploader("Choose an ipynb file to convert to PDF for submission")
if uploaded_file is not None:
    # To read file as bytes:
    with st.spinner('Converting...'):
        nb = nbformat.read(uploaded_file, 4)
        cells = [nbformat.v4.new_markdown_cell(source=hidestderr)]
        for question in range(20):
            qstr = f'Q{question}'
            if question > 0:
                cells.append(nbformat.v4.new_markdown_cell(source='# ' + qstr))
            else:
                cells.append(nbformat.v4.new_markdown_cell(source='CS152 Submission'))

            for cell in nb.cells:
                checksource = cell.source.strip().replace(' ', '').find('#!' + qstr) == 0
                if ('tags' in cell.metadata and qstr in cell.metadata.tags) or checksource:
                    if checksource:
                        cell.source = '\n'.join(cell.source.splitlines()[1:])
                    cell.outputs = [c for c in cell.outputs if not ('name' in c and c.name == 'stderr')]
                    cells.append(cell)
                    
            cells.append(nbformat.v4.new_markdown_cell(source=pagebreak))

        output = nbformat.v4.new_notebook()
        output.cells = cells
        (pdf, _) = WebPDFExporter(allow_chromium_download=True, embed_images=True).from_notebook_node(output)
        st.download_button('Download PDF', pdf, file_name='submission.pdf') 

st.markdown(troubleshooting)