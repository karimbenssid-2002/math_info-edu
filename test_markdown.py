import markdown
import re
text = """
Il existe plusieurs types de variables :
* **Entiers (int)** : Les nombres entiers comme `42`
* **Flottants (float)** : Les nombres à virgule comme `3.14`

Dans un repère $(O, \\vec{i}, \\vec{j})$, si $A(x_A, y_A)$ et $B(x_B, y_B)$ :
$\\vec{AB} \\begin{pmatrix} x_B - x_A \\\\ y_B - y_A \\end{pmatrix}$
"""

# Fix missing blank lines before lists (if a list item follows a non-empty line)
# We can just blindly add a newline before any list item if it's the first one, or easier: 
# Replace \n followed by * or - with \n\n if the previous line wasn't empty
fixed_text = re.sub(r'([^\n])\n([*+-] )', r'\1\n\n\2', text)
print("FIXED TEXT:\n", fixed_text)
print("HTML:")
print(markdown.markdown(fixed_text, extensions=['mdx_math', 'sane_lists'], extension_configs={'mdx_math': {'enable_dollar_delimiter': True}}))
